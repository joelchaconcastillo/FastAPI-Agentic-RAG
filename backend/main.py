from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import chromadb
import os
import json
import asyncio
import uuid

# Import provider clients
try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

app = FastAPI(title="FastAPI Agentic RAG")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB for memory
chroma_client = chromadb.PersistentClient(path="/app/chroma_db")

# Get or create collection for conversation history
try:
    collection = chroma_client.get_collection(name="conversation_history")
except Exception:
    collection = chroma_client.create_collection(name="conversation_history")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    provider: str = "openai"  # openai or gemini
    conversation_id: Optional[str] = None


class RAGAgent:
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if provider == "openai" and openai and self.openai_api_key:
            openai.api_key = self.openai_api_key
        elif provider == "gemini" and genai and self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
    
    def get_relevant_context(self, query: str, conversation_id: str, n_results: int = 3):
        """Retrieve relevant context from ChromaDB"""
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"conversation_id": conversation_id} if conversation_id else None
            )
            
            if results and results['documents']:
                return "\n".join(results['documents'][0])
            return ""
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
    
    def store_message(self, message: str, role: str, conversation_id: str):
        """Store message in ChromaDB for memory"""
        try:
            doc_id = str(uuid.uuid4())
            collection.add(
                documents=[message],
                metadatas=[{"role": role, "conversation_id": conversation_id}],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"Error storing message: {e}")
    
    async def generate_streaming_response(self, user_message: str, conversation_id: str):
        """Generate streaming response from the selected provider"""
        # Send conversation ID first
        yield f"data: {json.dumps({'type': 'conversation_id', 'content': conversation_id})}\n\n"
        await asyncio.sleep(0.01)
        
        # Store user message
        self.store_message(user_message, "user", conversation_id)
        
        # Get relevant context
        context = self.get_relevant_context(user_message, conversation_id)
        
        # Build prompt with context
        system_prompt = "You are a helpful AI assistant with access to conversation history."
        if context:
            system_prompt += f"\n\nRelevant context from previous conversation:\n{context}"
        
        # Send thinking status
        yield f"data: {json.dumps({'type': 'thinking', 'content': 'Analyzing your question...'})}\n\n"
        await asyncio.sleep(0.1)
        
        if self.provider == "openai" and openai and self.openai_api_key:
            async for chunk in self._stream_openai(system_prompt, user_message, conversation_id):
                yield chunk
        elif self.provider == "gemini" and genai and self.gemini_api_key:
            async for chunk in self._stream_gemini(system_prompt, user_message, conversation_id):
                yield chunk
        else:
            yield f"data: {json.dumps({'type': 'error', 'content': f'Provider {self.provider} not configured or available'})}\n\n"
    
    async def _stream_openai(self, system_prompt: str, user_message: str, conversation_id: str):
        """Stream response from OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True,
                temperature=0.7
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.get("content"):
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                    await asyncio.sleep(0.01)
            
            # Store assistant response
            self.store_message(full_response, "assistant", conversation_id)
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    async def _stream_gemini(self, system_prompt: str, user_message: str, conversation_id: str):
        """Stream response from Gemini"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Combine system prompt with user message
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            
            response = model.generate_content(
                full_prompt,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.text})}\n\n"
                    await asyncio.sleep(0.01)
            
            # Store assistant response
            self.store_message(full_response, "assistant", conversation_id)
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@app.get("/")
async def root():
    return {"message": "FastAPI Agentic RAG with ChromaDB"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat")
async def chat(request: ChatRequest):
    """Stream chat responses"""
    conversation_id = request.conversation_id or str(uuid.uuid4())
    agent = RAGAgent(provider=request.provider)
    
    return StreamingResponse(
        agent.generate_streaming_response(request.message, conversation_id),
        media_type="text/event-stream"
    )


@app.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history from ChromaDB"""
    try:
        results = collection.get(
            where={"conversation_id": conversation_id}
        )
        
        messages = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents']):
                metadata = results['metadatas'][i]
                messages.append({
                    "role": metadata.get("role", "unknown"),
                    "content": doc
                })
        
        return {"conversation_id": conversation_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

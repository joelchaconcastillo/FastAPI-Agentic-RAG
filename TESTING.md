# Testing Guide

This guide shows how to test the FastAPI Agentic RAG system.

## Prerequisites

- Docker and Docker Compose installed
- At least one API key (OpenAI or Gemini)

## Quick Start

1. **Setup**
   ```bash
   ./setup.sh
   ```

2. **Manual Setup** (alternative)
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Edit .env and add your API keys
   nano .env
   
   # Build and start services
   docker compose up --build
   ```

## Testing Steps

### 1. Verify Services are Running

```bash
# Check running containers
docker compose ps

# Should see both services running:
# - fastapi-rag-backend (port 8000)
# - fastapi-rag-frontend (port 3000)
```

### 2. Test Backend API

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Root endpoint
curl http://localhost:8000/
# Expected: {"message":"FastAPI Agentic RAG with ChromaDB"}

# API Documentation
# Visit: http://localhost:8000/docs
```

### 3. Test Chat Functionality

#### Using curl (with OpenAI):
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, who are you?",
    "provider": "openai"
  }'
```

#### Using curl (with Gemini):
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 2+2?",
    "provider": "gemini"
  }'
```

You should see streaming responses in Server-Sent Events format:
```
data: {"type": "thinking", "content": "Analyzing your question..."}

data: {"type": "token", "content": "Hello"}

data: {"type": "token", "content": "!"}

data: {"type": "done", "content": ""}
```

### 4. Test Frontend UI

1. Open browser to http://localhost:3000
2. You should see a chat interface with:
   - Header with "FastAPI Agentic RAG" title
   - Provider selector (OpenAI/Gemini)
   - Chat messages area
   - Input box and Send button

3. **Test conversation flow:**
   - Type a message: "Hello, what can you do?"
   - Click Send or press Enter
   - You should see:
     - Your message appears immediately
     - "Thinking..." status appears briefly
     - Response streams in token by token (real-time)
     - Cursor animation shows active streaming

4. **Test conversation memory:**
   - Ask: "What is the capital of France?"
   - Wait for response
   - Ask: "What did I just ask you?"
   - The AI should remember the context using ChromaDB

5. **Test provider switching:**
   - Switch between OpenAI and Gemini in the dropdown
   - Send messages to test both providers work

6. **Test new conversation:**
   - Click "New Conversation" button
   - Previous messages are cleared
   - Start a fresh conversation

### 5. Test Memory Persistence

```bash
# Stop services
docker compose down

# Start again
docker compose up -d

# The ChromaDB data should persist in the volume
# Previous conversations are still stored
```

### 6. View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### 7. Test ChromaDB Storage

```bash
# Get conversation history (replace with actual conversation_id)
curl http://localhost:8000/conversations/YOUR_CONVERSATION_ID

# Should return stored messages
```

## Expected Behavior

### Real-time Streaming
- ✅ "Thinking..." message appears before response
- ✅ Response appears token by token (not all at once)
- ✅ Blinking cursor shows active streaming
- ✅ No freezing or blocking

### Memory/RAG
- ✅ Context is maintained within a conversation
- ✅ AI can reference previous messages
- ✅ Data persists across container restarts
- ✅ Different conversations are isolated

### Multi-provider Support
- ✅ Can switch between OpenAI and Gemini
- ✅ Both providers stream responses
- ✅ Error messages if API key is missing/invalid

### Docker Integration
- ✅ Both containers run on same network
- ✅ Frontend can communicate with backend
- ✅ ChromaDB volume persists data
- ✅ Containers restart on failure
- ✅ Health checks monitor backend status

## Troubleshooting

### Backend not starting
```bash
docker compose logs backend
```
- Check API keys are set in .env
- Verify port 8000 is not in use

### Frontend not loading
```bash
docker compose logs frontend
```
- Verify port 3000 is not in use
- Check backend is running first

### API errors
- Ensure API keys are valid and active
- Check rate limits on your API accounts
- View detailed logs: `docker compose logs -f backend`

### Connection errors
- Ensure both containers are on same network
- Check docker compose networking: `docker network ls`
- Verify CORS is enabled (already configured)

## Cleanup

```bash
# Stop services
docker compose down

# Stop and remove volumes (clears ChromaDB data)
docker compose down -v

# Remove images
docker rmi fastapi-agentic-rag-backend fastapi-agentic-rag-frontend
```

## Performance Testing

### Load Test with curl
```bash
# Send 10 concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\", \"provider\": \"openai\"}" &
done
```

### Monitor Resources
```bash
# Monitor container stats
docker stats

# Should show CPU and memory usage for both containers
```

## Success Criteria

- ✅ Backend builds and starts without errors
- ✅ Frontend builds and serves static files
- ✅ Both services communicate over Docker network
- ✅ API endpoints respond correctly
- ✅ Real-time streaming works in browser
- ✅ ChromaDB persists conversation data
- ✅ Both OpenAI and Gemini providers work
- ✅ UI is responsive and shows streaming
- ✅ Containers restart automatically on failure
- ✅ Data persists across container restarts

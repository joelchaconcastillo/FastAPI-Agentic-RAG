# FastAPI-Agentic-RAG

A full-stack Dockerized application featuring a FastAPI backend with RAG (Retrieval-Augmented Generation) capabilities, ChromaDB for memory persistence, support for multiple AI providers (OpenAI and Gemini), and a React frontend with real-time streaming responses.

## Features

- 🚀 **FastAPI Backend**: High-performance async API with streaming support
- 🧠 **RAG with Memory**: ChromaDB integration for conversation history and context retrieval
- 🔄 **Real-time Streaming**: Server-Sent Events (SSE) for live response streaming
- 🤖 **Multiple AI Providers**: Support for both OpenAI and Google Gemini
- ⚛️ **React Frontend**: Modern UI with real-time chat interface
- 🐳 **Full Docker Support**: Complete docker-compose setup with networking
- 💾 **Persistent Storage**: ChromaDB data persisted across container restarts

## Architecture

```
┌─────────────────┐         Docker Network (rag-network)         ┌─────────────────┐
│                 │                                               │                 │
│  React Frontend │◄─────────────────────────────────────────────►│  FastAPI Backend│
│   (Port 3000)   │         Real-time SSE Streaming               │   (Port 8000)   │
│                 │                                               │                 │
└─────────────────┘                                               └────────┬────────┘
                                                                           │
                                                                           │
                                                                  ┌────────▼────────┐
                                                                  │    ChromaDB     │
                                                                  │  (Persistent)   │
                                                                  └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- API keys for at least one provider:
  - OpenAI API key (for GPT models)
  - Google Gemini API key

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/joelchaconcastillo/FastAPI-Agentic-RAG.git
   cd FastAPI-Agentic-RAG
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
FastAPI-Agentic-RAG/
├── backend/
│   ├── main.py              # FastAPI application with RAG logic
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend Docker configuration
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component with streaming
│   │   ├── App.css         # Styling
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # Node dependencies
│   ├── nginx.conf          # Nginx configuration
│   └── Dockerfile          # Frontend Docker configuration
├── docker-compose.yml       # Docker Compose orchestration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## API Endpoints

### POST /chat
Stream chat responses with RAG capabilities.

**Request Body:**
```json
{
  "message": "Your question here",
  "provider": "openai",  // or "gemini"
  "conversation_id": "optional-conversation-id"
}
```

**Response:** Server-Sent Events stream with:
- `thinking`: Agent processing status
- `token`: Streamed response tokens
- `done`: Completion signal
- `error`: Error messages

### GET /conversations/{conversation_id}
Retrieve conversation history from ChromaDB.

### GET /health
Health check endpoint.

## How It Works

### Real-time Streaming
The application uses Server-Sent Events (SSE) to provide real-time feedback:

1. User sends a message from the frontend
2. Backend streams status updates ("thinking...")
3. AI provider generates response token-by-token
4. Each token is immediately sent to frontend
5. User sees the response being generated in real-time

### RAG with Memory
The system maintains conversation context using ChromaDB:

1. User messages are stored in ChromaDB with conversation ID
2. For each new query, relevant previous context is retrieved
3. Context is included in the prompt to the AI provider
4. Responses are stored back to maintain conversation history

### Multi-Provider Support
The backend abstracts different AI providers:

- **OpenAI**: Uses GPT-3.5-turbo with streaming
- **Gemini**: Uses Google's Gemini Pro with streaming

Switch providers in the frontend UI without code changes.

## Development

### Running Backend Locally
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Running Frontend Locally
```bash
cd frontend
npm install
npm start
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Google Gemini API key
- `REACT_APP_BACKEND_URL`: Backend URL (default: http://localhost:8000)

## Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start services in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild a specific service
docker-compose build backend
docker-compose build frontend

# Remove volumes (clears ChromaDB data)
docker-compose down -v
```

## Features Explained

### ChromaDB Persistence
- Conversation history is stored in a Docker volume
- Data persists across container restarts
- Each conversation has a unique ID for context retrieval

### Docker Network
- Both containers run on a custom bridge network (`rag-network`)
- Services can communicate using container names
- Isolated from other Docker networks

### Health Checks
- Backend includes health check endpoint
- Docker monitors container health
- Automatic restart on failure

## Troubleshooting

**Port already in use:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "3001:80"    # Frontend
```

**API key errors:**
- Ensure .env file is in the root directory
- Check that API keys are valid and active
- Restart containers after updating .env

**ChromaDB errors:**
- Clear the volume: `docker-compose down -v`
- Rebuild: `docker-compose up --build`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- ChromaDB for vector database capabilities
- OpenAI and Google for AI provider APIs
- React for the frontend framework
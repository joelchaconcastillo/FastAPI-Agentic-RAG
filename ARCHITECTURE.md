# Architecture Documentation

## System Overview

The FastAPI Agentic RAG system is a full-stack application that provides AI-powered conversational capabilities with memory persistence. It's built with a microservices architecture using Docker containers.

## Components

### 1. Backend (FastAPI)
- **Technology**: Python 3.11, FastAPI, Uvicorn
- **Port**: 8000
- **Responsibilities**:
  - Handle incoming chat requests
  - Stream responses using Server-Sent Events (SSE)
  - Manage AI provider integrations (OpenAI, Gemini)
  - Store and retrieve conversation history
  - Coordinate with ChromaDB for RAG functionality

### 2. Frontend (React)
- **Technology**: React 18, Nginx
- **Port**: 3000
- **Responsibilities**:
  - Provide user interface for chat
  - Handle real-time streaming from backend
  - Display thinking status and responses
  - Manage provider selection
  - Handle conversation state

### 3. ChromaDB (Vector Database)
- **Technology**: ChromaDB with persistent storage
- **Storage**: Docker volume (chroma_data)
- **Responsibilities**:
  - Store conversation messages
  - Enable semantic search for context retrieval
  - Provide memory for RAG functionality
  - Persist data across container restarts

## Data Flow

### Chat Request Flow
```
User Input → Frontend → Backend → AI Provider
                ↓           ↓
            Display    ChromaDB Store
            
AI Response → Backend → Frontend → User Display
   (stream)      ↓
              ChromaDB
```

### Detailed Flow:
1. **User sends message**
   - Frontend captures input
   - POST request to /chat endpoint
   - Opens SSE stream connection

2. **Backend processing**
   - Receives message and conversation ID
   - Queries ChromaDB for relevant context
   - Builds prompt with context
   - Sends "thinking" status

3. **AI Provider interaction**
   - Streams request to OpenAI or Gemini
   - Receives token-by-token response
   - Forwards tokens to frontend via SSE

4. **Memory storage**
   - User message stored in ChromaDB
   - Assistant response stored in ChromaDB
   - Tagged with conversation ID

5. **Frontend display**
   - Receives SSE events
   - Updates UI in real-time
   - Shows streaming cursor
   - Accumulates full response

## Real-time Communication

### Server-Sent Events (SSE)
The system uses SSE for real-time streaming:

```
Event Types:
- thinking: Agent is processing
- token: Individual response tokens
- done: Stream complete
- error: Error occurred
```

### Benefits:
- Unidirectional server-to-client
- Built-in reconnection
- Simple HTTP-based protocol
- Works through firewalls/proxies

## RAG Implementation

### Retrieval-Augmented Generation:
1. **Store**: Messages saved with embeddings
2. **Retrieve**: Semantic search for relevant context
3. **Augment**: Add context to AI prompt
4. **Generate**: AI produces contextual response

### ChromaDB Usage:
```python
# Store message
collection.add(
    documents=[message],
    metadatas=[{"role": role, "conversation_id": id}],
    ids=[unique_id]
)

# Retrieve context
results = collection.query(
    query_texts=[query],
    n_results=3,
    where={"conversation_id": id}
)
```

## Docker Architecture

### Network:
- **Name**: rag-network
- **Type**: Bridge network
- **Purpose**: Isolate and connect containers

### Volumes:
- **chroma_data**: Persists ChromaDB data
- **Location**: Docker managed volume

### Container Communication:
```
Frontend Container (port 3000)
        ↓ HTTP requests
Backend Container (port 8000)
        ↓ writes/reads
ChromaDB Volume (persistent)
```

## Multi-Provider Support

### Provider Abstraction:
```
RAGAgent
  ├── OpenAI Provider
  │   └── GPT-3.5-turbo (streaming)
  └── Gemini Provider
      └── Gemini Pro (streaming)
```

### Selection:
- User selects provider in UI
- Request includes provider parameter
- Backend routes to appropriate handler
- Both support streaming responses

## Security Considerations

### API Keys:
- Stored in .env file (not committed)
- Passed as environment variables
- Not exposed to frontend

### CORS:
- Enabled for cross-origin requests
- Allows frontend-backend communication
- Configured in FastAPI middleware

### Network Isolation:
- Containers on private network
- Only exposed ports accessible
- Database not directly accessible

## Scalability Considerations

### Horizontal Scaling:
- Backend: Multiple instances behind load balancer
- Frontend: Multiple instances with shared volume
- ChromaDB: Consider cluster mode for production

### Current Limitations:
- Single ChromaDB instance
- No load balancing
- No caching layer

### Future Improvements:
- Redis for session management
- Load balancer (Nginx/Traefik)
- Kubernetes deployment
- Message queue for async processing

## Monitoring and Health

### Health Checks:
```yaml
backend:
  healthcheck:
    test: curl -f http://localhost:8000/health
    interval: 30s
    timeout: 10s
    retries: 3
```

### Logging:
- stdout/stderr captured by Docker
- View with: `docker compose logs -f`
- Structured JSON logging (optional)

### Metrics (Future):
- Request count
- Response times
- Error rates
- Token usage

## Development vs Production

### Development (docker-compose.dev.yml):
- Hot reloading enabled
- Source code mounted as volumes
- Debug logging
- Single instance of each service

### Production (docker-compose.yml):
- Optimized builds
- No hot reloading
- Production logging
- Health checks enabled
- Restart policies configured

## File Structure
```
FastAPI-Agentic-RAG/
├── backend/
│   ├── main.py              # FastAPI app + RAG logic
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container config
├── frontend/
│   ├── src/
│   │   ├── App.js          # React app with streaming
│   │   └── App.css         # Styling
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # Node dependencies
│   ├── nginx.conf          # Nginx config
│   └── Dockerfile          # Frontend container config
├── docker-compose.yml       # Production setup
├── docker-compose.dev.yml   # Development setup
├── .env.example            # Environment template
├── setup.sh                # Setup script
├── README.md               # User guide
├── TESTING.md              # Testing guide
└── ARCHITECTURE.md         # This file
```

## API Endpoints

### POST /chat
- **Purpose**: Stream chat responses
- **Input**: `{message, provider, conversation_id?}`
- **Output**: SSE stream of tokens
- **Authentication**: API keys via env vars

### GET /conversations/{id}
- **Purpose**: Retrieve conversation history
- **Input**: conversation_id in path
- **Output**: `{conversation_id, messages[]}`

### GET /health
- **Purpose**: Health check
- **Output**: `{status: "healthy"}`

### GET /
- **Purpose**: API info
- **Output**: `{message: "..."}`

## Environment Variables

### Backend:
- `OPENAI_API_KEY`: OpenAI API key
- `GEMINI_API_KEY`: Google Gemini API key

### Frontend:
- `REACT_APP_BACKEND_URL`: Backend URL (default: http://localhost:8000)

## Technology Stack

### Backend:
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **ChromaDB**: Vector database
- **OpenAI SDK**: GPT integration
- **Google Generative AI**: Gemini integration
- **Pydantic**: Data validation

### Frontend:
- **React**: UI framework
- **Nginx**: Web server
- **HTML5**: EventSource API for SSE

### Infrastructure:
- **Docker**: Containerization
- **Docker Compose**: Orchestration
- **Linux**: Base OS (Python 3.11 slim)

## Performance Characteristics

### Response Times:
- Health check: <10ms
- Chat initiation: 50-100ms
- First token: 500-2000ms (depends on AI provider)
- Subsequent tokens: 20-50ms each

### Resource Usage:
- Backend: ~200MB RAM, minimal CPU
- Frontend: ~50MB RAM, minimal CPU
- ChromaDB: Varies with data size

## Best Practices

### Development:
1. Use docker-compose.dev.yml for local work
2. Test with both providers
3. Check logs regularly
4. Clear volumes when testing fresh state

### Production:
1. Use docker-compose.yml
2. Set strong API keys
3. Enable HTTPS (add reverse proxy)
4. Monitor logs and metrics
5. Regular backups of ChromaDB volume
6. Rate limiting (future enhancement)

## Troubleshooting Guide

### Backend won't start:
- Check API keys in .env
- Verify port 8000 available
- Check Docker logs

### Frontend can't connect:
- Verify backend is running
- Check network configuration
- Confirm CORS settings

### Streaming not working:
- Check SSE support in browser
- Verify API key is valid
- Check network connectivity

### Memory issues:
- Clear ChromaDB: `docker compose down -v`
- Check conversation IDs
- Verify data persistence

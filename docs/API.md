# OpenSuperWhisper API Documentation

## Overview

OpenSuperWhisper provides a RESTful API for audio transcription and text formatting services. The API is built with FastAPI and includes automatic interactive documentation.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses environment variables for OpenAI API key configuration. Future versions will support API key authentication.

## Endpoints

### Health Check

#### `GET /`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.7.0",
  "timestamp": "2024-08-14T12:00:00Z"
}
```

### Transcribe Audio

#### `POST /transcribe`

Transcribe audio file to text with optional formatting.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| file | file | Yes | Audio file (WAV, MP3, M4A, etc.) | - |
| asr_model | string | No | ASR model to use | "whisper-1" |
| apply_formatting | boolean | No | Apply AI formatting | true |
| chat_model | string | No | Chat model for formatting | "gpt-4o-mini" |
| system_prompt | string | No | Custom formatting prompt | Default prompt |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "asr_model=whisper-1" \
  -F "apply_formatting=true" \
  -F "chat_model=gpt-4o-mini"
```

**Response:**
```json
{
  "success": true,
  "transcription": "This is the raw transcription text...",
  "formatted_text": "This is the formatted and polished text...",
  "metadata": {
    "duration": 5.2,
    "asr_model": "whisper-1",
    "chat_model": "gpt-4o-mini",
    "processing_time": 2.3
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information"
}
```

### Format Text

#### `POST /format-text`

Format existing text using AI models.

**Request:**
- Method: `POST`
- Content-Type: `application/json`

**Body:**
```json
{
  "text": "Raw text to format",
  "chat_model": "gpt-4o-mini",
  "system_prompt": "Optional custom prompt"
}
```

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| text | string | Yes | Text to format | - |
| chat_model | string | No | Chat model to use | "gpt-4o-mini" |
| system_prompt | string | No | Custom formatting prompt | Default prompt |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/format-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "um so basically what I wanted to say is that uh the project is going well",
    "chat_model": "gpt-4o-mini"
  }'
```

**Response:**
```json
{
  "success": true,
  "formatted_text": "The project is progressing well.",
  "metadata": {
    "chat_model": "gpt-4o-mini",
    "processing_time": 1.2,
    "token_count": 25
  }
}
```

## Interactive Documentation

### Swagger UI

Access interactive API documentation at:
```
http://localhost:8000/docs
```

Features:
- Interactive API testing
- Request/response examples
- Parameter descriptions
- Schema definitions

### ReDoc

Alternative documentation interface at:
```
http://localhost:8000/redoc
```

## Models

### Supported ASR Models

| Model | Description | Best For |
|-------|-------------|----------|
| whisper-1 | OpenAI Whisper v1 | General transcription |
| whisper-large-v3 | Large Whisper model | High accuracy |

### Supported Chat Models

| Model | Description | Best For |
|-------|-------------|----------|
| gpt-4o-mini | Fast, affordable GPT-4 | General formatting |
| gpt-4 | Most capable model | Complex formatting |
| gpt-3.5-turbo | Legacy model | Basic formatting |

## Rate Limits

Current rate limits (subject to OpenAI's limits):
- Transcription: 50 requests/minute
- Formatting: 100 requests/minute
- File size: Maximum 25MB per audio file

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Verify API key configuration |
| 413 | File Too Large | Reduce file size to < 25MB |
| 429 | Rate Limited | Reduce request frequency |
| 500 | Internal Server Error | Check server logs |
| 503 | Service Unavailable | OpenAI API may be down |

## WebSocket Support (Coming Soon)

Future versions will support WebSocket connections for:
- Real-time transcription streaming
- Live audio processing
- Progress updates

## SDK Examples

### Python

```python
import requests

# Transcribe audio
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/transcribe',
        files={'file': f},
        data={'apply_formatting': 'true'}
    )
    result = response.json()
    print(result['formatted_text'])
```

### JavaScript

```javascript
// Using fetch API
const formData = new FormData();
formData.append('file', audioFile);
formData.append('apply_formatting', 'true');

fetch('http://localhost:8000/transcribe', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => console.log(result.formatted_text));
```

### cURL

```bash
# Simple transcription
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.wav" \
  -o result.json

# With custom formatting
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.wav" \
  -F "apply_formatting=true" \
  -F "chat_model=gpt-4" \
  -F "system_prompt=Format as meeting minutes"
```

## Docker Deployment

### Run with Docker

```bash
# Basic usage
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  ghcr.io/yutaishy/opensuperwhisper:latest

# With custom configuration
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e WORKERS=4 \
  ghcr.io/yutaishy/opensuperwhisper:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  opensuperwhisper:
    image: ghcr.io/yutaishy/opensuperwhisper:latest
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HOST=0.0.0.0
      - PORT=8000
      - WORKERS=4
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## Performance

### Benchmarks

| Operation | Time | Throughput |
|-----------|------|------------|
| Audio Upload (1MB) | ~100ms | 10 req/s |
| Transcription (1min) | ~2s | 30 req/min |
| Formatting (1000 chars) | ~1s | 60 req/min |
| Total Pipeline | ~3s | 20 req/min |

### Optimization Tips

1. **Batch Processing**: Send multiple files in parallel
2. **Compression**: Use compressed audio formats (MP3, M4A)
3. **Caching**: Cache formatted results for identical inputs
4. **Connection Pooling**: Reuse HTTP connections

## Security

### Best Practices

1. **API Key Management**:
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **Network Security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Add authentication layer

3. **Input Validation**:
   - Validate file types
   - Check file sizes
   - Sanitize text inputs

### CORS Configuration

Default CORS settings allow all origins in development. For production:

```python
# Configure specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/

# Detailed health check (coming soon)
curl http://localhost:8000/health/detailed
```

### Metrics (Coming Soon)

Future versions will expose Prometheus metrics at `/metrics`:
- Request count
- Response times
- Error rates
- Model usage

## Changelog

### v0.7.0 (Current)
- Initial API release
- Basic transcription endpoint
- Text formatting endpoint
- Docker support

### Roadmap
- v0.8.0: WebSocket support
- v0.9.0: Batch processing
- v1.0.0: Production ready

## Support

- **GitHub Issues**: [Report bugs](https://github.com/Yutaishy/OpenSuperWhisper/issues)
- **Documentation**: [Wiki](https://github.com/Yutaishy/OpenSuperWhisper/wiki)
- **API Status**: Check `/` endpoint
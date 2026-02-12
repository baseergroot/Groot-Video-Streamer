# Video Streamer with FastAPI and yt-dlp

A simple example showing how video streaming works using FastAPI backend with yt-dlp and React frontend with axios.

## How It Works

### Backend (FastAPI)
- Uses `yt-dlp` to extract video stream from YouTube
- Streams video data in **chunks** (64KB at a time) using `StreamingResponse`
- Never loads entire video into memory
- Data flows: YouTube → yt-dlp → FastAPI → Client

### Frontend (React + Axios)
- **Stream**: Video player uses direct stream URL from backend
- **Download**: Uses axios with `responseType: 'blob'` to download with progress tracking
- **Info**: Simple JSON request to get video metadata

## Setup

### Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure yt-dlp is installed system-wide:
```bash
pip install yt-dlp
```

3. Run the server:
```bash
python backend.py
```

Server will run on `http://localhost:8000`

### Frontend

1. Install dependencies:
```bash
npm install axios react
# or
yarn add axios react
```

2. Import and use the component:
```jsx
import VideoStreamer from './VideoStreamer';

function App() {
  return <VideoStreamer />;
}
```

## API Endpoints

### GET `/stream?url={video_url}`
Streams video data in chunks. Returns video/mp4 content.

**Example:**
```bash
curl "http://localhost:8000/stream?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output video.mp4
```

### GET `/info?url={video_url}`
Returns video metadata (title, duration, thumbnail, formats).

**Example:**
```bash
curl "http://localhost:8000/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Key Concepts Demonstrated

### 1. Streaming Response (Backend)
```python
async def stream_video(url: str):
    process = await asyncio.create_subprocess_exec(...)
    chunk_size = 64 * 1024  # 64KB chunks
    while True:
        chunk = await process.stdout.read(chunk_size)
        if not chunk:
            break
        yield chunk  # Stream chunks as they arrive
```

### 2. Blob Download with Progress (Frontend)
```javascript
const response = await axios.get(`${API_BASE}/stream`, {
    responseType: 'blob',  // Important!
    onDownloadProgress: (progressEvent) => {
        const percent = (progressEvent.loaded * 100) / progressEvent.total;
        setDownloadProgress(percent);
    }
});
```

### 3. Direct Video Streaming (Frontend)
```javascript
// Just set the stream URL as video source
<video src="http://localhost:8000/stream?url=..." controls />
```

## Streaming vs Regular Response

### Regular JSON Response:
- Server processes everything first
- Sends complete response at once
- Client waits for entire response

### Streaming Response:
- Server sends data as it becomes available
- Client starts receiving immediately
- Lower memory usage
- Better for large files

## Notes

- For production, add proper error handling and validation
- Consider adding authentication for the API
- Add rate limiting to prevent abuse
- For large-scale usage, consider using a CDN or media server
- The streaming approach means the server doesn't buffer the entire video in RAM

## Troubleshooting

**CORS errors**: Make sure the FastAPI CORS middleware is configured correctly.

**yt-dlp errors**: Some videos may be geo-restricted or require authentication.

**Memory issues**: The streaming approach is designed to use minimal memory regardless of video size.
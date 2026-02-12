from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import subprocess
import asyncio
import httpx

app = FastAPI()

# https://www.instagram.com/reel/DUdLHnvjW4P/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ==

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_video_url(youtube_url: str):
    """Extract direct video URL using yt-dlp"""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Get best mp4 or best available
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

async def stream_video(url: str):
    # """Stream video data in chunks"""
    # Use yt-dlp to download and stream
    process = await asyncio.create_subprocess_exec(
        'yt-dlp',
        '-f', 'best[ext=mp4]/best',
        '-o', '-',  # Output to stdout
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    # print({"process": process})
    
    # Stream chunks from yt-dlp stdout
    chunk_size = 64 * 1024  # 64KB chunks
    while True:
        chunk = await process.stdout.read(chunk_size)
        # print({"chunk": chunk})
        if not chunk:
            break
        yield chunk
    
    await process.wait()

@app.get("/")
def read_root():
    return {"message": "yt-dlp streaming API"}

@app.get("/stream")
async def stream_video_endpoint(url: str):
    """
    Stream video from YouTube URL
    Usage: /stream?url=https://www.youtube.com/watch?v=VIDEO_ID
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    try:
        return StreamingResponse(
            stream_video(url),
            media_type="video/mp4",
            headers={
                "Content-Disposition": "inline",
                "Accept-Ranges": "bytes",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming video: {str(e)}")

@app.get("/info")
def get_video_info(url: str):
    """Get video information without downloading"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        ydl_opts = {
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return {
                "title": info.get('title'),
                "duration": info.get('duration'),
                "thumbnail": info.get('thumbnail'),
                "formats_available": len(info.get('formats', [])),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting info: {str(e)}")

@app.get("/proxy-image")
async def proxy_image(url: str):
    """
    Proxy images to bypass CORS restrictions
    Usage: /proxy-image?url=IMAGE_URL
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")

            # Return the image with appropriate headers
            return Response(
                content=response.content,
                media_type=response.headers.get('content-type', 'image/jpeg'),
                headers={
                    'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                    'Access-Control-Allow-Origin': '*',
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error proxying image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

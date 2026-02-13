from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import subprocess
import asyncio
import httpx
from dotenv import load_dotenv
import os
from typing import Optional
import base64
import re

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")
YTDLP_COOKIE_FILE = os.getenv("YTDLP_COOKIE_FILE")
YTDLP_COOKIES_FROM_BROWSER = os.getenv("YTDLP_COOKIES_FROM_BROWSER")
YTDLP_COOKIE_TEXT = os.getenv("YTDLP_COOKIE_TEXT")
YTDLP_COOKIE_TEXT_B64 = os.getenv("YTDLP_COOKIE_TEXT_B64")
app = FastAPI()

# https://www.instagram.com/reel/DUdLHnvjW4P/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ==

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_cookiefile_path() -> Optional[str]:
    if YTDLP_COOKIE_TEXT_B64:
        temp_path = "/tmp/yt_dlp_cookies.txt"
        try:
            decoded = base64.b64decode(YTDLP_COOKIE_TEXT_B64).decode("utf-8")
            with open(temp_path, "w") as f:
                f.write(decoded)
            return temp_path
        except Exception:
            return None
    if YTDLP_COOKIE_TEXT:
        temp_path = "/tmp/yt_dlp_cookies.txt"
        try:
            with open(temp_path, "w") as f:
                f.write(YTDLP_COOKIE_TEXT)
            return temp_path
        except Exception:
            return None
    if YTDLP_COOKIE_FILE and os.path.exists(YTDLP_COOKIE_FILE):
        return YTDLP_COOKIE_FILE
    return None

def sanitize_filename(name: Optional[str]) -> str:
    if not name:
        return "video.mp4"
    cleaned = re.sub(r'[^A-Za-z0-9._ -]+', '', name).strip()
    if not cleaned:
        return "video.mp4"
    if not cleaned.lower().endswith(".mp4"):
        cleaned = f"{cleaned}.mp4"
    return cleaned[:200]

def get_video_url(youtube_url: str):
    """Extract direct video URL using yt-dlp"""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Get best mp4 or best available
        'quiet': True,
    }
    cookiefile = get_cookiefile_path()
    if cookiefile:
        ydl_opts['cookiefile'] = cookiefile
    elif YTDLP_COOKIES_FROM_BROWSER:
        ydl_opts['cookiesfrombrowser'] = (YTDLP_COOKIES_FROM_BROWSER,)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

async def stream_video(url: str):
    # """Stream video data in chunks"""
    # Use yt-dlp to download and stream
    cmd = [
        'yt-dlp',
        '-f', 'best[ext=mp4]/best',
        '-o', '-',  # Output to stdout
    ]
    cookiefile = get_cookiefile_path()
    if cookiefile:
        cmd.extend(['--cookies', cookiefile])
    elif YTDLP_COOKIES_FROM_BROWSER:
        cmd.extend(['--cookies-from-browser', YTDLP_COOKIES_FROM_BROWSER])
    cmd.append(url)
    process = await asyncio.create_subprocess_exec(
        *cmd,
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

@app.get("/download")
async def download_video_endpoint(url: str, title: Optional[str] = None):
    """
    Download video as attachment
    Usage: /download?url=VIDEO_URL&title=My%20Video
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    filename = sanitize_filename(title)
    try:
        return StreamingResponse(
            stream_video(url),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Accept-Ranges": "bytes",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

@app.get("/info")
def get_video_info(url: str):
    """Get video information without downloading"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        ydl_opts = {
            'quiet': True,
        }
        cookiefile = get_cookiefile_path()
        if cookiefile:
            ydl_opts['cookiefile'] = cookiefile
        elif YTDLP_COOKIES_FROM_BROWSER:
            ydl_opts['cookiesfrombrowser'] = (YTDLP_COOKIES_FROM_BROWSER,)

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

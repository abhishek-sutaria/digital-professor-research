from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp
import os
import asyncio
import json
import zipfile
import shutil

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create downloads directory if it doesn't exist
os.makedirs("downloads", exist_ok=True)
# Mount downloads directory to serve static files
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Check for cookies in env var and write to file
if os.environ.get("YOUTUBE_COOKIES_CONTENT"):
    print("Writing cookies.txt from environment variable")
    with open("cookies.txt", "w") as f:
        f.write(os.environ["YOUTUBE_COOKIES_CONTENT"])


class SearchRequest(BaseModel):
    author: str
    limit: int = 20

@app.post("/search")
async def search_videos(request: SearchRequest):
    print(f"Searching for: {request.author}")
    search_opts = {
        'quiet': True,
        'extract_flat': True,
        'default_search': f'ytsearch{request.limit}',
        'ignoreerrors': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    try:
        # Run blocking yt-dlp search in a thread pool
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(f"ytsearch{request.limit}:{request.author}", download=False))
        
        results = []
        total_views = 0
        author_name = request.author

        if 'entries' in info:
            for entry in info['entries']:
                if entry:
                    thumbnail = entry.get('thumbnail')
                    if not thumbnail and 'thumbnails' in entry and entry['thumbnails']:
                        # Get the last thumbnail (usually best quality)
                        thumbnail = entry['thumbnails'][-1].get('url')
                    
                    view_count = entry.get('view_count', 0)
                    total_views += view_count
                    
                    # Try to get actual uploader name if available
                    if not author_name and entry.get('uploader'):
                        author_name = entry.get('uploader')

                    results.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'thumbnail': thumbnail,
                        'duration': entry.get('duration'),
                        'view_count': view_count,
                        'uploader': entry.get('uploader')
                    })
        
        return {
            "videos": results,
            "stats": {
                "total_views": total_views,
                "video_count": len(results),
                "author_name": author_name
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"WebSocket error: {e}")

# Add local bin to PATH for ffmpeg
import os
import traceback
import random
import asyncio
os.environ["PATH"] += os.pathsep + os.path.abspath("bin")

# Custom logger to prevent yt-dlp from writing to closed stdout/stderr
class MyLogger:
    def debug(self, msg):
        # Only print if it's not a progress line to reduce noise
        if not msg.startswith('[download]'):
            print(f"YTDLP: {msg}")

    def warning(self, msg):
        print(f"YTDLP WARNING: {msg}")

    def error(self, msg):
        print(f"YTDLP ERROR: {msg}")

@app.websocket("/ws/download")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Helper for safe sending
    async def safe_send_json(data):
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"WebSocket send failed: {e}")
            # Don't raise, just log. This prevents the loop from crashing if user disconnects.

    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        urls = request_data.get("urls", [])
        author = request_data.get("author", "Unknown")
        
        # Use local downloads folder for static serving
        downloads_path = "downloads"
        output_dir = os.path.join(downloads_path, author)
        os.makedirs(output_dir, exist_ok=True)

        # Shared state for cancellation
        state = {"stopped": False}
        listener_task = None # Initialize to avoid NameError

        # Progress hook to check for cancellation
        def progress_hook(d):
            if state["stopped"]:
                raise Exception("Download cancelled by user")
            
            if d['status'] == 'downloading':
                try:
                    # We can't easily send async messages from here without a loop reference
                    # But we can rely on the loop below to send start/finish events
                    pass 
                except Exception:
                    pass

        ydl_opts = {
            'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            # 'ignoreerrors': True, # Commented out to expose errors
            'logger': MyLogger(), # Use custom logger
            # 'extractor_args': {'youtube': {'player_client': ['android']}}, # Removed: Android client + desktop cookies can trigger bot detection
            'progress_hooks': [progress_hook],
            'source_address': '0.0.0.0', # Force IPv4 to avoid IPv6 blocks
        }

        # Add PO Token and Visitor Data if available (Critical for bot bypass)
        po_token = os.environ.get("YOUTUBE_PO_TOKEN")
        visitor_data = os.environ.get("YOUTUBE_VISITOR_DATA")
        user_agent_env = os.environ.get("YOUTUBE_USER_AGENT")
        
        # Set User Agent if provided (Must match the browser describing cookies/tokens)
        if user_agent_env:
            print(f"DEBUG: Using custom User Agent from env")
            ydl_opts['user_agent'] = user_agent_env

        if po_token and visitor_data:
            print(f"DEBUG: Using PO Token and Visitor Data")
            ydl_opts['extractor_args'] = {
                'youtube': {
                    'po_token': [f"web+{po_token}"],
                    'visitor_data': [visitor_data]
                }
            }
        else:
            print("DEBUG: PO Token or Visitor Data missing in env vars")

        # Check for cookies.txt
        if os.path.exists('cookies.txt'):
            size = os.path.getsize('cookies.txt')
            print(f"DEBUG: Using cookies.txt (size: {size} bytes)")
            ydl_opts['cookiefile'] = 'cookies.txt'
        else:
            print("DEBUG: No cookies.txt found")

        # Task to listen for stop command
        async def listen_for_stop():
            try:
                while not state["stopped"]:
                    msg = await websocket.receive_text()
                    if msg == "stop":
                        state["stopped"] = True
                        print("Stop command received")
            except Exception:
                pass

        listener_task = asyncio.create_task(listen_for_stop())

        total_videos = len(urls)
        downloaded_files = [] # Track successfully downloaded files

        for i, url in enumerate(urls):
            if state["stopped"]:
                break
            
            # Add random delay to avoid rate limiting (except for the first video)
            if i > 0:
                delay = random.uniform(3, 7)
                print(f"DEBUG: Waiting {delay:.2f}s before next download...")
                await safe_send_json({
                    "type": "progress",
                    "current_index": i,
                    "total": total_videos,
                    "status": f"Waiting {int(delay)}s...",
                    "video_url": url
                })
                await asyncio.sleep(delay)

            print(f"DEBUG: Starting download for {url}")
            await safe_send_json({
                "type": "progress",
                "current_index": i,
                "total": total_videos,
                "status": "downloading",
                "video_url": url
            })
            
            # Run download in executor
            loop = asyncio.get_event_loop()
            info = None
            error_msg = None
            
            # Run download in executor
            loop = asyncio.get_event_loop()
            info = None
            error_msg = None
            
            try:
                # Extract info first to get filename
                print(f"DEBUG: Calling yt-dlp extract_info for {url}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                print(f"DEBUG: yt-dlp finished for {url}")
            except Exception as e:
                print(f"Download interrupted for {url}: {e}")
                traceback.print_exc()
                error_msg = str(e)
                # Handle specific I/O error caused by HTTP 400
                if "I/O operation on closed file" in str(e):
                    error_msg = "YouTube blocked the request (HTTP 400). Try again later."
                elif "Sign in to confirm you’re not a bot" in str(e):
                    error_msg = "YouTube Bot Detection: Please update cookies and/or PO Token."
            
            if state["stopped"]:
                await safe_send_json({
                    "type": "cancelled",
                    "current_index": i,
                    "total": total_videos
                })
                break

            # Construct download URL
            download_url = ""
            if info:
                # yt-dlp might return a list if it's a playlist, but we set noplaylist=True
                if 'entries' in info:
                    info = info['entries'][0]
                
                # Debug logging
                # print(f"DEBUG: Info keys: {info.keys()}") # Reduced noise
                print(f"DEBUG: Filename from info: {info.get('filename')}")
                # print(f"DEBUG: Requested outtmpl: {ydl_opts['outtmpl']}")

                requested_filename = info.get('filename')
                if not requested_filename:
                    # Fallback: try to predict filename
                    requested_filename = ydl.prepare_filename(info)
                    print(f"DEBUG: Predicted filename: {requested_filename}")

                if requested_filename:
                     # Remove the 'downloads/' prefix if present
                    try:
                        # Add to list of downloaded files
                        downloaded_files.append(requested_filename)

                        rel_path = os.path.relpath(requested_filename, "downloads")
                        download_url = f"/downloads/{rel_path}"
                        print(f"DEBUG: Generated download_url: {download_url}")
                    except Exception as e:
                        print(f"DEBUG: Error generating relpath: {e}")
                        traceback.print_exc()
                        error_msg = str(e)
            elif not error_msg:
                error_msg = "Download failed (unknown error)"

            await safe_send_json({
                "type": "progress",
                "current_index": i + 1,
                "total": total_videos,
                "status": "finished",
                "video_url": url,
                "download_url": download_url,
                "error": error_msg
            })

        # Cleanup listener
        if listener_task:
            listener_task.cancel()
        
        if not state["stopped"]:
            # Create ZIP file if we have downloaded files
            zip_url = ""
            if downloaded_files:
                try:
                    zip_filename = f"{author}_videos.zip"
                    # Sanitize filename
                    zip_filename = "".join([c for c in zip_filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()
                    zip_path = os.path.join(downloads_path, zip_filename)
                    
                    print(f"DEBUG: Creating zip file at {zip_path}")
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for file_path in downloaded_files:
                            if os.path.exists(file_path):
                                # Add file to zip with just the filename (flat structure inside zip)
                                arcname = os.path.basename(file_path)
                                zipf.write(file_path, arcname)
                                print(f"DEBUG: Added {file_path} to zip as {arcname}")
                    
                    zip_url = f"/downloads/{zip_filename}"
                    print(f"DEBUG: Zip URL: {zip_url}")
                except Exception as e:
                    print(f"DEBUG: Error creating zip: {e}")
                    traceback.print_exc()

            await safe_send_json({
                "type": "complete",
                "zip_url": zip_url
            })
        
    except Exception as e:
        print(f"WebSocket error: {e}")
        traceback.print_exc()

@app.post("/open-folder")
async def open_folder(request: SearchRequest):
    import subprocess
    downloads_path = os.path.expanduser("~/Downloads")
    path = os.path.abspath(os.path.join(downloads_path, request.author))
    if os.path.exists(path):
        subprocess.run(["open", path])
        return {"status": "opened"}
    return {"error": "Folder not found"}

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import asyncio
import json

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        return {"error": str(e)}

@app.websocket("/ws/download")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        urls = request_data.get("urls", [])
        author = request_data.get("author", "Unknown")
        
        # Use system Downloads folder
        downloads_path = os.path.expanduser("~/Downloads")
        output_dir = os.path.join(downloads_path, author)
        os.makedirs(output_dir, exist_ok=True)

        # Shared state for cancellation
        state = {"stopped": False}

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
            'ignoreerrors': True, # We want to catch our cancellation exception though? 
                                  # ignoreerrors=True might swallow it. 
                                  # Let's keep it True for general errors but check state in loop.
            'extractor_args': {'youtube': {'player_client': ['android']}},
            # 'cookiesfrombrowser': ('chrome',), # Cookies caused 403, removing them
            'progress_hooks': [progress_hook]
        }

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
        for i, url in enumerate(urls):
            if state["stopped"]:
                break

            await websocket.send_json({
                "type": "progress",
                "current_index": i,
                "total": total_videos,
                "status": "downloading",
                "video_url": url
            })
            
            # Run download in executor
            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
            except Exception as e:
                print(f"Download interrupted: {e}")
            
            if state["stopped"]:
                await websocket.send_json({
                    "type": "cancelled",
                    "current_index": i,
                    "total": total_videos
                })
                break

            await websocket.send_json({
                "type": "progress",
                "current_index": i + 1,
                "total": total_videos,
                "status": "finished",
                "video_url": url
            })

        # Cleanup listener
        listener_task.cancel()
        
        if not state["stopped"]:
            await websocket.send_json({"type": "complete"})
        
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.post("/open-folder")
async def open_folder(request: SearchRequest):
    import subprocess
    downloads_path = os.path.expanduser("~/Downloads")
    path = os.path.abspath(os.path.join(downloads_path, request.author))
    if os.path.exists(path):
        subprocess.run(["open", path])
        return {"status": "opened"}
    return {"error": "Folder not found"}

import yt_dlp
import os
import json

# Mock data
AUTHOR = "Kevin Lane Keller"
URLS = ["https://www.youtube.com/watch?v=jNQXAC9IVRw"]

def test_download():
    print("--- Starting Debug V6 ---")
    
    # 1. Directory Creation
    try:
        downloads_path = os.path.expanduser("~/Downloads")
        output_dir = os.path.join(downloads_path, AUTHOR)
        print(f"Attempting to create directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        if os.path.exists(output_dir):
            print("Directory created successfully.")
        else:
            print("ERROR: Directory does not exist after creation attempt.")
            return
    except Exception as e:
        print(f"ERROR creating directory: {e}")
        return

    # 2. yt-dlp Configuration (Exact match from main.py)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False, # Changed to False for debug
        'no_warnings': False, # Changed to False for debug
        'ignoreerrors': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'cookiesfrombrowser': ('chrome',),
        'verbose': True
    }

    # 3. Download Execution
    print(f"Starting download for {len(URLS)} videos...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(URLS)
        print("Download process finished.")
    except Exception as e:
        print(f"ERROR during download: {e}")

if __name__ == "__main__":
    test_download()

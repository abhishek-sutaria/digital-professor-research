import yt_dlp
import os

def test_download(url, author="Test_Author"):
    print(f"Attempting to download: {url}")
    
    downloads_path = os.path.expanduser("~/Downloads")
    output_dir = os.path.join(downloads_path, author)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False, # Enable output to see errors
        'no_warnings': False,
        'ignoreerrors': False,
        'cookiesfrombrowser': ('safari',),
        'verbose': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download finished.")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    # Using a known short video for testing
    test_download("https://www.youtube.com/watch?v=jNQXAC9IVRw", "Kevin Lane Keller")

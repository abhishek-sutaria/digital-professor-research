import yt_dlp
import os

VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

def test_config(name, opts):
    print(f"\n--- Testing Configuration: {name} ---")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([VIDEO_URL])
        print(f"SUCCESS: {name}")
        return True
    except Exception as e:
        print(f"FAILED: {name} - {e}")
        return False

def main():
    base_opts = {
        'outtmpl': 'test_download_%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
    }

    configs = [
        (
            "iOS Client (No Cookies)",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['ios']}}}
        ),
        (
            "Android Client (No Cookies)",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['android']}}}
        ),
        (
            "TV Client (No Cookies)",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['tv']}}}
        ),
        (
            "Web Client (No Cookies, Spoofed UA)",
            {
                **base_opts, 
                'extractor_args': {'youtube': {'player_client': ['web']}},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
    ]

    for name, opts in configs:
        if test_config(name, opts):
            print(f"\nFound working configuration: {name}")
            break
    else:
        print("\nAll configurations failed.")

if __name__ == "__main__":
    main()

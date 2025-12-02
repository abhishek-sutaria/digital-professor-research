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
            "Android Client Only",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['android']}}}
        ),
        (
            "Web Client Only",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['web']}}}
        ),
        (
            "Android + Chrome Cookies",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['android']}}, 'cookiesfrombrowser': ('chrome',)}
        ),
        (
            "Web + Chrome Cookies",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['web']}}, 'cookiesfrombrowser': ('chrome',)}
        ),
         (
            "Android + Web + Chrome Cookies",
            {**base_opts, 'extractor_args': {'youtube': {'player_client': ['android', 'web']}}, 'cookiesfrombrowser': ('chrome',)}
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

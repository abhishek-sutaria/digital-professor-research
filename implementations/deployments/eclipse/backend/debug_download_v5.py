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
        'cookiesfrombrowser': ('chrome',),
        'force_ipv4': True,
    }

    configs = [
        (
            "Web Client + Cookies + Force IPv4",
            {
                **base_opts, 
                'extractor_args': {'youtube': {'player_client': ['web']}},
            }
        ),
         (
            "Android Client + Cookies + Force IPv4",
            {
                **base_opts, 
                'extractor_args': {'youtube': {'player_client': ['android']}},
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

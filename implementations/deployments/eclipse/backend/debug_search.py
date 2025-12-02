import yt_dlp
import json

def test_search(author, limit=5):
    print(f"Searching for: {author}")
    search_opts = {
        'quiet': True,
        'extract_flat': True,
        'default_search': f'ytsearch{limit}',
        'ignoreerrors': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{author}", download=False)
            
            if 'entries' in info:
                print(f"Found {len(info['entries'])} entries.")
                for i, entry in enumerate(info['entries']):
                    print(f"\nEntry {i+1}:")
                    print(f"Title: {entry.get('title')}")
                    print(f"View Count: {entry.get('view_count')}")
                    print(f"Uploader: {entry.get('uploader')}")
                    print(f"Keys: {list(entry.keys())}")
            else:
                print("No entries found.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search("Kevin Lane Keller")

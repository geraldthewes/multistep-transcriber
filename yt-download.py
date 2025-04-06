import yt_dlp
import ffmpeg
import os
import sys
import json

def download_and_convert(url, output_dir="."):
    os.makedirs(output_dir, exist_ok=True)
    video_id = None
    json_filename = None

    try:
        # --- Step 0: Fetch Metadata ---
        print(f"Fetching metadata for {url}...")
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_id = info_dict.get('id', 'video') # Use video ID for filename base

            # Select relevant metadata fields
            metadata = {
                'id': info_dict.get('id'),
                'title': info_dict.get('title'),
                'uploader': info_dict.get('uploader'),
                'uploader_id': info_dict.get('uploader_id'),
                'uploader_url': info_dict.get('uploader_url'),
                'upload_date': info_dict.get('upload_date'), # Format YYYYMMDD
                'description': info_dict.get('description'),
                'duration': info_dict.get('duration'),
                'view_count': info_dict.get('view_count'),
                'like_count': info_dict.get('like_count'),
                'channel': info_dict.get('channel'),
                'channel_id': info_dict.get('channel_id'),
                'channel_url': info_dict.get('channel_url'),
                'tags': info_dict.get('tags'),
                'categories': info_dict.get('categories'),
                'webpage_url': info_dict.get('webpage_url'),
                'original_url': info_dict.get('original_url'),
                'thumbnail': info_dict.get('thumbnail'),
                # Add more fields as needed
            }

            json_filename = os.path.join(output_dir, f"{video_id}.json")
            print(f"Saving metadata to {json_filename}")
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error fetching or saving metadata: {e}")
        print("Attempting to continue download without full metadata...")
        # Attempt to get just the ID if possible for filenames
        if not video_id:
             try:
                 with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'forceid': True}) as ydl_id:
                      minimal_info = ydl_id.extract_info(url, download=False)
                      video_id = minimal_info.get('id', 'downloaded_video')
             except Exception:
                 print("Warning: Could not determine video ID for filenames.")
                 video_id = 'downloaded_video' # Fallback filename base

    # --- Download Steps ---
    video_file = None
    audio_file = None
    output_wav = None

    try:
        # Step 1: Download video-only stream
        video_outtmpl = os.path.join(output_dir, f"{video_id}_video.%(ext)s")
        video_opts = {
            'format': 'bestvideo[height<=720]/best[height<=720]', # Prefer non-webm if possible, fallback
            'outtmpl': video_outtmpl,
        }

        print(f"Downloading video stream from {url} (max 720p)...")
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            video_info = ydl.extract_info(url, download=True)
            # Determine the actual downloaded file path
            video_file = ydl.prepare_filename(video_info)
            # Correct path if extension was added by yt-dlp template
            if '%(ext)s' in video_outtmpl:
                 video_file = video_outtmpl.replace('%(ext)s', video_info.get('ext', 'mp4')) # Guess mp4 if ext missing
            print(f"Downloaded video: {video_file}")


        # Step 2: Download audio-only stream
        audio_outtmpl = os.path.join(output_dir, f"{video_id}_audio.%(ext)s")
        audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_outtmpl,
        }

        print(f"Downloading audio stream from {url}...")
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            audio_info = ydl.extract_info(url, download=True)
            # Determine the actual downloaded file path
            audio_file = ydl.prepare_filename(audio_info)
             # Correct path if extension was added by yt-dlp template
            if '%(ext)s' in audio_outtmpl:
                 audio_file = audio_outtmpl.replace('%(ext)s', audio_info.get('ext', 'm4a')) # Guess m4a if ext missing
            print(f"Downloaded audio: {audio_file}")


        # Step 3: Convert audio to WAV
        output_wav = os.path.join(output_dir, f"{video_id}_audio.wav")
        
        print(f"Converting {audio_file} to WAV...")
        stream = ffmpeg.input(audio_file)
        stream = ffmpeg.output(stream, output_wav, 
                             acodec='pcm_s16le')  # WAV format
        ffmpeg.run(stream)

        print(f"Conversion complete! Files saved:")
        if json_filename and os.path.exists(json_filename):
            print(f" - Metadata: {json_filename}")
        if video_file and os.path.exists(video_file):
            print(f" - Video: {video_file}")
        if audio_file and os.path.exists(audio_file):
            print(f" - Audio: {audio_file}")
        if output_wav and os.path.exists(output_wav):
            print(f" - WAV: {output_wav}")

        # Optional: Clean up original downloaded audio file (keep video and WAV)
        #cleanup = input("Do you want to delete the original audio file (not WAV)? (y/n): ").lower()
        #if cleanup == 'y':
        #    os.remove(audio_file)
        #    print(f"Deleted {audio_file}")

    except ffmpeg.Error as e:
        print(f"FFmpeg error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yt-download.py <YouTube_URL> [output_directory]")
        sys.exit(1)

    youtube_url = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "."
    download_and_convert(youtube_url, output_directory)

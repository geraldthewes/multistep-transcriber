import yt_dlp
import ffmpeg
import os
import sys

def download_and_convert(url, output_dir="."):
    try:
        # Step 1: Download video-only stream
        video_opts = {
            'format': '232',  # 720p video-only
            'outtmpl': os.path.join(output_dir, '%(id)s_video.%(ext)s'),  # Video file
        }

        print(f"Downloading video stream from {url} (format 232)...")
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            video_info = ydl.extract_info(url, download=True)
            video_id = video_info['id']
            video_ext = video_info['ext']
            video_file = os.path.join(output_dir, f"{video_id}_video.{video_ext}")
        print(f"Download video {str(video_file)}")

        # Step 2: Download audio-only stream
        audio_opts = {
            'format': '233',  # Audio-only
            'outtmpl': os.path.join(output_dir, '%(id)s_audio.%(ext)s'),  # Audio file
        }

        print(f"Downloading audio stream from {url} (format 233)...")
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            audio_info = ydl.extract_info(url, download=True)
            audio_ext = audio_info['ext']
            audio_file = os.path.join(output_dir, f"{video_id}_audio.{audio_ext}")

        # Step 3: Convert audio to WAV
        output_wav = os.path.join(output_dir, f"{video_id}_audio.wav")
        
        print(f"Converting {audio_file} to WAV...")
        stream = ffmpeg.input(audio_file)
        stream = ffmpeg.output(stream, output_wav, 
                             acodec='pcm_s16le')  # WAV format
        ffmpeg.run(stream)

        print(f"Conversion complete! Files saved:")
        print(f" - Video: {video_file}")
        print(f" - Audio: {audio_file}")
        print(f" - WAV: {output_wav}")

        # Optional: Clean up original audio file (keep video and WAV)
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
        print("Usage: python script.py <YouTube_URL>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    download_and_convert(youtube_url)

import yt_dlp

def download_video(url, resolution='highest'):
    try:
        if resolution != 'highest':
            # Choose a format that has both audio and video (no merging needed)
            format_str = f'best[height<={resolution}]'
        else:
            format_str = 'best'

        ydl_opts = {
            'format': format_str,
            'outtmpl': '%(title)s.%(ext)s',  # Output file name template
            'merge_output_format': 'mp4',   # Optional, forces mp4 container
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    video_url = input("Enter YouTube URL: ")
    video_resolution = input("Enter resolution (e.g., 720 or leave blank for highest): ").strip()

    download_video(video_url, video_resolution or 'highest')

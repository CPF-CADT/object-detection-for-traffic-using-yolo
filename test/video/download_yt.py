import yt_dlp

url = "https://www.youtube.com/watch?v=cJatWBDNabE"

ydl_opts = {
    "outtmpl": "video.%(ext)s",  # output file name
    "format": "mp4",  # force mp4 if possible
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

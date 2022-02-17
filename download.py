import youtube_dl
import subprocess
import argparse
import pathlib
import glob
import math
import csv
import os


def video_extract_frames(video, imgdir, fps=1):
    """
    Extract image frames from a video
    Returns a list of file paths
    """
    # ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1
    args = [
        "ffprobe",
        "-hide_banner",
        "-loglevel",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video,
    ]
    duration = float(subprocess.check_output(args))
    print(
        "Duration %.2f sec, fps %.2f, extracting %d frames"
        % (duration, fps, (duration * fps + 1))
    )

    # There is a bug with the last second sometime, we just cut the video capture before for now
    # https://trac.ffmpeg.org/wiki/Scaling
    # args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-t", str(math.floor(duration)), "-i", video, "-vsync", "drop", "-vf", "fps="+str(fps), "-q:v", "10", os.path.join(imgdir, '%05d.jpg')]
    args = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-t",
        str(math.floor(duration)),
        "-i",
        video,
        "-vsync",
        "drop",
        "-vf",
        "fps="
        + str(fps)
        + ",scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2",
        "-q:v",
        "10",
        os.path.join(imgdir, video.split('/')[-1]+"_%05d.jpg"),
    ]
    # args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-t", str(math.floor(duration)), "-i", video, "-vsync", "drop", "-vf", "scale=320:240:force_original_aspect_ratio=increase,crop=320:240:fps="+str(fps), "-q:v", "10", os.path.join(imgdir, '%05d.jpg')]
    subprocess.call(args)


def main(args):

    with open(args.file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        links = [row["Link"] for row in reader]

    # ▶ youtube-dl --default-search "ytsearch20" "free+stock+footage+tar+moss" -vic -o '' --restrict-filenames -f bestvideo --max-filesize 10M --no-part
    # https://github.com/rg3/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312
    ydl_opts = {
        "outtmpl": os.path.join(args.dest, "%(id)s.%(ext)s"),
        "format": "mp4",
        # 'max_filesize': 20000000,
        "nopart": True,
    }

    # for idx, link in enumerate(links[:110]):
    #     print(f'{idx} | {link}')
    #     if "youtube" in link:
    #         ydl_opts["outtmpl"] = os.path.join(args.dest, "vids", "%(id)s.%(ext)s")
    #         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #             try:
    #                 ydl.download([link])
    #             except:
    #                 print("Somethin wrong")

    videos = glob.glob(f'{args.dest}/vids/*')
    for idx, video in enumerate(videos):
        print(f'{idx} | {video}')
        video_extract_frames(video, f'{args.dest}/imgs', .4)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="Csv file", required=True)
    parser.add_argument(
        "-d", "--dest", type=str, help="Destination folder", required=True
    )

    args = parser.parse_args()
    main(args)

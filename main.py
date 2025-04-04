import datetime
from ffmpeg import FFmpeg
import json
import os
import PIL.Image
import PIL.ExifTags
from pillow_heif import register_heif_opener
import sys

register_heif_opener()


if(len(sys.argv) != 2):
    print("This script requires a single argument which is the path to the folder that will be processed.")
    sys.exit()

folder_path = sys.argv[1]

def string_to_datetime(datetime_string, file):
    datetime_datetime = ""
    try:
        datetime_datetime = datetime.datetime.strptime(datetime_string, "%Y:%m:%d %H:%M:%S")
    except ValueError as e:
        try:
            datetime_datetime = datetime.datetime.fromisoformat(datetime_string)
        except ValueError as e:
            try:
                datetime_datetime = datetime.datetime.strptime(datetime_string[:19], "%Y:%m:%d %H:%M:%S")
            except ValueError as e:
                print(f"all methods of finding the date failed for {file} with date {datetime_string}")
    return datetime_datetime


def make_subfolders(year, month):
    if(not os.path.isdir(f"{folder_path}/{year}")):
        print(f"no {year} folder; creating...")
        os.mkdir(f"{folder_path}/{year}")
    # else:
    #     print(f"{year} folder exists")
    if(not os.path.isdir(f"{folder_path}/{year}/{month}")):
        print(f"no {month} folder; creating...")
        os.mkdir(f"{folder_path}/{year}/{month}")
    # else:
    #     print(f"{month} folder exists")

def try_to_rename(img_datetime, file):
    if(img_datetime):
        # print("python datetime", img_datetime)
        img_year = img_datetime.year
        img_month = str(img_datetime.month).zfill(2)
        print(f"moving {file} to {img_year}/{img_month}")
        new_folder_path = f"{folder_path}/{img_year}/{img_month}"
        # print(f"moving {folder_path}/{file} to {new_folder_path}/{file}")
        make_subfolders(img_year, img_month)
        os.rename(f"{folder_path}/{file}", f"{new_folder_path}/{file}")
        print('\n')

inc = 0

for file in os.listdir(folder_path):
    if(os.path.isdir(f"{folder_path}/{file}")):
        continue
    # print(file)
    inc += 1
    if(inc % 100 == 0):
        print(inc, file)
    # if(inc > 1000):
    #     break
    
    try:
        img = PIL.Image.open(folder_path + "/" + file)
        exif_data = img.getexif()
        img_datetime = None

        if(exif_data != {}):
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in img.getexif().items()
                if k in PIL.ExifTags.TAGS
            }
            # print(exif)
            if("DateTime" in exif):
                # print("DateTime", exif["DateTime"])
                img_datetime = string_to_datetime(exif["DateTime"], file)
            if("DateTimeOriginal" in exif):
                # print("DateTimeOriginal", exif["DateTimeOriginal"])
                img_datetime = string_to_datetime(exif["DateTimeOriginal"], file)
            # if("DateTimeDigitized" in exif):
            #     print("DateTimeDigitized", exif["DateTimeDigitized"])
            #     img_datetime = datetime.datetime.strptime(exif["DateTimeDigitized"], "%Y:%m:%d %H:%M:%S")
            # print(exif)
            # break
        try_to_rename(img_datetime, file)
    except Exception as e:
        try:
            # maybe it's a video
            if(type(e) == PIL.UnidentifiedImageError):
                ffprobe = FFmpeg(executable="ffprobe").input(
                    f"{folder_path}/{file}",
                    print_format="json", # ffprobe will output the results in JSON format
                    show_streams=None,
                )
                media = json.loads(ffprobe.execute())
                datetime_string = ""
                for stream in media["streams"]:
                    if("tags" in stream and "creation_time" in stream["tags"]):
                        datetime_string = stream["tags"]["creation_time"]
                        break
                # datetime_string = media["streams"][0]["tags"]["creation_time"]
                if(datetime_string != ""):
                    img_datetime = datetime.datetime.fromisoformat(datetime_string)
                # else:
                #     print(file)
                #     print(media)
                #     print('\n')
                try_to_rename(img_datetime, file)
                continue
        except Exception as e:
            print("error processing", file)
            print(e)
            print(type(e))
            print('\n')

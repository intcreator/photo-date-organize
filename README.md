# Photo Date Sort

This script will take a massive folder of photos and videos in common formats and sort them into subfolders of years and months based on EXIF data. Files that are not valid photos or videos or which do not have EXIF data will not be moved.

## Setup

Use a virtual environment to install the dependencies (see requirements.txt) and then run:

```sh
.venv/bin/python3 main.py
```

If the files you are working with are write protected you may need to run this script with `sudo`.
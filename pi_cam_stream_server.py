#pylint: disable=missing-docstring, C0301, E1101, W0703

"""

sudo apt install -y libatlas-base-dev
pip install opencv-python==3.4.17.61
pip install numpy==1.22.2 pytz==2021.3

# 2. autostart when system rebooted

```bash
# 1. use contab
crontab -e
# 2. append this line to the end, save then exit
@reboot /usr/bin/python /home/pi/Desktop/pi_cam_stream_server.py
# 3. reboot the board
```

# 3. set static IP as 10.0.0.4
sudo nano /etc/dhcpcd.conf

interface wlan0
static ip_address=10.0.0.4/24
static routers=10.0.0.1
static domain_name_servers=10.0.0.1

"""

import os
import sys
import time
import asyncio
import datetime
import glob
import pytz
import numpy as np
import cv2

assert sys.version_info >= (3, 5, 2)  # for reader.readuntil

#FRAME_SEPARATOR = b'\xE2\x82\xAC\xE2\x82\xAC'
# (chr(255)+chr(0)+chr(0)+chr(0)+chr(255)+chr(0)+chr(0)+chr(0)+chr(255)).encode('utf-8')
FRAME_SEPARATOR = b'\xc3\xbf\x00\x00\x00\xc3\xbf\x00\x00\x00\xc3\xbf'
SEPARATOR_LENGTH = len(FRAME_SEPARATOR)

SERVER_IP = '10.0.0.4'
SERVER_PORT = 8888

WRITE_VIDEO_TO_FILE = True
VIDEO_SAVE_PATH = '/home/pi/Desktop/videos/'
VIDEO_FPS = 10
VIDEO_CLIP_LENGTH_MINUTES = 60  # generate a new file every VIDEO_CLIP_LENGTH_MINUTES mins

DISPLAY_VIDEO = False

# max number of video files to be saved, 5 days. 120 = 24*5, if a video file is 1 hr long
MAX_NUM_VIDEOS_ROTATION = 120


def refresh_video_file(video_width:int=1280, video_height:int=720) -> cv2.VideoWriter:
    """rotate files, maintain a ringbuffer of 10 files
    """
    # ascending order
    #filenames = sorted([os.path.basename(name) for name in glob.glob(f'{VIDEO_SAVE_PATH}*')])
    filenames = sorted(glob.glob(f'{VIDEO_SAVE_PATH}*'))
    num_files = len(filenames)
    if num_files >= MAX_NUM_VIDEOS_ROTATION:
        oldest_filename = filenames[0]
        if os.path.exists(oldest_filename):
            print(f'Delete: {oldest_filename}')
            os.remove(oldest_filename)
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y_%m_%d_%H_%M_%S')
    #output_video_file = os.path.join(VIDEO_SAVE_PATH, f'{timestamp}.mp4')
    #   # XVID-> .avi, mp4v-> .mp4, FMP4-> .mp4
    #video_writer = cv2.VideoWriter(output_video_file,
    #                               cv2.VideoWriter_fourcc(*'FMP4'),
    #                               VIDEO_FPS,
    #                               (720, 1280))
    #idx = filename_idx % MAX_NUM_VIDEOS_ROTATION  # 000_<date>.avi
    #output_video_file = os.path.join(VIDEO_SAVE_PATH, f'{idx:03}_{timestamp}.avi')
    output_video_file = os.path.join(VIDEO_SAVE_PATH, f'{timestamp}.avi')
    video_writer = cv2.VideoWriter(output_video_file,
                                   cv2.VideoWriter_fourcc(*'XVID'),
                                   VIDEO_FPS,
                                   (video_width, video_height))
    print(f'Output File: {output_video_file}')
    return video_writer

async def handle_cam(reader, writer):
    """called whenever a new client connection is established
    """
    start_time = time.time()
    video_writer = None

    while True:
        try:
            raw_data = await reader.readuntil(separator=FRAME_SEPARATOR)  # blocked until read something
            # truncate the separator
            raw_data = raw_data[:-SEPARATOR_LENGTH]  # bytes
            frame = np.asarray(bytearray(raw_data), dtype=np.uint8)
            frame = cv2.imdecode(frame, -1)
            (video_height, video_width, channels) = frame.shape
            if frame is not None:
                # print the timestamp on frame
                now = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime('%m/%d/%Y %H:%M:%S')
                cv2.putText(frame, f'PST: {now}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if DISPLAY_VIDEO:
                    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    cv2.imshow('jpg', frame)
                    cv2.waitKey(1)

                if WRITE_VIDEO_TO_FILE:  # persist to disk file
                    if video_writer is None:
                        video_writer = refresh_video_file(video_width, video_height)
                    video_writer.write(frame)
                    now = time.time()
                    if int(now - start_time) >= 60 * VIDEO_CLIP_LENGTH_MINUTES:  # generate a new file every 30 mins
                        start_time = now
                        video_writer.release()
                        # refresh video file
                        video_writer = refresh_video_file(video_width, video_height)
            #data = str.encode("hello"+'\n')
            #writer.write(data)
            #await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionResetError, ConnectionAbortedError) as err:
            #asyncio.exceptions.IncompleteReadError: 0 bytes read on a total of undefined expected bytes
            raise err

        except Exception as err:
            raise err
            #cv2.destroyAllWindows()


async def main():
    """main entrypoint

    """
    while True:
        try:
            server = await asyncio.start_server(handle_cam,
                                        SERVER_IP,
                                        SERVER_PORT,
                                        limit=1024*1204*8)
            print('Serving on {}:{}'.format(SERVER_IP, SERVER_PORT))
            async with server:
                await server.serve_forever()
        except Exception as err:  # try to recover from any exceptions by re-establishing connection
            print(f'Unhandled: {err}')
    #print(dir(server))
    #await asyncio.sleep(60)
    #server.close()
    #await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())

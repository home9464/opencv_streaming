#pylint: disable=missing-docstring, C0301, E1101, W0703

"""
# 1. install dependencies
sudo apt install -y libatlas-base-dev
pip install opencv-python==3.4.17.61
pip install numpy==1.22.2
pip install schedule==1.1.0


# 2. autostart when system rebooted

```bash
# 1. use contab
crontab -e
# 2. append this line to the end, save then exit
@reboot /usr/bin/python /home/pi/Desktop/pi_cam_stream_client.py
# 3. reboot the board
```

# 3. enable camera
```bash
sudo raspi-config
"3. Interface Options"  -> "I1 Legacy Camera" -> "Yes" -> "Finish" -> "Reboot"
```

"""
import os
import sys
import time
import asyncio
import datetime
import socket
import logging

import cv2

assert sys.version_info >= (3, 5, 2)

# (chr(255)+chr(0)+chr(0)+chr(0)+chr(255)+chr(0)+chr(0)+chr(0)+chr(255)).encode('utf-8')
FRAME_SEPARATOR = b'\xc3\xbf\x00\x00\x00\xc3\xbf\x00\x00\x00\xc3\xbf'

# send video stream to this server
SERVER_IP = '10.0.0.99'
SERVER_PORT = 8888

# only capture videos during night (8pm to 8am)
CAPTURE_HOURS = set([20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8])


logging.basicConfig(filename='default.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

LOG = logging.getLogger('pi_cam_client')


def internet_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        LOG.info(f'test internet connection [OK]')
        return True
    except socket.error as ex:
        LOG.error(f'test internet connection [Failed], {ex}')
        return False


async def connect_server() -> None:
    """connect to server
    """
    while True:
        try:
            LOG.info(f'connect server -> {SERVER_IP}:{SERVER_PORT}')
            reader, writer = await asyncio.open_connection(SERVER_IP, SERVER_PORT)
            return reader, writer
        except Exception as err:
            LOG.error(f'failed to connect server -> {err}')
        time.sleep(1)


async def client_camera(video_width=1280,
                        video_height=720,
                        video_color_gray=False) -> None:
    """
    start the camera

    """
    # connect to server
    reader, writer = await connect_server()
    LOG.info('server connected')

    # start camera
    cap = cv2.VideoCapture(0)
    cap.set(3, video_width)  # width, max 3280
    cap.set(4, video_height)  # height, max 2464
    cap.set(5, 24)  # Frame Per Second
    LOG.info('camera connected')

    start_time = time.time()
    while True:
        try:
            if int(time.time() - start_time) % 60 == 0:  # every minute check out if internet connection OK
                if not internet_connected():
                    LOG.error('internet disconnected, reboot the machine')
                    time.sleep(60)  # wait for a minute
                    os.system('sudo reboot')

            hour = datetime.datetime.now().hour
            if hour not in CAPTURE_HOURS:  # only capture video within CAPTURE_HOURS
                time_seconds_to_sleep = int(20 - hour) * 3600  # 20 is '8pm'
                LOG.info('hibernate')
                time.sleep(time_seconds_to_sleep)  # hibernate

            _, frame = cap.read()
            if video_color_gray:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #frame = cv2.flip(frame, 0)  # vertical flip
            frame = cv2.flip(frame, -1)  # flip both horizontally and vetically 
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tostring()  # class 'bytes'
            writer.write(data)
            writer.write(FRAME_SEPARATOR)
            await writer.drain()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as err:
            LOG.error(f'steaming failed, try to reconnect -> {err}')
            reader, writer = await connect_server()

    LOG.info('close the camera')
    cap.release()
    cv2.destroyAllWindows()
    LOG.info('close the connection')
    writer.close()
    await writer.wait_closed()
    LOG.info('exit')

if __name__ == '__main__':
    asyncio.run(client_camera())

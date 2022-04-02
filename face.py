"""
https://github.com/home9464/selfdrivingcar/blob/master/cam/camera_async_server.py

pip install opencv-python==3.4.10.37

"""
import sys
import time
import socket
import asyncio
import multiprocessing
import numpy as np
import cv2
"""
#import dlib
#from mtcnn.mtcnn import MTCNN
#import face_recognition

# conda install cmake
# pip install dlib
# pip install mtcnn
# pip install face_recognition

import face_recognition
face_locations = face_recognition.face_locations(frame)
for (y1, x2, y2, x1) in face_locations:
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)



import dlib
detector = dlib.get_frontal_face_detector()
faceRects = detector(frame, 1)
for faceRect in faceRects:
    x1 = faceRect.left()
    y1 = faceRect.top()
    x2 = faceRect.right()
    y2 = faceRect.bottom()
    #cv2.putText(frame, str(x1), (10, 20))
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


from mtcnn.mtcnn import MTCNN
detector = MTCNN()
results = detector.detect_faces(pixels)
# extract the bounding box from the first face
x1, y1, width, height = results[0]['box']
x2, y2 = x1 + width, y1 + height


import face_recognition
face_locations = face_recognition.face_locations(frame)
for (y1, x2, y2, x1) in face_locations:
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

"""

assert sys.version_info >= (3, 5, 2)  # for reader.readuntil

#FRAME_SEPARATOR = b'\xE2\x82\xAC\xE2\x82\xAC'
# (chr(255)+chr(0)+chr(0)+chr(0)+chr(255)+chr(0)+chr(0)+chr(0)+chr(255)).encode('utf-8')
FRAME_SEPARATOR = b'\xc3\xbf\x00\x00\x00\xc3\xbf\x00\x00\x00\xc3\xbf'
#LOCAL_IP = socket.gethostbyname(socket.gethostname())  # 10.0.0.3
LOCAL_IP = '10.0.0.3'
LOCAL_PORT = 8888


#hog_face_detector = dlib.get_frontal_face_detector()
#mtcnn_detector = MTCNN()

P = multiprocessing.Pool(4)

def _process_image(image):
    resized = cv2.resize(image, (320, 240), interpolation=cv2.INTER_AREA)

    def _dlib(image):  # 0.06
        box = hog_face_detector(image, 1)[0]
        x1 = box.left()
        y1 = box.top()
        x2 = box.right()
        y2 = box.bottom()
        return [(x1, y1, x2, y2)]

    def _mtcnn(image):  # 0.10
        results = mtcnn_detector.detect_faces(image)
        # extract the bounding box from the first face
        x1, y1, width, height = results[0]['box']
        x2, y2 = x1 + width, y1 + height
        return [(x1, y1, x2, y2)]

    def _face_recog(image):  # 0.05
        face_locations = face_recognition.face_locations(image)
        box = face_locations[0]
        (y1, x2, y2, x1) = box
        return [(x1, y1, x2, y2)]

    return _face_recog(resized)


async def _handle_cam(reader, writer):
    sep_len = len(FRAME_SEPARATOR)
    while True:
        img = None
        frame = await reader.readuntil(separator=FRAME_SEPARATOR)  # blocked until read something
        # truncate the separator
        frame = frame[:-sep_len]
        frame = np.asarray(bytearray(frame), dtype=np.uint8)
        img = cv2.imdecode(frame, -1)
        if img is not None:
            #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            start = time.time()
            # P.map(_process_image, [img])
            #face_boxes = _process_image(img)
            #print(time.time()-start)
            #for x1, y1, x2, y2 in face_boxes:
                #cv2.putText(frame, str(x1), (10, 20))
            #    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow('jpg', img)
            cv2.waitKey(1)
        # some time-consuming operations
        #addr = writer.get_extra_info('peername')
        #ack = await _process_image(img)
        data = str.encode("hello"+'\n')
        writer.write(data)
        await writer.drain()
        #await asyncio.sleep(0)


async def camera_cb(reader, writer):
    """called whenever a new client connection is established
    """
    try:
        await _handle_cam(reader, writer)
    except (asyncio.IncompleteReadError, ConnectionResetError, ConnectionAbortedError):
        print('Lost client connection')
        cv2.destroyAllWindows()


async def main():
    server = await asyncio.start_server(camera_cb,
                                        LOCAL_IP,
                                        LOCAL_PORT,
                                        limit=1024*1204*8)
    print('Serving on {}:{}'.format(LOCAL_IP, LOCAL_PORT))
    #async with server:
    #    await server.serve_forever()
    #print(dir(server))
    await asyncio.sleep(60)
    server.close()
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
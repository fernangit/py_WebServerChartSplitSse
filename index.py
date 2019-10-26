# coding: utf-8
from bottle import run, route, response, view, static_file
import time
import os
import random
import json
from threading import (Event, Thread)

import picamera
import picamera.array
import cv2
import analyze_emotion as em

#cascade_file = "/home/pi/work/haarcascades/haarcascade_frontalface_default.xml"
cascade_file = "/home/pi/work/haarcascades/haarcascade_frontalface_alt2.xml"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'assets')

event = Event()

@route('/')
@view("index.html")
def index():
    return dict()

@route('/sse')
def sse():
#    count = 0
    emotion = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content_Type']  = 'text/event-stream'
    while (True):
        enc = json.dumps(emotion)
        print(enc)
        print(type(enc))
        yield 'data: %s\n\n' % enc
#        yield 'data:"hello SSE"\n\n'
#        yield 'data: %s\n' 'retry:10\n\n' % str(count)
#        yield 'data: %i\n\n' % str(count)
#        yield 'data: %s\n\n' % emotion['angry']
#        yield 'data: {0}\n\n' .format(count)
#        yield 'data: {0}\n\n' .format(emotion['angry'])
        time.sleep(1)
#        count = count + 1
#        count = random.randint(1, 50)
#        emotion['angry'] = random.randint(1, 50)
        rint = random.randint(0, 6)
        if rint == 0:
            emotion['angry'] = random.randint(1, 50)
        elif rint == 1:
            emotion['disgust'] = random.randint(1, 50)
        elif rint == 2:
            emotion['fear'] = random.randint(1, 50)
        elif rint == 3:
            emotion['happy'] = random.randint(1, 50)
        elif rint == 4:
            emotion['sad'] = random.randint(1, 50)
        elif rint == 5:
            emotion['surprise'] = random.randint(1, 50)
        elif rint == 6:
            emotion['neutral'] = random.randint(1, 50)
         

@route('/assets/css/<filename:path>')
def send_static(filename):
    """cssファイルを返す
    """
    return static_file(filename, root=f'{STATIC_DIR}/css')

@route('/assets/js/<filename:path>')
def send_static(filename):
    """jsファイルを返す
    """
    return static_file(filename, root=f'{STATIC_DIR}/js')

def face_analyze():
    print('face_analyze')
    # 初期化
    model, predicts = em.init_emotion(10)
    print(predicts)

    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (320, 240)
            while True:
                # stream.arrayにRGBの順で映像データを格納
                camera.capture(stream, 'bgr', use_video_port=True)

                # グレースケールに変換
                gray = cv2.cvtColor(stream.array, cv2.COLOR_BGR2GRAY)

                # カスケードファイルを利用して顔の位置を見つける
                cascade = cv2.CascadeClassifier(cascade_file)
                face_list = cascade.detectMultiScale(gray, minSize=(100, 100), minNeighbors=3)

                for (x, y, w, h) in face_list:
#                    print("face_position:",x, y, w, h)
                    color = (0, 0, 255)
                    pen_w = 5
                    # 画像切り出し
                    dst = stream.array[y:y+h, x:x+w]
                    # 画像保存
                    cv2.imwrite("images/face.jpg", dst)
                    # 矩形表示
                    cv2.rectangle(stream.array, (x, y), (x+w, y+h), color, thickness = pen_w)
                    # 感情分析
                    predict = em.emotion(model)
                    print(predict)
                    # 平均算出
                    predicts = em.mean_emotion(predict, predicts)

                # system.arrayをウィンドウに表示
                cv2.imshow('frame', stream.array)

                # "q"でウィンドウを閉じる
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                # streamをリセット
                stream.seek(0)
                stream.truncate()
            cv2.destroyAllWindows()

#スレッド開始
thread = Thread(target=face_analyze)
thread.start()

# run(host="localhost", port=8080, debug=True, reloader=True)
myport = os.getenv("PORT", 8080)
myaddr = os.getenv("IP", "localhost")
run(host=myaddr, port=myport, debug=True, reloader=True)

# coding: utf-8
from bottle import run, route, response, view, static_file
import time
import os
import random
import json
import pickle
from threading import (Event, Thread)

import numpy as np
import picamera
import picamera.array
import cv2
import analyze_emotion as em

#for ガスセンサー
import RPi.GPIO as GPIO
from TP401T import TP401T

#for 温湿度センサー
import smbus2
import bme280

#cascade_file = "/home/pi/work/haarcascades/haarcascade_frontalface_default.xml"
cascade_file = "/home/pi/work/haarcascades/haarcascade_frontalface_alt2.xml"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'assets')

#感情平均
predict_mean = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.4])

#空気
air_status = TP401T.WAITING
air_value = 0

#温湿度
BME280_ADDR = 0x76
BUS_NO = 1
temp = 0
humid = 0

@route('/')
#@view("index.html")
@view("dashBoard.html")
def index():
    return dict()

@route('/sse')
def sse():
    value = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0, 'air': 0, 'airValue': 0, 'temp': 0, 'humid': 0}
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content_Type']  = 'text/event-stream'

    global air_status
    global air_value
    global temp
    global humid

    while (True):
####テスト ランダムに感情値を変えてみる
#        rint = random.randint(0, 6)
#        if rint == 0:
#            value['angry'] = random.randint(1, 50)
#        elif rint == 1:
#            value['disgust'] = random.randint(1, 50)
#        elif rint == 2:
#            value['fear'] = random.randint(1, 50)
#        elif rint == 3:
#            value['happy'] = random.randint(1, 50)
#        elif rint == 4:
#            value['sad'] = random.randint(1, 50)
#        elif rint == 5:
#            value['surprise'] = random.randint(1, 50)
#        elif rint == 6:
#            value['neutral'] = random.randint(1, 50)
####感情分析結果を反映する
        with open('list.txt', 'rb') as l:
            predict_mean = pickle.load(l)
        print('sse:', predict_mean)

        print('before:', value)
        value['angry'] = predict_mean[0]
        value['disgust'] = predict_mean[1]
        value['fear'] = predict_mean[2]
        value['happy'] = predict_mean[3]
        value['sad'] = predict_mean[4]
        value['surprise'] = predict_mean[5]
        value['neutral'] = predict_mean[6]
        value['air'] = air_status
        value['airValue'] = air_value
        value['temp'] = temp
        value['humid'] = humid
        print('after:', value)

        enc = json.dumps(value)
        print(enc)
        print(type(enc))
        yield 'data: %s\n\n' % enc
        time.sleep(1)

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
    print('face_analyze:', predicts)

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
                    predicts, predict_mean = em.mean_emotion(predict, predicts)
                    print('face_analyze()')
                    print(predict_mean)
                    with open('list.txt', 'wb') as l:
                        pickle.dump(predict_mean, l)

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
thread1 = Thread(target=face_analyze)
thread1.start()

def air_analyze():
    print('air_analyze')
    global air_status
    global air_value
    sensor = TP401T()
    sensor.start()
    print('待機中です')
    while sensor.state == TP401T.WAITING:	# 測定開始待ち
        time.sleep(3)
    while True:
        air_status = sensor.state
        air_value = sensor.value
#        print('air_status:{0} air_value:{1}'.format(air_status, air_value))
        time.sleep(3)
	
#スレッド開始
thread2 = Thread(target=air_analyze)
thread2.start()

def temp_humid_analyze():
    print('temp_humid_analyze')
    global temp
    global humid
    # BME280
    i2c = smbus2.SMBus(BUS_NO)
    bme280.load_calibration_params(i2c, BME280_ADDR)

    while True:
        data = bme280.sample(i2c, BME280_ADDR)
        temp = round(data.temperature,1)
#        print('temp:{0}'.format(temp))
        humid = round(data.humidity,1)
#        print('humid:{0}'.format(humid))
        time.sleep(1)
	
#スレッド開始
thread3 = Thread(target=temp_humid_analyze)
thread3.start()

# run(host="localhost", port=8080, debug=True, reloader=True)
myport = os.getenv("PORT", 8080)
myaddr = os.getenv("IP", "localhost")
run(host=myaddr, port=myport, debug=True, reloader=True)

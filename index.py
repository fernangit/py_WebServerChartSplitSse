from bottle import run, route, response, view, static_file
import time
import os
import random
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'assets')

@route('/')
#@view("index.min.html")
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

# run(host="localhost", port=8080, debug=True, reloader=True)
myport = os.getenv("PORT", 8080)
myaddr = os.getenv("IP", "localhost")
run(host=myaddr, port=myport, debug=True, reloader=True)

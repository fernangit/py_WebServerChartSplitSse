# py_WebServerChartSplitSse
Dynamic display switching of a chart and messages on the python web server bottle.
---
* python Webサーバ  
  * WebフレームワークBottleの使用  
    * CSS, JS(Static)ファイルの読み込み  
* サーバークライアントデータ送信  
  * SSE(Server Sent Event)の使用(IE,Edge未対応)    
    * JSONエンコード／デコードによる複数データの送信  
* グラフ表示  
  * Chart.jsの使用  
* BOX横ならべ  
  * FlexBoxの使用  
* マウスカーソルを非表示  
  * unclutterの使用  
* スリープモードをオフ  


## HOW TO USE
### インストール
1. Bottle
```
pip3 install bottle
```
2. Chart.js  
GitHubからライブラリをダウンロード  
https://www.chartjs.org/  
Zipファイルを解凍して、Chart.min.jsを任意のフォルダに設定  
py_WebServerChartSplitSse\assets\js\Chart.min.js  
円グラフ用オプションをダウンロード  
https://github.com/emn178/chartjs-plugin-labels  
Zipファイルを解凍して、Chart.min.jsを任意のフォルダに設定  
py_WebServerChartSplitSse\assets\js\chartjs-plugin-labels.js  

3. unclutter  
```
sudo apt-get install unclutter
```
さらに  
/etc/xdg/lxsession/LXDE/autostart  
に、以下の文字列を追加し、リブート
```
@unclutter -idle 0.1 -root
```
4. スリープモードオフ  
/etc/xdg/lxsession/LXDE/autostart  
に、以下の文字列を追加
```
# スクリーンセーバーをオフに
@xset s off
# X serverをオフに 
@xset s noblank
# DPMS (Display Power Management Signaling) をオフに
@xset -dpms
```
/etc/lightdm/lightdm.conf  
に、以下の文字列を追加し、リブート
```
xserver-command=X -s 0 -dpms
```


### サーバ／クライアントの記述
#### サーバ起動の記述
```
from bottle import run, route, view
 
@route('/')
@view("index.html")
def index():
    return dict()

myport = os.getenv("PORT", 8080)
myaddr = os.getenv("IP", "localhost")
run(host=myaddr, port=myport, debug=True, reloader=True)
```
#### Staticファイル読み込みの記述  
cssファイル、jsファイルを任意のフォルダに設定  
py_WebServerChartSplitSse\assets\js  
py_WebServerChartSplitSse\assets\css

static_fileをインポートして、処理を記述する
```
from bottle import run, route, view, static_file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'assets')

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
```
#### SSE(Server Sent Event)の記述  
responseをインポートして、処理を記述する。  
配列データをJson型からScript型にエンコードして送信する。  
```
from bottle import run, route, response, view, static_file
@route('/sse')
def sse():
    emotion = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content_Type']  = 'text/event-stream'
    while (True):
        enc = json.dumps(emotion)
        yield 'data: %s\n\n' % enc
        time.sleep(1)
```
クライアント側では受信データをJson型にデコードする
```
let eventSrc = new EventSource("/sse")
eventSrc.addEventListener("message", getMessage)
//SSEメッセージ受信
function getMessage(e) {
    obj = JSON.parse(e.data);
    console.log(obj);
}
```
#### グラフ表示の記述  
クライアント側  
```
<head>
  <meta charset="UTF-8">
  <title>Chart.js v2.0</title>
  <script src="assets/js/Chart.min.js"></script>
</head>
<body>
    <script>
        //グラフ描画
        var ctx = document.getElementById("canvas").getContext("2d");
        var option = {
        animation: false
        };
        window.myLine = new Chart(ctx, {
        type: 'pie',
        options: option,
        data: {
            labels: ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"],
            datasets: [{
            backgroundColor: [
                "#2ecc71",
                "#3498db",
                "#95a5a6",
                "#9b59b6",
                "#f1c40f",
                "#e74c3c",
                "#34495e"
            ],
            data: [emotion[0], emotion[1], emotion[2], emotion[3], emotion[4], emotion[5], emotion[6]]
            }],
        }
        };
    </script>
</body>
```
#### BOXの横ならべ記述  
cssに記述。flexを利用する。
```
 /* --- 外枠の定義 ---------------------------------------------*/
.flexbox {
  display        : flex;    /* FlexBox定義         */

 /* --- 個別のBOXの定義 --------------------------------------- */
#split-left, #split-right {
flex-grow      : 1; /* 各BOXを均等に割当て */
```

### 温湿度センサ
独Bosch Sensortec社　BME280  
RPi.MME280モジュールを利用する。  
```
sudo pip3 install Rpi.BME280  
```

### ガス度センサ
Shenzhen Dovelet Sensors Technology社　TP-401T
ADコンバータ　MCP3424  
```
sudo sh -c "echo 'mcp3424 0x68' > /sys/bus/i2c/devices/i2c-1/new_device"
sudo sh -c "echo 15 > /sys/bus/i2c/devices/1-0068/iio\:device0/in_voltage_sampling_frequency"
```
常用するには/etc/rc.localに以下を追加する。
```
echo 'mcp3424 0x68' > /sys/bus/i2c/devices/i2c-1/new_device
echo 15 > /sys/bus/i2c/devices/1-0068/iio\:device0/in_voltage_sampling_frequency
```

### サーバ起動  
```
python index.py  
```

### ブラウザ表示  
ブラウザ上で  
http://localhost:8080/  
* chromium-browserでKIOSK表示  
  * chromium-browser --kiosk --incoginito localhost:8080    
* ALT + F4でKIOSKモード解除  

## 参考情報
Python Bottleフレームワーク  
https://www.netmarvs.com/archives/697  
Chart.js  
https://www.chartjs.org/  
グラフ作成にオススメ！「Chart.js」がかんたんに使えてイイ感じ  
http://vdeep.net/chart-js  
Chart.jsを使って、棒グラフ、折れ線グラフ、レーダーチャート、円グラフを表示しよう！（サンプル・解説付き）  
https://www.wp-benricho.com/chart-js/  
Chart.pieceLabelの利用（対象：円グラフ、ドーナツチャート）  
http://www.kogures.com/hitoshi/javascript/chartjs/piece-label.html  
Chart.jsで凡例を削除する  
https://hacknote.jp/archives/21133/  
CSSを外部ファイルに記述 - bottle  
https://tmg0525.hatenadiary.jp/entry/2018/03/04/004706  
PythonとWebフレームワークとServer Sent Events  
https://note.mu/v416/n/n2fe9227ad4e1  
Server-Sent Events はこんなに簡単  
https://rch850.hatenablog.com/entry/20101207/1291694802  
【CSS】Flexboxの使い方を徹底解説！基本から実践まで(サンプルあり)  
https://creive.me/archives/15427/  
CSSでDIVを横並びにする色々な方法  
https://webparts.cman.jp/box/siderow/  
Raspberry Pi でマウスカーソルを非表示にする  
https://blog.withachristianwife.com/2017/04/09/disable-mouse-cursor-in-raspberry-pi/  

## License

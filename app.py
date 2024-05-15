import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import touch as t

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域请求
touch = t.Touch (port="COM1", baudrate=9600, touch_side="L")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/touch')
def touch_handler():
    region = request.args.get('region')
    # 使用 socketio 对象发送消息到客户端
    socketio.emit('response', json.dumps({'msg': 'ok', "action": "touch"}))
    # 调用 touch 对象的实例方法
    touch.send_multi_touch([region])
    return {'resp': 'ok', "data": ""}

@socketio.on('ping')
def handle_ping(data):
    emit('pong', 'pong')

@socketio.on('message')
def handle_message(data):
    print(data)
    try:
        data = json.loads(data)
    except Exception as e:
        emit('response', json.dumps({'msg': 'json parse err', 'action': 'err'}))
        return None
    print(data)
    # 使用传统的 if-elif-else 结构处理不同的情况
    if data["action"] == 'touch':
        if touch.allow_to_send_touch:
            touch.send_multi_touch(data["regions"])
            emit('response', json.dumps({'msg': 'ok', "action": 'touch'}))
        else:
            emit('response', json.dumps({'msg': 'not allowed', 'action': 'touch'}))
    elif data["action"] == 'ping':
        emit('response', json.dumps({'msg': 'pong', "action": "ping"}))
    elif data["action"] == 'check':
        emit('response', json.dumps({'msg': str(touch.allow_to_send_touch).lower(), 'action': 'check'}))
    else:
        emit('response', json.dumps({'msg': 'unknown action', 'action': data['action']}))

if __name__ == '__main__':
    # 使用 socketio 对象启动服务器
    socketio.run(app, host="0.0.0.0", port=9000, debug=True)

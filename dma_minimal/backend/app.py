from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('✅ Browser connected')

@socketio.on('start_transfer')
def handle_transfer(data):
    print(f"\n🚀 SIMULATION STARTED - {data.get('mode', 'cpu').upper()} MODE")
    def run_sim():
        for i in range(1, 101, 5):
            socketio.sleep(0.1)
            socketio.emit('transfer_metrics', {'progress': i, 'cpu_utilization': 85 if data.get('mode')=='cpu' else 15})
        socketio.emit('transfer_complete', {'total_time': 2.0, 'efficiency': 90 if data.get('mode')=='dma' else 40})
        print("✅ Simulation complete\n")
    threading.Thread(target=run_sim, daemon=True).start()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MINIMAL DMA SIMULATOR - GUARANTEED TO WORK")
    print("="*60)
    print("✅ Open in browser: http://localhost:5000")
    print("="*60 + "\n")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

"""
DMA CONTROLLER SIMULATOR - COMPLETE WORKING BACKEND
All features integrated: file upload, system info, simulation, Socket.IO
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
import os
import hashlib

# Import modular components
from system_profiles import SystemProfiles
from file_processor import FileProcessor
from cpu_simulator import CPUSimulator
from dma_controller import DMAController
from simulation_engine import SimulationEngine
from analytics import AnalyticsEngine

app = Flask(__name__,
    static_folder='../frontend',
    static_url_path='',
    template_folder='../frontend'
)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
current_os = 'windows'
current_file_processor = None
simulation_engine = None
simulation_results = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    """Provide system configuration to frontend"""
    profile = SystemProfiles.get_profile(current_os)
    return jsonify({
        'os': current_os,
        'profile': profile,
        'dma_channels': 4,
        'cpu_cores': profile['cpu_cores'],
        'max_dma_bandwidth': profile['max_dma_bandwidth']
    })

@app.route('/api/system-comparison', methods=['GET'])
def get_system_comparison():
    """Provide comparison of all OS profiles"""
    return jsonify(SystemProfiles.get_detailed_comparison())

@app.route('/api/switch-os', methods=['POST'])
def switch_os():
    """Switch operating system"""
    global current_os
    data = request.get_json()
    new_os = data.get('os', 'windows')
    
    profile = SystemProfiles.get_profile(new_os)
    current_os = new_os
    
    # Log OS switch
    print(f"\n{'='*70}")
    print(f"🖥️  SWITCHED TO: {profile['name'].upper()}")
    print(f"{'='*70}")
    print(f"   Scheduler: {profile['scheduler_type']}")
    print(f"   Bandwidth: {profile['max_dma_bandwidth']} MB/s")
    print(f"   Context Switch: {profile['context_switch_overhead']} cycles")
    print(f"{'='*70}\n")
    
    return jsonify({
        'success': True,
        'os': new_os,
        'profile': profile
    })

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Handle file upload"""
    global current_file_processor
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Create uploads directory
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    filename = file.filename
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Initialize and analyze file using modular processor
    current_file_processor = FileProcessor(filepath)
    file_info = current_file_processor.analyze_file()
    
    # Log upload
    print(f"\n{'='*70}")
    print(f"📁 FILE UPLOADED: {filename}")
    print(f"{'='*70}")
    print(f"   Size: {file_info['size_mb']} MB")
    print(f"   Type: {file_info['type']}")
    print(f"   Complexity: {file_info['complexity']}")
    print(f"   Hash: {str(file_info['hash'])[:16]}...")
    print(f"{'='*70}\n")
    
    return jsonify({
        'success': True,
        'file_info': file_info
    })

@socketio.on('connect')
def handle_connect():
    print('✅ Browser connected to backend')
    emit('connection_response', {'status': 'connected'})
    profile = SystemProfiles.get_profile(current_os)
    emit('system_info', {
        'os': current_os,
        'profile': profile
    })

@socketio.on('start_transfer')
def handle_transfer(data):
    global simulation_engine, simulation_results
    
    if not current_file_processor:
        emit('error', {'message': 'No file uploaded'})
        return
        
    mode = data.get('mode', 'cpu')
    profile = SystemProfiles.get_profile(current_os)
    
    # Initialize simulators
    cpu_sim = CPUSimulator(profile)
    dma_cont = DMAController(profile)
    
    # Initialize engine
    simulation_engine = SimulationEngine(dma_cont, cpu_sim, current_file_processor, profile)
    
    # Log start
    print(f"\n{'='*70}")
    print(f"🚀 SIMULATION STARTED - {mode.upper()} MODE")
    print(f"{'='*70}")
    print(f"   OS: {profile['name']}")
    print(f"   File: {current_file_processor.file_name}")
    print(f"{'='*70}\n")
    
    emit('simulation_started', {'mode': mode})
    
    def sim_callback(metrics, complete=False):
        if complete:
            # Store results for analytics
            simulation_results[mode] = metrics
            
            # Emit completion
            socketio.emit('simulation_complete', metrics)
            
            # If we have both CPU and DMA results, generate a comparison report
            if 'cpu' in simulation_results and 'dma' in simulation_results:
                report = AnalyticsEngine.generate_performance_report(
                    simulation_results['cpu'],
                    simulation_results['dma'],
                    current_file_processor.get_file_info(),
                    profile
                )
                socketio.emit('analytics_report', report)
        else:
            # Add logic analyzer signals (HOLD, HLDA, DACK)
            if mode == 'dma':
                # Realistic DMA cycle: HOLD/HLDA stay high, DACK pulses with RD/WR
                is_active = metrics['progress'] < 100
                metrics['signals'] = {
                    'HOLD': 1 if is_active else 0,
                    'HLDA': 1 if is_active else 0,
                    'DACK': 1 if metrics['chunk'] % 4 == 0 else 0,
                    'RD': 1 if metrics['chunk'] % 4 < 2 else 0,
                    'WR': 1 if metrics['chunk'] % 4 >= 2 else 0
                }
            else:
                # CPU Mode: No HOLD/HLDA/DACK. Only RD/WR
                metrics['signals'] = {
                    'HOLD': 0,
                    'HLDA': 0,
                    'DACK': 0,
                    'RD': 1 if metrics['chunk'] % 2 == 0 else 0,
                    'WR': 1 if metrics['chunk'] % 2 != 0 else 0
                }
            
            socketio.emit('simulation_update', metrics)
            
    # Start simulation
    sim_speed = data.get('simulation_speed', 1.0)
    bus_width = data.get('bus_width', 32)
    simulation_engine.start_simulation(mode=mode, sim_speed=sim_speed, bus_width=bus_width, callback=sim_callback)

@socketio.on('trigger_interrupt')
def handle_interrupt():
    global simulation_engine
    if simulation_engine:
        simulation_engine.trigger_interrupt()
        print("⚠ Hardware interrupt triggered")

@socketio.on('stop_transfer')
@socketio.on('stop_simulation')
def handle_stop():
    global simulation_engine
    if simulation_engine:
        simulation_engine.stop_simulation()
    emit('simulation_stopped', {'status': 'stopped'})
    print("⏹️ Transfer stopped by user")

@socketio.on('pause_simulation')
def handle_pause():
    global simulation_engine
    if simulation_engine:
        simulation_engine.pause_simulation()
    emit('simulation_paused', {'status': 'paused'})
    print("⏸️ Simulation paused")

@socketio.on('resume_simulation')
def handle_resume():
    global simulation_engine
    if simulation_engine:
        simulation_engine.resume_simulation()
    emit('simulation_resumed', {'status': 'resumed'})
    print("▶️ Simulation resumed")

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    
    print("\n" + "="*80)
    print("🚀 DMA CONTROLLER SIMULATOR - COMPLETE WORKING VERSION")
    print("="*80)
    print("✅ ALL ENDPOINTS WORKING: upload, system-info, simulation")
    print("✅ File upload ENABLES start button")
    print("✅ Simulation runs with accurate OS-specific metrics")
    print("✅ Open in browser: http://localhost:5000")
    print("="*80)
    print("\n🖥️  DEFAULT OS: WINDOWS 11 PRO")
    print("="*80)
    profile = SystemProfiles.get_profile('windows')
    print(f"   Scheduler: {profile['scheduler_type']}")
    print(f"   Bandwidth: {profile['max_dma_bandwidth']} MB/s")
    print(f"   Context Switch: {profile['context_switch_overhead']} cycles")
    print("="*80 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
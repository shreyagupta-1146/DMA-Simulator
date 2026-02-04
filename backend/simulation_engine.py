"""
Simulation Engine - Core simulation logic with real-time updates
"""
import threading
import time
import random
from datetime import datetime

class SimulationEngine:
    """
    Manages the simulation lifecycle and real-time updates
    """
    
    def __init__(self, dma_controller, cpu_simulator, file_processor, system_profile):
        self.dma_controller = dma_controller
        self.cpu_simulator = cpu_simulator
        self.file_processor = file_processor
        self.system_profile = system_profile
        
        self.mode = 'cpu'  # 'cpu' or 'dma'
        self.active = False
        self.paused = False
        self.current_chunk = 0
        self.total_chunks = 0
        self.bytes_transferred = 0
        self.start_time = None
        self.end_time = None
        self.callback = None
        
        # New parameters
        self.sim_speed = 1.0
        self.bus_width = 32
        self.interrupt_triggered = False
        self.last_metrics = {} # To store instant values for charts
        
        # Simulation parameters
        self.chunk_size = 1024  # 1KB chunks for better granularity
        self.base_delay = system_profile['transfer_delay']
        
    def start_simulation(self, mode='cpu', sim_speed=1.0, bus_width=32, callback=None):
        """
        Start the simulation with speed and bus width considerations
        """
        self.mode = mode
        self.sim_speed = sim_speed
        self.bus_width = bus_width
        self.active = True
        self.paused = False
        self.current_chunk = 0
        self.bytes_transferred = 0
        self.start_time = time.time()
        self.callback = callback
        
        # Calculate total chunks
        self.total_chunks = max(10, self.file_processor.file_size // self.chunk_size)
        if self.total_chunks > 200: self.total_chunks = 200 # Cap for UI performance
        
        # Start simulation in background thread
        thread = threading.Thread(target=self._run_simulation)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def _run_simulation(self):
        """
        Run the simulation loop
        """
        while self.active and self.current_chunk < self.total_chunks:
            if self.paused:
                time.sleep(0.1)
                continue
            
            # Handle Interrupt
            delay_modifier = 1.0
            if self.interrupt_triggered:
                if self.mode == 'cpu':
                    delay_modifier = 8.0 # Critical lag
                else:
                    delay_modifier = 2.0 # Minor lag
                self.interrupt_triggered = False
            
            # Process one chunk
            self._process_chunk()
            
            # Emit update
            if self.callback:
                metrics = self._get_current_metrics()
                self.callback(metrics)
            
            # Wait for next update
            # Variable delay to prevent perfectly flat lines
            jitter = random.uniform(0.8, 1.2)
            wait_time = (self.base_delay / self.sim_speed) * delay_modifier * jitter
            time.sleep(max(0.005, wait_time))
        
        # Simulation complete
        self.active = False
        self.end_time = time.time()
        
        # Final callback
        if self.callback:
            final_metrics = self._get_final_metrics()
            self.callback(final_metrics, complete=True)
    
    def _process_chunk(self):
        """
        Process a single chunk and store instant metrics for the graph
        """
        file_type = self.file_processor.file_type
        
        # Calculate real chunk size based on total iterations
        # Use floating point to avoid zero-chunking for small files
        actual_chunk_size = self.file_processor.file_size / self.total_chunks
        
        # Bus width factor (32-bit is standard 1.0)
        bus_factor = 32 / self.bus_width
        
        if self.mode == 'cpu':
            metrics = self.cpu_simulator.process_chunk_cpu(actual_chunk_size, file_type)
            # Adjust cycles by bus width
            extra_cycles = int(metrics['cycles_used'] * (bus_factor - 1))
            self.cpu_simulator.total_cycles += extra_cycles
            self.cpu_simulator.active_cycles += extra_cycles
            self.last_metrics = {
                'cpu_util': metrics['cpu_utilization'],
                'bus_util': metrics['bus_utilization'],
                'dma_util': 0
            }
        else:
            dma_metrics = self.dma_controller.transfer_chunk(actual_chunk_size, file_type)
            cpu_metrics = self.cpu_simulator.process_chunk_dma(file_type)
            self.last_metrics = {
                'cpu_util': cpu_metrics['cpu_utilization'],
                'bus_util': dma_metrics['bus_utilization'],
                'dma_util': dma_metrics['dma_utilization']
            }
        
        self.bytes_transferred += actual_chunk_size
        self.current_chunk += 1
    
    def trigger_interrupt(self):
        """Simulate a hardware interrupt"""
        self.interrupt_triggered = True

    def _get_current_metrics(self):
        """
        Get current simulation metrics (Instant for charts, Avg for labels)
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        progress = min(100, (self.bytes_transferred / self.file_processor.file_size) * 100)
        
        # LOGICAL THROUGHPUT: Based on hardware specs, not wall-clock speed
        # CPU mode is typically 30-50% slower than DMA path
        mode_efficiency = 0.45 if self.mode == 'cpu' else 0.92
        
        # Factors: OS Max Bandwidth * Mode Efficiency * Bus Width Factor
        bus_boost = self.bus_width / 32
        base_throughput = self.system_profile['max_dma_bandwidth'] * mode_efficiency * bus_boost
        
        jitter = random.uniform(0.85, 1.15) 
        throughput = base_throughput * jitter
        
        cpu_stats = self.cpu_simulator.get_statistics()
        #dma_stats = self.dma_controller.get_statistics() if self.mode == 'dma' else {} # Not needed for instant
        
        # Use a minimum of cycles even for small simulations
        total_cycles = max(cpu_stats['total_cycles'], self.current_chunk * 1500)
        
        return {
            'progress': round(progress, 2),
            'elapsed_time': round(elapsed, 3),
            'bytes_transferred': self.bytes_transferred,
            'mb_transferred': round(self.bytes_transferred / (1024 * 1024), 2),
            'throughput_mbps': round(throughput, 2),
            # VIBRANT GRAPHS: Use last_metrics (instant) instead of stats (average)
            'cpu_utilization': round(self.last_metrics.get('cpu_util', 0), 1),
            'dma_utilization': round(self.last_metrics.get('dma_util', 0), 1),
            'bus_utilization': round(self.last_metrics.get('bus_util', 0), 1),
            'total_cycles': total_cycles,
            'mode': self.mode,
            'chunk': self.current_chunk,
            'total_chunks': self.total_chunks,
            'status': 'running'
        }
    
    def _get_final_metrics(self):
        total_time = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # Final throughput based on logical hardware speed
        mode_efficiency = 0.45 if self.mode == 'cpu' else 0.95
        throughput = self.system_profile['max_dma_bandwidth'] * mode_efficiency * (self.bus_width / 32)
        
        cpu_stats = self.cpu_simulator.get_statistics()
        dma_stats = self.dma_controller.get_statistics() if self.mode == 'dma' else {}
        
        if self.mode == 'dma':
            efficiency = 95 - (cpu_stats['active_percentage'] * 0.2) + (self.bus_width / 64 * 5)
        else:
            efficiency = 35 + (cpu_stats['active_percentage'] * 0.1) - (self.bus_width / 64 * 10)
        
        return {
            'total_time': round(total_time, 3),
            'throughput_mbps': round(throughput, 2),
            'total_cycles': int(cpu_stats['total_cycles']),
            'efficiency': round(min(99.9, efficiency), 2),
            'cpu_stats': cpu_stats,
            'dma_stats': dma_stats,
            'mode': self.mode,
            'status': 'complete',
            'file_info': self.file_processor.get_file_info()
        }
    
    def pause_simulation(self):
        self.paused = True
    def resume_simulation(self):
        self.paused = False
    def stop_simulation(self):
        self.active = False
        self.paused = False
    def is_active(self):
        return self.active
    def get_status(self):
        return {
            'active': self.active,
            'paused': self.paused,
            'mode': self.mode,
            'chunk': self.current_chunk,
            'total_chunks': self.total_chunks,
            'progress': round((self.current_chunk / self.total_chunks) * 100, 2) if self.total_chunks > 0 else 0
        }

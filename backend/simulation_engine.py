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
        
        # Simulation parameters
        self.chunk_size = 4096  # 4KB chunks
        self.update_interval = system_profile['transfer_delay']
        
    def start_simulation(self, mode='cpu', callback=None):
        """
        Start the simulation in a separate thread
        """
        self.mode = mode
        self.active = True
        self.paused = False
        self.current_chunk = 0
        self.bytes_transferred = 0
        self.start_time = time.time()
        self.callback = callback
        
        # Calculate total chunks
        self.total_chunks = max(1, self.file_processor.file_size // self.chunk_size)
        
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
            
            # Process one chunk
            self._process_chunk()
            
            # Emit update
            if self.callback:
                metrics = self._get_current_metrics()
                self.callback(metrics)
            
            # Wait for next update
            time.sleep(self.update_interval)
        
        # Simulation complete
        self.active = False
        self.end_time = time.time()
        
        # Final callback
        if self.callback:
            final_metrics = self._get_final_metrics()
            self.callback(final_metrics, complete=True)
    
    def _process_chunk(self):
        """
        Process a single chunk based on mode
        """
        file_type = self.file_processor.file_type
        
        if self.mode == 'cpu':
            # CPU-only transfer: high CPU usage
            metrics = self.cpu_simulator.process_chunk_cpu(self.chunk_size, file_type)
            dma_util = 0
            bus_util = metrics['bus_utilization']
        else:
            # DMA-assisted transfer: low CPU usage
            dma_metrics = self.dma_controller.transfer_chunk(self.chunk_size, file_type)
            metrics = self.cpu_simulator.process_chunk_dma(file_type)
            dma_util = dma_metrics['dma_utilization']
            bus_util = dma_metrics['bus_utilization']
        
        self.bytes_transferred += self.chunk_size
        self.current_chunk += 1
    
    def _get_current_metrics(self):
        """
        Get current simulation metrics
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        progress = min(100, (self.bytes_transferred / self.file_processor.file_size) * 100)
        throughput = (self.bytes_transferred / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        
        cpu_stats = self.cpu_simulator.get_statistics()
        dma_stats = self.dma_controller.get_statistics() if self.mode == 'dma' else {}
        
        return {
            'progress': round(progress, 2),
            'elapsed_time': round(elapsed, 3),
            'bytes_transferred': self.bytes_transferred,
            'mb_transferred': round(self.bytes_transferred / (1024 * 1024), 2),
            'throughput_mbps': round(throughput, 2),
            'cpu_utilization': cpu_stats['active_percentage'],
            'dma_utilization': dma_stats.get('avg_dma_utilization', 0),
            'bus_utilization': dma_stats.get('avg_bus_utilization', cpu_stats['active_percentage']),
            'total_cycles': cpu_stats['total_cycles'],
            'mode': self.mode,
            'chunk': self.current_chunk,
            'total_chunks': self.total_chunks,
            'status': 'running'
        }
    
    def _get_final_metrics(self):
        """
        Get final simulation metrics
        """
        total_time = self.end_time - self.start_time if self.start_time and self.end_time else 0
        total_mb = self.file_processor.file_size / (1024 * 1024)
        throughput = total_mb / total_time if total_time > 0 else 0
        
        cpu_stats = self.cpu_simulator.get_statistics()
        dma_stats = self.dma_controller.get_statistics() if self.mode == 'dma' else {}
        
        # Calculate efficiency
        if self.mode == 'dma':
            efficiency = 95 - (cpu_stats['active_percentage'] * 0.2)
        else:
            efficiency = 40 + (cpu_stats['active_percentage'] * 0.1)
        
        return {
            'total_time': round(total_time, 3),
            'throughput_mbps': round(throughput, 2),
            'total_cycles': cpu_stats['total_cycles'],
            'efficiency': round(efficiency, 2),
            'cpu_stats': cpu_stats,
            'dma_stats': dma_stats,
            'mode': self.mode,
            'status': 'complete',
            'file_info': self.file_processor.get_file_info()
        }
    
    def pause_simulation(self):
        """Pause the simulation"""
        self.paused = True
    
    def resume_simulation(self):
        """Resume the simulation"""
        self.paused = False
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.active = False
        self.paused = False
    
    def is_active(self):
        """Check if simulation is active"""
        return self.active
    
    def get_status(self):
        """Get current simulation status"""
        return {
            'active': self.active,
            'paused': self.paused,
            'mode': self.mode,
            'chunk': self.current_chunk,
            'total_chunks': self.total_chunks,
            'progress': round((self.current_chunk / self.total_chunks) * 100, 2) if self.total_chunks > 0 else 0
        }
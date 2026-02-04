"""
CPU Simulator - Advanced with realistic overhead calculations
"""
import random
import time

class CPUSimulator:
    """
    Simulates CPU processing during data transfers with realistic metrics
    """
    
    def __init__(self, system_profile):
        self.profile = system_profile
        self.cpu_cores = system_profile['cpu_cores']
        self.clock_speed_ghz = system_profile['clock_speed_ghz']
        self.cycles_per_byte = system_profile['cycles_per_byte']
        self.context_switch_overhead = system_profile['context_switch_overhead']
        
        self.total_cycles = 0
        self.idle_cycles = 0
        self.active_cycles = 0
        self.context_switches = 0
        self.instruction_count = 0
        self.cycle_history = []
        
    def process_chunk_cpu(self, chunk_size, file_type='generic'):
        """
        Simulate CPU processing a data chunk (CPU-only mode)
        High CPU usage because CPU does all the work
        """
        file_complexity = self._get_file_complexity(file_type)
        
        # CPU must copy data byte by byte
        cycles_for_transfer = chunk_size * self.cycles_per_byte * file_complexity
        
        # Add overhead for memory access and I/O operations
        memory_access_overhead = chunk_size * 2 * file_complexity  # Read + Write
        io_overhead = chunk_size * 0.5 * file_complexity  # I/O operations
        
        total_cycles = cycles_for_transfer + memory_access_overhead + io_overhead
        
        # CPU utilization is very high (80-98%) with high jitter
        base_utilization = 82 + random.uniform(-10, 15)
        cpu_utilization = min(99.5, base_utilization * file_complexity)
        
        # Bus utilization (CPU monopolizes the bus)
        bus_utilization = min(98, 70 + random.uniform(-20, 25) * file_complexity)
        
        # Track statistics
        setup_cost = random.randint(1000, 3000) # Base setup for each chunk
        self.total_cycles += (total_cycles + setup_cost)
        self.active_cycles += (total_cycles + setup_cost)
        self.instruction_count += int(chunk_size * 1.5)
        
        # Record cycle data
        cycle_record = {
            'cycles_used': int(total_cycles),
            'cpu_utilization': cpu_utilization,
            'bus_utilization': bus_utilization,
            'memory_accesses': int(chunk_size * 2),
            'mode': 'cpu_intensive',
            'timestamp': time.time()
        }
        self.cycle_history.append(cycle_record)
        
        return cycle_record
    
    def process_chunk_dma(self, file_type='generic'):
        """
        Simulate minimal CPU overhead when DMA is handling transfer
        CPU just initiates DMA and does other tasks
        """
        file_complexity = self._get_file_complexity(file_type)
        
        # CPU only needs to set up DMA transfer
        setup_cycles = self.context_switch_overhead + random.randint(50, 200)
        setup_cycles *= file_complexity
        
        # CPU performs context switch
        self.context_switches += 1
        
        # CPU utilization is very low with high jitter
        base_util = 8 + random.uniform(-4, 12)
        cpu_utilization = min(35, base_util * file_complexity)
        
        # Track statistics
        self.total_cycles += setup_cycles
        self.idle_cycles += setup_cycles
        self.instruction_count += 50  # Minimal instructions
        
        return {
            'cycles_used': int(setup_cycles),
            'cpu_utilization': cpu_utilization,
            'mode': 'dma_assisted',
            'context_switches': self.context_switches
        }
    
    def _get_file_complexity(self, file_type):
        """Return complexity multiplier for different file types"""
        complexities = {
            'text': 0.7,
            'image': 1.3,
            'document': 1.4,
            'video': 1.6,
            'audio': 1.2,
            'archive': 1.5,
            'generic': 1.0
        }
        return complexities.get(file_type, 1.0)
    
    def get_statistics(self):
        """Get comprehensive CPU statistics"""
        total = self.total_cycles
        if total == 0:
            return {
                'total_cycles': 0,
                'active_cycles': 0,
                'idle_cycles': 0,
                'active_percentage': 0,
                'idle_percentage': 0,
                'context_switches': 0,
                'instruction_count': 0
            }
        
        return {
            'total_cycles': int(total),
            'active_cycles': int(self.active_cycles),
            'idle_cycles': int(self.idle_cycles),
            'active_percentage': round((self.active_cycles / total) * 100, 2),
            'idle_percentage': round((self.idle_cycles / total) * 100, 2),
            'context_switches': self.context_switches,
            'instruction_count': self.instruction_count,
            'cycles_per_instruction': round(total / self.instruction_count, 2) if self.instruction_count > 0 else 0
        }
    
    def get_cycle_history(self, limit=50):
        """Get recent cycle history"""
        return self.cycle_history[-limit:] if self.cycle_history else []
    
    def reset(self):
        """Reset CPU statistics"""
        self.total_cycles = 0
        self.idle_cycles = 0
        self.active_cycles = 0
        self.context_switches = 0
        self.instruction_count = 0
        self.cycle_history = []
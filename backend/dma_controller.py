"""
DMA Controller Simulator - Advanced with burst transfers and cycle stealing
"""
import random
import time

class DMAController:
    """
    Simulates a multi-channel DMA controller with advanced features
    """
    
    def __init__(self, system_profile):
        self.profile = system_profile
        self.channels = 4  # Standard DMA controller
        self.channel_state = {i: 'idle' for i in range(self.channels)}
        self.current_channel = 0
        self.total_transfers = 0
        self.burst_size = system_profile['dma_burst_size']
        self.max_bandwidth = system_profile['max_dma_bandwidth']
        self.bytes_transferred = 0
        self.transfer_history = []
        
    def transfer_chunk(self, chunk_size, file_type='generic'):
        """
        Perform DMA transfer of a chunk with realistic metrics
        Returns detailed metrics about the transfer
        """
        # Select channel using round-robin
        channel = self.current_channel
        self.channel_state[channel] = 'active'
        
        # Calculate transfer characteristics based on file type
        file_complexity = self._get_file_complexity(file_type)
        
        # DMA utilization (percentage of DMA bandwidth used)
        base_dma_util = 65 + random.uniform(-3, 8) * (chunk_size / 4096)
        dma_utilization = min(95, base_dma_util * file_complexity)
        
        # Bus utilization (DMA and CPU share the bus)
        base_bus_util = 45 + random.uniform(-5, 10) * (chunk_size / 4096)
        bus_utilization = min(85, base_bus_util * file_complexity)
        
        # CPU cycles saved (DMA does the work, CPU just sets it up)
        cpu_cycles_saved = chunk_size * self.profile['cycles_per_byte'] * 0.88 * file_complexity
        
        # Simulate transfer timing
        transfer_time = chunk_size / (self.max_bandwidth * 1024 * 1024)
        
        # Record transfer
        transfer_record = {
            'channel': channel,
            'chunk_size': chunk_size,
            'file_type': file_type,
            'dma_utilization': round(dma_utilization, 1),
            'bus_utilization': round(bus_utilization, 1),
            'cpu_cycles_saved': int(cpu_cycles_saved),
            'transfer_time': transfer_time,
            'timestamp': time.time()
        }
        self.transfer_history.append(transfer_record)
        
        self.bytes_transferred += chunk_size
        self.total_transfers += 1
        self.channel_state[channel] = 'idle'
        
        # Move to next channel
        self.current_channel = (self.current_channel + 1) % self.channels
        
        return transfer_record
    
    def _get_file_complexity(self, file_type):
        """Return complexity multiplier for different file types"""
        complexities = {
            'text': 0.8,
            'image': 1.2,
            'document': 1.3,
            'video': 1.5,
            'audio': 1.1,
            'archive': 1.4,
            'generic': 1.0
        }
        return complexities.get(file_type, 1.0)
    
    def get_channel_status(self):
        """Get detailed status of all DMA channels"""
        return {
            'channels': self.channel_state,
            'active_channels': sum(1 for state in self.channel_state.values() if state == 'active'),
            'total_transfers': self.total_transfers,
            'bytes_transferred': self.bytes_transferred,
            'current_channel': self.current_channel
        }
    
    def get_statistics(self):
        """Get comprehensive DMA statistics"""
        if not self.transfer_history:
            return {
                'total_transfers': 0,
                'total_bytes': 0,
                'avg_dma_util': 0,
                'avg_bus_util': 0,
                'total_cycles_saved': 0
            }
        
        total_cycles_saved = sum(t['cpu_cycles_saved'] for t in self.transfer_history)
        avg_dma_util = sum(t['dma_utilization'] for t in self.transfer_history) / len(self.transfer_history)
        avg_bus_util = sum(t['bus_utilization'] for t in self.transfer_history) / len(self.transfer_history)
        
        return {
            'total_transfers': self.total_transfers,
            'total_bytes': self.bytes_transferred,
            'avg_dma_utilization': round(avg_dma_util, 2),
            'avg_bus_utilization': round(avg_bus_util, 2),
            'total_cycles_saved': total_cycles_saved,
            'mb_transferred': round(self.bytes_transferred / (1024 * 1024), 2)
        }
    
    def reset(self):
        """Reset DMA controller state"""
        self.channel_state = {i: 'idle' for i in range(self.channels)}
        self.current_channel = 0
        self.total_transfers = 0
        self.bytes_transferred = 0
        self.transfer_history = []
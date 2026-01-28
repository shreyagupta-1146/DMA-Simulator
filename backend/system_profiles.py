"""
System Profiles - OS-specific configurations with detailed specs
"""
class SystemProfiles:
    PROFILES = {
        'windows': {
            'name': 'Windows 11 Pro',
            'cpu_cores': 4,
            'clock_speed_ghz': 2.8,
            'cycles_per_byte': 4,
            'context_switch_overhead': 1200,
            'dma_burst_size': 64,
            'max_dma_bandwidth': 133,
            'transfer_delay': 0.01,
            'scheduler_type': 'Multilevel Queue',
            'dma_priority': 'high',
            'color': '#0078D7',
            'description': 'Windows uses a multilevel feedback queue scheduler with high DMA priority. Context switch overhead is relatively high at 1200 cycles.'
        },
        'linux': {
            'name': 'Ubuntu 22.04 LTS',
            'cpu_cores': 8,
            'clock_speed_ghz': 3.2,
            'cycles_per_byte': 3,
            'context_switch_overhead': 800,
            'dma_burst_size': 128,
            'max_dma_bandwidth': 200,
            'transfer_delay': 0.008,
            'scheduler_type': 'Completely Fair Scheduler (CFS)',
            'dma_priority': 'very_high',
            'color': '#DD4814',
            'description': 'Linux CFS provides excellent DMA optimization with lowest context switch overhead (800 cycles) and highest bandwidth (200 MB/s).'
        },
        'macos': {
            'name': 'macOS Sonoma',
            'cpu_cores': 6,
            'clock_speed_ghz': 3.0,
            'cycles_per_byte': 3.5,
            'context_switch_overhead': 1000,
            'dma_burst_size': 64,
            'max_dma_bandwidth': 166,
            'transfer_delay': 0.009,
            'scheduler_type': 'Mach Kernel Scheduler',
            'dma_priority': 'high',
            'color': '#6C6C6C',
            'description': 'macOS uses Mach microkernel with optimized memory management. Balanced performance with 1000 cycle context switch overhead.'
        },
        'android': {
            'name': 'Android 14',
            'cpu_cores': 8,
            'clock_speed_ghz': 2.4,
            'cycles_per_byte': 5,
            'context_switch_overhead': 1500,
            'dma_burst_size': 32,
            'max_dma_bandwidth': 100,
            'transfer_delay': 0.012,
            'scheduler_type': 'EAS Scheduler',
            'dma_priority': 'medium',
            'color': '#3DDC84',
            'description': 'Android uses modified Linux kernel optimized for power efficiency. Higher context switch overhead (1500 cycles) but mobile-optimized.'
        }
    }
    
    @classmethod
    def get_profile(cls, os_type):
        return cls.PROFILES.get(os_type.lower(), cls.PROFILES['windows'])
    
    @classmethod
    def get_all_profiles(cls):
        return cls.PROFILES
    
    @classmethod
    def get_detailed_comparison(cls):
        """Return detailed comparison of all OS profiles"""
        comparison = {}
        for os_name, profile in cls.PROFILES.items():
            comparison[os_name] = {
                'scheduler': profile['scheduler_type'],
                'bandwidth': f"{profile['max_dma_bandwidth']} MB/s",
                'context_switch': f"{profile['context_switch_overhead']} cycles",
                'dma_priority': profile['dma_priority'],
                'cpu_cores': profile['cpu_cores'],
                'clock_speed': f"{profile['clock_speed_ghz']} GHz"
            }
        return comparison
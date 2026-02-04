"""
System Profiles - OS-specific configurations with detailed specs
"""
class SystemProfiles:
    PROFILES = {
        'windows': {
            'name': 'Windows 11 Pro',
            'cpu_cores': 4,
            'clock_speed_ghz': 2.8,
            'cycles_per_byte': 8,
            'context_switch_overhead': 1500,
            'dma_burst_size': 64,
            'max_dma_bandwidth': 133,
            'transfer_delay': 0.08,
            'scheduler_type': 'Multilevel Queue',
            'dma_priority': 'high',
            'color': '#0078D7',
            'description': 'Windows uses a multilevel feedback queue scheduler. High DMA priority but significant context switch overhead (1500 cycles).'
        },
        'linux': {
            'name': 'Ubuntu 22.04 LTS',
            'cpu_cores': 8,
            'clock_speed_ghz': 3.4,
            'cycles_per_byte': 4,
            'context_switch_overhead': 600,
            'dma_burst_size': 128,
            'max_dma_bandwidth': 250,
            'transfer_delay': 0.04,
            'scheduler_type': 'Completely Fair Scheduler (CFS)',
            'dma_priority': 'very_high',
            'color': '#DD4814',
            'description': 'Linux CFS provides aggressive DMA optimization with extremely low context switch overhead (600 cycles).'
        },
        'macos': {
            'name': 'macOS Sonoma',
            'cpu_cores': 10,
            'clock_speed_ghz': 3.2,
            'cycles_per_byte': 5,
            'context_switch_overhead': 900,
            'dma_burst_size': 64,
            'max_dma_bandwidth': 200,
            'transfer_delay': 0.06,
            'scheduler_type': 'Mach Kernel Scheduler',
            'dma_priority': 'high',
            'color': '#6C6C6C',
            'description': 'macOS uses a microkernel architecture with optimized memory throughput and balanced scheduling.'
        },
        'android': {
            'name': 'Android 14',
            'cpu_cores': 8,
            'clock_speed_ghz': 2.4,
            'cycles_per_byte': 12,
            'context_switch_overhead': 2000,
            'dma_burst_size': 32,
            'max_dma_bandwidth': 80,
            'transfer_delay': 0.12,
            'scheduler_type': 'EAS Scheduler',
            'dma_priority': 'medium',
            'color': '#3DDC84',
            'description': 'Android EAS focuses on power efficiency, resulting in higher transfer latency (0.12s) and cycle cost per byte.'
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
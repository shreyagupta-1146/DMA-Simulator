"""
Analytics Module - Performance analysis and comparison
"""
import statistics

class AnalyticsEngine:
    """
    Provides advanced analytics and performance comparisons
    """
    
    @staticmethod
    def compare_modes(cpu_results, dma_results):
        """
        Compare CPU-only vs DMA-assisted performance
        """
        comparison = {
            'time_saved': cpu_results['total_time'] - dma_results['total_time'],
            'time_saved_percent': ((cpu_results['total_time'] - dma_results['total_time']) / cpu_results['total_time']) * 100,
            'cycles_saved': cpu_results['total_cycles'] - dma_results['total_cycles'],
            'cycles_saved_percent': ((cpu_results['total_cycles'] - dma_results['total_cycles']) / cpu_results['total_cycles']) * 100,
            'throughput_improvement': dma_results['throughput_mbps'] - cpu_results['throughput_mbps'],
            'throughput_improvement_percent': ((dma_results['throughput_mbps'] - cpu_results['throughput_mbps']) / cpu_results['throughput_mbps']) * 100,
            'efficiency_gain': dma_results['efficiency'] - cpu_results['efficiency']
        }
        
        return comparison
    
    @staticmethod
    def generate_performance_report(cpu_results, dma_results, file_info, system_profile):
        """
        Generate comprehensive performance report
        """
        comparison = AnalyticsEngine.compare_modes(cpu_results, dma_results)
        
        report = {
            'file_info': file_info,
            'system_profile': system_profile['name'],
            'cpu_mode': {
                'total_time': cpu_results['total_time'],
                'throughput': cpu_results['throughput_mbps'],
                'total_cycles': cpu_results['total_cycles'],
                'efficiency': cpu_results['efficiency'],
                'cpu_utilization': cpu_results['cpu_stats']['active_percentage']
            },
            'dma_mode': {
                'total_time': dma_results['total_time'],
                'throughput': dma_results['throughput_mbps'],
                'total_cycles': dma_results['total_cycles'],
                'efficiency': dma_results['efficiency'],
                'cpu_utilization': dma_results['cpu_stats']['active_percentage'],
                'dma_utilization': dma_results['dma_stats'].get('avg_dma_utilization', 0),
                'cycles_saved': dma_results['dma_stats'].get('total_cycles_saved', 0)
            },
            'comparison': comparison,
            'recommendations': AnalyticsEngine._generate_recommendations(comparison, file_info)
        }
        
        return report
    
    @staticmethod
    def _generate_recommendations(comparison, file_info):
        """
        Generate recommendations based on performance comparison
        """
        recommendations = []
        
        if comparison['time_saved_percent'] > 50:
            recommendations.append({
                'priority': 'HIGH',
                'message': f'DMA provides {comparison["time_saved_percent"]:.1f}% faster transfers. Always use DMA for this file type.'
            })
        
        if comparison['cycles_saved_percent'] > 70:
            recommendations.append({
                'priority': 'HIGH',
                'message': f'DMA saves {comparison["cycles_saved_percent"]:.1f}% CPU cycles. Significant CPU overhead reduction.'
            })
        
        if file_info['size_mb'] > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'message': f'Large file ({file_info["size_mb"]} MB). DMA is highly recommended for files over 10MB.'
            })
        
        if file_info['complexity'] > 1.2:
            recommendations.append({
                'priority': 'MEDIUM',
                'message': f'Complex file type ({file_info["type"]}). DMA handles complex files more efficiently.'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'LOW',
                'message': 'Both modes perform similarly for this file. Use CPU-only for simplicity.'
            })
        
        return recommendations
    
    @staticmethod
    def calculate_efficiency_score(results, mode):
        """
        Calculate overall efficiency score (0-100)
        """
        score = 0
        
        # Throughput contribution (max 30 points)
        throughput = results['throughput_mbps']
        score += min(30, throughput / 10 * 30)
        
        # Time efficiency (max 30 points)
        time_score = 30 - min(30, results['total_time'] / 10 * 30)
        score += max(0, time_score)
        
        # Cycle efficiency (max 20 points)
        cycles = results['total_cycles']
        cycle_score = 20 - min(20, cycles / 1000000 * 20)
        score += max(0, cycle_score)
        
        # Mode bonus (max 20 points)
        if mode == 'dma':
            score += 15  # DMA gets bonus for efficiency
        else:
            score += 5   # CPU-only gets minimal bonus
        
        return round(score, 2)
    
    @staticmethod
    def get_bottleneck_analysis(cpu_stats, dma_stats, mode):
        """
        Analyze performance bottlenecks
        """
        bottlenecks = []
        
        if mode == 'cpu':
            if cpu_stats['active_percentage'] > 90:
                bottlenecks.append({
                    'component': 'CPU',
                    'issue': 'CPU is maxed out at {:.1f}% utilization'.format(cpu_stats['active_percentage']),
                    'impact': 'HIGH',
                    'recommendation': 'Use DMA to offload I/O operations'
                })
            
            if cpu_stats['context_switches'] > 100:
                bottlenecks.append({
                    'component': 'Context Switching',
                    'issue': '{} context switches causing overhead'.format(cpu_stats['context_switches']),
                    'impact': 'MEDIUM',
                    'recommendation': 'Reduce context switches with DMA'
                })
        else:
            if dma_stats.get('avg_dma_utilization', 0) > 90:
                bottlenecks.append({
                    'component': 'DMA Controller',
                    'issue': 'DMA at {:.1f}% utilization, may be bottleneck'.format(dma_stats['avg_dma_utilization']),
                    'impact': 'MEDIUM',
                    'recommendation': 'Consider upgrading DMA controller or optimizing transfer size'
                })
            
            if dma_stats.get('avg_bus_utilization', 0) > 85:
                bottlenecks.append({
                    'component': 'Memory Bus',
                    'issue': 'Bus at {:.1f}% utilization'.format(dma_stats['avg_bus_utilization']),
                    'impact': 'MEDIUM',
                    'recommendation': 'Bus bandwidth may limit performance'
                })
        
        if not bottlenecks:
            bottlenecks.append({
                'component': 'None',
                'issue': 'No significant bottlenecks detected',
                'impact': 'LOW',
                'recommendation': 'System performing optimally'
            })
        
        return bottlenecks
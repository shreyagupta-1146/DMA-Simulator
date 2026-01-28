"""
File Processor - Handles file uploads and processing
"""
import os
import mimetypes
import hashlib

class FileProcessor:
    """
    Simulates file processing with different characteristics based on file type
    """
    
    FILE_TYPE_CONFIGS = {
        'text': {
            'name': 'Text File',
            'extension': '.txt',
            'complexity': 0.8,
            'compression_ratio': 0.6,
            'typical_size_mb': 0.5,
            'processing_overhead': 50
        },
        'image': {
            'name': 'Image File',
            'extension': '.jpg',
            'complexity': 1.2,
            'compression_ratio': 0.8,
            'typical_size_mb': 5,
            'processing_overhead': 150
        },
        'document': {
            'name': 'Document',
            'extension': '.pdf',
            'complexity': 1.3,
            'compression_ratio': 0.7,
            'typical_size_mb': 2,
            'processing_overhead': 120
        },
        'video': {
            'name': 'Video File',
            'extension': '.mp4',
            'complexity': 1.5,
            'compression_ratio': 0.9,
            'typical_size_mb': 50,
            'processing_overhead': 200
        },
        'audio': {
            'name': 'Audio File',
            'extension': '.mp3',
            'complexity': 1.1,
            'compression_ratio': 0.7,
            'typical_size_mb': 4,
            'processing_overhead': 100
        },
        'archive': {
            'name': 'Archive',
            'extension': '.zip',
            'complexity': 1.4,
            'compression_ratio': 0.5,
            'typical_size_mb': 20,
            'processing_overhead': 180
        },
        'binary': {
            'name': 'Binary File',
            'extension': '.bin',
            'complexity': 1.0,
            'compression_ratio': 1.0,
            'typical_size_mb': 10,
            'processing_overhead': 80
        }
    }
    
    def __init__(self, file_path=None, file_size_bytes=0, file_type='text'):
        self.file_path = file_path
        self.file_size = file_size_bytes
        self.file_type = file_type.lower()
        self.config = self.FILE_TYPE_CONFIGS.get(self.file_type, self.FILE_TYPE_CONFIGS['text'])
        self.file_name = os.path.basename(file_path) if file_path else 'Unknown'
        self.file_hash = None
        
    def analyze_file(self):
        """Analyze actual file and extract metadata"""
        if not self.file_path or not os.path.exists(self.file_path):
            return self.get_file_info()
        
        # Get actual file size
        self.file_size = os.path.getsize(self.file_path)
        
        # Detect file type from extension
        ext = os.path.splitext(self.file_path)[1].lower()
        detected_type = self._detect_file_type(ext)
        if detected_type:
            self.file_type = detected_type
            self.config = self.FILE_TYPE_CONFIGS[detected_type]
        
        # Calculate file hash
        self.file_hash = self._calculate_hash()
        
        return self.get_file_info()
    
    def _detect_file_type(self, extension):
        """Detect file type from extension"""
        type_mapping = {
            '.txt': 'text', '.log': 'text', '.csv': 'text',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
            '.pdf': 'document', '.doc': 'document', '.docx': 'document',
            '.mp4': 'video', '.avi': 'video', '.mkv': 'video',
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio',
            '.zip': 'archive', '.rar': 'archive', '.tar': 'archive', '.gz': 'archive',
            '.bin': 'binary', '.exe': 'binary', '.dll': 'binary'
        }
        return type_mapping.get(extension)
    
    def _calculate_hash(self):
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(self.file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def get_file_info(self):
        """Get comprehensive information about the file"""
        return {
            'name': self.file_name,
            'size_bytes': self.file_size,
            'size_mb': round(self.file_size / (1024 * 1024), 2),
            'type': self.config['name'],
            'file_type': self.file_type,
            'extension': self.config['extension'],
            'complexity': self.config['complexity'],
            'compression_ratio': self.config['compression_ratio'],
            'processing_overhead': self.config['processing_overhead'],
            'hash': self.file_hash,
            'typical_size_mb': self.config['typical_size_mb']
        }
    
    def get_processing_overhead(self):
        """
        Calculate additional processing overhead based on file type
        """
        base_overhead = 100
        complexity_overhead = self.config['complexity'] * 50
        file_size_overhead = (self.file_size / (1024 * 1024)) * 10  # 10 cycles per MB
        
        return int(base_overhead + complexity_overhead + file_size_overhead)
    
    def estimate_transfer_time(self, bandwidth_mbps, mode='cpu'):
        """
        Estimate transfer time based on bandwidth and mode
        """
        size_mb = self.file_size / (1024 * 1024)
        
        # Base transfer time
        base_time = size_mb / bandwidth_mbps
        
        # Add complexity overhead
        complexity_factor = self.config['complexity']
        if mode == 'cpu':
            # CPU mode is slower due to processing overhead
            time_with_overhead = base_time * (1 + complexity_factor * 0.5)
        else:
            # DMA mode is much faster
            time_with_overhead = base_time * (1 + complexity_factor * 0.1)
        
        return time_with_overhead
    
    @classmethod
    def get_all_file_types(cls):
        """Get all supported file types"""
        return list(cls.FILE_TYPE_CONFIGS.keys())
    
    @classmethod
    def get_typical_size(cls, file_type):
        """Get typical file size for a file type"""
        config = cls.FILE_TYPE_CONFIGS.get(file_type, cls.FILE_TYPE_CONFIGS['text'])
        return int(config['typical_size_mb'] * 1024 * 1024)
    
    @classmethod
    def get_file_type_info(cls, file_type):
        """Get detailed info for a specific file type"""
        return cls.FILE_TYPE_CONFIGS.get(file_type, cls.FILE_TYPE_CONFIGS['text'])
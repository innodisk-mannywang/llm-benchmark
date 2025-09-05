"""
Resource monitoring utilities for LLM benchmark
"""
import time
import threading
from typing import List, Optional
import psutil

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


class ResourceMonitor:
    """Monitor system resources during benchmark execution"""
    
    def __init__(self):
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.gpu_usage: List[float] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Initialize GPU monitoring if available
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_count = pynvml.nvmlDeviceGetCount()
            except Exception:
                self.gpu_count = 0
        else:
            self.gpu_count = 0
    
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # GPU usage
                gpu_percent = 0.0
                if self.gpu_count > 0 and PYNVML_AVAILABLE:
                    try:
                        # Get average GPU usage across all GPUs
                        total_gpu_util = 0
                        for i in range(self.gpu_count):
                            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                            total_gpu_util += util.gpu
                        gpu_percent = total_gpu_util / self.gpu_count
                    except Exception:
                        gpu_percent = 0.0
                
                with self.lock:
                    self.cpu_usage.append(cpu_percent)
                    self.memory_usage.append(memory_percent)
                    self.gpu_usage.append(gpu_percent)
                
                time.sleep(0.5)  # Monitor every 500ms
                
            except Exception:
                # Continue monitoring even if one sample fails
                time.sleep(0.5)
    
    def get_stats(self) -> dict:
        """Get resource usage statistics"""
        with self.lock:
            if not self.cpu_usage:
                return {
                    "cpu_percent": {"average": 0.0, "max": 0.0, "per_channel": []},
                    "memory_percent": {"average": 0.0, "max": 0.0, "per_channel": []},
                    "gpu_percent": {"average": 0.0, "max": 0.0, "per_channel": []},
                }
            
            cpu_avg = sum(self.cpu_usage) / len(self.cpu_usage)
            cpu_max = max(self.cpu_usage)
            
            memory_avg = sum(self.memory_usage) / len(self.memory_usage)
            memory_max = max(self.memory_usage)
            
            gpu_avg = sum(self.gpu_usage) / len(self.gpu_usage)
            gpu_max = max(self.gpu_usage)
            
            return {
                "cpu_percent": {
                    "average": cpu_avg,
                    "max": cpu_max,
                    "per_channel": [cpu_avg]  # Single value for all channels
                },
                "memory_percent": {
                    "average": memory_avg,
                    "max": memory_max,
                    "per_channel": [memory_avg]
                },
                "gpu_percent": {
                    "average": gpu_avg,
                    "max": gpu_max,
                    "per_channel": [gpu_avg]
                },
            }
    
    def __enter__(self):
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring()
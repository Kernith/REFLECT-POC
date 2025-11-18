import time
from typing import List, Tuple, Any, Dict


class ObservationCollector:
    """Pure data collection service for observations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.responses = []
        self.start_time = None
    
    def start_observation(self) -> float:
        """Start the observation and return start time"""
        self.start_time = time.time()
        self.responses = []
        return self.start_time
    
    def record_response(self, category: str, response: str, value: Any = None) -> None:
        """Record a response with optional value"""
        if not self.start_time:
            return
        
        current_time = time.time() - self.start_time

        self.responses.append((current_time, category, response, value))
        print(f"Recorded {category}: {response} (value: {value}) at {current_time:.3f}s")
    
    def get_responses(self) -> List[Tuple]:
        """Get all recorded responses"""
        return self.responses.copy()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since observation started"""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0
    
    def get_start_time(self) -> float:
        """Get the start time of the observation"""
        return self.start_time
    
    def clear_responses(self) -> None:
        """Clear all recorded responses"""
        self.responses = []
    
    def is_observation_active(self) -> bool:
        """Check if observation is currently active"""
        return self.start_time is not None
    
    def stop_observation(self) -> List[Tuple]:
        """Stop observation and return all responses"""
        responses = self.get_responses()
        self.start_time = None
        return responses

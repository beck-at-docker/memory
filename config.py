"""
Configuration management for Claude Memory System
"""
import os
import secrets
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration class for Claude Memory System"""
    # Base directory - where the code lives
    BASE_DIR = Path(__file__).parent.resolve()
    
    # PID file directory
    PID_DIR = BASE_DIR / 'pids'

    
    # Database settings
    DATABASE_PATH = os.getenv('MEMORY_DB_PATH', 'memory.db')
    TEST_DATABASE_PATH = os.getenv('TEST_DB_PATH', 'test.db')
    
    # API settings
    API_HOST = os.getenv('MEMORY_API_HOST', '127.0.0.1')
    API_PORT = int(os.getenv('MEMORY_API_PORT', '8001'))
    API_URL = f"http://{API_HOST}:{API_PORT}"
    
    # Security settings
    TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', 'HS256')
    SECRET_KEY = os.getenv('SECRET_KEY', 'memory_system_secret_key_for_local_development_only')
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Timeouts
    CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '5'))
    READ_TIMEOUT = int(os.getenv('READ_TIMEOUT', '10'))
    
    # Paths
    ALLOWED_PROJECT_DIRS = os.getenv('ALLOWED_PROJECT_DIRS', '/Users/beck/Documents').split(',')
    
    # Crisis detection patterns
    CRISIS_PATTERNS = [
        r'\b(?:kill|harm|hurt|suicide|die|death|end.*life)\s+(?:myself|me)\b',
        r'\bsuicidal\s+(?:thoughts|ideation)\b',
        r'\bwant\s+to\s+(?:die|kill\s+myself)\b',
        r'\bno\s+(?:point|reason)\s+(?:in\s+)?living\b',
        r'\bcan\'?t\s+(?:take|handle)\s+(?:it|this)\s+anymore\b',
        r'\beveryone\s+(?:would\s+be\s+)?better\s+(?:off\s+)?without\s+me\b',
    ]
    
    # Insight trigger patterns
    INSIGHT_PATTERNS = [
        r'\b(?:insight|pattern|trend|learning|realization|understanding)\b',
        r'\b(?:remember|recall|note|important|key\s+point)\b',
        r'\b(?:therapy|counseling|mental\s+health|wellbeing)\b',
        r'\b(?:goal|objective|plan|strategy)\b',
        r'\b(?:challenge|difficulty|struggle|problem)\b',
        r'\b(?:success|achievement|progress|improvement)\b',
    ]
    
    @classmethod
    def get_database_path(cls, test: bool = False) -> str:
        """Get database path for regular or test database"""
        return cls.TEST_DATABASE_PATH if test else cls.DATABASE_PATH
    
    @classmethod
    def generate_secure_token(cls, data: str) -> str:
        """Generate a secure token using secrets module"""
        import hashlib
        import hmac
        
        # Use HMAC with secret key for secure token generation
        return hmac.new(
            cls.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @classmethod
    def is_path_allowed(cls, path: str) -> bool:
        """Check if path is in allowed project directories"""
        path_obj = Path(path).resolve()
        for allowed_dir in cls.ALLOWED_PROJECT_DIRS:
            try:
                path_obj.relative_to(Path(allowed_dir).resolve())
                return True
            except ValueError:
                continue
        return False
    
    @classmethod
    def get_pid_file(cls, service_name: str) -> Path:
        """Get PID file path for a service"""
        cls.PID_DIR.mkdir(exist_ok=True)
        return cls.PID_DIR / f"{service_name}.pid"
    
    @classmethod
    def write_pid_file(cls, service_name: str, pid: int):
        """Write PID to file"""
        pid_file = cls.get_pid_file(service_name)
        pid_file.write_text(str(pid))
    
    @classmethod
    def read_pid_file(cls, service_name: str) -> Optional[int]:
        """Read PID from file"""
        pid_file = cls.get_pid_file(service_name)
        if not pid_file.exists():
            return None
        try:
            return int(pid_file.read_text().strip())
        except (ValueError, OSError):
            return None
    
    @classmethod
    def remove_pid_file(cls, service_name: str):
        """Remove PID file"""
        pid_file = cls.get_pid_file(service_name)
        if pid_file.exists():
            pid_file.unlink()

    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary for debugging"""
        return {
            'api_host': cls.API_HOST,
            'api_port': cls.API_PORT,
            'database_path': cls.DATABASE_PATH,
            'rate_limit': cls.RATE_LIMIT_PER_MINUTE,
            'allowed_dirs': cls.ALLOWED_PROJECT_DIRS,
        }
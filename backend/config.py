"""
Configuration for Demo Therapist Backend
Loads environment variables and provides centralized config
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    TWELVE_LABS_API_KEY: Optional[str] = os.getenv("TWELVE_LABS_API_KEY")
    DEEPGRAM_API_KEY: Optional[str] = os.getenv("DEEPGRAM_API_KEY")
    
    # Gemini Model Selection
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")  # 2.5 flash (fast!)
    
    # Server config
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Storage paths
    VIDEO_UPLOAD_DIR: str = os.getenv("VIDEO_UPLOAD_DIR", "./uploads")
    RESULTS_CACHE_DIR: str = os.getenv("RESULTS_CACHE_DIR", "./cache")
    
    # Analysis parameters (tuned for hackathon)
    WINDOW_SIZE_SECONDS: int = 10  # Fixed window size
    RISK_THRESHOLD: float = 4.0  # Flag issues above this risk score
    
    # Signal weights (for risk scoring)
    SIGNAL_WEIGHTS = {
        "concept_spike": 1.0,
        "grounding_gap": 1.3,
        "tmb": 1.2,
        "visual_mismatch": 1.5,
        "structure_order": 1.4,
        "ramble_ratio": 0.8
    }
    
    # Clarity score tiers
    CLARITY_TIERS = [
        (90, "Judge Whisperer"),
        (70, "Solid Senior Engineer"),
        (50, "Wait...what are we building?"),
        (0, "3AM Red Bull PowerPoint")
    ]
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration and return (is_valid, missing_keys)
        """
        missing = []
        
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        
        # TwelveLabs is required for Person A but not for testing Person B's tools
        if not cls.TWELVE_LABS_API_KEY:
            missing.append("TWELVE_LABS_API_KEY (required for full pipeline)")
        
        is_valid = len(missing) == 0
        return is_valid, missing
    
    @classmethod
    def get_clarity_tier(cls, score: int) -> str:
        """Get tier label for a clarity score"""
        for threshold, label in cls.CLARITY_TIERS:
            if score >= threshold:
                return label
        return cls.CLARITY_TIERS[-1][1]
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.VIDEO_UPLOAD_DIR, exist_ok=True)
        os.makedirs(cls.RESULTS_CACHE_DIR, exist_ok=True)


# For convenience
def get_config() -> Config:
    """Get configuration instance"""
    return Config


# Validate on import during development
if __name__ == "__main__":
    print("🔧 Checking configuration...\n")
    
    config = Config()
    is_valid, missing = config.validate()
    
    if is_valid:
        print("✅ Configuration is valid!")
        print(f"   Gemini Model: {config.GEMINI_MODEL}")
        print(f"   Port: {config.PORT}")
    else:
        print("⚠️  Missing required configuration:")
        for key in missing:
            print(f"   - {key}")
        print("\n💡 Create a .env file or set environment variables:")
        print("   export GEMINI_API_KEY='your-key'")
        print("   export TWELVE_LABS_API_KEY='your-key'")

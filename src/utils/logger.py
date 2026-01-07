
import logging
import sys
from pathlib import Path
from src.utils.paths import get_base_path

def setup_logger():
    """Configures the application logger."""
    log_file = get_base_path() / "thesisflow.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("ThesisFlow")
    logger.info("Logger initialized.")
    return logger

def get_logger():
    return logging.getLogger("ThesisFlow")

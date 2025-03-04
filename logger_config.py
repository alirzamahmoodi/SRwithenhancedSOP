import logging
from logging.handlers import RotatingFileHandler
import yaml

def setup_logging(config_path='config.yaml', log_file='app.log'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    log_levels = config.get('LOGGING_LEVELS', {})
    basic_level = getattr(logging, log_levels.get('basic', 'INFO').upper(), logging.INFO)
    detailed_level = getattr(logging, log_levels.get('detailed', 'DEBUG').upper(), logging.DEBUG)
    error_level = getattr(logging, log_levels.get('error', 'ERROR').upper(), logging.ERROR)
    
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(log_formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    
    logging.basicConfig(
        level=basic_level,
        handlers=[file_handler, stream_handler]
    )
    
    logging.getLogger('detailed').setLevel(detailed_level)
    logging.getLogger('error').setLevel(error_level)
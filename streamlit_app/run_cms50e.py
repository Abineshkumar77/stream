import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

def run_cms50e_script(port: str, file: str):
    script_path = os.path.join(os.path.dirname(__file__), 'cms50e.py')
    logger.debug(f"Running CMS50E capture script: {script_path} with port: {port} and file: {file}")
    
    try:
        process = subprocess.Popen(
            ['python', script_path, port, file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Script failed with error code {process.returncode}")
            logger.error(f"Standard Error: {stderr.decode()}")
        else:
            logger.debug(f"Script output: {stdout.decode()}")
        
        return process
    except Exception as e:
        logger.error(f"Exception occurred while running CMS50E script: {e}")
        return None

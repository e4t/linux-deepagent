import logging
import subprocess

from langchain_core.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
@tool
def get_process_using_port() -> str:
    """Use lsof to find the process using <port>.
    Args:
      port: the port number to check.
    Returns:
      str: the output of the `lsof -i :<port>` command.
    """
    cmd = ["lsof", "-i", f":{port}"]
    if os.geteuid() != 0:
        cmd.insert(0, "sudo")
    logger.info(f"Running command: {cmd}")
    process = subprocess.run(cmd, stdout=subprocess.PIPE)
    return process.stdout.decode("utf-8")
    

import logging
import subprocess

from langchain_core.tools import tool

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
@tool
def free_memory() -> str:
    """Get free and used memory in the system.
    Returns: the output of `free -h`.
    """
    cmd = "free -h"
    logger.info(f"Running command: {cmd}")
    return subprocess.getoutput(cmd)


import logging
import subprocess
import os

from langchain_core.tools import tool

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_apache_config() -> str:
    """Use this tool to check the apache config.
    Args:
      none.
    Returns:
      str: the output of `apachectl configtest`.
    """
    cmd = ["sh", "/usr/sbin/start_apache2", "-t"]
    if os.geteuid() != 0:
        cmd.insert(0, "sudo")
    logger.info(f"Running command: {cmd}")
    process = subprocess.run(cmd, stderr=subprocess.PIPE)
    line=""
    return (process.stderr.decode("utf-8"))

if __name__ == "__main__":
    print(check_apache_config())

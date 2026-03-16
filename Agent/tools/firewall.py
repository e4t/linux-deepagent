import logging
import subprocess

from langchain_core.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
@tool
def firewall_cmd_list_ports() -> str:
    """Use firewall-cmd to list open ports.
    Returns:
        str: the output of the `firewall-cmd --list-ports` command.
    """
    cmd = ["firewall-cmd", "--list-ports"]
    if os.geteuid() != 0:
        cmd.insert(0, "sudo")
    logger.info(f"Running command: {cmd}")
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return process.stdout.decode("utf-8")
    except FileNotFoundError:
        return "firewall-cmd not found. It may not be installed."

@tool
def firewall_cmd_list_services() -> str:
    """Use firewall-cmd to list open services.
    Returns:
        str: the output of the `firewall-cmd --list-services` command.
    """
    cmd = ["firewall-cmd", "--list-services"]
    if os.geteuid() != 0:
        cmd.insert(0, "sudo")
    logger.info(f"Running command: {cmd}")
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE)
        return process.stdout.decode("utf-8")
    except FileNotFoundError:
        return "firewall-cmd not found. It may not be installed."

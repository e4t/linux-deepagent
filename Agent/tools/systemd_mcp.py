import logging
import subprocess
import os
import asyncio

from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def systemd_mcp_tools(): 

    client = MultiServerMCPClient(
        {
            "systemd": {
                "transport": "stdio",
                "command": "systemd-mcp",
                "args": [ "-r", "--noauth", "ThisIsInsecure", "--verbose", "--logfile", "/tmp/systemd-mcp-log" ],
            }
        }
    )

    return await client.get_tools()


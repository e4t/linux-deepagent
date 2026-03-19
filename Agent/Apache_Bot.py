import os
import platform
import logging
from rich.console import Console
from rich.markdown import Markdown

from typing import TypedDict, List, Literal, Union
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from tools import firewall, memory, network, process, systemd, check_apache_config
from dotenv import load_dotenv # used to store secret stuff like API keys or configuration values
from utils import Input

load_dotenv()
PROVIDER=os.getenv("PROVIDER")
if not PROVIDER:
    print("No provider!")
    exit(1)
elif PROVIDER == 'ollama':
    MODEL=os.getenv("OLLAMA_MODEL")     
    if not MODEL:
        print("No Model!")
        exit(1)
    model = ChatOllama(
        model=f"{MODEL}",
        thinking={"type": "enabled", "budget_tokens": 10000},
    )
elif PROVIDER == 'google_genai':
    API_KEY=os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("No API Key!")
        exit(1)
    MODEL=os.getenv("GOOGLE_GENAI_MODEL")
    if not MODEL:
        print("No Model!")
        exit(1)
    model = ChatGoogleGenerativeAI(
        model=f"{MODEL}",
    )
else:
    print("Unknown provider!")
    exit(1)

logging.basicConfig(level=logging.WARNING)

general_health_subagent = {
    "name": "general_health",
    "description": "Performs a general health check on the system",
    "system_prompt": '''Use all the tools to do a general health check of the system.
    Be concise and only report details for things that may be problematic.
    Use the free_memory tool to check that the system has adequate free memory.
    Take note of any processes using a lot of cpu. Ignore the `top` process and don't mention it in your report.
    Report processes that are using a significant percent of memory.
    When commenting on processes, always include their pid and any pertinent information.''',
    "tools": [memory.free_memory, process.top_processes_by_cpu, process.top_processes_by_memory, systemd.failed_systemd_units],
    "model": model,
}

LINUX_DISTRO = platform.freedesktop_os_release().get("ID", "unknown")
apache_subagent = {
    "name": "apache_agent",
    "description": "Troubleshoot apache problems.",
    "system_prompt": f"""Use the get_systemctl_status tool passing the
    systemd unit name that is used for apache on {LINUX_DISTRO}.
    Use the firewall-cmd tools for connectivity issues. If the firewall
    is running check that the required ports or services are open.
    Use check_apache_config to run a config file checker for Apache.
    """,
    "tools": [systemd.get_systemctl_status, network.get_process_using_port,
              firewall.firewall_cmd_list_ports, firewall.firewall_cmd_list_services,
              check_apache_config.check_apache_config],
    "model": model,
}

network_subagent = {
    "name": "network_agent",
    "description": "Troubleshoot network problems.",
    "system_prompt": """Use get_process_using_port to determine which process
    uses a specific network tcp port""",
    "tools": [ network.get_process_using_port ],
    "model": model,
}

firewall_subagent = {
    "name": "firewall_agent",
    "description": "Troubleshoot firewall issues.",
    "system_prompt": """Use the firewall-cmd tools for connectivity issues.
    If the firewall is running check that the required ports or services are open""",
    "tools": [firewall.firewall_cmd_list_ports, firewall.firewall_cmd_list_services],
    "model": model,
}

memory_subagent = {
    "name": "memory-analysis-agent",
    "description": "Troubleshoot memory consumption issues.",
    "system_prompt": """Use the free-memory tools to check for memory consumption""",
    "tools": [memory.free_memory],
    "model": model,
}

process_subagent = {
    "name": "process-analysis-agent",
    "description": "Used to determine the processes which consume the most CPU or memory",
    "system_prompt": "You are a professional process analysis tool",
    "tools": [process.top_processes_by_cpu, process.top_processes_by_memory],
    "model": model,
}

systemd_subagent = {
    "name": "systemd-analysis-agent",
    "description": "Used to determine which system services have failed",
    "system_prompt": "You are a professional system service analysis tool",
    "tools": [systemd.get_systemctl_status, systemd.failed_systemd_units],
    "model": model,
}

subagents = [general_health_subagent, apache_subagent, memory_subagent, process_subagent, systemd_subagent, firewall_subagent]
agent = create_deep_agent(model=model,
                          system_prompt="""Help the user troubleshoot their linux problems.""",
                          subagents=subagents)

console = Console()
user_input = Input.UserPrompt("Enter: ")
while user_input not in [ "/exit", "/quit", "" ]:
    try:
        result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
        content = result["messages"][-1].content
        if isinstance(content, list):
#            print(f"AI: {result["messages"][-1].text}")
            console.print(Markdown(f"AI: {result["messages"][-1].text}"))
        else:
#            print(f"AI: {content}")
            console.print(Markdown(f"AI: {content}"))
        user_input = Input.UserPrompt("Enter: ")
    except KeyboardInterrupt:
        exit(0)

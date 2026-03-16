import os
from typing import TypedDict, List, Literal, Union
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from tools import firewall, memory, network, process, systemd
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

network_subagent = {
    "name": "network-analysis-agent",
    "description": "Used to determine which application uses a port",
    "system_prompt": "You are a professional network analyzer for Linux",
    "tools": [network.get_process_using_port],
    "model": model,
}

firewall_subagent = {
    "name": "firewall-analysis-agent",
    "description": "Used to check for ports and services open in the firewall",
    "system_prompt": "You are a professional firewall analyzer and troubleshooter for Linux",
    "tools": [firewall.firewall_cmd_list_ports, firewall.firewall_cmd_list_services],
    "model": model,
}

memory_subagent = {
    "name": "memory-analysis-agent",
    "description": "Used to check memory consumption on a Linux system",
    "system_prompt": "You are a professional memory analyzer for Linux",
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

subagents = [network_subagent, firewall_subagent, memory_subagent, process_subagent, systemd_subagent]
agent = create_deep_agent(model=model, subagents=subagents)


user_input = Input.UserPrompt("Enter: ")
while user_input != "/exit":
    try:
        result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
        content = result["messages"][-1].content
        if isinstance(content, list):
            print(f"AI: {result["messages"][-1].text}")
        else:
            print(f"AI: {content}")
        user_input = Input.UserPrompt("Enter: ")
    except KeyboardInterrupt:
        exit(0)

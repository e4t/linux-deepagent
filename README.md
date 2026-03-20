# Linux System Agent using LangChain's DeepAgents

## To run the Agent:

1. To initialize dependencies, run:
```
uv venv
uv sync
```

2. To select your provider/model and add your API key if necessary edit `.env`.
To collect information about the sub-agents called, set:
```
VERBOSE=1
```
To include the deepagent-generated promots, set:
```
VERBOSE=2
```

3. Run the agent:
```
cd Agent
uv run Agent_Bot.py
```


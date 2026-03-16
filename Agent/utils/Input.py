import readline
from typing import Optional

def UserPrompt(prompt: Optional[str]):
    try:
        return input(prompt)
    except EOFError:
        exit(0)
    except KeyboardInterrupt:
        print()
        exit(0)
        

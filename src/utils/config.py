import os
import sys
import json

GLOBAL_CONFIGS = None

def load_configs() -> dict:
    path = "/configs/deploy.json" if sys.argv[1] == "deploy" else "configs/debug.json"
    with open(os.path.abspath(path)) as f:
        return json.load(f)
    
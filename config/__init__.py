import json
import os


def load_constants():
    constants_path = os.path.join(os.path.dirname(__file__), "constants.json")
    with open(constants_path) as f:
        return json.load(f)

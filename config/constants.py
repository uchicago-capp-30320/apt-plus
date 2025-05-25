"""

WARNING: When modifying this file you must also update static/constants.json

"""

import json
import sys
from pathlib import Path

# Load JSON file
_path = Path(__file__).resolve().parents[1] / "static" / "constants.json"
with open(_path) as f:
    _constants = json.load(f)

# Inject each constant into the module's namespace
_current_module = sys.modules[__name__]
for k, v in _constants.items():
    setattr(_current_module, k, v)

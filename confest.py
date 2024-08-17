import sys
import os
from pathlib import Path

prj_path = str(Path(__file__).resolve().parent)
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), prj_path)))

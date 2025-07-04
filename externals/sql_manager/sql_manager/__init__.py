import json
from pathlib import Path

from sql_manager.core.model import DynamicModel
from sql_manager.core.manager import Manager


BASE_DIR = Path(__file__).resolve().parent

version_info = json.loads(BASE_DIR.joinpath('version', 'version.json').read_text())
__version__ = version_info['version']

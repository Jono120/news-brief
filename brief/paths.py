from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "brief.db"
OUTPUT_DIR = ROOT / "output"
CONFIG_DIR = ROOT / "config"

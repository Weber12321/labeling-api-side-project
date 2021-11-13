from pathlib import Path, PurePath

ROOT_DIR = PurePath(__file__).parent
LOGS_DIR = Path(ROOT_DIR / "logs")
Path(LOGS_DIR).mkdir(exist_ok=True)

SCRAP_FOLDER = Path(ROOT_DIR / "scrap_file")
Path(SCRAP_FOLDER).mkdir(exist_ok=True)

SAVE_FOLDER = Path(ROOT_DIR / "save_file")
Path(SAVE_FOLDER).mkdir(exist_ok=True)

RULE_FOLDER = Path(ROOT_DIR / "rules")
Path(RULE_FOLDER).mkdir(exist_ok=True)

DEEPNLP_POS_API = "http://127.0.0.1/segment"
DEEPNLP_POS_API_TOKEN = ""

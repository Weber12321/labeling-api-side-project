from pathlib import Path
from typing import Dict
import pandas as pd

def read_csv_to_dict(file_path: Path) -> Dict:
    df = pd.read_csv(file_path, encoding='utf-8')

    _dict = {}
    for _, row in df.iterrows():
        temp_dict = {
            row.source_id : row.table
        }
        _dict.update(temp_dict)

    return _dict



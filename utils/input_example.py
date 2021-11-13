from dataclasses import dataclass, astuple, field
from datetime import datetime
from typing import Optional

@dataclass
class InputExample:
    id_: str
    s_area_id: str
    author: str
    title: str
    content: str
    post_time: Optional[datetime]
    label: Optional[str] = field(default=None)

    def __iter__(self):
        return iter(astuple(self))

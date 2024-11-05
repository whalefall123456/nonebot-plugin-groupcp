from pydantic import BaseModel
from pathlib import Path
from typing import ClassVar


class Config(BaseModel):
    """Plugin Config Here"""
    data_path: ClassVar[Path] = Path() / "data" / "groupcp"
    group_data_path: Path = data_path / "group_data.json"


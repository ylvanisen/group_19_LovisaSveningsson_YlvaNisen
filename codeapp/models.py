from __future__ import annotations

# python built-in imports
from dataclasses import dataclass
from datetime import date


@dataclass
class Movies:
    id: int
    title: str
    genres: list[str]
    runtime: int
    release_date: date
    budget: int
    score: float

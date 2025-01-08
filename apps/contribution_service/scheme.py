from pydantic import BaseModel
from datetime import date
from utils.scheme import SUser
from typing import Optional


class RepositoryScheme(BaseModel):
    id: int
    repository_title: str
    user: Optional[SUser] = None


class ContributionsScheme(BaseModel):
    id: int
    date: date
    repository_id: int
    commit_count: int
    repository: Optional[RepositoryScheme] = None

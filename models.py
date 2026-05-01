from typing import List, Optional
from pydantic import BaseModel

class NoteHealth(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    last_edited_at: Optional[int] = None   # unix timestamp
    last_viewed_at: Optional[int] = None   # unix timestamp  
    is_empty: bool = False
    is_public: bool = False
    is_verified: bool = False
    is_inactive: bool = False
    word_count: Optional[int] = None
    owner_id: Optional[str] = None
    health_score: int = 100         # computed 0-100
    issues: List[str] = []          # list of issue strings

class WorkspaceHealthReport(BaseModel):
    total_docs: int
    healthy_docs: int
    warning_docs: int
    critical_docs: int
    overall_score: int
    stale_count: int
    empty_count: int
    public_count: int
    unverified_count: int
    no_owner_count: int
    notes: List[NoteHealth]

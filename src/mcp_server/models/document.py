from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List

class Section(BaseModel):
    """Represents a section in an AsciiDoc document."""
    title: str
    level: int
    content: List[str] = Field(default_factory=list)
    subsections: List[Section] = Field(default_factory=list)

class Document(BaseModel):
    """Represents a single AsciiDoc document file."""
    filepath: str
    sections: List[Section] = Field(default_factory=list)

from typing import List

from pydantic import BaseModel, Field


class BulletSubsection(BaseModel):
    title: str = Field(default_factory=str)
    bullets: List[str] = Field(default_factory=list)


class Section(BaseModel):
    title: str = Field(default_factory=str)
    subsections: List[BulletSubsection] = Field(default_factory=list)


class OutlineResponse(BaseModel):
    sections: List[Section] = Field(default_factory=list)




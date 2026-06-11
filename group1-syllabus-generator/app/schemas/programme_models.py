from pydantic import BaseModel, Field
from typing import List, Optional

class PEORequest(BaseModel):
    programme_name: str = Field(..., min_length=3, max_length=100)
    programme_description: str = Field(..., min_length=10, max_length=1000)
    n_peos: int = Field(default=5, ge=3, le=8)

class PEOObject(BaseModel):
    peo_id: str
    text: str
    focus_area: str

class PEOResponse(BaseModel):
    programme_name: str
    peos: List[PEOObject]

class PORequest(BaseModel):
    programme_name: str = Field(..., min_length=3, max_length=100)
    programme_description: str = Field(..., min_length=10, max_length=1000)

class POObject(BaseModel):
    po_id: str
    title: str
    text: str

class POResponse(BaseModel):
    programme_name: str
    pos: List[POObject]

class PSORequest(BaseModel):
    programme_name: str = Field(..., min_length=3, max_length=100)
    course_list: Optional[List[str]] = []
    n_psos: int = Field(default=3, ge=2, le=5)

class PSOObject(BaseModel):
    pso_id: str
    text: str
    domain: str

class PSOResponse(BaseModel):
    programme_name: str
    psos: List[PSOObject]

class ProgrammeRequest(BaseModel):
    programme_name: str = Field(..., min_length=3, max_length=100)
    programme_description: str = Field(..., min_length=10, max_length=1000)
    course_list: Optional[List[str]] = []
    n_peos: int = Field(default=5, ge=3, le=8)
    n_psos: int = Field(default=3, ge=2, le=5)

class ProgrammeResponse(BaseModel):
    programme_name: str
    peos: List[PEOObject]
    pos: List[POObject]
    psos: List[PSOObject]
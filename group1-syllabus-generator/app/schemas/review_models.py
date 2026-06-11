from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ReviewAction(str, Enum):
    accept = "accept"
    reject = "reject"
    edit   = "edit"

class OutcomeReview(BaseModel):
    outcome_id: str
    course_name: str
    original_text: str
    edited_text: Optional[str] = None
    bloom_level: str
    action: ReviewAction
    reviewer_comment: Optional[str] = None

class ReviewRequest(BaseModel):
    reviews: List[OutcomeReview]

class ReviewSummary(BaseModel):
    total_reviewed: int
    accepted: int
    rejected: int
    edited: int
    saved_to: str
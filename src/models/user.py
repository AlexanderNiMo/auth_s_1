from pydantic import BaseModel, validate_email, validator
from typing import Optional


class User(BaseModel):

    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]

    @validator('email')
    def validate_email(cls, v):
        validate_email(v)
        return v

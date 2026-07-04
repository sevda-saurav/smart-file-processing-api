from pydantic import BaseModel, EmailStr, field_validator, Field


class EmployeeRow(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    age: int = Field(ge=18, le=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank or whitespace")
        return v.strip()
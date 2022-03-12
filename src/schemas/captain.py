from pydantic import BaseModel

# Shared properties
# class UserBase(BaseModel):
#     phone: Optional[str] = None


# Properties to receive via API on creation
class Captain(BaseModel):
    phone: str


# class UserInDBBase(UserBase):
#     id: Optional[int] = None

#     class Config:
#         orm_mode = True


# Additional properties to return via API
# class User(UserInDBBase):
#     pass


# Additional properties stored in DB
class CaptainInDB(Captain):
    id: int
    phone: str
    raiting: float

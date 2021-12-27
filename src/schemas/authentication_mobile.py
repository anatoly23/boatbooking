from pydantic import BaseModel


class AuthenticationMobile(BaseModel):
    phone: str
    code: str

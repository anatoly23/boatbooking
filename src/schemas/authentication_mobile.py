from src.schemas.captain import Captain


class AuthenticationMobile(Captain):
    phone: str
    code: str

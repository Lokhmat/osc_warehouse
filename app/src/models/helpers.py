from fastapi import HTTPException, status
from pydantic import BaseModel

UNATHORIZED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Either username and password or token are incorrect',
    headers={'WWW-Authenticate': 'Bearer'},
)

NO_PERMISSIONS_ERROR = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='You do not have enough permissions for this request',
    headers={'WWW-Authenticate': 'Bearer'},
)

NOT_FOUND_ERROR = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Not found',
    headers={'WWW-Authenticate': 'Bearer'},
)

class EmptyResponse(BaseModel):
    pass

class ErrorResponse(BaseModel):
    detail: str

BAD_REQUEST_RESPONSE = {400: {'model': ErrorResponse}}

def get_bad_request(detail: str):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
        headers={'WWW-Authenticate': 'Bearer'},
    )
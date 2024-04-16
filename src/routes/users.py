from fastapi import APIRouter, HTTPException, status, Path, Query, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.database.schemas import UserSchema, UserResponseSchema, TokenSchema, UserDBSchema
from src.repository import users as rep_users
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    user = await rep_users.get_user_by_email(email=body.email, db=db)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists.')
    print(1)
    record = UserDBSchema(
        username=body.username,
        email=body.email,
        pwd_hash=auth_service.get_pasword_hash(body.password)
    )
    print(2)
    user = await rep_users.create_user(record, db=db)
    print(3)
    return user


@router.post("/login", response_model=TokenSchema)
async def login_user(body: OAuth2PasswordRequestForm =Depends(), db: AsyncSession = Depends(get_db)):
    user = await rep_users.get_user_by_email(email=body.username, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid e-mail.')
    if not auth_service.verify_password(body.password, user.pwd_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid password.')
    
    response = TokenSchema(
        access_token=await auth_service.create_access_token(data={'sub': user.email}),
        refresh_token=await auth_service.create_refresh_token(data={'sub': user.email})
        )

    refreshed_user = await rep_users.update_user_token(user=user, token=response.refresh_token, db=db)
    if refreshed_user.refresh_token != response.refresh_token:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Database error.')
    
    return response


@router.get("/refresh", response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token=token)
    user = await rep_users.get_user_by_email(email=email, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    elif user.refresh_token != token:
        await rep_users.update_user_token(user=user, token=None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    else:
        response = TokenSchema(
            access_token = await auth_service.create_access_token(data={'sub': email}),
            refresh_token = await auth_service.create_refresh_token(data={'sub': email})
        )

        refreshed_user = await rep_users.update_user_token(user=user, token=response.refresh_token, db=db)
        if refreshed_user.refresh_token != response.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Database error.')

    return response

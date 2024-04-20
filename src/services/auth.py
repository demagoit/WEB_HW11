from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt
from src.database.db import get_db
from src.repository import users as rep_users
from src.conf.config import config

class Auth():

    pwd_context = CryptContext(schemes=['bcrypt'])
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    SECRET_KEY = config.SECRET_JWT
    ALGORITHM = config.ALGORITHM_JWT

    def verify_password(self, plaine_pwd: str, hashed_pwd: str) -> bool:
        return self.pwd_context.verify(plaine_pwd, hashed_pwd)

    def get_pasword_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[int] = 15) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expires_delta)
        to_encode.update(
            {'iat': now.timestamp(), 'exp': expire.timestamp(), 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, key=self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[int] = 7*24*60) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expires_delta)
        to_encode.update(
            {'iat': now.timestamp(), 'exp': expire.timestamp(), 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(
            to_encode, key=self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token=token, key=self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope of token')
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token=Depends(oauth2_scheme), db: AsyncSession=Depends(get_db)):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token=token, key=self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credential_exception
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope of token')
        except JWTError:
            raise credential_exception
        
        user = await rep_users.get_user_by_email(email=email, db=db)
        if user is None:
            raise credential_exception
        return user

auth_service = Auth()
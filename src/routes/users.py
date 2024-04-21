import cloudinary.uploader
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary

from src.database.db import get_db
from src.database.schemas import UserSchema, UserResponseSchema, TokenSchema, UserDBSchema, EmailSchema
from src.database.models import User
from src.repository import users as rep_users
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf.config import route_rst, config

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()

@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED, 
             dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def create_user(body: UserSchema, background_task: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    user = await rep_users.get_user_by_email(email=body.email, db=db)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists.')
    record = UserDBSchema(
        username=body.username,
        email=body.email,
        pwd_hash=auth_service.get_pasword_hash(body.password)
    )
    user = await rep_users.create_user(record, db=db)
    background_task.add_task(send_email, email=body.email, username=body.username, host=str(request.base_url))
    return user


@router.post("/login", response_model=TokenSchema, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def login_user(body: OAuth2PasswordRequestForm =Depends(), db: AsyncSession = Depends(get_db)):
    user = await rep_users.get_user_by_email(email=body.username, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid e-mail.')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='E-mail not confirmed.')
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


@router.get("/refresh", response_model=TokenSchema, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_token(token=token, scope='refresh_token')
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


@router.post("/resend_email", dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def send_in_background(body: EmailSchema, background_task: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    user = await rep_users.get_user_by_email(email=body.email, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Invalid e-mail')
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='E-mail already confirmed')
    background_task.add_task(send_email, email=user.email,
                        username=user.username, host=str(request.base_url))
    return {'message': 'email has been sent'}


@router.get("/confirm_email/{token}", dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.decode_token(token=token, scope='email_token')
    user = await rep_users.get_user_by_email(email=email, db=db)
        
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'E-mail already confirmed'}
    await rep_users.user_email_confirmation(user=user, db=db)

    return {'message': 'E-mail confirmed'}


@router.patch("/upload_avatar/", response_model=UserResponseSchema, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def upload_avatar(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'user:{current_user.email}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'user:{current_user.email}').build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await rep_users.update_user_avatar(user=current_user, url=src_url, db=db)
    return user

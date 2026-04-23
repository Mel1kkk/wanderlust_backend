# from fastapi import (
#     APIRouter,
#     status,
#     Body,
#     Depends
# )
# from fastapi.responses import JSONResponse
# from sqlalchemy.ext.asyncio import AsyncSession

# from utils.db import connect_db
# from utils.facades.Auth import Auth
# from utils.facades.Hasher import Hasher
# from entities.user.entity import User
# from entities.user.types import (
#     UserSignUpData,
#     UserSignInData,
#     UserAsPrimary
# )


# router = APIRouter()


# @router.post('/sign-up', response_model = UserAsPrimary)
# async def sign_up(
#     request_data: UserSignUpData = Body(),
#     db: AsyncSession = Depends(connect_db)
# ):
#     user = await User.new(
#         db,
#         firstname = request_data.firstname,
#         lastname = request_data.lastname,
#         email = request_data.email,
#         password_hash = Hasher.hash_it(request_data.password)
#     )
#     return JSONResponse(
#         headers = Auth.get_auth_headers(user.id),
#         status_code = status.HTTP_201_CREATED,
#         content = UserAsPrimary.resource(user)
#     )


# @router.post('/sign-in', response_model = UserAsPrimary)
# async def sign_in(
#     request_data: UserSignInData = Body(),
#     db: AsyncSession = Depends(connect_db)
# ):
#     user = await User.get(
#         db,
#         email = request_data.email,
#         password_hash = Hasher.hash_it(request_data.password)
#     )
#     return JSONResponse(
#         headers = Auth.get_auth_headers(user.id),
#         content = UserAsPrimary.resource(user)
#     )


# @router.get('/me', response_model = UserAsPrimary)
# async def me(me: User = Depends(Auth.authenticate_me)):
#     return JSONResponse(
#         headers = Auth.get_auth_headers(me.id),
#         content = UserAsPrimary.resource(me)
#     )


from fastapi import APIRouter, status, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from utils.facades.Hasher import Hasher
from entities.user.entity import User
from entities.user.types import UserSignUpData, UserSignInData, UserAsPrimary


router = APIRouter()


@router.post('/sign-up', response_model=UserAsPrimary)
async def sign_up(
    request_data: UserSignUpData = Body(),
    db: AsyncSession = Depends(connect_db)
):
    user = await User.new_educator(
        db,
        firstname=request_data.firstname,
        lastname=request_data.lastname,
        login=request_data.login,
        password_hash=Hasher.hash_it(request_data.password)
    )
    return JSONResponse(
        headers=Auth.get_auth_headers(user.id, user.role),
        status_code=status.HTTP_201_CREATED,
        content=UserAsPrimary.resource(user)
    )


@router.post('/sign-in', response_model=UserAsPrimary)
async def sign_in(
    request_data: UserSignInData = Body(),
    db: AsyncSession = Depends(connect_db)
):
    user = await User.get(
        db,
        login=request_data.login,
        password_hash=Hasher.hash_it(request_data.password)
    )
    return JSONResponse(
        headers=Auth.get_auth_headers(user.id, user.role),
        content=UserAsPrimary.resource(user)
    )


@router.get('/me', response_model=UserAsPrimary)
async def me(me: User = Depends(Auth.authenticate_me)):
    return JSONResponse(
        headers=Auth.get_auth_headers(me.id, me.role),
        content=UserAsPrimary.resource(me)
    )
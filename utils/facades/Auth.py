# from fastapi import (
#     Header,
#     Depends,
#     HTTPException,
#     status
# )
# from jwt import encode, decode
# from datetime import datetime, timedelta
# import pytz
# from sqlalchemy.ext.asyncio import AsyncSession

# from utils.db import connect_db
# from entities.user.entity import User

# path_to_keys_dir = 'config'

# with open(f'{path_to_keys_dir}/public-key.pem', 'rb') as file:
#     PUBLIC_KEY = file.read()

# with open(f'{path_to_keys_dir}/private-key.pem', 'rb') as file:
#     PRIVATE_KEY = file.read()

# class Auth:
#     def generate_token(id: int) -> str:
#         almaty_tz = pytz.timezone('Asia/Almaty')
#         now = datetime.now(almaty_tz)
#         expiration_time = now + timedelta(hours=10)

#         return encode(
#             {
#                 'exp': int(expiration_time.timestamp()),
#                 'sub': str(id)  # Преобразуем ID в строку
#             },
#             PRIVATE_KEY,
#             'RS256'
#         )

#     def authenticate_token(token: str = Header(alias='Auth')) -> int:
#         return decode(
#             token.replace('Bearer ', '').strip(),
#             PUBLIC_KEY,
#             ['RS256']
#         )['sub']

#     def get_auth_headers(id: int) -> dict:
#         return { 'Auth': f'Bearer {Auth.generate_token(id)}' }

#     async def authenticate_me(
#         token: str = Header(alias='Auth'),
#         db: AsyncSession = Depends(connect_db)
#     ) -> User:
#         me = await User.get_by_id(db, Auth.authenticate_token(token))
#         if not me:
#             raise HTTPException(
#                 status.HTTP_401_UNAUTHORIZED,
#                 'Invalid Token'
#             )
#         return me


from fastapi import Header, Depends, HTTPException, status
from jwt import encode, decode
from datetime import datetime, timedelta
import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from entities.user.entity import User

path_to_keys_dir = 'config'

with open(f'{path_to_keys_dir}/public-key.pem', 'rb') as file:
    PUBLIC_KEY = file.read()

with open(f'{path_to_keys_dir}/private-key.pem', 'rb') as file:
    PRIVATE_KEY = file.read()


class Auth:
    def generate_token(id: int, role: str) -> str:
        almaty_tz = pytz.timezone('Asia/Almaty')
        now = datetime.now(almaty_tz)
        expiration_time = now + timedelta(hours=10)

        return encode(
            {
                'exp': int(expiration_time.timestamp()),
                'sub': str(id),
                'role': role
            },
            PRIVATE_KEY,
            'RS256'
        )

    def authenticate_token(token: str = Header(alias='Auth')) -> int:
        return int(
            decode(
                token.replace('Bearer ', '').strip(),
                PUBLIC_KEY,
                ['RS256']
            )['sub']
        )

    def get_auth_headers(id: int, role: str) -> dict:
        return {'Auth': f'Bearer {Auth.generate_token(id, role)}'}

    async def authenticate_me(
        token: str = Header(alias='Auth'),
        db: AsyncSession = Depends(connect_db)
    ) -> User:
        user = await User.get_by_id(db, Auth.authenticate_token(token))
        if not user or not user.is_active:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                'Invalid Token'
            )
        return user
# from fastapi import HTTPException, status
# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     select,
#     exists
# )
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.exc import SQLAlchemyError

# from utils.db import BaseEntity


# class User(BaseEntity):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key = True)
#     firstname = Column(String(25), nullable = False)
#     lastname = Column(String(25), nullable = False)
#     email = Column(String, unique = True, nullable = False)
#     password_hash = Column(String, nullable = False)


#     async def new(
#         db: AsyncSession,
#         firstname: str,
#         lastname: str,
#         email: str,
#         password_hash: str
#     ) -> 'User':
#         query = select(exists(User).where(User.email == email))
#         email_used = (await db.execute(query)).scalar()
#         if email_used:
#             raise HTTPException(
#                 status.HTTP_409_CONFLICT,
#                 'This Email Already Taken'
#             )

#         user = User(
#             firstname = firstname,
#             lastname = lastname,
#             email = email,
#             password_hash = password_hash
#         )
#         db.add(user)

#         try:
#             await db.commit()
#         except SQLAlchemyError:
#             await db.rollback()
#             raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return user
        

#     async def get(
#         db: AsyncSession,
#         email: str,
#         password_hash: str
#     ) -> 'User':
#         query = select(User).where(
#             User.email == email,
#             User.password_hash == password_hash
#         )
#         user = (await db.execute(query)).scalar_one_or_none()

#         if not user:
#             raise HTTPException(
#                 status.HTTP_404_NOT_FOUND,
#                 f'User[email={email} & password] Not Found'
#             )
#         return user
    
    
#     async def get_by_id(
#         db: AsyncSession,
#         id: int
#     ) -> 'User':
#         query = select(User).where(User.id == id)
#         user = (await db.execute(query)).scalar_one_or_none()
        
#         if not user:
#             raise HTTPException(
#                 status.HTTP_404_NOT_FOUND,
#                 f'User[id={id}] Not Found'
#             )
#         return user


from fastapi import HTTPException, status
from sqlalchemy import Column, Integer, String, Boolean, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from utils.db import BaseEntity


class User(BaseEntity):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(25), nullable=False)
    lastname = Column(String(25), nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(20), nullable=False, default='educator')
    must_change_password = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    @classmethod
    async def new_educator(cls, db: AsyncSession, firstname: str, lastname: str, login: str, password_hash: str) -> 'User':
        login_used = (await db.execute(select(exists().where(User.login == login)))).scalar()
        if login_used:
            raise HTTPException(status.HTTP_409_CONFLICT, 'This Login Already Taken')

        user = cls(
            firstname=firstname,
            lastname=lastname,
            login=login,
            password_hash=password_hash,
            role='educator',
            must_change_password=False,
            is_active=True
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return user

    @classmethod
    async def new_parent(cls, db: AsyncSession, login: str, password_hash: str) -> 'User':
        login_used = (await db.execute(select(exists().where(User.login == login)))).scalar()
        if login_used:
            raise HTTPException(status.HTTP_409_CONFLICT, 'This Login Already Taken')

        user = cls(
            firstname='Parent',
            lastname='Account',
            login=login,
            password_hash=password_hash,
            role='parent',
            must_change_password=True,
            is_active=True
        )
        db.add(user)
        try:
            await db.flush()
            await db.commit()
            await db.refresh(user)
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return user

    @classmethod
    async def get(cls, db: AsyncSession, login: str, password_hash: str) -> 'User':
        query = select(User).where(
            User.login == login,
            User.password_hash == password_hash,
            User.is_active == True
        )
        user = (await db.execute(query)).scalar_one_or_none()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f'User[login={login} & password] Not Found')
        return user

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int) -> 'User':
        query = select(User).where(User.id == id)
        user = (await db.execute(query)).scalar_one_or_none()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f'User[id={id}] Not Found')
        return user

    @classmethod
    async def get_by_login(cls, db: AsyncSession, login: str) -> 'User | None':
        query = select(User).where(User.login == login)
        return (await db.execute(query)).scalar_one_or_none()

    @classmethod
    async def update_password(cls, db: AsyncSession, user: 'User', password_hash: str, must_change_password: bool = True) -> 'User':
        user.password_hash = password_hash
        user.must_change_password = must_change_password
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def update_profile(cls, db: AsyncSession, user: 'User', firstname: str, lastname: str) -> 'User':
        user.firstname = firstname
        user.lastname = lastname
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
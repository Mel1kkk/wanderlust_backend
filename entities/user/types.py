# from pydantic import BaseModel, Field

# from entities.user.entity import User


# class UserSignInData(BaseModel):
#     email: str = Field(pattern=r'[^@]+@[^@]+\.[^@]+', examples=['stranger.things2004@sdu.edu.kz'])
#     password: str =Field(min_length=8, max_length=25, pattern=r'^[A-Za-z\d@$!%*?&]+$')


# class UserSignUpData(UserSignInData):
#     firstname: str = Field(max_length=25, examples=['Joe'])
#     lastname: str = Field(max_length=25, examples=['Keery'])
    

# class UserAsPrimary(BaseModel):
#     id: int
#     email: str
#     firstname: str
#     lastname: str

#     def resource(user: User):
#         return UserAsPrimary(
#             id = user.id,
#             email = user.email,
#             firstname = user.firstname,
#             lastname = user.lastname
#         ).model_dump()



from pydantic import BaseModel, Field

from entities.user.entity import User


class UserSignInData(BaseModel):
    login: str = Field(min_length=3, max_length=50, examples=['educator_01'])
    password: str = Field(min_length=8, max_length=64, pattern=r'^[A-Za-z\d@$!%*?&]+$')


class UserSignUpData(UserSignInData):
    firstname: str = Field(max_length=25, examples=['Joe'])
    lastname: str = Field(max_length=25, examples=['Keery'])


class UserAsPrimary(BaseModel):
    id: int
    login: str
    firstname: str
    lastname: str
    role: str
    must_change_password: bool

    def resource(user: User):
        return UserAsPrimary(
            id=user.id,
            login=user.login,
            firstname=user.firstname,
            lastname=user.lastname,
            role=user.role,
            must_change_password=user.must_change_password
        ).model_dump()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.db import lifespan
from routes.auth.api import router as auth_router
from routes.chatbot.api import router as chatbot_router
from routes.children_groups.api import router as children_groups
from routes.plan_notes.api import router as plan_notes_router
from routes.parents.api import router as parents_router
from routes.parent_notes.api import router as parent_notes_router
from routes.children.api import router as children_router


app = FastAPI(
    title = 'Wanderlust 😎',
    lifespan = lifespan
)

app.include_router(auth_router, prefix = '/auth')
app.include_router(chatbot_router, prefix='/chatbot')
app.include_router(children_groups, prefix="/children_groups")
app.include_router(children_router, prefix='/children')
app.include_router(plan_notes_router, prefix="/plan_notes")
app.include_router(parents_router, prefix='/parents')
app.include_router(parent_notes_router, prefix='/parent_notes')

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials=True,
    allow_headers = ['*'],
    allow_methods = ['*'],
    expose_headers=["auth"]
)


# if __name__ == '__main__':
#     from uvicorn import run
#     run('main:app', port = 8000, reload = True)
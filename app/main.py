from fastapi import FastAPI

from .router import router as user_router
from referral_code.router import router as code_router



app = FastAPI()


app.include_router(user_router)
app.include_router(code_router)

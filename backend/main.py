from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import auth, mail

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mail Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mail.router)


@app.get("/health")
def health():
    return {"status": "ok"}

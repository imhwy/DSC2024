"""
Run the code in this file
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.api.routers import chat_router


app = FastAPI()

# app.include_router(root_router)
app.include_router(chat_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000
    )

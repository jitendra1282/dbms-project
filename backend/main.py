# In backend/main.py
from fastapi import FastAPI
from modules.module_E3.api import router as e3_router

app = FastAPI(title="Medical Copilot System")
app.include_router(e3_router)

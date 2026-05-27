from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI

load_dotenv(find_dotenv(usecwd=True))

from src.routes.ingestDoctors import router as ingestDoctorsRouter
from src.routes.searchDoctors import router as searchDoctorsRouter
from src.routes.searchQuery import router as searchQueryRouter

app = FastAPI(title="wonderful")
app.include_router(ingestDoctorsRouter)
app.include_router(searchDoctorsRouter)
app.include_router(searchQueryRouter)

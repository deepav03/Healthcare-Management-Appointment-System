import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.appointments import router as appointments_router
from app.api.routes.clinical import router as clinical_router
from app.api.routes.billing import router as billing_router
from app.api.routes.reporting import router as reporting_router
from app.api.routes.doctors import router as doctors_router
from app.api.routes.health import router as health_router
from app.api.routes.patients import router as patients_router
from app.api.routes.schedules import router as schedules_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error while processing %s", request.url.path)
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
    origin = request.headers.get("origin")
    if origin in settings.cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(doctors_router)
app.include_router(schedules_router)
app.include_router(appointments_router)
app.include_router(clinical_router)
app.include_router(billing_router)
app.include_router(reporting_router)

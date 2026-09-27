import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

log = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login")
async def login(req: LoginRequest):
    raise HTTPException(status_code=501, detail="Not implemented: Login route pending implementation by Nikhil.")

@router.get("/auth/me")
async def get_me():
    raise HTTPException(status_code=501, detail="Not implemented: Get current user route pending implementation by Nikhil.")

@router.get("/businesses")
async def get_businesses():
    raise HTTPException(status_code=501, detail="Not implemented: Get businesses route pending implementation by Nikhil.")

@router.get("/businesses/{id}/catalog")
async def get_catalog(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Get catalog route pending implementation by Nikhil.")

@router.get("/businesses/{id}/services")
async def get_services(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Get services route pending implementation by Nikhil.")

@router.get("/businesses/{id}/slots")
async def get_slots(id: str, service_id: str = None):
    raise HTTPException(status_code=501, detail="Not implemented: Get slots route pending implementation by Nikhil.")

@router.get("/businesses/{id}/orders")
async def get_orders(id: str, status: str = None):
    raise HTTPException(status_code=501, detail="Not implemented: Get orders route pending implementation by Nikhil.")

@router.get("/businesses/{id}/holds")
async def get_holds(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Get holds route pending implementation by Jagdeep.")

@router.post("/businesses/{id}/holds")
async def resolve_hold(id: str, payload: dict):
    raise HTTPException(status_code=501, detail="Not implemented: Resolve hold route pending implementation by Jagdeep.")

@router.get("/businesses/{id}/evidence")
async def get_evidence(id: str):
    raise HTTPException(status_code=501, detail="Not implemented: Get evidence route pending implementation by Jagdeep.")

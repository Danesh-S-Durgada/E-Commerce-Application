from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def cart_health():
    return {"service": "cart", "status": "planned"}

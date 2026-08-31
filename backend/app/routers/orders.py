from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def order_health():
    return {"service": "orders", "status": "planned"}

from fastapi import FastAPI
from fastapi.routing import APIRouter
import uvicorn

from api.routes.handlers import router as users_router 
from api.routes.auth import router as auth_router
from api.routes.admin import router as admin_router
from api.routes.public_products import router as public_products_router
from api.routes.cart import router as cart_router
from api.routes.address import router as address_router
from api.routes.order import router as order_router

app = FastAPI(title="Shop")


main_router = APIRouter()


main_router.include_router(users_router, prefix="", tags=["users"])  
main_router.include_router(auth_router, prefix="", tags=["auth"])    
main_router.include_router(admin_router, prefix="", tags=["admin"])
main_router.include_router(public_products_router, prefix="", tags=["public_products"])
main_router.include_router(cart_router, prefix="", tags=["cart"])
main_router.include_router(address_router, prefix="", tags=["adresses"])
main_router.include_router(order_router, prefix="", tags=["order"])

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
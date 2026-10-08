from fastapi import FastAPI

from routes.inbound_invoices import router as invoice_router
from routes.inventory_stocks import router as stocks_router
from routes.users import router as user_router
from routes.warehouse_cells import router as warehouse_roter
from shared.exception_handler import register_exception_handlers

# Инициализация fastapi
app = FastAPI()


# Обработчик для доменных ошибок
register_exception_handlers(app)


# Роуты
@app.get("/health")
def healthChecker():
  return {"message": "All rights!"}


app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(warehouse_roter, prefix="/api", tags=["warehouse_cell"])
app.include_router(invoice_router, prefix="/api", tags=["inbound_invoices"])
app.include_router(stocks_router, prefix="/api", tags=["inventory_stocks"])

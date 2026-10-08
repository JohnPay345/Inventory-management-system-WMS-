from functools import partial
from types import SimpleNamespace
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status as web_status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.inventory_stocks import (
  repo_stocks_create,
  repo_stocks_exists,
  repo_stocks_get,
  repo_stocks_update,
)
from repositories.products import repo_get_product
from repositories.warehouse_cells import repo_cell_exists, repo_cell_update
from shared.dependency import get_db, verify_access_token
from shared.schemas import (
  NewInventoryStocksRequest,
  ResponseSchema,
  TokenPayload,
  UpdateInventoryStocksRequest,
)
from use_cases.inventory_stocks import case_stocks_create, case_stocks_get, case_stocks_update


def inventory_stocks_repo(db: Annotated[AsyncSession, Depends(get_db)]):
  return SimpleNamespace(
    repo_stocks_exists=partial(repo_stocks_exists, db),
    repo_stocks_get=partial(repo_stocks_get, db),
    repo_stocks_create=partial(repo_stocks_create, db),
    repo_stocks_update=partial(repo_stocks_update, db),
    repo_cell_update=partial(repo_cell_update, db),
    repo_cell_exists=partial(repo_cell_exists, db),
    repo_get_product=partial(repo_get_product, db),
  )


router = APIRouter()


@router.get("/stocks_get", response_model=ResponseSchema)
async def inventory_stocks_get(
  user: Annotated[TokenPayload, Depends(verify_access_token)],
  limit: int = Query(default=10, ge=1),
  offset: int = Query(default=0, ge=0),
  repo=Depends(inventory_stocks_repo),
):
  list_stocks = await case_stocks_get(limit, offset, repo)
  if not list_stocks:
    return ResponseSchema.error(
      code=web_status.HTTP_404_NOT_FOUND, data=list_stocks, message="List inventory_stocks is empty"
    )
  return ResponseSchema.success(data=list_stocks, message="Get list inventory_stocks")


@router.post("/stocks_create", response_model=ResponseSchema)
async def inventory_stocks_create(
  stocks_data: NewInventoryStocksRequest,
  user: Annotated[TokenPayload, Depends(verify_access_token)],
  repo=Depends(inventory_stocks_repo),
):
  new_stocks = await case_stocks_create(stocks_data, repo)
  return ResponseSchema.success(
    code=web_status.HTTP_201_CREATED, data=new_stocks, message="Created new stocks"
  )


@router.patch("/stocks_update", response_model=ResponseSchema)
async def inventory_stocks_update(
  stocks_data: UpdateInventoryStocksRequest,
  user: Annotated[TokenPayload, Depends(verify_access_token)],
  repo=Depends(inventory_stocks_repo),
):
  updated_stocks = await case_stocks_update(stocks_data, repo)
  return ResponseSchema.success(data=updated_stocks, message="Update stocks")

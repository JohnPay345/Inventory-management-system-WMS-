from functools import partial
from types import SimpleNamespace
from typing import Annotated

from fastapi import APIRouter, Depends, status as web_status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.warehouse_cells import (
  repo_cell_create,
  repo_cell_exists,
  repo_cell_update,
  repo_get_cell_by_coordinates,
)
from shared.dependency import PermissionChecker, get_db
from shared.enum import UserRole
from shared.schemas import (
  NewWarehouseCellRequest,
  ResponseSchema,
  UpdateWarehouseCellRequest,
)
from use_cases.warehouse_cells import case_cell_create, case_cell_update


def warehouse_repo(db: Annotated[AsyncSession, Depends(get_db)]):
  return SimpleNamespace(
    repo_cell_exists=partial(repo_cell_exists, db),
    repo_get_cell_by_coordinates=partial(repo_get_cell_by_coordinates, db),
    repo_cell_create=partial(repo_cell_create, db),
    repo_cell_update=partial(repo_cell_update, db),
  )


router = APIRouter(dependencies=[Depends(PermissionChecker([UserRole.MANAGER]))])


@router.post("/cell_create", response_model=ResponseSchema)
async def warehouse_cell_create(
  cell_data: NewWarehouseCellRequest,
  repo=Depends(warehouse_repo),
):
  new_cell = await case_cell_create(cell_data=cell_data, repository=repo)
  return ResponseSchema.success(
    code=web_status.HTTP_201_CREATED, data=new_cell, message="Created new warehouse cell"
  )


@router.patch("/cell_update/{warehouse_cell_id}", response_model=ResponseSchema)
async def warehouse_cell_update(
  cell_data: UpdateWarehouseCellRequest,
  warehouse_cell_id: str,
  repo=Depends(warehouse_repo),
):
  updated_cell = await case_cell_update(
    cell_data=cell_data, warehouse_cell_id=warehouse_cell_id, repository=repo
  )
  return ResponseSchema.success(data=updated_cell, message="Update cell")

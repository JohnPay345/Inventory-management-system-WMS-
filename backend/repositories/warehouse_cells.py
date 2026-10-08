from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import NotFoundError
from domain.warehouse_cell import WarehouseCell as WarehouseCellEntity
from shared.mappers import map_domain_to_orm_flat, map_orm_to_domain_flat
from shared.models import WarehouseCell as WarehouseCellModel


async def repo_cell_exists(db: AsyncSession, cell_id: UUID) -> WarehouseCellEntity | None:
  query = select(WarehouseCellModel).where(WarehouseCellModel.warehouse_cell_id == cell_id)
  result = await db.execute(query)
  orm_cell = result.scalars().first()
  return map_orm_to_domain_flat(orm_cell, WarehouseCellEntity)


async def repo_get_cell_by_coordinates(
  db: AsyncSession, zone_code: str, rack_number: int, shelf_number: int
) -> WarehouseCellEntity | None:
  query = select(WarehouseCellModel).where(
    WarehouseCellModel.zone_code == zone_code,
    WarehouseCellModel.rack_number == rack_number,
    WarehouseCellModel.shelf_number == shelf_number,
  )
  result = await db.execute(query)
  orm_cell = result.one_or_none()
  if orm_cell is None:
    return None
  return map_orm_to_domain_flat(orm_cell, WarehouseCellEntity)


async def repo_get_cells(
  db: AsyncSession, limit: int = 10, offset: int = 0
) -> list[WarehouseCellEntity]:
  query = select(WarehouseCellModel).limit(limit).offset(offset)
  result = await db.execute(query)
  warehouse_cells = result.scalars().all()
  if not warehouse_cells:
    return []
  return [map_orm_to_domain_flat(cell, WarehouseCellEntity) for cell in warehouse_cells]


async def repo_cell_create(db: AsyncSession, cell_data: WarehouseCellEntity) -> WarehouseCellEntity:
  orm_cell = map_domain_to_orm_flat(domain_entity=cell_data, orm_class=WarehouseCellModel)
  db.add(orm_cell)
  await db.flush()
  await db.refresh(orm_cell)
  entity_cell = map_orm_to_domain_flat(orm_object=orm_cell, domain_class=WarehouseCellEntity)
  return entity_cell


async def repo_cell_update(
  db: AsyncSession, cell_id: UUID, cell_data: WarehouseCellEntity
) -> WarehouseCellEntity:
  orm_cell = await db.get(WarehouseCellModel, cell_id)
  if not orm_cell:
    raise NotFoundError(entity_name="WarehouseCell", identifier=str(cell_id))
  cell_dict = asdict(cell_data)
  cell_dict.pop("warehouse_cell_id")
  for key, value in cell_dict.items():
    setattr(orm_cell, key, value)
  await db.flush()
  await db.refresh(orm_cell)
  entity_cell = map_orm_to_domain_flat(orm_cell, WarehouseCellEntity)
  return entity_cell

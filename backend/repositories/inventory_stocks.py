from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import NotFoundError
from domain.inventory_stocks import InventoryStocks as InventoryStocksEntity
from shared.mappers import map_domain_to_orm_flat, map_orm_to_domain_flat
from shared.models import InventoryStocks as InventoryStocksModel


async def repo_stocks_exists(
  db: AsyncSession, product_id: UUID, cell_id: UUID
) -> InventoryStocksEntity | None:
  query = select(InventoryStocksModel).where(
    InventoryStocksModel.product_id == product_id, InventoryStocksModel.cell_id == cell_id
  )
  result = await db.execute(query)
  orm_stocks = result.scalar_one_or_none()
  if orm_stocks is None:
    return None
  entity_stocks = map_orm_to_domain_flat(orm_stocks, InventoryStocksEntity)
  return entity_stocks


async def repo_stocks_get(db: AsyncSession, limit: int, offset: int) -> list[InventoryStocksEntity]:
  query = select(InventoryStocksModel).limit(limit).offset(offset)
  result = await db.execute(query)
  orm_stocks = result.scalars().all()
  if not orm_stocks:
    return []
  entity_stocks = [map_orm_to_domain_flat(item, InventoryStocksEntity) for item in orm_stocks]
  return entity_stocks


async def repo_stocks_create(
  db: AsyncSession, stocks_data: InventoryStocksEntity
) -> InventoryStocksEntity:
  orm_stocks = map_domain_to_orm_flat(stocks_data, InventoryStocksModel)
  db.add(orm_stocks)
  await db.flush()
  await db.refresh(orm_stocks)
  entity_stocks = map_orm_to_domain_flat(orm_stocks, InventoryStocksEntity)
  return entity_stocks


async def repo_stocks_update(
  db: AsyncSession, stocks_data: InventoryStocksEntity
) -> InventoryStocksEntity:
  orm_stocks = await db.get(
    InventoryStocksModel,
    InventoryStocksModel.product_id == stocks_data.product_id
    and InventoryStocksModel.cell_id == stocks_data.cell_id,
  )
  if not orm_stocks:
    raise NotFoundError(
      entity_name="InventoryStocks", identifier=f"{stocks_data.product_id}:{stocks_data.cell_id}"
    )
  orm_stocks.quantity = stocks_data.quantity
  await db.flush()
  await db.refresh(orm_stocks)
  return stocks_data

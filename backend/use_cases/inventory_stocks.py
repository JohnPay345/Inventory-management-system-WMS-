from typing import Protocol
from uuid import UUID

from domain.exceptions import AlreadyExistsError, NotFoundError
from domain.inventory_stocks import InventoryStocks as InventoryStocksEntity
from domain.products import Product as ProductEntity
from domain.services.warehouse_stocks import WarehouseDomainService
from domain.warehouse_cell import WarehouseCell as WarehouseCellEntity
from shared.schemas import NewInventoryStocksRequest, UpdateInventoryStocksRequest


class InventoryStocksProtocol(Protocol):
  async def repo_stocks_exists(
    self, product_id: UUID, cell_id: UUID
  ) -> InventoryStocksEntity | None: ...
  async def repo_stocks_get(self, limit: int, offset: int) -> list[InventoryStocksEntity]: ...
  async def repo_stocks_create(
    self, stocks_data: InventoryStocksEntity
  ) -> InventoryStocksEntity: ...
  async def repo_stocks_update(
    self, stocks_data: InventoryStocksEntity
  ) -> InventoryStocksEntity: ...
  async def repo_cell_update(
    self, cell_id: UUID, cell_data: WarehouseCellEntity
  ) -> WarehouseCellEntity: ...
  async def repo_cell_exists(self, cell_id: UUID) -> WarehouseCellEntity | None: ...
  async def repo_get_product(self, product_id: UUID) -> ProductEntity | None: ...


async def case_stocks_get(
  limit: int, offset: int, repository: InventoryStocksProtocol
) -> list[InventoryStocksEntity]:
  list_stocks = await repository.repo_stocks_get(limit, offset)
  return list_stocks


async def case_stocks_create(
  stocks_data: NewInventoryStocksRequest, repository: InventoryStocksProtocol
) -> InventoryStocksEntity:
  is_stocks = await repository.repo_stocks_exists(stocks_data.product_id, stocks_data.cell_id)
  if is_stocks is not None:
    raise AlreadyExistsError(
      entity_name="InventoryStocks", conflict_details="Место под продукт уже занято"
    )
  new_stocks = InventoryStocksEntity.create(
    stocks_data.product_id, stocks_data.cell_id, stocks_data.quantity
  )
  created_stocks = await repository.repo_stocks_create(new_stocks)
  return created_stocks


async def case_stocks_update(
  stocks_data: UpdateInventoryStocksRequest,
  repository: InventoryStocksProtocol,
) -> InventoryStocksEntity:
  is_stocks = await repository.repo_stocks_exists(stocks_data.product_id, stocks_data.cell_id)
  if is_stocks is None:
    raise NotFoundError(
      entity_name="InventoryStocks", identifier=f"{stocks_data.product_id}:{stocks_data.cell_id}"
    )
  cell = await repository.repo_cell_exists(stocks_data.cell_id)
  product = await repository.repo_get_product(stocks_data.product_id)
  if cell is None or product is None:
    raise NotFoundError(
      entity_name="InventoryStocks", identifier=f"{stocks_data.product_id}:{stocks_data.cell_id}"
    )
  WarehouseDomainService.update_stock_and_cell_weight(
    cell, is_stocks, product.weight_kg, stocks_data.quantity
  )
  await repository.repo_cell_update(stocks_data.cell_id, cell)
  updated_stocks = await repository.repo_stocks_update(is_stocks)
  return updated_stocks

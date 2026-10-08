from dataclasses import asdict
from typing import Protocol
from uuid import UUID

from domain.exceptions import AlreadyExistsError, BusinessRuleViolationError, NotFoundError
from domain.warehouse_cell import WarehouseCell as WarehouseCellEntity
from shared.schemas import NewWarehouseCellRequest, UpdateWarehouseCellRequest


class WarehouseCellProtocol(Protocol):
  async def repo_cell_exists(self, cell_id: UUID) -> WarehouseCellEntity | None: ...
  async def repo_get_cell_by_coordinates(
    self, zone_code: str, rack_number: int, shelf_number: int
  ) -> WarehouseCellEntity | None: ...
  async def repo_get_cells(self, limit: int = 10, offset: int = 0) -> list[WarehouseCellEntity]: ...
  async def repo_cell_create(self, cell_data: WarehouseCellEntity) -> WarehouseCellEntity: ...
  async def repo_cell_update(
    self, cell_id: UUID, cell_data: WarehouseCellEntity
  ) -> WarehouseCellEntity: ...


async def case_cell_create(
  cell_data: NewWarehouseCellRequest, repository: WarehouseCellProtocol
) -> WarehouseCellEntity:
  is_cell = await repository.repo_get_cell_by_coordinates(
    cell_data.zone_code, cell_data.rack_number, cell_data.shelf_number
  )
  if is_cell is None:
    raise AlreadyExistsError(
      entity_name="WarehouseCell",
      conflict_details=f"Зона: {cell_data.zone_code}, Стеллаж: {cell_data.rack_number}, Полка: {cell_data.shelf_number} уже заняты",
    )
  new_cell_aggregate = WarehouseCellEntity.create(
    zone_code=cell_data.zone_code,
    rack_number=cell_data.rack_number,
    shelf_number=cell_data.shelf_number,
    max_weight_kg=cell_data.max_weight_kg,
    current_weight_kg=cell_data.current_weight_kg,
    is_occupied=cell_data.is_occupied,
  )
  new_cell = await repository.repo_cell_create(new_cell_aggregate)
  return new_cell


async def case_cell_update(
  cell_data: UpdateWarehouseCellRequest, warehouse_cell_id: str, repository: WarehouseCellProtocol
) -> WarehouseCellEntity:
  is_cell = await repository.repo_cell_exists(cell_id=UUID(warehouse_cell_id))
  if is_cell is None:
    raise NotFoundError(entity_name="WarehouseCell", identifier=warehouse_cell_id)
  is_cell.change_max_weight_limit(cell_data.new_max_weight_kg)
  updated_cell = await repository.repo_cell_update(UUID(warehouse_cell_id), is_cell)
  return updated_cell

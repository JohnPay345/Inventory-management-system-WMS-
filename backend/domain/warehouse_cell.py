from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleViolationError


@dataclass
class WarehouseCell:
  warehouse_cell_id: UUID | None
  zone_code: str
  rack_number: int
  shelf_number: int
  max_weight_kg: Decimal = Decimal("0.00")
  current_weight_kg: Decimal = Decimal("0.00")
  is_occupied: bool = False

  @classmethod
  def create(
    cls,
    zone_code: str,
    rack_number: int,
    shelf_number: int,
    max_weight_kg: Decimal,
    current_weight_kg: Decimal,
    is_occupied: bool,
  ) -> "WarehouseCell":
    if zone_code == "" or rack_number < 0 or shelf_number < 0:
      raise BusinessRuleViolationError(
        entity_name="WarehouseCell",
        identifier="-",
        conflict_details="Номер складской ячейки не может быть пустым или отрицательным",
      )
    if max_weight_kg < 0.00 or current_weight_kg < 0.00:
      raise BusinessRuleViolationError(
        entity_name="WarehouseCell",
        identifier="-",
        conflict_details="Вес не может быть отрицательным",
      )
    if is_occupied == True:
      raise BusinessRuleViolationError(
        entity_name="WarehouseCell",
        identifier="-",
        conflict_details="Складская ячейка не может быть занята при создании",
      )
    return cls(
      warehouse_cell_id=uuid4(),
      zone_code=zone_code,
      rack_number=rack_number,
      shelf_number=shelf_number,
      max_weight_kg=max_weight_kg,
      current_weight_kg=current_weight_kg,
      is_occupied=is_occupied,
    )

  def add_stock(self, product_weight: Decimal):
    if product_weight < Decimal("0.00"):
      raise BusinessRuleViolationError(
        entity_name="WarehouseCell",
        identifier=str(self.warehouse_cell_id),
        conflict_details="Превышена максимальная грузоподъемность ячейки!",
      )
    self.current_weight_kg = product_weight
    self.is_occupied = True

  def change_max_weight_limit(self, new_max_weight: Decimal):
    if new_max_weight < self.current_weight_kg:
      raise BusinessRuleViolationError(
        entity_name="WarehouseDomainService",
        identifier=str(self.warehouse_cell_id),
        conflict_details=f"Невозможно уменьшить лимит ячейки {self} до {new_max_weight} кг. \
          В ней уже находятся товары общим весом {self.current_weight_kg} кг. \
          Сначала переместите или спишите излишек товара.",
      )
    self.max_weight_kg = new_max_weight

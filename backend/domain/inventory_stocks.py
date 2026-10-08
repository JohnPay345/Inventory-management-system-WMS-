from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from domain.exceptions import BusinessRuleViolationError


@dataclass
class InventoryStocks:
  product_id: UUID
  cell_id: UUID
  created_at: datetime
  updated_at: datetime
  quantity: int = 0

  @classmethod
  def create(cls, product_id: UUID, cell_id: UUID, quantity: int) -> "InventoryStocks":
    if quantity < 0:
      raise BusinessRuleViolationError(
        entity_name="InventoryStocks",
        identifier="-",
        conflict_details="Товаров на складе не может быть меньше нуля",
      )
    return cls(
      product_id=product_id,
      cell_id=cell_id,
      quantity=quantity,
      created_at=datetime.now(UTC),
      updated_at=datetime.now(UTC),
    )

  def change_quantity(self, new_quantity: int):
    if new_quantity < 0:
      raise BusinessRuleViolationError(
        entity_name="InventoryStocks",
        identifier=f"{self.product_id}:{self.cell_id}",
        conflict_details="Новое количество товаров не может быть меньше нуля",
      )
    self.quantity = new_quantity

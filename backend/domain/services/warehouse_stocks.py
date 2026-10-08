from decimal import Decimal

from domain.exceptions import BusinessRuleViolationError
from domain.inventory_stocks import InventoryStocks
from domain.warehouse_cell import WarehouseCell


class WarehouseDomainService:
  @classmethod
  def update_stock_and_cell_weight(
    cls, cell: WarehouseCell, stock: InventoryStocks, product_weight: Decimal, new_quantity: int
  ):
    old_quantity = stock.quantity
    quantity_delta = new_quantity - old_quantity

    if quantity_delta == 0:
      return

    weight_delta = product_weight * Decimal(quantity_delta)
    calculated_new_weight = cell.current_weight_kg + weight_delta

    if calculated_new_weight > cell.max_weight_kg:
      raise BusinessRuleViolationError(
        entity_name="WarehouseDomainService",
        identifier=f"{stock.cell_id}:{stock.product_id}",
        conflict_details=f"Операция отклонена: превышен лимит веса ячейки {cell.zone_code}. \
        Максимальная вместимость: {cell.max_weight_kg} кг. \
        Текущий вес: {cell.current_weight_kg} кг. \
        Пытаемся добавить: {weight_delta} кг.  \
        Итоговый вес составил бы: {calculated_new_weight} кг.",
      )

    cell.add_stock(calculated_new_weight)
    stock.change_quantity(new_quantity)

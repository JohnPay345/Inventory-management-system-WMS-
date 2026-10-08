from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleViolationError


@dataclass
class Product:
  product_id: UUID | None
  sku: str
  barcode: str
  title: str
  created_at: datetime
  updated_at: datetime
  description: str = ""
  current_price: Decimal = Decimal("0.00")
  weight_kg: Decimal = Decimal("0.00")
  is_active: bool = True

  @classmethod
  def create(
    cls,
    sku: str,
    barcode: str,
    title: str,
    current_price: Decimal,
    weight_kg: Decimal,
    description: str = "",
  ) -> "Product":
    if sku == "" or barcode == "" or title == "":
      raise BusinessRuleViolationError(
        entity_name="Products",
        identifier="-",
        conflict_details="SKU код, штрих-код и названия обязательны",
      )
    if current_price < Decimal("0.00") or weight_kg < Decimal("0.00"):
      raise BusinessRuleViolationError(
        entity_name="Products",
        identifier="-",
        conflict_details="Цена и вес не могут быть отрицательными",
      )
    now = datetime.now(UTC)
    return cls(
      product_id=uuid4(),
      sku=sku,
      barcode=barcode,
      title=title,
      description=description,
      current_price=current_price,
      weight_kg=weight_kg,
      is_active=True,
      created_at=now,
      updated_at=now,
    )

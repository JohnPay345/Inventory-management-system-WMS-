from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleViolationError
from shared.enum import InboundInvoicesStatus


@dataclass
class InboundInvoiceItem:
  inbound_invoice_item_id: UUID | None
  product_id: UUID
  target_cell_id: UUID
  invoice_id: UUID | None = None
  quantity: int = 0
  price_at_received: Decimal = Decimal("0.00")


@dataclass
class InboundInvoice:
  inbound_invoice_id: UUID | None
  invoice_number: str
  supplier_name: str
  status: InboundInvoicesStatus
  received_at: datetime
  created_by: UUID
  created_at: datetime
  updated_at: datetime
  items: list[InboundInvoiceItem]

  @classmethod
  def create(
    cls,
    invoice_number: str,
    supplier_name: str,
    created_by: UUID,
    received_at: datetime,
    items: list,
  ) -> "InboundInvoice":
    if not items:
      raise BusinessRuleViolationError(
        entity_name="InboundInvoice",
        identifier="-",
        conflict_details="Накладная не может быть пустой",
      )
    generated_invoice_id = uuid4()
    domain_items = [
      InboundInvoiceItem(
        inbound_invoice_item_id=uuid4(),
        invoice_id=generated_invoice_id,
        product_id=item.product_id,
        target_cell_id=item.target_cell_id,
        quantity=item.quantity,
        price_at_received=item.price_at_received,
      )
      for item in items
    ]
    now = datetime.now(UTC)
    return cls(
      inbound_invoice_id=generated_invoice_id,
      invoice_number=invoice_number,
      supplier_name=supplier_name,
      status=InboundInvoicesStatus.DRAFT,
      received_at=received_at,
      created_by=created_by,
      created_at=now,
      updated_at=now,
      items=domain_items,
    )

  def update(self, changes) -> "InboundInvoice":
    if self.status in ["posted", "cancelled"]:
      raise BusinessRuleViolationError(
        entity_name="InboundInvoice",
        identifier=str(self.inbound_invoice_id),
        conflict_details="Нельзя редактировать закрытый документ",
      )
    if "inbound_invoice_id" in changes or "created_at" in changes:
      raise BusinessRuleViolationError(
        entity_name="InboundInvoice",
        identifier=str(self.inbound_invoice_id),
        conflict_details="Нельзя изменять системные поля",
      )
    updated_entity = replace(self, **changes)
    updated_entity._validate()
    return updated_entity

  def _validate(self):
    if not self.items:
      raise BusinessRuleViolationError(
        entity_name="InboundInvoice",
        identifier=str(self.inbound_invoice_id),
        conflict_details="Накладная не может быть без товаров",
      )

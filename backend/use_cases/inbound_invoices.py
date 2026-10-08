from typing import Protocol
from uuid import UUID, uuid4

from domain.exceptions import AlreadyExistsError, NotFoundError
from domain.inbound_invoice import (
  InboundInvoice as InboundInvoiceEntity,
  InboundInvoiceItem as InboundInvoiceItemEntity,
)
from shared.schemas import NewInvoiceRequest, UpdateInvoiceRequest


class InboundInvoiceProtocol(Protocol):
  async def repo_inbound_exists(self, invoice_id: UUID) -> bool: ...
  async def repo_get_inbound_by_number(
    self, invoice_number: str
  ) -> InboundInvoiceEntity | None: ...
  async def repo_invoice_create(
    self, invoice_data: InboundInvoiceEntity
  ) -> InboundInvoiceEntity: ...
  async def repo_invoice_update(
    self, invoice_data: InboundInvoiceEntity, current_invoice_data: InboundInvoiceEntity
  ) -> InboundInvoiceEntity: ...


async def case_invoice_create(
  invoice_data: NewInvoiceRequest, current_user_id: UUID, repository: InboundInvoiceProtocol
) -> InboundInvoiceEntity:
  is_invoice = await repository.repo_get_inbound_by_number(invoice_data.header.invoice_number)
  if is_invoice is None:
    raise AlreadyExistsError(
      entity_name="InboundInvoice",
      conflict_details=f"Накладная с номером уже '{invoice_data.header.invoice_number}' существует",
    )
  new_invoice_aggregate = InboundInvoiceEntity.create(
    invoice_number=invoice_data.header.invoice_number,
    supplier_name=invoice_data.header.supplier_name,
    received_at=invoice_data.header.received_at,
    created_by=current_user_id,
    items=invoice_data.items,
  )
  new_invoice = await repository.repo_invoice_create(new_invoice_aggregate)
  return new_invoice


async def case_invoice_update(
  invoice_data: UpdateInvoiceRequest,
  inbound_invoice_number: str,
  repository: InboundInvoiceProtocol,
) -> InboundInvoiceEntity:
  is_invoice = await repository.repo_get_inbound_by_number(inbound_invoice_number)
  if not is_invoice:
    raise NotFoundError(entity_name="InboundInvoice", identifier=inbound_invoice_number)
  updated_data = invoice_data.model_dump(exclude_unset=True)
  if "items" in updated_data:
    updated_data["items"] = [
      InboundInvoiceItemEntity(
        inbound_invoice_item_id=uuid4(),
        product_id=item["product_id"],
        target_cell_id=item["target_cell_id"],
        quantity=item["quantity"],
        price_at_received=item["price_at_received"],
      )
      for item in updated_data["items"]
    ]
  updated_invoice_data = is_invoice.update(updated_data)
  updated_invoice = await repository.repo_invoice_update(updated_invoice_data, is_invoice)
  return updated_invoice

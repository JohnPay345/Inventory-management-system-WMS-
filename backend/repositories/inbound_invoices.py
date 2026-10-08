from dataclasses import asdict
from uuid import UUID

from sqlalchemy import delete, exists, insert, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.inbound_invoice import (
  InboundInvoice as InboundInvoiceEntity,
  InboundInvoiceItem as InboundInvoiceItemEntity,
)
from shared.mappers import map_orm_to_domain_flat
from shared.models import (
  InboundInvoice as InboundInvoiceModel,
  InboundInvoiceItem as InboundInvoiceItemModel,
)


def map_to_invoice_entity(
  orm_invoice: InboundInvoiceModel, orm_items: list[InboundInvoiceItemModel]
) -> InboundInvoiceEntity:
  header_data = {attr.key: attr.value for attr in inspect(orm_invoice).attrs}
  header_data["items"] = [
    map_orm_to_domain_flat(item, InboundInvoiceItemEntity) for item in orm_items
  ]
  return InboundInvoiceEntity(**header_data)


def map_to_invoice_orm(
  entity_invoice: InboundInvoiceEntity,
) -> tuple[InboundInvoiceModel, list[InboundInvoiceItemModel]]:
  header_data = asdict(entity_invoice)
  domain_items = header_data.pop("items", [])
  orm_invoice = InboundInvoiceModel(**header_data)
  orm_items = []
  for item in domain_items:
    item["invoice_id"] = entity_invoice.inbound_invoice_id
    orm_items.append(InboundInvoiceItemModel(**item))
  return orm_invoice, orm_items


async def repo_inbound_exists(db: AsyncSession, inbound_id: UUID) -> bool:
  query = select(exists().where(InboundInvoiceModel.inbound_invoice_id == inbound_id))
  result = await db.execute(query)
  return bool(result.scalar())


async def repo_get_inbound_by_number(
  db: AsyncSession, invoice_number: str
) -> InboundInvoiceEntity | None:
  header_query = select(InboundInvoiceModel).where(
    InboundInvoiceModel.invoice_number == invoice_number
  )
  header_result = await db.execute(header_query)
  orm_invoice = header_result.scalar_one_or_none()
  if not orm_invoice:
    return None

  items_query = select(InboundInvoiceItemModel).where(
    InboundInvoiceItemModel.invoice_id == orm_invoice.inbound_invoice_id
  )
  items_result = await db.execute(items_query)
  orm_items = list(items_result.scalars().all())
  return map_to_invoice_entity(orm_invoice, orm_items)


async def repo_invoice_create(
  db: AsyncSession, invoice_data: InboundInvoiceEntity
) -> InboundInvoiceEntity:
  orm_invoice, orm_items = map_to_invoice_orm(invoice_data)
  db.add(orm_invoice)
  db.add_all(orm_items)
  await db.flush()
  await db.refresh(orm_invoice)
  return map_to_invoice_entity(orm_invoice, orm_items)


async def repo_invoice_update(
  db: AsyncSession, invoice_data: InboundInvoiceEntity, current_invoice_data: InboundInvoiceEntity
) -> InboundInvoiceEntity:
  # 1. Обновляем заголовок накладной
  header_data = asdict(invoice_data)
  header_data.pop("items", None)  # Убираем вложенный список товаров
  header_id = header_data.pop("inbound_invoice_id")

  await db.execute(
    update(InboundInvoiceModel)
    .where(InboundInvoiceModel.inbound_invoice_id == header_id)
    .values(**header_data)
  )

  # 2. Вычисляем разницу между списками товаров в памяти Python
  old_ids = {item.inbound_invoice_item_id for item in current_invoice_data.items}
  new_ids = {
    item.inbound_invoice_item_id for item in invoice_data.items if item.inbound_invoice_item_id
  }

  ids_to_delete = list(old_ids - new_ids)
  to_create = [item for item in invoice_data.items if item.inbound_invoice_item_id not in old_ids]
  to_update = [item for item in invoice_data.items if item.inbound_invoice_item_id in old_ids]

  # 3. Действие А: Удаляем позиции, которые пользователь убрал из накладной
  if ids_to_delete:
    await db.execute(
      delete(InboundInvoiceItemModel).where(
        InboundInvoiceItemModel.inbound_invoice_item_id.in_(ids_to_delete)
      )
    )

  # 4. Действие Б: Обновляем изменившиеся позиции (Динамически)
  for item in to_update:
    item_data = asdict(item)
    item_pk = item_data.pop("inbound_invoice_item_id")
    item_data.pop("invoice_id", None)  # FK менять при обновлении строки не нужно

    await db.execute(
      update(InboundInvoiceItemModel)
      .where(InboundInvoiceItemModel.inbound_invoice_item_id == item_pk)
      .values(**item_data)  # Автоматически обновляет любые новые поля товара
    )

  # 5. Действие В: Массово вставляем новые позиции (Динамически)
  if to_create:
    items_to_insert = []
    for item in to_create:
      item_data = asdict(item)
      item_data["invoice_id"] = invoice_data.inbound_invoice_id  # Принудительно связываем
      items_to_insert.append(item_data)

    await db.execute(insert(InboundInvoiceItemModel), items_to_insert)

  # 6. Синхронизируем транзакцию и подтягиваем header
  await db.flush()

  orm_invoice = await db.get(InboundInvoiceModel, invoice_data.inbound_invoice_id)
  if orm_invoice:
    await db.refresh(orm_invoice)
    # Синхронизируем даты в возвращаемом Entity
    invoice_data.created_at = orm_invoice.created_at
    invoice_data.updated_at = orm_invoice.updated_at

  return invoice_data

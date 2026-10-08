from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.products import Product as ProductEntity
from shared.mappers import map_domain_to_orm_flat, map_orm_to_domain_flat
from shared.models import Products as ProductModel


async def repo_get_product(db: AsyncSession, product_id: UUID) -> ProductEntity | None:
  orm_product = await db.get(ProductModel, product_id)
  if not orm_product:
    return None
  return map_orm_to_domain_flat(orm_product, ProductEntity)


async def repo_product_create(db: AsyncSession, product_data: ProductEntity) -> ProductEntity:
  orm_product = map_domain_to_orm_flat(product_data, ProductModel)
  db.add(orm_product)
  await db.flush()
  await db.refresh(orm_product)
  return map_orm_to_domain_flat(orm_product, ProductEntity)


async def repo_product_update(db: AsyncSession, product_data: ProductEntity):
  pass

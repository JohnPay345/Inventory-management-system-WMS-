from functools import partial
from types import SimpleNamespace
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status as web_status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.inbound_invoices import (
  repo_get_inbound_by_number,
  repo_inbound_exists,
  repo_invoice_create,
  repo_invoice_update,
)
from shared.dependency import PermissionChecker, get_db
from shared.enum import UserRole
from shared.schemas import NewInvoiceRequest, ResponseSchema, TokenPayload, UpdateInvoiceRequest
from use_cases.inbound_invoices import case_invoice_create, case_invoice_update


def inbound_invoices_repo(db: AsyncSession = Depends(get_db)):
  return SimpleNamespace(
    repo_inbound_exists=partial(repo_inbound_exists, db),
    repo_get_inbound_by_number=partial(repo_get_inbound_by_number, db),
    repo_invoice_create=partial(repo_invoice_create, db),
    repo_invoice_update=partial(repo_invoice_update, db),
  )


router = APIRouter()


@router.post("/invoices_create/{user_id}", response_model=ResponseSchema)
async def inbound_invoices_create(
  invoice_data: NewInvoiceRequest,
  user: Annotated[
    TokenPayload, Depends(PermissionChecker([UserRole.MANAGER, UserRole.PICKER], True))
  ],
  repo=Depends(inbound_invoices_repo),
):
  user_id = UUID(user.user_id)
  new_invoice = await case_invoice_create(invoice_data, user_id, repo)
  return ResponseSchema.success(
    code=web_status.HTTP_201_CREATED, data=new_invoice, message="Invoice created"
  )


@router.patch("/invoices_update/{user_id}/{inbound_invoice_number}", response_model=ResponseSchema)
async def inbound_invoices_update(
  invoice_data: UpdateInvoiceRequest,
  inbound_invoice_number: str,
  user: Annotated[
    TokenPayload, Depends(PermissionChecker([UserRole.MANAGER, UserRole.PICKER], True))
  ],
  repo=Depends(inbound_invoices_repo),
):
  updated_invoice = await case_invoice_update(invoice_data, inbound_invoice_number, repo)
  return ResponseSchema.success(data=updated_invoice, message="Updated invoice")

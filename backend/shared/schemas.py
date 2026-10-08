from decimal import Decimal
from typing import Literal, Optional, TypeVar
from uuid import UUID

from fastapi import status as web_status
from pydantic import AwareDatetime, BaseModel, Field

from shared.enum import InboundInvoicesStatus, ResponseStatus, UserRole

T = TypeVar("T")


# Использование Generic позволяет не создавать кучу наследников
class ResponseSchema[T](BaseModel):
  code: int
  status: ResponseStatus
  data: Optional[T] = None
  message: Optional[str]

  @classmethod
  def success(
    cls,
    code: int = web_status.HTTP_200_OK,
    status: ResponseStatus = ResponseStatus.SUCCESS,
    data: T = None,
    message: Optional[str] = "Success",
  ):
    return cls(code=code, status=status, data=data, message=message)

  @classmethod
  def error(
    cls,
    code: int = web_status.HTTP_400_BAD_REQUEST,
    status: ResponseStatus = ResponseStatus.ERROR,
    data: Optional[T] = None,
    message: str = "Error",
  ):
    return cls(code=code, status=status, data=data, message=message)


class TokenPayload(BaseModel):
  sub: str
  username: str
  roles: list[UserRole]
  type: Literal["AT", "RT"]


class LoginRequest(BaseModel):
  username: str = Field(..., max_length=50)
  password: str = Field(..., max_length=50)


class RegisterRequest(BaseModel):
  first_name: str = Field(..., max_length=50)
  middle_name: str = Field(..., max_length=50)
  last_name: str | None = None
  password: str = Field(..., max_length=50)
  username: str = Field(..., max_length=50)
  role: UserRole


class NewProductRequest(BaseModel):
  sku: str = Field(..., max_length=50)
  barcode: str = Field(..., max_length=50)
  title: str = Field(..., max_length=50)
  description: str | None = None
  current_price: Decimal = Decimal(0)
  weight_kg: Decimal = Field(..., ge=0)


class UpdateProductRequest(BaseModel):
  sku: Optional[str] = Field(default=None, max_length=50)
  barcode: Optional[str] = Field(default=None, max_length=50)
  title: Optional[str] = Field(default=None, max_length=50)
  desription: Optional[str] = None
  current_price: Optional[Decimal] = Field(default=None, ge=0)
  weight_kg: Optional[Decimal] = Field(..., ge=0)
  is_active: Optional[bool] = None


class NewWarehouseCellRequest(BaseModel):
  zone_code: str = Field(..., max_length=10)
  rack_number: int
  shelf_number: int
  max_weight_kg: Decimal = Field(default=Decimal("0.00"), ge=0)
  current_weight_kg: Decimal = Field(default=Decimal("0.00"), ge=0)
  is_occupied: bool = Field(default=False)


class UpdateWarehouseCellRequest(BaseModel):
  new_max_weight_kg: Decimal = Field(default=Decimal("0.00"), ge=0)


class NewInventoryStocksRequest(BaseModel):
  product_id: UUID
  cell_id: UUID
  quantity: int = Field(default=0, ge=0)


class UpdateInventoryStocksRequest(BaseModel):
  product_id: UUID
  cell_id: UUID
  quantity: int = Field(default=0, ge=0)


class InboundInvoices(BaseModel):
  invoice_number: str = Field(..., max_length=100)
  supplier_name: str = Field(..., max_length=255)
  status: InboundInvoicesStatus = InboundInvoicesStatus.DRAFT
  received_at: AwareDatetime


class InboundInvoiceItem(BaseModel):
  product_id: UUID
  target_cell_id: UUID
  quantity: int = Field(..., ge=0)
  price_at_received: Decimal = Field(..., ge=Decimal("0.00"))


class NewInvoiceRequest(BaseModel):
  header: InboundInvoices
  items: list[InboundInvoiceItem]


class InboundInvoicesUpdate(BaseModel):
  invoice_number: Optional[str] = Field(default=None, max_length=100)
  supplier_name: Optional[str] = Field(default=None, max_length=255)
  status: Optional[InboundInvoicesStatus] = None
  received_at: Optional[AwareDatetime] = None


class InboundInvoiceItemUpdate(BaseModel):
  target_cell_id: Optional[UUID] = None
  quantity: Optional[int] = Field(default=None, ge=0)
  price_at_received: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))


class UpdateInvoiceRequest(BaseModel):
  header: Optional[InboundInvoicesUpdate] = None
  items: Optional[list[InboundInvoiceItemUpdate]] = None

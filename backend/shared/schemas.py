from decimal import Decimal
from typing import Generic, List, Optional, TypeVar
from uuid import UUID
from pydantic import AwareDatetime, BaseModel, Field
from backend.shared.enum import InboundInvoicesStatus, ResponseStatus, UserRole

T = TypeVar("T")

# Использование Generic позволяет не создавать кучу наследников
class Response(BaseModel, Generic[T]):
  code: int
  status: ResponseStatus
  data: Optional[T] = None
  message: Optional[str]

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

class UpdateProductRequest(BaseModel):
  sku: Optional[str] = Field(default=None, max_length=50)
  barcode: Optional[str] = Field(default=None, max_length=50)
  title: Optional[str] = Field(default=None, max_length=50)
  desription: Optional[str] = None
  current_price: Optional[Decimal] = Field(default=None, ge=0)
  is_active: Optional[bool] = None

class NewWarehouseCellRequest(BaseModel):
  zone_code: str = Field(..., max_length=10)
  rack_number: int
  shelf_number: int
  max_weight: Decimal = Field(..., ge=0)

class UpdateWarehouseCellRequest(BaseModel):
  zone_code: Optional[str] = Field(default=None, max_length=10)
  rack_number: Optional[int] = None
  shelf_number: Optional[int] = None
  max_weight: Optional[Decimal] = Field(default=None, ge=0)

class InboundInvoices(BaseModel):
  invoice_number: str = Field(..., max_length=100)
  supplier_name: str = Field(..., max_length=255)
  status: InboundInvoicesStatus = InboundInvoicesStatus.DRAFT
  received_at: AwareDatetime

class InboundInvoiceItem(BaseModel):
  invoice_id: UUID
  product_id: UUID
  target_cell_id: UUID
  quantity: int = Field(..., ge=0)
  price_at_received: Decimal = Field(..., ge=Decimal("0.00"))

class NewInvoiceRequest(BaseModel):
  header: InboundInvoices
  items: List[InboundInvoiceItem]

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
  items: Optional[List[InboundInvoiceItemUpdate]] = None
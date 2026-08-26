from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from backend.sevices.database import Base

status_inbound_invoices = ENUM("draft", "posted", "cancelled", name="status_inbound_invoices")
action_type_log = ENUM("create", "update", "annull", name="action_type_log")
user_role = ENUM("manager", "storekeeper", "picker", name="user_role")

class Products(Base):
  __tablename__ = "products"
  product_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  sku: Mapped[str] = mapped_column(String(50))
  barcode: Mapped[str] = mapped_column(String(50))
  title: Mapped[str] = mapped_column(String(50))
  description: Mapped[Optional[str]] = mapped_column(Text, default=None)
  current_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), CheckConstraint("current_price > 0.00"), default=Decimal("0.00"))
  is_active: Mapped[bool] = mapped_column(default=True)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
  updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), server_onupdate=func.now())

class WarehouseCell(Base):
  __tablename__ = "warehouse_cells"
  warehouse_cell_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  zone_code: Mapped[str] = mapped_column(String(10), unique=True)
  rack_number: Mapped[int] = mapped_column(unique=True)
  shelf_number: Mapped[int] = mapped_column(unique=True)
  max_weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), CheckConstraint("max_weight_kg >= 0.00"), default=Decimal("0.00"))
  is_occupied: Mapped[bool] = mapped_column(default=False)

class User(Base):
  __tablename__ = "users"
  user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  first_name: Mapped[str] = mapped_column(String(50))
  middle_name: Mapped[str] = mapped_column(String(50))
  last_name: Mapped[Optional[str]] = mapped_column(String(50), default=None)
  username: Mapped[str] = mapped_column(String(50))
  password_hash: Mapped[str] = mapped_column(String(50))
  role: Mapped[str] = mapped_column(user_role)
  is_active: Mapped[bool] = mapped_column(default=True)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

class InboundInvoice(Base):
  __tablename__ = "inbound_invoices"
  inbound_invoice_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  invoice_number: Mapped[str] = mapped_column(String(100), unique=True)
  supplier_name: Mapped[str] = mapped_column(String(255))
  status: Mapped[str] = mapped_column(status_inbound_invoices)
  received_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
  created_by: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
  updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class InboundInvoiceItem(Base):
  __tablename__ = "inbound_invoice_items"
  inbound_invoice_item_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  invoice_id: Mapped[UUID] = mapped_column(ForeignKey("inbound_invoices.inbound_invoice_id"))
  product_id: Mapped[UUID] = mapped_column(ForeignKey("products.product_id"))
  target_cell_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse_cells.warehouse_cell_id"))
  quantity: Mapped[int] = mapped_column(CheckConstraint("quantity >= 0"))
  price_at_received: Mapped[Decimal] = mapped_column(Numeric(12, 2), CheckConstraint("price_at_received > 0.00"), default=Decimal("0.00"))

class WarehouseAuditLog(Base):
  __tablename__ = "warehouse_audit_log"
  log_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
  entity_name: Mapped[str] = mapped_column(String(50))
  entity_id: Mapped[UUID] = mapped_column()
  action_type: Mapped[str] = mapped_column(action_type_log)
  old_values: Mapped[dict] = mapped_column(JSONB, default=None)
  new_values: Mapped[dict] = mapped_column(JSONB, default=None)
  ip_address: Mapped[str] = mapped_column(String(45), default=None)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
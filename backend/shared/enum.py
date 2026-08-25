from enum import StrEnum

class ResponseStatus(StrEnum):
  SUCCESS = "SUCCESS"
  CREATED = "CREATED"
  BAD_REQUEST = "BAD_REQUEST"
  UNAUTHORIZED = "UNAUTHORIZED"
  ERROR = "ERROR"

class InboundInvoicesStatus(StrEnum):
  DRAFT = "draft"
  POSTED = "posted"
  CANCELLED = "cancelled"

class UserRole(StrEnum):
  MANAGER = "manager"
  STOREKEEPER = "storekeeper"
  PICKER = "picker"
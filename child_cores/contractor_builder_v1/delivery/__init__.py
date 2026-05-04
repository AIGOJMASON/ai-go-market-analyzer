"""
Delivery surfaces for contractor_builder_v1.

This package owns the governed delivery branch for contractor phase closeout:
- email delivery schema
- email runtime
- read receipt runtime
- delivery receipts

Delivery records communication events.
It does not create workflow truth or fake signatures.
"""

from .email_schema import (
    EMAIL_SCHEMA_VERSION,
    READ_RECEIPT_STATUS_ENUM,
    build_email_delivery_record,
    validate_email_delivery_record,
)
from .email_runtime import send_email
from .read_receipt_runtime import (
    build_read_receipt_event,
    mark_email_opened,
)
from .delivery_receipt_builder import (
    build_delivery_receipt,
    write_delivery_receipt,
)

__all__ = [
    "EMAIL_SCHEMA_VERSION",
    "READ_RECEIPT_STATUS_ENUM",
    "build_email_delivery_record",
    "validate_email_delivery_record",
    "send_email",
    "build_read_receipt_event",
    "mark_email_opened",
    "build_delivery_receipt",
    "write_delivery_receipt",
]
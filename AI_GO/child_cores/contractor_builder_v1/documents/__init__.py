"""
Document surfaces for contractor_builder_v1.

This package owns the governed document branch for contractor phase closeout:
- PDF artifact schema
- PDF artifact builder
- PDF receipts

Documents are generated from structured truth only.
They do not mutate workflow or approvals.
"""

from .phase_closeout_pdf_schema import (
    PHASE_CLOSEOUT_PDF_SCHEMA_VERSION,
    build_phase_closeout_pdf_artifact,
    validate_phase_closeout_pdf_artifact,
)
from .phase_closeout_pdf_builder import build_phase_closeout_pdf
from .pdf_receipt_builder import (
    build_pdf_receipt,
    write_pdf_receipt,
)

__all__ = [
    "PHASE_CLOSEOUT_PDF_SCHEMA_VERSION",
    "build_phase_closeout_pdf_artifact",
    "validate_phase_closeout_pdf_artifact",
    "build_phase_closeout_pdf",
    "build_pdf_receipt",
    "write_pdf_receipt",
]
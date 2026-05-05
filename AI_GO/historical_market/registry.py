"""
AI_GO Historical Market Registry

Purpose:
    Declares the bounded subsystem surfaces for the historical market layer.

Authority posture:
    Registry only. No execution, no public writes, no live-ingress mutation.
"""

from __future__ import annotations

from typing import Any, Dict


HISTORICAL_MARKET_REGISTRY: Dict[str, Any] = {
    "subsystem_id": "historical_market",
    "status": "active_draft_surface",
    "authority_posture": {
        "append_only": True,
        "public_write_allowed": False,
        "execution_authority": False,
        "recommendation_mutation_allowed": False,
        "live_ingress_owner": False,
    },
    "surfaces": {
        "layer_doc": {
            "path": "AI_GO/historical_market/_HISTORICAL_MARKET_LAYER.md",
            "role": "authority_surface",
            "function": "defines_lawful_scope_and_constraints",
        },
        "policy": {
            "path": "AI_GO/historical_market/policy.py",
            "role": "constraint_surface",
            "function": "defines_storage_and_write_rules",
        },
        "storage_db_paths": {
            "path": "AI_GO/historical_market/storage/db_paths.py",
            "role": "path_authority",
            "function": "declares_canonical_storage_paths",
        },
        "raw_store": {
            "path": "AI_GO/historical_market/storage/raw_store.py",
            "role": "append_only_raw_writer",
            "function": "writes_raw_or_normalized_market_bar_records",
        },
        "curated_store": {
            "path": "AI_GO/historical_market/storage/curated_store.py",
            "role": "append_only_curated_writer",
            "function": "writes_curated_historical_records",
        },
    },
    "future_surfaces": {
        "loaders": [
            "historical_backfill_runner",
            "historical_incremental_runner",
            "source_client_alpha_vantage",
            "source_client_polygon",
        ],
        "normalization": [
            "bar_normalizer",
            "symbol_mapper",
            "timestamp_normalizer",
            "asset_classifier",
        ],
        "derivation": [
            "setup_detector",
            "outcome_labeler",
            "relationship_engine",
        ],
        "retrieval": [
            "historical_query_runtime",
            "setup_similarity_runtime",
            "relationship_lookup_runtime",
            "outcome_summary_runtime",
        ],
        "adapters": [
            "operator_translation_adapter",
            "child_core_history_adapter",
        ],
    },
    "canonical_record_families": {
        "raw": [
            "market_bar_record",
        ],
        "curated": [
            "historical_intake_event",
            "historical_merge_event",
            "historical_outcome_event",
            "historical_setup_pattern",
            "historical_asset_relationship",
        ],
        "receipts": [
            "raw_fetch_receipt",
            "raw_write_receipt",
            "curated_write_receipt",
            "query_receipt",
        ],
    },
}


def get_historical_market_registry() -> Dict[str, Any]:
    """
    Return the canonical registry for the historical market subsystem.
    """
    return HISTORICAL_MARKET_REGISTRY.copy()
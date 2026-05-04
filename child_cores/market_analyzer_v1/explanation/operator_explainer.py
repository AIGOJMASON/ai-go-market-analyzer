from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from child_cores.market_analyzer_v1.explanation.outcome_interpreter import (
    build_labeled_outcomes_panel_from_source_2_summary,
)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _split_sentences_decimal_safe(text: str) -> str:
    if not text:
        return ""

    out = []
    length = len(text)
    for i, char in enumerate(text):
        out.append(char)
        if char != ".":
            continue

        prev_char = text[i - 1] if i > 0 else ""
        next_char = text[i + 1] if i + 1 < length else ""

        if prev_char.isdigit() and next_char.isdigit():
            continue

        if next_char and next_char != " ":
            out.append(" ")

    return "".join(out).strip()


def _extract_current_case(payload: Dict[str, Any]) -> Dict[str, Any]:
    operator_packet = _safe_dict(payload.get("operator_packet"))
    current_case = _safe_dict(operator_packet.get("current_case"))
    if current_case:
        return current_case

    direct_current_case = _safe_dict(payload.get("current_case"))
    if direct_current_case:
        return direct_current_case

    return {
        "request_id": payload.get("request_id"),
        "headline": _safe_dict(payload.get("runtime_panel")).get("headline"),
        "recommendation_panel": _safe_dict(payload.get("recommendation_panel")),
        "governance_panel": _safe_dict(payload.get("governance_panel")),
        "live_event_panel": _safe_dict(payload.get("live_event_panel")),
    }


def _extract_symbol(current_case: Dict[str, Any]) -> str:
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    if live_event_panel.get("symbol"):
        return _safe_str(live_event_panel.get("symbol"))

    if current_case.get("symbol"):
        return _safe_str(current_case.get("symbol"))

    recommendation_panel = _safe_dict(current_case.get("recommendation_panel"))
    items = _safe_list(recommendation_panel.get("items"))
    if items and isinstance(items[0], dict):
        return _safe_str(items[0].get("symbol"))

    return ""


def _extract_headline(current_case: Dict[str, Any]) -> str:
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    if live_event_panel.get("headline"):
        return _safe_str(live_event_panel.get("headline"))

    if current_case.get("headline"):
        return _safe_str(current_case.get("headline"))

    return ""


def _extract_price_change_pct(current_case: Dict[str, Any]) -> Optional[float]:
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    if "price_change_pct" in live_event_panel:
        return _safe_float(live_event_panel.get("price_change_pct"))

    if "price_change_pct" in current_case:
        return _safe_float(current_case.get("price_change_pct"))

    return None


def _extract_confirmation(current_case: Dict[str, Any]) -> str:
    live_event_panel = _safe_dict(current_case.get("live_event_panel"))
    if live_event_panel.get("confirmation"):
        return _safe_str(live_event_panel.get("confirmation"))
    return ""


def _extract_historical_reference(payload: Dict[str, Any]) -> Dict[str, Any]:
    operator_packet = _safe_dict(payload.get("operator_packet"))
    historical_reference = _safe_dict(operator_packet.get("historical_reference"))
    if historical_reference:
        return historical_reference

    direct_historical_reference = _safe_dict(payload.get("historical_reference"))
    if direct_historical_reference:
        return direct_historical_reference

    return _safe_dict(payload.get("source_2_summary"))


def _extract_external_memory_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    direct_packet = _safe_dict(payload.get("external_memory_packet"))
    if direct_packet:
        return direct_packet

    operator_packet = _safe_dict(payload.get("operator_packet"))
    nested_packet = _safe_dict(operator_packet.get("external_memory_packet"))
    if nested_packet:
        return nested_packet

    return {}


def _extract_labeled_outcomes_panel(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    direct_panel = _safe_dict(payload.get("labeled_outcomes_panel"))
    if direct_panel:
        return direct_panel

    operator_packet = _safe_dict(payload.get("operator_packet"))
    nested_panel = _safe_dict(operator_packet.get("labeled_outcomes_panel"))
    if nested_panel:
        return nested_panel

    historical_reference = _extract_historical_reference(payload)
    generated = build_labeled_outcomes_panel_from_source_2_summary(historical_reference)
    return generated if isinstance(generated, dict) and generated else None


def _extract_setup_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    historical_reference = _extract_historical_reference(payload)
    setup_detection = _safe_dict(historical_reference.get("setup_detection"))
    historical_context = _safe_dict(historical_reference.get("historical_context"))
    setup_history_panel = _safe_dict(historical_context.get("setup_history_panel"))

    return {
        "setup_detected": _safe_bool(setup_detection.get("detected")),
        "setup_type": _safe_str(setup_detection.get("setup_type")),
        "setup_reason": _safe_str(_safe_dict(setup_detection.get("supporting_features")).get("reason")),
        "historical_posture": _safe_str(setup_history_panel.get("historical_posture")),
        "setup_lookup_type": _safe_str(setup_history_panel.get("setup_type")),
        "historical_status": _safe_str(historical_context.get("status")),
        "historical_operator_summary": _safe_str(historical_context.get("operator_summary")),
        "follow_through_rate_pct": _safe_float(setup_history_panel.get("follow_through_rate_pct")),
        "failure_rate_pct": _safe_float(setup_history_panel.get("failure_rate_pct")),
        "outcome_count": int(_safe_float(setup_history_panel.get("outcome_count"), 0.0)),
    }


def _extract_watchlist_panel(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    direct_panel = _safe_dict(payload.get("watchlist_panel"))
    if direct_panel:
        return direct_panel

    operator_packet = _safe_dict(payload.get("operator_packet"))
    nested_panel = _safe_dict(operator_packet.get("watchlist_panel"))
    if nested_panel:
        return nested_panel

    return None


def _symbols_from_bucket(bucket_items: List[Dict[str, Any]], limit: int = 3) -> str:
    symbols: List[str] = []
    for item in bucket_items:
        if not isinstance(item, dict):
            continue
        symbol = _safe_str(item.get("symbol"))
        if symbol:
            symbols.append(symbol)
        if len(symbols) >= limit:
            break
    return ", ".join(symbols)


def _formal_score_band(score: float) -> str:
    if score >= 0.75:
        return "buy-grade"
    if score >= 0.55:
        return "watch-grade"
    if score >= 0.40:
        return "avoid-grade"
    return "fade-grade"


def _extract_watchlist_model(watchlist_panel: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    panel = _safe_dict(watchlist_panel)
    model = _safe_dict(panel.get("model"))
    context = _safe_dict(panel.get("context"))

    confidence = _safe_float(
        model.get("confidence", context.get("confidence")),
        0.0,
    )
    historical_edge_raw = _safe_float(
        model.get("historical_edge_raw", context.get("historical_edge_raw")),
        0.0,
    )
    sample_weight = _safe_float(
        model.get("sample_weight", context.get("sample_weight")),
        0.0,
    )
    historical_edge_adjusted = _safe_float(
        model.get("historical_edge_adjusted", context.get("historical_edge_adjusted")),
        0.0,
    )
    setup_multiplier = _safe_float(
        model.get("setup_multiplier", context.get("setup_multiplier")),
        0.0,
    )
    formal_score = _safe_float(
        model.get("formal_score", context.get("formal_score")),
        0.0,
    )
    formal_classification = _safe_str(
        model.get("formal_classification", context.get("formal_classification"))
    )

    return {
        "confidence": confidence,
        "historical_edge_raw": historical_edge_raw,
        "sample_weight": sample_weight,
        "historical_edge_adjusted": historical_edge_adjusted,
        "setup_multiplier": setup_multiplier,
        "formal_score": formal_score,
        "formal_classification": formal_classification,
        "formal_score_band": _formal_score_band(formal_score),
    }


def _build_watchlist_guidance(watchlist_panel: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not isinstance(watchlist_panel, dict) or not watchlist_panel:
        return {
            "summary": "",
            "buy_symbols": "",
            "avoid_symbols": "",
            "fade_symbols": "",
            "driver_symbols": "",
            "posture_phrase": "",
        }

    buckets = _safe_dict(watchlist_panel.get("buckets"))
    buy_symbols = _symbols_from_bucket(_safe_list(buckets.get("buy")))
    avoid_symbols = _symbols_from_bucket(_safe_list(buckets.get("avoid")))
    fade_symbols = _symbols_from_bucket(_safe_list(buckets.get("fade")))
    driver_symbols = _symbols_from_bucket(_safe_list(buckets.get("driver")), limit=3)

    summary = _safe_str(watchlist_panel.get("summary"))
    posture_label = _safe_str(watchlist_panel.get("posture_label"))
    no_trade_state = _safe_dict(watchlist_panel.get("no_trade_state"))
    model = _extract_watchlist_model(watchlist_panel)

    posture_parts: List[str] = []
    if posture_label:
        posture_parts.append(f"Watchlist posture: {posture_label}")

    if model.get("formal_classification"):
        posture_parts.append(
            f"Formal score is {model['formal_score']:.2f} ({model['formal_score_band']})"
        )

    if no_trade_state:
        is_no_trade = _safe_bool(no_trade_state.get("is_no_trade"))
        reason = _safe_str(no_trade_state.get("reason"))
        if is_no_trade and reason:
            posture_parts.append(f"No-trade is active because {reason.lower()}")
        elif is_no_trade:
            posture_parts.append("No-trade is active")
        else:
            posture_parts.append("No-trade is not active")

    return {
        "summary": summary,
        "buy_symbols": buy_symbols,
        "avoid_symbols": avoid_symbols,
        "fade_symbols": fade_symbols,
        "driver_symbols": driver_symbols,
        "posture_phrase": ". ".join(part for part in posture_parts if part).strip(),
    }


def _build_memory_language(external_memory_packet: Dict[str, Any]) -> Dict[str, str]:
    advisory_summary = _safe_dict(external_memory_packet.get("advisory_summary"))
    memory_context_panel = _safe_dict(external_memory_packet.get("memory_context_panel"))

    decision = _safe_str(advisory_summary.get("decision"))
    advisory_posture = _safe_str(
        advisory_summary.get("advisory_posture")
        or external_memory_packet.get("advisory_posture")
    )
    record_count = advisory_summary.get("record_count")
    coherence_flags = _safe_list(advisory_summary.get("coherence_flags"))
    promoted_ids = _safe_list(memory_context_panel.get("promoted_memory_ids"))

    if advisory_posture == "strong_context" or decision == "promoted":
        count_text = ""
        if isinstance(record_count, int) and record_count > 0:
            count_text = f" across {record_count} promoted recent records"

        coherent_text = ""
        if coherence_flags:
            coherent_text = " Recent memory is coherent across symbol and sector."

        return {
            "summary": f"Recent memory context is strong{count_text}.{coherent_text}".strip(),
            "memory_strength": "strong",
            "memory_record_count": str(record_count) if record_count is not None else "",
            "memory_ids_present": "yes" if promoted_ids else "no",
        }

    if advisory_posture or decision:
        return {
            "summary": "Recent memory context is present, but not strong enough to drive the case on its own.",
            "memory_strength": "present",
            "memory_record_count": str(record_count) if record_count is not None else "",
            "memory_ids_present": "yes" if promoted_ids else "no",
        }

    return {
        "summary": "",
        "memory_strength": "absent",
        "memory_record_count": "",
        "memory_ids_present": "no",
    }


def _join_sentences(*parts: str) -> str:
    clean = [part.strip().rstrip(".") for part in parts if part and part.strip()]
    if not clean:
        return ""
    return ". ".join(clean) + "."


def _build_score_language(
    *,
    watchlist_panel: Optional[Dict[str, Any]],
    setup_context: Dict[str, Any],
) -> Dict[str, str]:
    model = _extract_watchlist_model(watchlist_panel)
    follow = setup_context.get("follow_through_rate_pct", 0.0)
    fail = setup_context.get("failure_rate_pct", 0.0)
    count = setup_context.get("outcome_count", 0)
    classification = model.get("formal_classification") or ""
    score = float(model.get("formal_score") or 0.0)

    if not classification:
        return {
            "score_summary": "",
            "score_implication": "",
        }

    band = model.get("formal_score_band", "")
    score_summary = (
        f"Formal score is {score:.2f}, which reads as {band}."
    )

    if classification == "buy":
        implication = (
            f"The model leans constructive, with follow-through {follow:.1f}% versus failure {fail:.1f}% "
            f"across {count} outcomes."
        )
    elif classification == "watch":
        implication = (
            f"The model is conditional rather than decisive, with follow-through {follow:.1f}% versus failure {fail:.1f}% "
            f"across {count} outcomes."
        )
    elif classification == "avoid":
        implication = (
            f"The model does not support clean exposure here, with follow-through {follow:.1f}% versus failure {fail:.1f}% "
            f"across {count} outcomes."
        )
    else:
        implication = (
            f"The model leans failure-first, with follow-through {follow:.1f}% versus failure {fail:.1f}% "
            f"across {count} outcomes."
        )

    return {
        "score_summary": score_summary,
        "score_implication": implication,
    }


def _build_refined_historical_language(
    *,
    labeled_outcomes_panel: Dict[str, Any],
    setup_context: Dict[str, Any],
    watchlist_panel: Optional[Dict[str, Any]],
    memory_language: Dict[str, str],
) -> Dict[str, str]:
    operator_summary = _safe_str(
        labeled_outcomes_panel.get("operator_summary"),
        "Historical outcomes are available but not fully summarized.",
    )
    why_user_should_care = _safe_str(
        labeled_outcomes_panel.get("why_user_should_care"),
        "Use the current signal cautiously until stronger confirmation appears.",
    )
    edge_class = _safe_str(labeled_outcomes_panel.get("edge_class"))
    setup_reason = setup_context.get("setup_reason", "")
    setup_lookup_type = setup_context.get("setup_lookup_type", "")
    historical_posture = setup_context.get("historical_posture", "")
    watch = _build_watchlist_guidance(watchlist_panel)
    score_language = _build_score_language(
        watchlist_panel=watchlist_panel,
        setup_context=setup_context,
    )

    if setup_reason == "live_confirmed_event_with_pre_event_backdrop":
        whats_been_happening = _join_sentences(
            memory_language.get("summary", "") if memory_language.get("memory_strength") == "strong" else "",
            "This reads as a live rebound against a weak recent backdrop",
            operator_summary,
            score_language.get("score_implication", ""),
        )

        if edge_class == "fragile":
            lead_shape = "The current signal is confirmed, but history still argues for caution"
        elif edge_class == "constructive":
            lead_shape = "The current signal is confirmed, and history suggests similar rebounds have often held"
        elif edge_class == "indecisive":
            lead_shape = "The current signal is confirmed, but similar rebounds have often stalled instead of trending cleanly"
        else:
            lead_shape = "The current signal is confirmed, but the historical record does not establish a clear edge"

        support_shape = ""
        if watch["buy_symbols"] and watch["fade_symbols"]:
            support_shape = (
                f"Long ideas remain conditional in names such as {watch['buy_symbols']}, "
                f"while failure risk still points toward {watch['fade_symbols']}"
            )
        elif watch["buy_symbols"]:
            support_shape = f"Long ideas remain conditional in names such as {watch['buy_symbols']}"
        elif watch["fade_symbols"]:
            support_shape = f"Failure risk still points toward {watch['fade_symbols']}"

        what_this_looks_like = _join_sentences(
            lead_shape,
            score_language.get("score_summary", ""),
            support_shape,
        )

        if watch["buy_symbols"] and watch["fade_symbols"] and watch["driver_symbols"]:
            what_to_watch_next = _join_sentences(
                f"Only treat {watch['buy_symbols']} as actionable if the lane keeps confirming",
                f"If momentum fails, shift focus toward fade names such as {watch['fade_symbols']}",
                f"Use {watch['driver_symbols']} as the confirmation gate",
            )
        elif historical_posture or setup_lookup_type:
            what_to_watch_next = _join_sentences(
                f"Watch whether this rebound can convert into a stronger {setup_lookup_type or 'continuation'} read",
                f"If strength fades quickly, the {historical_posture or 'historical'} pattern remains the better guide",
            )
        else:
            what_to_watch_next = _join_sentences(
                "Watch whether the rebound can hold above reclaimed levels",
                "If strength fades quickly, treat the historical pattern as the better guide",
            )

        why_it_matters = _join_sentences(
            why_user_should_care,
            watch.get("summary", ""),
            score_language.get("score_summary", ""),
        )

        return {
            "why_it_matters_refined": why_it_matters,
            "whats_been_happening": whats_been_happening,
            "what_this_looks_like": what_this_looks_like,
            "what_to_watch_next": what_to_watch_next,
        }

    whats_been_happening = _join_sentences(
        memory_language.get("summary", "") if memory_language.get("memory_strength") == "strong" else "",
        operator_summary if operator_summary else "",
        score_language.get("score_implication", ""),
        "Formal historical setup support remains limited" if memory_language.get("memory_strength") == "strong" else "",
    )

    lead_shape = why_user_should_care
    support_shape = ""
    if watch["buy_symbols"] and watch["fade_symbols"]:
        support_shape = (
            f"Long ideas remain conditional in {watch['buy_symbols']}, while failure risk still centers on {watch['fade_symbols']}"
        )
    elif watch["buy_symbols"]:
        support_shape = f"Long ideas remain conditional in {watch['buy_symbols']}"
    elif watch["fade_symbols"]:
        support_shape = f"Failure risk still centers on {watch['fade_symbols']}"

    what_this_looks_like = _join_sentences(
        lead_shape,
        score_language.get("score_summary", ""),
        support_shape,
    )

    if watch["buy_symbols"] and watch["fade_symbols"] and watch["driver_symbols"]:
        what_to_watch_next = _join_sentences(
            f"Only treat {watch['buy_symbols']} as actionable if the lane keeps confirming",
            f"If momentum fails, shift focus toward {watch['fade_symbols']}",
            f"Use {watch['driver_symbols']} as the confirmation gate",
        )
    else:
        what_to_watch_next = _join_sentences(
            "Use the historical distribution as context, not permission",
            "Watch whether new confirmation improves the edge",
        )

    why_it_matters = _join_sentences(
        why_user_should_care,
        watch.get("summary", ""),
        score_language.get("score_summary", ""),
    )

    return {
        "why_it_matters_refined": why_it_matters,
        "whats_been_happening": whats_been_happening,
        "what_this_looks_like": what_this_looks_like,
        "what_to_watch_next": what_to_watch_next,
    }


def _build_watchlist_first_language(
    *,
    watchlist_panel: Optional[Dict[str, Any]],
    setup_context: Dict[str, Any],
    memory_language: Dict[str, str],
) -> Dict[str, str]:
    watch = _build_watchlist_guidance(watchlist_panel)
    score_language = _build_score_language(
        watchlist_panel=watchlist_panel,
        setup_context=setup_context,
    )
    historical_operator_summary = setup_context.get("historical_operator_summary", "")
    historical_status = setup_context.get("historical_status", "")

    why_it_matters = _join_sentences(
        watch.get("summary", ""),
        score_language.get("score_summary", ""),
        "Recent memory context is strong, but that does not override governance"
        if memory_language.get("memory_strength") == "strong"
        else "",
        "Formal historical setup support remains limited"
        if historical_status == "not_available" or not setup_context.get("setup_detected")
        else "",
    )

    whats_been_happening = _join_sentences(
        memory_language.get("summary", ""),
        historical_operator_summary,
        score_language.get("score_implication", ""),
        "The formal historical detector did not produce a supported setup sample"
        if (historical_status == "not_available" and not historical_operator_summary)
        else "",
    )

    lead_shape = "This is an active lane with conditional expressions, not a statistically clean historical edge"
    support_shape = ""
    if watch["buy_symbols"] and watch["fade_symbols"]:
        support_shape = (
            f"Long ideas remain conditional in {watch['buy_symbols']}, while downside risk still points toward {watch['fade_symbols']}"
        )
    elif watch["buy_symbols"]:
        support_shape = f"Long ideas remain conditional in {watch['buy_symbols']}"
    elif watch["fade_symbols"]:
        support_shape = f"Downside risk still points toward {watch['fade_symbols']}"
    elif watch["avoid_symbols"]:
        support_shape = f"Avoid names with no clear edge still include {watch['avoid_symbols']}"

    what_this_looks_like = _join_sentences(
        lead_shape,
        score_language.get("score_summary", ""),
        support_shape,
    )

    if watch["buy_symbols"] and watch["fade_symbols"] and watch["driver_symbols"]:
        what_to_watch_next = _join_sentences(
            f"Only treat {watch['buy_symbols']} as actionable if the lane keeps confirming",
            f"If momentum fails, shift focus toward {watch['fade_symbols']}",
            f"Use {watch['driver_symbols']} as the confirmation gate",
        )
    elif watch["driver_symbols"]:
        what_to_watch_next = _join_sentences(
            "Watch whether the active lane keeps confirming",
            f"Use {watch['driver_symbols']} as the confirmation gate before treating any expression as actionable",
        )
    else:
        what_to_watch_next = _join_sentences(
            "Watch whether the active lane keeps confirming",
            "Do not treat listed expressions as actionable until the lane strengthens",
        )

    return {
        "why_it_matters_refined": why_it_matters,
        "whats_been_happening": whats_been_happening,
        "what_this_looks_like": what_this_looks_like,
        "what_to_watch_next": what_to_watch_next,
    }


def _build_posture_text(
    *,
    governance_panel: Dict[str, Any],
    watchlist_panel: Optional[Dict[str, Any]],
) -> str:
    approval_required = _safe_bool(governance_panel.get("approval_required"), True)
    execution_allowed = _safe_bool(governance_panel.get("execution_allowed"), False)

    watch = _build_watchlist_guidance(watchlist_panel)

    return _join_sentences(
        watch.get("posture_phrase", ""),
        "This remains advisory-only. Approval is required. Execution is not allowed."
        if approval_required and not execution_allowed
        else "This remains governed. Follow the visible approval and execution controls.",
    )


def _build_deterministic_explanation(payload: Dict[str, Any]) -> Dict[str, Any]:
    current_case = _extract_current_case(payload)
    governance_panel = (
        _safe_dict(current_case.get("governance_panel"))
        or _safe_dict(payload.get("governance_panel"))
    )

    symbol = _extract_symbol(current_case) or "This case"
    headline = _extract_headline(current_case)
    price_change_pct = _extract_price_change_pct(current_case)
    confirmation = _extract_confirmation(current_case)

    labeled_outcomes_panel = _extract_labeled_outcomes_panel(payload)
    setup_context = _extract_setup_context(payload)
    watchlist_panel = _extract_watchlist_panel(payload)
    external_memory_packet = _extract_external_memory_packet(payload)
    memory_language = _build_memory_language(external_memory_packet)
    watch = _build_watchlist_guidance(watchlist_panel)

    if watch["summary"]:
        what_to_watch = watch["summary"]
    elif price_change_pct is None:
        what_to_watch = f"{symbol} is active on a {confirmation or 'current'} signal."
    else:
        sign = "+" if price_change_pct >= 0 else ""
        what_to_watch = f"{symbol} is at {sign}{price_change_pct:.1f}% on a {confirmation or 'current'} signal."

    why_it_matters = (
        f"The system produced a governed advisory around the current headline: {headline}."
        if headline
        else "The system produced a governed advisory around the current case."
    )

    if labeled_outcomes_panel:
        refined = _build_refined_historical_language(
            labeled_outcomes_panel=labeled_outcomes_panel,
            setup_context=setup_context,
            watchlist_panel=watchlist_panel,
            memory_language=memory_language,
        )
        if refined.get("why_it_matters_refined"):
            why_it_matters = refined["why_it_matters_refined"]
        whats_been_happening = refined["whats_been_happening"]
        what_this_looks_like = refined["what_this_looks_like"]
        what_to_watch_next = refined["what_to_watch_next"]
    elif watchlist_panel or memory_language.get("memory_strength") != "absent":
        refined = _build_watchlist_first_language(
            watchlist_panel=watchlist_panel,
            setup_context=setup_context,
            memory_language=memory_language,
        )
        if refined.get("why_it_matters_refined"):
            why_it_matters = refined["why_it_matters_refined"]
        whats_been_happening = refined["whats_been_happening"] or "Recent memory context is present but still bounded."
        what_this_looks_like = refined["what_this_looks_like"] or "This case remains conditional rather than statistically clean."
        what_to_watch_next = refined["what_to_watch_next"]
    else:
        whats_been_happening = "Historical context is not strong enough to summarize confidently."
        what_this_looks_like = "This case does not yet have a strong historical edge."
        what_to_watch_next = (
            f"Watch whether {symbol} continues to confirm the current read. If confirmation weakens, treat the case more cautiously."
        )

    posture = _build_posture_text(
        governance_panel=governance_panel,
        watchlist_panel=watchlist_panel,
    )

    approval_required = _safe_bool(governance_panel.get("approval_required"), True)
    execution_allowed = _safe_bool(governance_panel.get("execution_allowed"), False)

    return {
        "what_to_watch": _split_sentences_decimal_safe(what_to_watch),
        "why_it_matters": _split_sentences_decimal_safe(why_it_matters),
        "whats_been_happening": _split_sentences_decimal_safe(whats_been_happening),
        "what_this_looks_like": _split_sentences_decimal_safe(what_this_looks_like),
        "what_to_watch_next": _split_sentences_decimal_safe(what_to_watch_next),
        "posture": _split_sentences_decimal_safe(posture),
        "advisory_only": True,
        "approval_required": approval_required,
        "execution_allowed": execution_allowed,
        "fallback_used": False,
        "source": "deterministic_formal_watchlist_truth",
    }


def _build_openai_prompt(payload: Dict[str, Any], deterministic: Dict[str, Any]) -> str:
    current_case = _extract_current_case(payload)
    labeled_outcomes_panel = _extract_labeled_outcomes_panel(payload)
    watchlist_panel = _extract_watchlist_panel(payload)
    external_memory_packet = _extract_external_memory_packet(payload)
    model = _extract_watchlist_model(watchlist_panel)

    symbol = _extract_symbol(current_case)
    headline = _extract_headline(current_case)
    price_change_pct = _extract_price_change_pct(current_case)
    confirmation = _extract_confirmation(current_case)

    allowed_historical_text = ""
    if labeled_outcomes_panel:
        allowed_historical_text = (
            f"Labeled outcomes summary: {labeled_outcomes_panel.get('operator_summary', '')}\n"
            f"Why user should care: {labeled_outcomes_panel.get('why_user_should_care', '')}\n"
            f"Edge class: {labeled_outcomes_panel.get('edge_class', '')}\n"
        )

    allowed_watchlist_text = ""
    if watchlist_panel:
        buckets = _safe_dict(watchlist_panel.get("buckets"))
        allowed_watchlist_text = (
            f"Buy bucket symbols: {_symbols_from_bucket(_safe_list(buckets.get('buy')))}\n"
            f"Avoid bucket symbols: {_symbols_from_bucket(_safe_list(buckets.get('avoid')))}\n"
            f"Fade bucket symbols: {_symbols_from_bucket(_safe_list(buckets.get('fade')))}\n"
            f"Driver symbols: {_symbols_from_bucket(_safe_list(buckets.get('driver')), limit=3)}\n"
            f"Watchlist summary: {watchlist_panel.get('summary', '')}\n"
            f"Watchlist posture label: {watchlist_panel.get('posture_label', '')}\n"
            f"No trade reason: {_safe_dict(watchlist_panel.get('no_trade_state')).get('reason', '')}\n"
            f"Formal score: {model.get('formal_score', '')}\n"
            f"Formal classification: {model.get('formal_classification', '')}\n"
            f"Confidence: {model.get('confidence', '')}\n"
            f"Adjusted historical edge: {model.get('historical_edge_adjusted', '')}\n"
            f"Setup multiplier: {model.get('setup_multiplier', '')}\n"
        )

    allowed_memory_text = ""
    if external_memory_packet:
        advisory_summary = _safe_dict(external_memory_packet.get("advisory_summary"))
        allowed_memory_text = (
            f"External memory advisory posture: {external_memory_packet.get('advisory_posture', '')}\n"
            f"External memory decision: {advisory_summary.get('decision', '')}\n"
            f"External memory record_count: {advisory_summary.get('record_count', '')}\n"
            f"External memory coherence_flags: {advisory_summary.get('coherence_flags', [])}\n"
        )

    return f"""
You are writing a bounded operator explanation for AI_GO.

Rules:
- Do not invent facts.
- Do not introduce causes, patterns, or confidence not present in the provided structured truth.
- If structured historical text is provided, preserve its meaning.
- If watchlist guidance is provided, use it only as conditional trade guidance, never as execution permission.
- Keep the distinction between recent memory strength and formal historical setup strength.
- Keep the distinction between formal score, posture label, and governance status.
- Prefer one lead sentence and one support sentence over long chained lists.
- Do not mutate governance posture.
- Be concise, plain-English, and operator-facing.
- Never imply execution is allowed when it is not.

Current case:
- symbol: {symbol}
- headline: {headline}
- price_change_pct: {price_change_pct}
- confirmation: {confirmation}

Deterministic explanation baseline:
- what_to_watch: {deterministic.get('what_to_watch', '')}
- why_it_matters: {deterministic.get('why_it_matters', '')}
- whats_been_happening: {deterministic.get('whats_been_happening', '')}
- what_this_looks_like: {deterministic.get('what_this_looks_like', '')}
- what_to_watch_next: {deterministic.get('what_to_watch_next', '')}
- posture: {deterministic.get('posture', '')}

{allowed_historical_text}
{allowed_watchlist_text}
{allowed_memory_text}

Return JSON with exactly these keys:
what_to_watch
why_it_matters
whats_been_happening
what_this_looks_like
what_to_watch_next
posture
""".strip()


def _validate_openai_result(candidate: Dict[str, Any], deterministic: Dict[str, Any]) -> bool:
    required_keys = [
        "what_to_watch",
        "why_it_matters",
        "whats_been_happening",
        "what_this_looks_like",
        "what_to_watch_next",
        "posture",
    ]

    if not isinstance(candidate, dict):
        return False

    for key in required_keys:
        value = candidate.get(key)
        if not isinstance(value, str) or not value.strip():
            return False

    posture_text = candidate.get("posture", "").lower()
    if "execution is not allowed" not in posture_text and "approval" not in posture_text:
        return False

    det_next = deterministic.get("what_to_watch_next", "").lower()
    cand_next = candidate.get("what_to_watch_next", "").lower()
    tracked_tokens = ["eog", "oxy", "slb", "xle", "mro", "apa", "cl", "uso", "driver"]
    if any(token in det_next for token in tracked_tokens):
        if not any(token in cand_next for token in tracked_tokens):
            return False

    return True


def generate_operator_explanation(payload: Dict[str, Any]) -> Dict[str, Any]:
    deterministic = _build_deterministic_explanation(payload)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return deterministic

    try:
        from openai import OpenAI
    except Exception:
        return deterministic

    try:
        client = OpenAI(api_key=api_key)
        prompt = _build_openai_prompt(payload, deterministic)

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "operator_explanation",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "what_to_watch": {"type": "string"},
                            "why_it_matters": {"type": "string"},
                            "whats_been_happening": {"type": "string"},
                            "what_this_looks_like": {"type": "string"},
                            "what_to_watch_next": {"type": "string"},
                            "posture": {"type": "string"},
                        },
                        "required": [
                            "what_to_watch",
                            "why_it_matters",
                            "whats_been_happening",
                            "what_this_looks_like",
                            "what_to_watch_next",
                            "posture",
                        ],
                    },
                }
            },
        )

        parsed = None
        if hasattr(response, "output_parsed") and response.output_parsed:
            parsed = response.output_parsed
        elif hasattr(response, "output_text") and response.output_text:
            import json
            parsed = json.loads(response.output_text)

        if not _validate_openai_result(parsed, deterministic):
            return deterministic

        parsed["advisory_only"] = True
        parsed["approval_required"] = deterministic["approval_required"]
        parsed["execution_allowed"] = deterministic["execution_allowed"]
        parsed["fallback_used"] = False
        parsed["source"] = "openai_bounded_paraphrase"
        return parsed

    except Exception:
        return deterministic
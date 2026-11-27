"""The R1 targets and the rule that judges them. See docs/r1-preregistration.md.

The numbers here are the registered ones. Checking a report never edits them, and a miss is a result.
"""
from __future__ import annotations

TARGETS = {"hit_rate": 0.90, "mean_recall": 0.80, "precision_likely": 0.60,
           "right_in_likely": 0.95, "wrong_in_also_check": 0.85}
LITERAL_PRECISION_TARGET = 0.60   # the same 60%, read on the full list of up to 8 pages
MIN_EVENTS = 60                   # below this a corpus is reported but not counted
CORPORA = ("Hugging Face Hub docs", "OpenBB docs", "Prometheus docs", "GOV.UK service manual")
GAIN_TOP3 = 0.02                  # a pass is kept for a corpus on +2 points in the top 3 ...
GAIN_MRR = 0.02                   # ... or +0.02 in mean reciprocal rank
_EPS = 1e-9


def _measure(value, target) -> dict:
    return {"value": value, "target": target, "met": value is not None and value + _EPS >= target}


def check(report: dict) -> dict:
    """One corpus, newer half only. Hit rate and recall come from the summary, the rest from the triage step."""
    events = report["summary"]["overall"]["events"]
    if events < MIN_EVENTS:
        return {"status": "too few events", "events": events, "all_met": None, "measures": {}}
    newer = report["summary"]["by_period"]["newer half"]
    triage = report["triage_step"]["by_period"]["newer half"]
    measures = {name: _measure((newer if name in ("hit_rate", "mean_recall") else triage).get(name), target)
                for name, target in TARGETS.items()}
    return {"status": "evaluated", "events": events, "all_met": all(m["met"] for m in measures.values()),
            "measures": measures,
            "literal_precision_full_list": _measure(triage.get("precision_full_list"), LITERAL_PRECISION_TARGET)}


def release_verdict(reports: dict[str, dict]) -> dict:
    """Every corpus must meet every target. True, False, or None when nothing missed but some corpus had too few events."""
    corpora = {name: check(report) for name, report in reports.items()}
    flags = [c["all_met"] for c in corpora.values()]
    passed = False if False in flags else (None if None in flags else True)
    return {"passed": passed, "corpora": corpora}


def pass_gain(before: dict, after: dict) -> dict:
    hit = round(after["top_3_hit"] - before["top_3_hit"], 3)
    mrr = round(after["mrr"] - before["mrr"], 3)
    return {"hit_at_3_gain": hit, "mrr_gain": mrr, "kept": hit + _EPS >= GAIN_TOP3 or mrr + _EPS >= GAIN_MRR}


def pass_scope(kept_by_corpus: dict[str, bool]) -> str:
    kept = sum(kept_by_corpus.values())
    return "kept" if kept >= 3 else "removed" if kept == 0 else "corpus-dependent"

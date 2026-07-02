"""Unit tests for Business Intelligence platform."""

import pytest

from app.domain.bi.metrics import BI_METRIC_CATALOG, BI_NAMESPACES, SYSTEM_REPORT_TEMPLATES


@pytest.mark.unit
def test_bi_metric_catalog_namespaces():
    assert "revenue" in BI_NAMESPACES
    assert "ai_cost" in BI_NAMESPACES
    assert "retention" in BI_NAMESPACES
    assert "growth" in BI_NAMESPACES


@pytest.mark.unit
def test_bi_metric_catalog_keys():
    assert "mrr_cents" in BI_METRIC_CATALOG["revenue"]
    assert "total_cost_usd" in BI_METRIC_CATALOG["ai_cost"]
    assert "seat_utilization_pct" not in BI_METRIC_CATALOG["usage"]  # computed KPI


@pytest.mark.unit
def test_system_report_templates():
    types = {t["report_type"] for t in SYSTEM_REPORT_TEMPLATES}
    assert "executive" in types
    assert "revenue" in types
    assert "usage" in types

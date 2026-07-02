"""Unit tests for enterprise workflow automation."""

import pytest

from app.domain.workflow.conditions import evaluate_condition
from app.domain.workflow.context import WorkflowContext


@pytest.mark.unit
def test_condition_field_presence():
    ctx = WorkflowContext(topic="test", project_id=1)
    ctx.script_text = "hello"
    assert evaluate_condition("script", ctx) is True
    assert evaluate_condition("research", ctx) is False


@pytest.mark.unit
def test_condition_negation_and_compound():
    ctx = WorkflowContext(topic="match day highlights", project_id=1)
    ctx.research_text = "data"
    ctx.script_text = "script"
    assert evaluate_condition("!video", ctx) is True
    assert evaluate_condition("research && script", ctx) is True
    assert evaluate_condition("research || video", ctx) is True
    assert evaluate_condition("topic=highlights", ctx) is True


@pytest.mark.unit
def test_condition_topic_equality():
    ctx = WorkflowContext(topic="Champions League Final", project_id=1)
    assert evaluate_condition("topic=champions", ctx) is True
    assert evaluate_condition("topic=nba", ctx) is False

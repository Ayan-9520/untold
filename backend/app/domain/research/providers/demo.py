"""Demo research provider — rich structured output without external APIs."""

from datetime import datetime, timedelta, timezone

from app.domain.research.types import ResearchAgentRequest, ResearchAgentResult
from app.domain.research.providers.base import ResearchProvider


class DemoResearchProvider(ResearchProvider):
    id = "demo"
    label = "Demo Research Agent"

    def is_available(self) -> bool:
        return True

    def research(self, request: ResearchAgentRequest) -> ResearchAgentResult:
        topic = request.topic or "Untitled topic"
        prompt = request.prompt.strip()
        base_year = 2010

        statistics = [
            {"label": "Career span (years)", "value": "18", "source": "Public records", "confidence": 0.92},
            {"label": "Documented awards", "value": "24+", "source": "Official federation data", "confidence": 0.88},
            {"label": "Archive footage hours", "value": "120+", "source": "Broadcast partners", "confidence": 0.75},
        ]
        public_facts = [
            {"fact": f"{topic} has extensive publicly documented career milestones.", "source": "Wikipedia / official bios", "verified": True},
            {"fact": "Primary statistics are published by governing bodies and reputable sports archives.", "source": "Public domain", "verified": True},
            {"fact": "Interview transcripts from major outlets are available for cross-reference.", "source": "Press archives", "verified": False},
        ]
        now = datetime.now(timezone.utc)
        timeline_events = [
            {"title": "Early career breakthrough", "event_date": (now - timedelta(days=365 * 8)).isoformat(), "description": "First major international recognition", "event_type": "milestone"},
            {"title": "Peak performance period", "event_date": (now - timedelta(days=365 * 4)).isoformat(), "description": "Dominant era with multiple titles", "event_type": "achievement"},
            {"title": "Legacy-defining moment", "event_date": (now - timedelta(days=365 * 2)).isoformat(), "description": "Cultural impact beyond sport", "event_type": "key_event"},
        ]
        follow_ups = [
            f"What primary sources confirm the central claim about {topic}?",
            "Who are the three most credible independent experts to interview?",
            "Which statistics have conflicting reports across outlets?",
            "What archival footage rights are publicly licensable?",
        ]
        suggestions = [
            "Cross-reference at least three independent sources per major claim",
            "Add timeline milestones with exact dates from primary records",
            "Flag any statistic lacking an official citation for fact-check",
        ]
        summary = (
            f"## Research brief: {topic}\n\n"
            f"**Focus:** {prompt or 'General documentary research'}\n\n"
            f"Publicly available material supports a narrative arc from early career through peak achievement "
            f"to lasting cultural legacy. Prioritize verified statistics, licensed archival footage, and "
            f"on-record interviews. Conflicting narratives should be documented with source credibility scores.\n\n"
            f"**Recommended next steps:** gather federation statistics, map timeline to primary dates, "
            f"and queue fact-checks for any claim below 85% source confidence."
        )

        action = request.action
        result = ResearchAgentResult(provider=self.id, meta={"action": action, "simulated": True})

        if action in ("full_research", "summary"):
            result.summary = summary
            result.suggestions = suggestions
        if action in ("full_research", "follow_up"):
            result.follow_up_questions = follow_ups
        if action in ("full_research", "statistics"):
            result.statistics = statistics
        if action in ("full_research", "public_facts"):
            result.public_facts = public_facts
        if action in ("full_research", "timeline"):
            result.timeline_events = timeline_events
        if action == "fact_check":
            result.fact_check_hints = [
                {"claim": prompt or "Central narrative claim", "status": "needs_review", "notes": "Verify against 2+ primary sources"},
            ]
            result.summary = f"Fact-check guidance for: {prompt}"

        if not result.summary and action != "fact_check":
            result.summary = summary

        return result

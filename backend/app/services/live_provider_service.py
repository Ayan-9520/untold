"""Sports API adapters — SportMonks, Sportradar, CricAPI."""

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.live import LiveEventType, LiveProvider, LiveSport, MatchStatus

logger = logging.getLogger("untold")
settings = get_settings()

SUPPORTED_PROVIDERS = ["sportmonks", "sportradar", "cricapi"]

THUMBNAILS = {
    LiveSport.CRICKET: "https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80",
    LiveSport.FOOTBALL: "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80",
    LiveSport.TENNIS: "https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=1200&q=80",
    LiveSport.FORMULA_1: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=80",
}


def infer_event_type(text: str, sport: LiveSport) -> LiveEventType:
    lower = text.lower()
    if any(w in lower for w in ("goal", "scores", "equalizer")):
        return LiveEventType.GOAL
    if any(w in lower for w in ("wicket", "bowled", "caught", "lbw")):
        return LiveEventType.WICKET
    if "six" in lower:
        return LiveEventType.SIX
    if any(w in lower for w in ("four", "boundary")):
        return LiveEventType.BOUNDARY
    if "lap" in lower or sport == LiveSport.FORMULA_1:
        return LiveEventType.LAP
    if "point" in lower or sport == LiveSport.TENNIS:
        return LiveEventType.POINT
    if any(w in lower for w in ("incident", "crash", "penalty")):
        return LiveEventType.INCIDENT
    return LiveEventType.DEFAULT


class LiveProviderService:
    @staticmethod
    def fetch_all_live() -> list[dict[str, Any]]:
        matches: list[dict] = []
        matches.extend(LiveProviderService.fetch_cricapi())
        matches.extend(LiveProviderService.fetch_sportmonks())
        matches.extend(LiveProviderService.fetch_sportradar())
        return matches

    @staticmethod
    def fetch_cricapi() -> list[dict]:
        if not settings.cricapi_api_key:
            return []
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(
                    "https://api.cricapi.com/v1/currentMatches",
                    params={"apikey": settings.cricapi_api_key, "offset": 0},
                )
                response.raise_for_status()
                data = response.json().get("data", [])
        except Exception as exc:
            logger.warning("CricAPI fetch failed: %s", exc)
            return []

        results = []
        for m in data:
            teams = m.get("teams", ["Team A", "Team B"])
            home, away = teams[0], teams[1] if len(teams) > 1 else "TBD"
            score = m.get("score", [])
            display = m.get("status", "Live")
            if score:
                display = " | ".join(str(s) for s in score[:2])

            results.append(
                {
                    "external_id": str(m.get("id", "")),
                    "provider": LiveProvider.CRICAPI,
                    "sport": LiveSport.CRICKET,
                    "event_name": m.get("name", f"{home} vs {away}"),
                    "team_home": home,
                    "team_away": away,
                    "score_home": display.split("|")[0].strip() if "|" in display else display,
                    "score_away": display.split("|")[1].strip() if "|" in display else None,
                    "score_display": display,
                    "status": MatchStatus.LIVE if "won" not in m.get("status", "").lower() else MatchStatus.COMPLETED,
                    "timer": m.get("status", "Live"),
                    "league": m.get("matchType", "Cricket"),
                    "thumbnail_url": THUMBNAILS[LiveSport.CRICKET],
                    "events": [],
                }
            )
        return results

    @staticmethod
    def fetch_sportmonks() -> list[dict]:
        if not settings.sportmonks_api_key:
            return []
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(
                    "https://api.sportmonks.com/v3/football/livescores/inplay",
                    params={"api_token": settings.sportmonks_api_key},
                )
                response.raise_for_status()
                data = response.json().get("data", [])
        except Exception as exc:
            logger.warning("SportMonks fetch failed: %s", exc)
            return []

        results = []
        for m in data:
            participants = m.get("participants", [])
            home = next((p["name"] for p in participants if p.get("meta", {}).get("location") == "home"), "Home")
            away = next((p["name"] for p in participants if p.get("meta", {}).get("location") == "away"), "Away")
            scores = m.get("scores", [])
            home_score = next((s.get("score", {}).get("goals", 0) for s in scores if s.get("description") == "CURRENT"), 0)
            away_score = home_score
            display = f"{home_score} - {away_score}"

            results.append(
                {
                    "external_id": str(m.get("id", "")),
                    "provider": LiveProvider.SPORTMONKS,
                    "sport": LiveSport.FOOTBALL,
                    "event_name": f"{home} vs {away}",
                    "team_home": home,
                    "team_away": away,
                    "score_home": str(home_score),
                    "score_away": str(away_score),
                    "score_display": display,
                    "status": MatchStatus.LIVE,
                    "timer": f"{m.get('periods', [{}])[-1].get('minutes', 0)}'",
                    "league": m.get("league", {}).get("name", "Football"),
                    "thumbnail_url": THUMBNAILS[LiveSport.FOOTBALL],
                    "events": [],
                }
            )
        return results

    @staticmethod
    def fetch_sportradar() -> list[dict]:
        if not settings.sportradar_api_key:
            return []
        results = []
        endpoints = [
            ("https://api.sportradar.com/soccer/trial/v4/en/schedules/live/summaries.json", LiveSport.FOOTBALL),
        ]
        for url, sport in endpoints:
            try:
                with httpx.Client(timeout=20) as client:
                    response = client.get(url, params={"api_key": settings.sportradar_api_key})
                    response.raise_for_status()
                    payload = response.json()
            except Exception as exc:
                logger.warning("Sportradar fetch failed (%s): %s", sport.value, exc)
                continue

            for summary in payload.get("summaries", []):
                event = summary.get("sport_event", {})
                status = summary.get("sport_event_status", {})
                competitors = event.get("competitors", [])
                home = competitors[0].get("name", "Home") if competitors else "Home"
                away = competitors[1].get("name", "Away") if len(competitors) > 1 else "Away"
                hs = status.get("home_score", 0)
                aws = status.get("away_score", 0)

                results.append(
                    {
                        "external_id": event.get("id", ""),
                        "provider": LiveProvider.SPORTRADAR,
                        "sport": sport,
                        "event_name": f"{home} vs {away}",
                        "team_home": home,
                        "team_away": away,
                        "score_home": str(hs),
                        "score_away": str(aws),
                        "score_display": f"{hs} - {aws}",
                        "status": MatchStatus.LIVE,
                        "timer": status.get("match_status", "Live"),
                        "league": event.get("sport_event_context", {}).get("competition", {}).get("name", ""),
                        "thumbnail_url": THUMBNAILS.get(sport, THUMBNAILS[LiveSport.FOOTBALL]),
                        "events": [],
                    }
                )
        return results

    @staticmethod
    def parse_webhook(provider: str, payload: dict) -> dict | None:
        event = payload.get("event", payload)
        raw = event.get("raw") or event.get("text") or event.get("description", "")
        if not raw:
            return None

        sport_map = {
            "cricapi": LiveSport.CRICKET,
            "sportmonks": LiveSport.FOOTBALL,
            "sportradar": LiveSport.FOOTBALL,
        }
        sport = sport_map.get(provider, LiveSport.FOOTBALL)
        event_type_str = event.get("type", "default")

        try:
            event_type = LiveEventType(event_type_str)
        except ValueError:
            event_type = infer_event_type(raw, sport)

        return {
            "external_id": event.get("id") or event.get("external_id"),
            "match_external_id": payload.get("match_external_id") or event.get("match_id"),
            "event_type": event_type,
            "raw_text": raw,
            "minute_or_over": event.get("minute") or event.get("over"),
            "occurred_at": datetime.now(timezone.utc),
        }

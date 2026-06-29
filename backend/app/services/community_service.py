"""Fan community — Fan Wars, Predictions, Fan DNA, Debates."""

from datetime import datetime, timezone

FAN_DNA = {
    "passion_level": 95,
    "debate_index": 88,
    "loyalty_score": 92,
    "badge": "Elite Fan",
    "personality": "Dangerous Debater",
    "sports_twin": "MS Dhoni",
    "sports_twin_match": 94,
    "traits": ["Clutch Thinker", "Calm Under Pressure", "Finisher Mentality"],
}

DEBATES = [
    {
        "id": "messi-ronaldo",
        "title": "Messi vs Ronaldo",
        "sport": "Football",
        "option_a": {"id": "messi", "label": "Messi", "votes": 12480},
        "option_b": {"id": "ronaldo", "label": "Ronaldo", "votes": 11820},
    },
    {
        "id": "kohli-dhoni",
        "title": "Kohli vs Dhoni",
        "sport": "Cricket",
        "option_a": {"id": "kohli", "label": "Kohli", "votes": 8920},
        "option_b": {"id": "dhoni", "label": "Dhoni", "votes": 10240},
    },
]

FAN_WARS = [
    {
        "id": "ind-pak",
        "title": "India vs Pakistan",
        "sport": "Cricket",
        "team_a": {"id": "india", "name": "India", "votes": 45200},
        "team_b": {"id": "pakistan", "name": "Pakistan", "votes": 41800},
        "status": "live",
    },
    {
        "id": "rcb-csk",
        "title": "RCB vs CSK",
        "sport": "IPL",
        "team_a": {"id": "rcb", "name": "RCB", "votes": 28400},
        "team_b": {"id": "csk", "name": "CSK", "votes": 31200},
        "status": "live",
    },
]

PREDICTION_EVENTS = [
    {
        "id": "pred-ipl-final",
        "title": "IPL 2026 Final",
        "sport": "Cricket",
        "closes_at": "2026-05-28T18:30:00Z",
        "pool": 125000,
        "rewards": {"coins": 500, "badge": "Oracle"},
    },
]

LEADERBOARD = [
    {"rank": 1, "name": "CricketKing_99", "points": 4820, "accuracy": 78},
    {"rank": 2, "name": "GoalMachine", "points": 4610, "accuracy": 76},
    {"rank": 3, "name": "DhoniFan_Mumbai", "points": 4390, "accuracy": 74},
]

_votes: dict[str, dict] = {}
_predictions: list[dict] = []


class CommunityService:
    @staticmethod
    def get_fan_dna(user_id: int | None = None) -> dict:
        return {
            "passionLevel": FAN_DNA["passion_level"],
            "debateIndex": FAN_DNA["debate_index"],
            "loyaltyScore": FAN_DNA["loyalty_score"],
            "badge": FAN_DNA["badge"],
            "personality": FAN_DNA["personality"],
            "sportsTwin": FAN_DNA["sports_twin"],
            "sportsTwinMatch": FAN_DNA["sports_twin_match"],
            "traits": FAN_DNA["traits"],
            "user_id": user_id,
        }

    @staticmethod
    def get_debates() -> list[dict]:
        return DEBATES

    @staticmethod
    def get_fan_wars() -> list[dict]:
        return FAN_WARS

    @staticmethod
    def vote_fan_war(war_id: str, side: str, user_id: int | None = None) -> dict:
        key = f"{war_id}:{user_id or 'anon'}"
        _votes[key] = {"war_id": war_id, "side": side, "at": datetime.now(timezone.utc).isoformat()}
        for war in FAN_WARS:
            if war["id"] == war_id:
                if side in ("a", "team_a", war["team_a"]["id"]):
                    war["team_a"]["votes"] += 1
                else:
                    war["team_b"]["votes"] += 1
                break
        return {"ok": True, "war_id": war_id, "side": side}

    @staticmethod
    def get_predictions() -> dict:
        return {"events": PREDICTION_EVENTS, "leaderboard": LEADERBOARD}

    @staticmethod
    def submit_prediction(user_id: int | None, event_id: str, answers: dict) -> dict:
        entry = {
            "user_id": user_id,
            "event_id": event_id,
            "answers": answers,
            "points_earned": 50,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _predictions.append(entry)
        return entry

    @staticmethod
    def get_leaderboard() -> list[dict]:
        return LEADERBOARD

"""Fan community — Fan Wars, Predictions, Fan DNA, Debates (DB-backed votes)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import FanVote, Prediction, User

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
        "optionA": {"id": "messi", "label": "Messi", "votes": 0},
        "optionB": {"id": "ronaldo", "label": "Ronaldo", "votes": 0},
        "image": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=800&q=80",
    },
    {
        "id": "kohli-dhoni",
        "title": "Kohli vs Dhoni",
        "sport": "Cricket",
        "optionA": {"id": "kohli", "label": "Kohli", "votes": 0},
        "optionB": {"id": "dhoni", "label": "Dhoni", "votes": 0},
        "image": "https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=800&q=80",
    },
]

FAN_WARS = [
    {
        "id": "ind-pak",
        "title": "India vs Pakistan",
        "sport": "Cricket",
        "teamA": {"id": "india", "name": "India", "votes": 0},
        "teamB": {"id": "pakistan", "name": "Pakistan", "votes": 0},
        "status": "live",
    },
    {
        "id": "rcb-csk",
        "title": "RCB vs CSK",
        "sport": "IPL",
        "teamA": {"id": "rcb", "name": "RCB", "votes": 0},
        "teamB": {"id": "csk", "name": "CSK", "votes": 0},
        "status": "live",
    },
]

PREDICTION_EVENTS = [
    {
        "id": "pred-ipl-final",
        "title": "IPL 2026 Final",
        "sport": "Cricket",
        "closesAt": "2026-05-28T18:30:00Z",
        "pool": 125000,
        "rewards": {"coins": 500, "badge": "Oracle"},
    },
]


class CommunityService:
    @staticmethod
    def _vote_counts(db: Session, war_id: str) -> dict[str, int]:
        rows = db.query(FanVote.side, func.count(FanVote.id)).filter(FanVote.war_id == war_id).group_by(FanVote.side).all()
        return {side: count for side, count in rows}

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
    def get_debates(db: Session) -> list[dict]:
        items = []
        for debate in DEBATES:
            counts = CommunityService._vote_counts(db, debate["id"])
            option_a = {**debate["optionA"], "votes": counts.get(debate["optionA"]["id"], 0)}
            option_b = {**debate["optionB"], "votes": counts.get(debate["optionB"]["id"], 0)}
            items.append({**debate, "optionA": option_a, "optionB": option_b})
        return items

    @staticmethod
    def get_fan_wars(db: Session) -> list[dict]:
        items = []
        for war in FAN_WARS:
            counts = CommunityService._vote_counts(db, war["id"])
            team_a = {**war["teamA"], "votes": counts.get(war["teamA"]["id"], 0)}
            team_b = {**war["teamB"], "votes": counts.get(war["teamB"]["id"], 0)}
            items.append({**war, "teamA": team_a, "teamB": team_b})
        return items

    @staticmethod
    def vote_fan_war(db: Session, war_id: str, side: str, user_id: int | None = None) -> dict:
        normalized = side
        for war in FAN_WARS + [{"id": d["id"], "teamA": d["optionA"], "teamB": d["optionB"]} for d in DEBATES]:
            if war["id"] != war_id:
                continue
            if side in ("a", "team_a", "teamA"):
                normalized = war["teamA"]["id"]
            elif side in ("b", "team_b", "teamB"):
                normalized = war["teamB"]["id"]
            break

        db.add(FanVote(user_id=user_id, war_id=war_id, side=normalized))
        db.commit()
        return {"ok": True, "war_id": war_id, "side": normalized}

    @staticmethod
    def get_predictions(db: Session) -> dict:
        return {
            "events": PREDICTION_EVENTS,
            "leaderboard": CommunityService.get_leaderboard(db, user_id=None),
        }

    @staticmethod
    def submit_prediction(db: Session, user_id: int | None, event_id: str, answers: dict) -> dict:
        points = 50
        row = Prediction(
            user_id=user_id,
            event_id=event_id,
            answers_json=json.dumps(answers),
            points_earned=points,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "ok": True,
            "event_id": event_id,
            "points_earned": points,
            "created_at": row.created_at.isoformat() if row.created_at else datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def get_leaderboard(db: Session, user_id: int | None = None) -> list[dict]:
        rows = (
            db.query(
                Prediction.user_id,
                func.sum(Prediction.points_earned).label("points"),
                func.count(Prediction.id).label("predictions"),
            )
            .filter(Prediction.user_id.isnot(None))
            .group_by(Prediction.user_id)
            .order_by(func.sum(Prediction.points_earned).desc())
            .limit(20)
            .all()
        )

        leaderboard: list[dict] = []
        for rank, (uid, points, count) in enumerate(rows, start=1):
            user = db.query(User).filter(User.id == uid).first()
            name = user.full_name if user else f"Fan_{uid}"
            accuracy = min(99, 60 + (count % 20))
            leaderboard.append({
                "rank": rank,
                "name": name,
                "points": int(points or 0),
                "accuracy": accuracy,
                "isUser": user_id is not None and uid == user_id,
            })

        if not leaderboard:
            leaderboard = [
                {"rank": 1, "name": "CricketKing_99", "points": 4820, "accuracy": 78, "isUser": False},
                {"rank": 2, "name": "GoalMachine", "points": 4610, "accuracy": 76, "isUser": False},
                {"rank": 3, "name": "DhoniFan_Mumbai", "points": 4390, "accuracy": 74, "isUser": False},
            ]
        return leaderboard

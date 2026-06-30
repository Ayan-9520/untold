"""IP allow/deny rule evaluation."""

from __future__ import annotations

import ipaddress

from sqlalchemy.orm import Session

from app.models.studio_platform import EnterpriseIpRule


def ip_in_cidr(ip: str, cidr: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return False


def check_ip_access(db: Session, ip: str, scope: str = "studio") -> None:
    """Raise ForbiddenError if IP is denied or not in allowlist when allow rules exist."""
    from app.core.exceptions import ForbiddenError

    rules = (
        db.query(EnterpriseIpRule)
        .filter(EnterpriseIpRule.enabled.is_(True), EnterpriseIpRule.scope == scope)
        .all()
    )
    if not rules:
        return

    for rule in rules:
        if rule.rule_type == "deny" and ip_in_cidr(ip, rule.cidr):
            raise ForbiddenError(f"Access denied from IP {ip}")

    allow_rules = [r for r in rules if r.rule_type == "allow"]
    if allow_rules:
        if not any(ip_in_cidr(ip, r.cidr) for r in allow_rules):
            raise ForbiddenError(f"IP {ip} not in allowlist")

# Runbook: Incident Response

## Trigger

- `UntoldApiDown` alert firing
- `/ready` returning `not_ready`
- Elevated 5xx rate (> 5% for 5+ minutes)
- Security alert (unusual auth, key leak report)

## Roles

| Role | Responsibility |
|------|------------------|
| **Incident commander** | Coordinates response, communicates status |
| **Responder** | Investigates and applies fixes |
| **Comms** | Updates stakeholders |

## SEV-1 procedure

### 1. Acknowledge (0–5 min)

- Acknowledge alert in PagerDuty/Slack
- Open incident channel
- Assign incident commander

### 2. Assess (5–15 min)

```bash
curl -fsS https://api.yourdomain.com/health | jq .
kubectl get pods -n untold
kubectl top pods -n untold
```

Check Grafana dashboards:
- API request rate and error rate
- Postgres connections
- Redis memory
- Celery queue depth

### 3. Mitigate (15–60 min)

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| All pods CrashLoop | Bad deploy | [Rollback](./deployment-rollback.md) |
| DB down | Postgres failure | Failover managed DB; check `DATABASE_URL` |
| Redis down | Cache/broker outage | Restore Redis; API may 503 rate limits |
| High latency | Query load | Scale API replicas; check slow queries |
| 503 on gateway | Redis unavailable | Restore Redis (prod fails closed) |
| Celery backlog | Worker crash | Scale workers; check `celery inspect ping` |

### 4. Communicate

Template:

> **Incident:** [brief description]  
> **Impact:** [user-facing impact]  
> **Status:** Investigating / Mitigating / Resolved  
> **ETA:** [if known]

### 5. Resolve

- Confirm smoke tests pass
- Confirm alerts cleared
- Monitor 30 minutes

### 6. Post-incident (within 48h)

- Write incident report: timeline, root cause, action items
- Update runbooks if gaps found
- Create ADR if architectural change needed

## Security incident

If credential leak suspected:

1. Rotate `SECRET_KEY` (forces re-login) — plan downtime
2. Revoke API keys via `/studio/api-gateway`
3. Review `enterprise_audit_events`
4. Rotate `ENCRYPTION_KEY` only with data migration plan
5. Engage security team

## Related

- [Deployment Rollback](./deployment-rollback.md)
- [Backup & Restore](./backup-restore.md)

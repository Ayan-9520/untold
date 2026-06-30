"""Sample backend plugins — reference implementations."""

from __future__ import annotations

import logging
from typing import Any

from app.plugins.sdk import BasePlugin, PluginContext

logger = logging.getLogger(__name__)


class SlackNotifyPlugin(BasePlugin):
    """Posts workflow and publish events to a Slack webhook URL."""

    slug = "slack-notify"

    def on_event(self, ctx: PluginContext, event_name: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not ctx.has_permission("webhook.send"):
            return {"skipped": True, "reason": "missing webhook.send permission"}

        webhook_url = ctx.get_setting("webhook_url")
        if not webhook_url:
            return {"skipped": True, "reason": "webhook_url not configured"}

        channel = ctx.get_setting("channel", "#studio-alerts")
        message = self._format_message(event_name, payload)
        logger.info(
            "SlackNotifyPlugin dispatch slug=%s event=%s channel=%s message=%s",
            ctx.plugin_slug,
            event_name,
            channel,
            message[:200],
        )
        return {
            "dispatched": True,
            "channel": channel,
            "webhook_url": webhook_url[:32] + "...",
            "message_preview": message[:500],
        }

    def _format_message(self, event_name: str, payload: dict[str, Any]) -> str:
        if event_name == "workflow.run.finished":
            return f"Workflow run {payload.get('run_id')} finished with status: {payload.get('status')}"
        if event_name == "publish.completed":
            return f"Published to {payload.get('platform')} (job {payload.get('job_id')})"
        if event_name == "collab.comment.created":
            return f"New comment on project {payload.get('project_id')}"
        return f"Studio event: {event_name}"


class CustomSEOFormatterPlugin(BasePlugin):
    """Transforms SEO titles and descriptions via hook points."""

    slug = "custom-seo-formatter"

    def hook_seo_format_title(self, ctx: PluginContext, payload: dict[str, Any]) -> dict[str, Any]:
        title = payload.get("title") or ""
        prefix = ctx.get_setting("title_prefix", "")
        suffix = ctx.get_setting("title_suffix", " | UNTOLD")
        max_len = int(ctx.get_setting("max_title_length", 60))
        formatted = f"{prefix}{title}{suffix}".strip()
        if len(formatted) > max_len:
            formatted = formatted[: max_len - 3] + "..."
        return {"title": formatted}

    def hook_seo_format_description(self, ctx: PluginContext, payload: dict[str, Any]) -> dict[str, Any]:
        description = payload.get("description") or ""
        append = ctx.get_setting("description_append", "")
        if append and append not in description:
            description = f"{description} {append}".strip()
        return {"description": description}

    def on_hook(self, ctx: PluginContext, hook_name: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if hook_name == "seo.format_title":
            return self.hook_seo_format_title(ctx, payload)
        if hook_name == "seo.format_description":
            return self.hook_seo_format_description(ctx, payload)
        return None


BACKEND_PLUGIN_REGISTRY: dict[str, type[BasePlugin]] = {
    "slack-notify": SlackNotifyPlugin,
    "custom-seo-formatter": CustomSEOFormatterPlugin,
}

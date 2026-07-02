"""Graph workflow executor — DAG traversal with parallel, conditions, loops, approvals."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.studio.enums import ProjectStage
from app.domain.workflow.conditions import evaluate_condition
from app.domain.workflow.context import WorkflowContext
from app.domain.workflow.engine import WorkflowEngine
from app.domain.workflow.events import notify_workflow_event
from app.domain.workflow.graph import WorkflowGraph
from app.domain.workflow.logs import append_log
from app.domain.workflow.nodes import AGENT_NODE_TYPES, AGENT_TO_ENGINE_STEP
from app.domain.workflow.prompts import merge_prompts
from app.models.studio import Production
from app.models.studio_platform import ProductionPipelineRun, StudioNotification

logger = logging.getLogger("untold.workflow.executor")


def _run_plugin_hooks(db: Session, hook_name: str, payload: dict, user_id: int | None) -> dict:
    try:
        from app.domain.plugins.registry import PluginEventBus

        return PluginEventBus.run_hooks(db, hook_name, payload, user_id=user_id, commit=False)
    except Exception:
        logger.exception("Plugin hook %s failed", hook_name)
        return payload

class GraphExecutor:
    @staticmethod
    def _init_node_executions(graph: WorkflowGraph) -> dict:
        return {
            n.id: {"node_id": n.id, "type": n.type, "label": n.data.get("label") or n.type, "status": "pending"}
            for n in graph.nodes
        }

    @staticmethod
    def _progress(graph: WorkflowGraph, node_executions: dict) -> int:
        total = len(graph.nodes) or 1
        done = sum(1 for v in node_executions.values() if v.get("status") == "completed")
        return min(100, int(done / total * 100))

    @staticmethod
    def _update_node(node_executions: dict, node_id: str, **updates) -> None:
        entry = dict(node_executions.get(node_id) or {})
        entry.update(updates)
        node_executions[node_id] = entry

    @staticmethod
    def _run_with_retries(db: Session, run: ProductionPipelineRun, ctx: WorkflowContext, node, fn):
        attempts = max(0, node.retries) + 1
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                if node.timeout_seconds:
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        fut = pool.submit(fn)
                        return fut.result(timeout=node.timeout_seconds)
                return fn()
            except FuturesTimeoutError as exc:
                last_exc = TimeoutError(f"Node {node.id} timed out after {node.timeout_seconds}s")
                append_log(db, run.id, f"Node timeout (attempt {attempt}/{attempts}): {node.id}", level="warn", stage=node.type)
                db.commit()
            except Exception as exc:
                last_exc = exc
                append_log(db, run.id, f"Node failed (attempt {attempt}/{attempts}): {node.id} — {exc}", level="warn", stage=node.type)
                db.commit()
            if attempt < attempts:
                time.sleep(min(2 ** attempt, 30))
        raise last_exc or RuntimeError(f"Node {node.id} failed")

    @staticmethod
    def _should_pause(run: ProductionPipelineRun) -> bool:
        db_run = run
        return bool(db_run and db_run.status in ("cancelled", "pending_approval"))

    @staticmethod
    def _execute_agent(db: Session, run: ProductionPipelineRun, ctx: WorkflowContext, node):
        step_id = AGENT_TO_ENGINE_STEP.get(node.type, node.type)

        def _agent_call():
            return WorkflowEngine._run_agent(db, run, ctx, step_id)

        result = GraphExecutor._run_with_retries(db, run, ctx, node, _agent_call)
        WorkflowEngine._advance_project_stage(db, run.project_id, step_id)
        return result

    @staticmethod
    def _execute_node(
        db: Session,
        run: ProductionPipelineRun,
        ctx: WorkflowContext,
        graph: WorkflowGraph,
        node_id: str,
    ) -> None:
        run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run.id).first()
        if not run or run.status == "cancelled":
            return

        graph = WorkflowGraph.from_dict(run.graph_snapshot or graph.to_dict())
        node_map = graph.node_map()
        node = node_map.get(node_id)
        if not node:
            return

        node_executions = dict(run.node_executions or GraphExecutor._init_node_executions(graph))
        state = node_executions.get(node_id, {})
        if state.get("status") == "completed":
            for edge in graph.outgoing(node_id):
                GraphExecutor._execute_node(db, run, ctx, graph, edge.target)
            return

        now = datetime.now(timezone.utc).isoformat()
        GraphExecutor._update_node(node_executions, node_id, status="running", started_at=now)
        run.node_executions = node_executions
        run.current_stage = node_id
        run.progress = GraphExecutor._progress(graph, node_executions)
        append_log(db, run.id, f"Node started: {node.label} ({node.type})", level="info", stage=node.type, node_id=node_id)
        db.commit()
        notify_workflow_event(
            run.created_by_id,
            run_id=run.id,
            event="node_started",
            payload={"node_id": node_id, "type": node.type, "progress": run.progress},
        )

        hook_result = _run_plugin_hooks(
            db,
            "workflow.before_node",
            {"run_id": run.id, "node_id": node_id, "type": node.type, "context": {}},
            run.created_by_id,
        )
        if hook_result.get("skip"):
            GraphExecutor._update_node(node_executions, node_id, status="skipped", completed_at=now)
            run.node_executions = node_executions
            append_log(db, run.id, f"Node skipped by plugin hook: {node.label}", level="info", stage=node.type, node_id=node_id)
            db.commit()
            for edge in graph.outgoing(node_id):
                GraphExecutor._execute_node(db, run, ctx, graph, edge.target)
            return

        try:
            if node.type in AGENT_NODE_TYPES:
                result = GraphExecutor._execute_agent(db, run, ctx, node)
                GraphExecutor._update_node(
                    node_executions,
                    node_id,
                    generation_id=result.generation_id,
                    output_preview=result.output_preview,
                    result_url=result.result_url,
                )

            elif node.type == "approval":
                meta = dict(run.output_meta or {})
                meta["pending_node_id"] = node_id
                run.output_meta = meta
                run.requires_approval = True
                run.approval_status = "pending"
                run.status = "pending_approval"
                GraphExecutor._update_node(node_executions, node_id, status="pending_approval", completed_at=now)
                run.node_executions = node_executions
                append_log(db, run.id, "Approval gate — awaiting reviewer", level="warn", stage="approval")
                db.commit()
                notify_workflow_event(
                    run.created_by_id,
                    run_id=run.id,
                    event="approval_required",
                    payload={"node_id": node_id},
                )
                return

            elif node.type == "condition":
                branch = "true" if evaluate_condition(node.data.get("expression"), ctx) else "false"
                GraphExecutor._update_node(node_executions, node_id, status="completed", branch=branch, completed_at=now)
                run.node_executions = node_executions
                db.commit()
                for edge in graph.outgoing(node_id, branch):
                    GraphExecutor._execute_node(db, run, ctx, graph, edge.target)
                return

            elif node.type == "parallel":
                children = [graph.node_map()[e.target] for e in graph.outgoing(node_id)]
                if children:
                    import threading

                    from app.db.session import SessionLocal

                    ctx_lock = threading.Lock()

                    def _run_child(child_id: str) -> None:
                        child_db = SessionLocal()
                        try:
                            child_run = (
                                child_db.query(ProductionPipelineRun)
                                .filter(ProductionPipelineRun.id == run.id)
                                .first()
                            )
                            if not child_run:
                                return
                            with ctx_lock:
                                GraphExecutor._execute_node(child_db, child_run, ctx, graph, child_id)
                            child_db.commit()
                        finally:
                            child_db.close()

                    with ThreadPoolExecutor(max_workers=min(8, len(children))) as pool:
                        futures = [pool.submit(_run_child, c.id) for c in children]
                        for fut in futures:
                            fut.result()
                    run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run.id).first()
                    if run:
                        node_executions = dict(run.node_executions or node_executions)
                run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run.id).first()
                if GraphExecutor._should_pause(run):
                    return

            elif node.type == "loop":
                max_iter = int(node.data.get("max_iterations") or 3)
                until_field = (node.data.get("until_field") or "").strip().lower()
                body_edges = graph.outgoing(node_id)
                for iteration in range(1, max_iter + 1):
                    GraphExecutor._update_node(node_executions, node_id, iteration=iteration, status="running")
                    run.node_executions = node_executions
                    db.commit()
                    for edge in body_edges:
                        GraphExecutor._execute_node(db, run, ctx, graph, edge.target)
                    if until_field and evaluate_condition(until_field, ctx):
                        break
                    run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run.id).first()
                    if GraphExecutor._should_pause(run):
                        return

            elif node.type == "notification":
                title = node.data.get("title") or f"Workflow: {run.topic[:60]}"
                body = node.data.get("body") or f"Stage reached: {node.label}"
                notify_user = node.data.get("user_id") or run.created_by_id
                if notify_user:
                    db.add(
                        StudioNotification(
                            user_id=int(notify_user),
                            notification_type=node.data.get("notification_type") or "workflow_notification",
                            title=title,
                            body=body,
                            data={"pipeline_run_id": run.id, "node_id": node_id},
                        )
                    )
                append_log(db, run.id, f"Notification sent: {title}", level="info", stage="notification", node_id=node_id)

            elif node.type == "delay":
                delay_seconds = int(node.data.get("delay_seconds") or 0)
                if delay_seconds > 0:
                    append_log(db, run.id, f"Delay {delay_seconds}s", level="info", stage="delay")
                    db.commit()
                    time.sleep(delay_seconds)

            else:
                append_log(db, run.id, f"Skipped unknown control node: {node.type}", level="warn", stage=node.type)

            completed_at = datetime.now(timezone.utc).isoformat()
            GraphExecutor._update_node(node_executions, node_id, status="completed", completed_at=completed_at)
            run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run.id).first()
            if not run:
                return
            run.node_executions = node_executions
            run.progress = GraphExecutor._progress(graph, node_executions)
            append_log(db, run.id, f"Node completed: {node.label}", level="info", stage=node.type, node_id=node_id)
            db.commit()
            _run_plugin_hooks(
                db,
                "workflow.after_node",
                {"run_id": run.id, "node_id": node_id, "type": node.type, "output": node_executions.get(node_id, {})},
                run.created_by_id,
            )
            notify_workflow_event(
                run.created_by_id,
                run_id=run.id,
                event="node_completed",
                payload={"node_id": node_id, "type": node.type, "progress": run.progress},
            )
            try:
                from app.domain.plugins.registry import PluginEventBus

                PluginEventBus.emit(
                    db,
                    "workflow.node.completed",
                    {"run_id": run.id, "node_id": node_id, "output": {"type": node.type, "progress": run.progress}},
                    user_id=run.created_by_id,
                    commit=True,
                )
            except Exception:
                logger.exception("Plugin event dispatch failed for workflow.node.completed")

            for edge in graph.outgoing(node_id):
                GraphExecutor._execute_node(db, run, ctx, graph, edge.target)

        except Exception as exc:
            GraphExecutor._update_node(node_executions, node_id, status="failed", error=str(exc), completed_at=now)
            run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run.id).first()
            if run:
                run.node_executions = node_executions
                run.status = "failed"
                run.error_message = str(exc)
                run.completed_at = datetime.now(timezone.utc)
                append_log(db, run.id, f"Node failed: {node.id} — {exc}", level="error", stage=node.type)
                db.commit()
                notify_workflow_event(
                    run.created_by_id,
                    run_id=run.id,
                    event="run_failed",
                    payload={"node_id": node_id, "error": str(exc)},
                )
            raise

    @staticmethod
    def execute_run(db: Session, run_id: int) -> None:
        run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
        if not run or not run.graph_snapshot:
            WorkflowEngine.execute_run(db, run_id)
            return
        if run.status in ("cancelled", "completed", "failed"):
            return
        if run.requires_approval and run.approval_status != "approved" and run.status == "pending_approval":
            return

        graph = WorkflowGraph.from_dict(run.graph_snapshot)
        errors = graph.validate()
        if errors:
            run.status = "failed"
            run.error_message = "; ".join(errors)
            db.commit()
            return

        meta = dict(run.output_meta or {})
        ctx = WorkflowContext(
            topic=run.topic,
            project_id=run.project_id,
            providers=meta.get("providers") or {},
            publish_platforms=meta.get("publish_platforms") or ["originals", "youtube"],
            prompts=merge_prompts(meta.get("prompts")),
            translation_language=meta.get("translation_language"),
        )

        if not run.node_executions:
            run.node_executions = GraphExecutor._init_node_executions(graph)
        run.status = "running"
        if not run.started_at:
            run.started_at = datetime.now(timezone.utc)
        append_log(db, run_id, "Graph workflow engine running", level="info")
        db.commit()
        notify_workflow_event(run.created_by_id, run_id=run_id, event="run_started", payload={})
        try:
            from app.domain.plugins.registry import PluginEventBus

            PluginEventBus.emit(
                db,
                "workflow.run.started",
                {"run_id": run.id, "topic": run.topic, "project_id": run.project_id},
                user_id=run.created_by_id,
                commit=True,
            )
        except Exception:
            logger.exception("Plugin event dispatch failed for workflow.run.started")

        try:
            entries = graph.entry_nodes()
            if not entries:
                raise ValueError("Workflow has no entry nodes")

            resume_node = meta.get("resume_after_node")
            if resume_node:
                for edge in graph.outgoing(resume_node):
                    GraphExecutor._execute_node(db, run, ctx, graph, edge.target)
            else:
                for entry in entries:
                    GraphExecutor._execute_node(db, run, ctx, graph, entry.id)

            run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
            if not run or run.status in ("cancelled", "pending_approval", "failed"):
                return

            run.status = "completed"
            run.current_stage = "complete"
            run.progress = 100
            run.completed_at = datetime.now(timezone.utc)
            run.output_meta = {
                **meta,
                "research_preview": (ctx.research_text or "")[:500],
                "script_preview": (ctx.script_text or "")[:500],
                "translation_preview": (ctx.translation_text or "")[:500] if ctx.translation_text else None,
                "storyboard_scenes": len(ctx.storyboard_scenes),
                "image_url": ctx.image_url,
                "voice_url": ctx.voice_url,
                "video_url": ctx.video_url,
                "music_url": ctx.music_url,
                "seo_variants": ctx.seo_variants,
                "publish_run_id": ctx.publish_run_id,
                "analytics_summary": ctx.analytics_summary,
            }
            if run.project_id:
                project = db.query(Production).filter(Production.id == run.project_id).first()
                if project:
                    project.stage = ProjectStage.COMPLETED.value
            if run.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=run.created_by_id,
                        notification_type="workflow_complete",
                        title=f"Workflow complete — {run.topic[:80]}",
                        body="Graph workflow finished successfully",
                        data={"pipeline_run_id": run.id},
                    )
                )
            append_log(db, run_id, "Graph workflow completed successfully", level="info")
            db.commit()
            notify_workflow_event(run.created_by_id, run_id=run_id, event="run_completed", payload={"progress": 100})
            try:
                from app.domain.plugins.registry import PluginEventBus

                PluginEventBus.emit(
                    db,
                    "workflow.run.finished",
                    {
                        "run_id": run.id,
                        "status": "completed",
                        "project_id": run.project_id,
                        "definition_id": run.workflow_definition_id,
                    },
                    user_id=run.created_by_id,
                    commit=True,
                )
            except Exception:
                logger.exception("Plugin event dispatch failed for workflow.run.finished")

        except Exception:
            run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
            if run and run.status not in ("cancelled", "pending_approval"):
                run.status = "failed"
                run.completed_at = datetime.now(timezone.utc)
                db.commit()
            raise

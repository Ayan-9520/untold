"""Workflow graph model — nodes, edges, validation, execution order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.workflow.nodes import AGENT_NODE_TYPES, ALL_NODE_TYPES, CONTROL_NODE_TYPES


@dataclass
class WorkflowNode:
    id: str
    type: str
    position: dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def label(self) -> str:
        return self.data.get("label") or self.type

    @property
    def retries(self) -> int:
        return int(self.data.get("retries", 2))

    @property
    def timeout_seconds(self) -> int | None:
        val = self.data.get("timeout_seconds")
        return int(val) if val is not None else None


@dataclass
class WorkflowEdge:
    id: str
    source: str
    target: str
    source_handle: str = "default"
    target_handle: str = "in"


@dataclass
class WorkflowGraph:
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]
    viewport: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> WorkflowGraph:
        nodes = [
            WorkflowNode(
                id=n["id"],
                type=n["type"],
                position=n.get("position") or {"x": 0, "y": 0},
                data=n.get("data") or {},
            )
            for n in raw.get("nodes") or []
        ]
        edges = [
            WorkflowEdge(
                id=e["id"],
                source=e["source"],
                target=e["target"],
                source_handle=e.get("sourceHandle") or e.get("source_handle") or "default",
                target_handle=e.get("targetHandle") or e.get("target_handle") or "in",
            )
            for e in raw.get("edges") or []
        ]
        return cls(nodes=nodes, edges=edges, viewport=raw.get("viewport") or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type,
                    "position": n.position,
                    "data": n.data,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source,
                    "target": e.target,
                    "sourceHandle": e.source_handle,
                    "targetHandle": e.target_handle,
                }
                for e in self.edges
            ],
            "viewport": self.viewport,
        }

    def node_map(self) -> dict[str, WorkflowNode]:
        return {n.id: n for n in self.nodes}

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.nodes:
            errors.append("Workflow must contain at least one node")
            return errors

        ids = {n.id for n in self.nodes}
        for e in self.edges:
            if e.source not in ids:
                errors.append(f"Edge {e.id} references unknown source {e.source}")
            if e.target not in ids:
                errors.append(f"Edge {e.id} references unknown target {e.target}")

        for n in self.nodes:
            if n.type not in ALL_NODE_TYPES:
                errors.append(f"Unknown node type: {n.type}")

        # Cycle detection
        if self._has_cycle():
            errors.append("Workflow graph contains a cycle")

        return errors

    def _has_cycle(self) -> bool:
        adj: dict[str, list[str]] = {n.id: [] for n in self.nodes}
        for e in self.edges:
            adj[e.source].append(e.target)

        visited: set[str] = set()
        stack: set[str] = set()

        def dfs(node_id: str) -> bool:
            if node_id in stack:
                return True
            if node_id in visited:
                return False
            visited.add(node_id)
            stack.add(node_id)
            for nxt in adj.get(node_id, []):
                if dfs(nxt):
                    return True
            stack.remove(node_id)
            return False

        return any(dfs(n.id) for n in self.nodes)

    def entry_nodes(self) -> list[WorkflowNode]:
        """Nodes with no incoming edges."""
        targets = {e.target for e in self.edges}
        return [n for n in self.nodes if n.id not in targets]

    def outgoing(self, node_id: str, handle: str | None = None) -> list[WorkflowEdge]:
        result = [e for e in self.edges if e.source == node_id]
        if handle:
            result = [e for e in result if e.source_handle == handle]
        return result

    def execution_plan(self) -> list[list[str]]:
        """
        Topological levels. Nodes in the same level with a parallel parent
        are grouped for concurrent execution.
        """
        node_map = self.node_map()
        in_degree = {n.id: 0 for n in self.nodes}
        for e in self.edges:
            in_degree[e.target] = in_degree.get(e.target, 0) + 1

        levels: list[list[str]] = []
        ready = [n.id for n in self.nodes if in_degree[n.id] == 0]
        visited: set[str] = set()

        while ready:
            batch: list[str] = []
            next_ready: list[str] = []
            for node_id in ready:
                if node_id in visited:
                    continue
                visited.add(node_id)
                batch.append(node_id)
                node = node_map[node_id]
                out_edges = self.outgoing(node_id)
                if node.type == "parallel":
                    # All parallel branches form one concurrent group
                    for e in out_edges:
                        if e.target not in visited:
                            batch.append(e.target)
                            visited.add(e.target)
                            for e2 in self.edges:
                                if e2.source == e.target:
                                    in_degree[e2.target] -= 1
                                    if in_degree[e2.target] == 0:
                                        next_ready.append(e2.target)
                    continue
                for e in out_edges:
                    in_degree[e.target] -= 1
                    if in_degree[e.target] == 0:
                        next_ready.append(e.target)
            if batch:
                levels.append(batch)
            ready = list(dict.fromkeys(next_ready))

        return levels

"""
ToolRegistry — singleton registry for all tool instances.

Agents call ToolRegistry.get("jira") instead of importing
directly, enabling easy mock injection in tests and runtime
hot-swapping of implementations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from utils.logger import get_logger

if TYPE_CHECKING:
    from tools.base_tool import BaseTool

logger = get_logger("ToolRegistry")

_registry: Dict[str, "BaseTool"] = {}


class ToolRegistry:
    """Central store for named BaseTool instances."""

    @classmethod
    def register(cls, key: str, tool: "BaseTool") -> None:
        _registry[key] = tool
        logger.info(f"[ToolRegistry] Registered '{key}' → {tool.__class__.__name__}")

    @classmethod
    def get(cls, key: str) -> Optional["BaseTool"]:
        tool = _registry.get(key)
        if not tool:
            logger.warning(f"[ToolRegistry] '{key}' not found — returning None")
        return tool

    @classmethod
    def list_tools(cls) -> dict:
        return {k: v.describe() for k, v in _registry.items()}

    @classmethod
    def bootstrap(cls) -> None:
        """
        Instantiate all tools from environment config.
        Call exactly ONCE at application startup.
        """
        import os

        from tools.jenkins_tool import JenkinsTool
        from tools.jira_tool import JiraTool
        from tools.grafana_tool import GrafanaTool

        cls.register(
            "jenkins",
            JenkinsTool(base_url=os.getenv("JENKINS_URL", "")),
        )
        cls.register(
            "jira",
            JiraTool(
                url=os.getenv("JIRA_URL", ""),
                user=os.getenv("JIRA_USER", ""),
                token=os.getenv("JIRA_TOKEN", ""),
            ),
        )
        cls.register(
            "grafana",
            GrafanaTool(base_url=os.getenv("GRAFANA_URL", "")),
        )
        logger.info(f"[ToolRegistry] Bootstrap done: {list(_registry.keys())}")
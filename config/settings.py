# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Configuration for Multi-Agent Gateway
"""

from typing import Dict

class AgentConfig:
    def __init__(self, name: str, role: str, max_concurrent: int = 3, timeout_seconds: float = 30.0, priority: int = 1):
        self.name = name
        self.role = role
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self.priority = priority

class GatewayConfig:
    def __init__(self):
        self.global_rate_limit_per_minute = 60
        self.per_agent_rate_limit = 20
        self.cache_ttl_seconds = 300
        self.enable_cache = True
        self.max_parallel_agents = 4
        self.load_balance_strategy = "round_robin"
        self.aggregation_mode = "smart"
        self.require_consensus = False
        self.enable_parallel = True
        self.max_retries = 2
        self.log_level = "INFO"
        self.enable_detailed_logs = True

AGENTS: Dict[str, AgentConfig] = {
    "planner": AgentConfig(
        name="PlannerAgent",
        role="Breaks down complex tasks into sub-tasks and creates execution plan",
        max_concurrent=2,
        priority=1
    ),
    "researcher": AgentConfig(
        name="ResearcherAgent",
        role="Gathers information, facts, and context needed for the task",
        max_concurrent=3,
        priority=2
    ),
    "analyst": AgentConfig(
        name="AnalystAgent",
        role="Analyzes data, finds patterns, and provides insights",
        max_concurrent=3,
        priority=2
    ),
    "generator": AgentConfig(
        name="GeneratorAgent",
        role="Generates final content, code, or solutions based on analysis",
        max_concurrent=2,
        priority=1
    ),
    "critic": AgentConfig(
        name="CriticAgent",
        role="Reviews outputs for quality, correctness, and completeness",
        max_concurrent=2,
        priority=1
    ),
    "coordinator": AgentConfig(
        name="CoordinatorAgent",
        role="Internal collaboration orchestrator",
        max_concurrent=1,
        priority=0
    ),
}

DEFAULT_GATEWAY = GatewayConfig()

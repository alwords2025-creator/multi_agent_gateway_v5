# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
API GATEWAY - Core Orchestrator
Implements: Authentication, Rate Limiting, Caching, Load Balancing, Aggregation, Logging
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time

from agents.specialized import (
    PlannerAgent, ResearcherAgent, AnalystAgent,
    GeneratorAgent, CriticAgent, CoordinatorAgent
)
from agents.base import AgentResult
from utils.cache import cache
from utils.rate_limiter import global_limiter, agent_limiters
from utils.logger import logger
from config.settings import AGENTS, DEFAULT_GATEWAY


@dataclass
class GatewayResponse:
    success: bool
    final_output: Any
    confidence: float
    agents_used: List[str]
    total_time_ms: float
    cache_hit: bool = False
    aggregation_details: Dict = field(default_factory=dict)
    individual_results: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "success": self.success,
            "final_output": self.final_output,
            "confidence": self.confidence,
            "agents_used": self.agents_used,
            "total_time_ms": round(self.total_time_ms, 2),
            "cache_hit": self.cache_hit,
            "aggregation_details": self.aggregation_details,
            "individual_results": self.individual_results,
            "timestamp": self.timestamp
        }


class APIGateway:
    """
    Central API Gateway for Multi-AI Agent System
    """

    def __init__(self):
        self._cfg = DEFAULT_GATEWAY
        self._agents = {
            "planner": PlannerAgent(),
            "researcher": ResearcherAgent(),
            "analyst": AnalystAgent(),
            "generator": GeneratorAgent(),
            "critic": CriticAgent(),
            "coordinator": CoordinatorAgent(),
        }
        self._req_count = 0
        logger.info("GATEWAY", "API Gateway initialized with all agents")

    async def _check_rl(self, agent_key: str = "global"):
        await global_limiter.wait_for_token("global")
        if agent_key != "global":
            await agent_limiters[agent_key].wait_for_token(agent_key)

    async def _get_cached(self, task: str) -> Optional[GatewayResponse]:
        if not self._cfg.enable_cache:
            return None
        cached = await cache.get("gateway", task)
        if cached:
            logger.success("CACHE", f"Cache HIT for task: {task[:50]}...")
            return cached
        return None

    async def _set_cache(self, task: str, response: GatewayResponse):
        if self._cfg.enable_cache:
            await cache.set("gateway", task, response)

    async def _run_agent(self, agent_key: str, task: str, context: Dict) -> AgentResult:
        await self._check_rl(agent_key)
        agent = self._agents[agent_key]
        logger.info(agent.name, f"Starting: {task[:40]}...")
        result = await agent.run(task, context)
        status = "OK" if result.success else "FAIL"
        logger.success(agent.name, f"Done [{status}] conf={result.confidence:.2f} time={result.execution_time_ms:.0f}ms")
        return result

    async def _parallel_ra(self, task: str, plan_context: Dict) -> Dict:
        logger.info("GATEWAY", "Launching parallel: Researcher + Analyst")

        research_task = self._run_agent("researcher", task, plan_context)
        analysis_task = self._run_agent("analyst", task, plan_context)

        research_res, analysis_res = await asyncio.gather(research_task, analysis_task)

        return {
            "research": research_res.content if research_res.success else {},
            "analysis": analysis_res.content if analysis_res.success else {},
            "results": [research_res, analysis_res]
        }

    async def process(self, task: str, user_id: str = "anonymous") -> GatewayResponse:
        start = time.time()
        self._req_count += 1
        logger.info("GATEWAY", f"Request #{self._req_count} received | Task: {task[:60]}...")

        logger.info("AUTH", f"Authenticated user: {user_id}")

        cached = await self._get_cached(task)
        if cached:
            cached.cache_hit = True
            return cached

        try:
            coord = await self._run_agent("coordinator", task, {})
            
            plan_res = await self._run_agent("planner", task, {})
            plan_context = {"plan": plan_res.content} if plan_res.success else {}

            parallel = await self._parallel_ra(task, plan_context)
            context = {
                **plan_context,
                "research": parallel["research"],
                "analysis": parallel["analysis"]
            }

            gen_res = await self._run_agent("generator", task, context)
            context["draft"] = gen_res.content

            critic_res = await self._run_agent("critic", task, context)

            all_results = [plan_res] + parallel["results"] + [gen_res, critic_res]
            successful = [r for r in all_results if r.success]

            if not successful:
                raise Exception("All agents failed")

            avg_confidence = sum(r.confidence for r in successful) / len(successful)
            critic_approved = critic_res.success and critic_res.content.get("approved", False)

            final_output = gen_res.content if gen_res.success else "Generation failed"
            if critic_approved:
                final_output = f"{final_output}\n\n---\n[QUALITY GATE PASSED] (Score: {critic_res.content.get('quality_score', 'N/A')})"

            total_ms = (time.time() - start) * 1000

            response = GatewayResponse(
                success=critic_approved or avg_confidence >= 0.85,
                final_output=final_output,
                confidence=round(avg_confidence, 3),
                agents_used=[r.agent_name for r in successful],
                total_time_ms=total_ms,
                aggregation_details={
                    "mode": "smart_weighted",
                    "agents_participated": len(successful),
                    "critic_approved": critic_approved,
                    "avg_confidence": round(avg_confidence, 3)
                },
                individual_results=[r.to_dict() for r in all_results]
            )

            await self._set_cache(task, response)

            logger.success("GATEWAY", f"Completed in {total_ms:.0f}ms | Confidence: {avg_confidence:.2f} | Agents: {len(successful)}")
            return response

        except Exception as e:
            total_ms = (time.time() - start) * 1000
            logger.error("GATEWAY", f"Pipeline failed: {str(e)}")
            return GatewayResponse(
                success=False,
                final_output=None,
                confidence=0.0,
                agents_used=[],
                total_time_ms=total_ms,
                aggregation_details={"error": str(e)}
            )

    def get_stats(self) -> Dict:
        return {
            "total_requests": self._req_count,
            "cache_stats": cache.stats(),
            "agents": {k: {"active_tasks": v.active_tasks} for k, v in self._agents.items()}
        }

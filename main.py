#!/usr/bin/env python3
# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Multi-Agent Gateway - Fast Collaborative AI System
Architecture based on API Gateway pattern (Nginx / AWS API Gateway)
"""

import asyncio
import sys
import argparse

from gateway import APIGateway
from utils.logger import logger


def _print_header():
    print("=" * 70)
    print("  Multi-Agent Gateway")
    print("  API Gateway Pattern | Parallel Collaboration | Quality Output")
    print("=" * 70)


def _print_panel(title: str, content: str, success: bool = True):
    border = "+" + "-" * 68 + "+"
    print(border)
    status = "[OK]" if success else "[FAIL]"
    print(f"| {status} {title:<64} |")
    print(border)
    for line in content.split("\n"):
        print(f"| {line[:66]:<66} |")
    print(border)


async def _run_pipeline(task: str = None):
    _print_header()

    _gw = APIGateway()

    _tasks = [
        task or "Design a high-performance multi-agent AI system that can complete complex tasks quickly through internal collaboration and produce high quality final output"
    ]

    for i, t in enumerate(_tasks, 1):
        print(f"\nTask {i}: {t}\n")
        print("-" * 70)

        _resp = await _gw.process(t, user_id="demo_user")

        if _resp.success:
            _print_panel("FINAL OUTPUT (Quality Gate Passed)", str(_resp.final_output), success=True)
        else:
            _print_panel("FAILED", str(_resp.final_output or "Unknown error"), success=False)

        print("\nPerformance Metrics")
        print(f"  Total Time      : {_resp.total_time_ms:.0f} ms")
        print(f"  Confidence      : {_resp.confidence:.1%}")
        print(f"  Agents Used     : {', '.join(_resp.agents_used)}")
        print(f"  Cache Hit       : {'Yes' if _resp.cache_hit else 'No'}")
        print(f"  Critic Approved : {_resp.aggregation_details.get('critic_approved', False)}")
        print(f"  Aggregation     : {_resp.aggregation_details.get('mode', 'N/A')}")

        if _resp.individual_results:
            print("\nAgent Collaboration Breakdown")
            print(f"  {'Agent':<20} {'Success':<10} {'Confidence':<12} {'Time (ms)'}")
            print("  " + "-" * 55)
            for r in _resp.individual_results:
                status = "OK" if r["success"] else "FAIL"
                print(f"  {r['agent']:<20} {status:<10} {r['confidence']:.0%}{'':<8} {r['execution_time_ms']:.0f}")

    _stats = _gw.get_stats()
    print("\n" + "=" * 70)
    print("  Gateway Stats")
    print(f"  Total Requests : {_stats['total_requests']}")
    print(f"  Cache Hit Rate : {_stats['cache_stats']['hit_rate']}")
    print(f"  Cache Size     : {_stats['cache_stats']['size']}")
    print("=" * 70)

    logger.show_summary()


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Gateway System")
    parser.add_argument("--task", "-t", type=str, help="Task for the multi-agent system")
    args = parser.parse_args()

    try:
        asyncio.run(_run_pipeline(args.task))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

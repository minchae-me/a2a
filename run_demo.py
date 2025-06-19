#!/usr/bin/env python3
"""
🚀 ADK + A2A 통합 데모 - 원클릭 실행 스크립트

빠르게 통합 데모를 실행하여 ADK와 A2A의 차이점을 확인할 수 있습니다.
"""

import asyncio
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from integration_example import main as run_integration_demo


def print_demo_banner():
    """데모 배너 출력"""
    banner = """
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
   ⚡ ADK + A2A 통합 데모 - 원클릭 실행
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

   이 데모는 ADK와 A2A의 차이점과 상호 보완 관계를 실증합니다:

   🧠 ADK: 에이전트 내부 워크플로우 및 상태 관리
   📡 A2A: 에이전트 간 표준 통신 프로토콜
   🤝 통합: 완전한 분산 에이전트 시스템

🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
"""
    print(banner)


async def run_quick_demo():
    """빠른 데모 실행"""
    print_demo_banner()

    print("⚡ 통합 데모를 실행합니다...")
    print("   약 10-15초 정도 소요됩니다.\n")

    try:
        await run_integration_demo()
        print("\n✅ 데모가 성공적으로 완료되었습니다!")
        print("📚 더 자세한 정보는 'python main.py'를 실행하여 확인하세요.")

    except Exception as e:
        print(f"❌ 데모 실행 중 오류가 발생했습니다: {e}")
        print("🔧 문제 해결을 위해 개별 테스트를 실행해보세요:")
        print("   • python adk_agents/travel_agent.py")
        print("   • python a2a_agents/travel_agent.py")


if __name__ == "__main__":
    try:
        asyncio.run(run_quick_demo())
    except KeyboardInterrupt:
        print("\n👋 데모가 중단되었습니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")

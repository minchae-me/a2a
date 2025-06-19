#!/usr/bin/env python3
"""
🤖 ADK + A2A 통합 여행 추천 에이전트 시스템 - 메인 실행 스크립트

이 스크립트는 ADK와 A2A의 차이점을 실증하는 통합 데모를 제공합니다.
"""

import asyncio
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from integration_example import main as run_integration_demo
from adk_agents.travel_agent import test_adk_travel_agent
from a2a_agents.travel_agent import test_a2a_communication


def print_banner():
    """프로젝트 배너 출력"""
    banner = """
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
   🤖 ADK + A2A 통합 여행 추천 에이전트 시스템
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

   Google ADK와 A2A Protocol의 차이점과 상호 보완 관계 실증

   💡 핵심 차이점:
   • ADK = 에이전트 내부 개발 프레임워크 (로직·워크플로우 중심)
   • A2A = 에이전트 간 통신 표준 (인터페이스 중심)
   • 통합 = ADK_internal_logic + A2A_communication_wrapper

🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
"""
    print(banner)


def print_menu():
    """메뉴 출력"""
    menu = """
📋 실행 옵션을 선택하세요:

1. 🎯 통합 데모 (ADK + A2A 차이점 실증)
2. 🧠 ADK 에이전트 테스트 (내부 워크플로우)
3. 📡 A2A 에이전트 테스트 (통신 프로토콜)
4. 📚 프로젝트 정보 보기
5. ❌ 종료

선택 (1-5): """
    return input(menu).strip()


def print_project_info():
    """프로젝트 정보 출력"""
    info = """
📚 ADK + A2A 통합 프로젝트 정보
================================================================================

🎯 프로젝트 목적:
   Google의 ADK와 A2A 기술의 차이점을 실제 코드로 구현하여 실증

🏗️ 아키텍처:
   ┌─────────────────────────────────────────────────────────────────┐
   │                    통합 에이전트 시스템                            │
   ├─────────────────────────────────────────────────────────────────┤
   │  🧠 ADK (내부 구조)          │  📡 A2A (통신 인터페이스)      │
   │  ─────────────────────       │  ──────────────────────        │
   │  • BaseAgent 상속            │  • JSON-RPC 프로토콜           │
   │  • State 관리 (enum)         │  • Agent Card 서비스           │
   │  • Sequential/Parallel       │  • 인증 & 세션 관리            │
   │  • 도구 체이닝 & MCP         │  • 스트리밍 지원               │
   │  • 이벤트 기반 콜백          │  • 분산 에이전트 협업          │
   └─────────────────────────────────────────────────────────────────┘

📂 주요 파일:
   • integration_example.py   - ADK + A2A 통합 데모
   • adk_agents/travel_agent.py - ADK 기반 에이전트 (내부 로직)
   • a2a_agents/travel_agent.py - A2A 기반 에이전트 (통신 인터페이스)
   • adk_config.py            - ADK 설정

🚀 개발 흐름:
   1️⃣  ADK로 에이전트 내부 구현 (로직·워크플로우)
   2️⃣  A2A로 통신 인터페이스 구성 (인터페이스)
   3️⃣  통합하여 완전한 분산 에이전트 시스템 구축

💡 학습 포인트:
   • ADK = "에이전트를 어떻게 만들 것인가?" (How to Build)
   • A2A = "에이전트들을 어떻게 연결할 것인가?" (How to Connect)
   • 상호 보완적 관계로 완전한 에이전트 생태계 구현

================================================================================
"""
    print(info)


async def main():
    """메인 실행 함수"""
    print_banner()

    while True:
        try:
            choice = print_menu()

            if choice == "1":
                print("🎯 통합 데모 실행 중...")
                print("   ADK와 A2A의 차이점과 상호 보완 관계를 실증합니다.\n")
                await run_integration_demo()

            elif choice == "2":
                print("🧠 ADK 에이전트 테스트 실행 중...")
                print("   에이전트 내부 구조와 워크플로우를 테스트합니다.\n")
                await test_adk_travel_agent()

            elif choice == "3":
                print("📡 A2A 에이전트 테스트 실행 중...")
                print("   에이전트 간 통신 프로토콜을 테스트합니다.\n")
                await test_a2a_communication()

            elif choice == "4":
                print_project_info()

            elif choice == "5":
                print("👋 프로그램을 종료합니다. 감사합니다!")
                break

            else:
                print("❌ 잘못된 선택입니다. 1-5 사이의 숫자를 입력해주세요.")

            # 각 실행 후 사용자 입력 대기
            if choice in ["1", "2", "3"]:
                input("\n⏸️  결과를 확인하셨으면 Enter를 눌러 메뉴로 돌아가세요...")

        except KeyboardInterrupt:
            print("\n\n👋 프로그램이 중단되었습니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
            input("Enter를 눌러 계속...")


def run_sync():
    """동기 실행 함수 (진입점용)"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    # 직접 실행시 메뉴 방식으로 실행
    run_sync()

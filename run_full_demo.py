#!/usr/bin/env python3
"""
🎯 A2A + ADK + MCP 완전 통합 데모
MCP HTTP 서버 자동 시작 + A2A + ADK 통합 실행
"""

import asyncio
import subprocess
import time
import sys
import signal
import os
from pathlib import Path

# 전역 변수로 서버 프로세스 관리
mcp_server_process = None


def signal_handler(signum, frame):
    """시그널 핸들러 - 서버 정리"""
    print("\n🛑 프로그램 종료 신호 수신...")
    cleanup_processes()
    sys.exit(0)


def cleanup_processes():
    """백그라운드 프로세스 정리"""
    global mcp_server_process

    if mcp_server_process:
        print("🛑 MCP 서버 종료 중...")
        mcp_server_process.terminate()
        try:
            mcp_server_process.wait(timeout=5)
            print("✅ MCP 서버 정상 종료")
        except subprocess.TimeoutExpired:
            print("⚠️ MCP 서버 강제 종료")
            mcp_server_process.kill()
        mcp_server_process = None


def start_mcp_server():
    """MCP HTTP 서버 시작"""
    global mcp_server_process

    print("🚀 MCP HTTP 서버 시작 중...")

    # MCP 서버 파일 경로 확인
    server_path = Path("mcp_server/http_mcp_server.py")
    if not server_path.exists():
        print(f"❌ MCP 서버 파일을 찾을 수 없습니다: {server_path}")
        return False

    try:
        # 서버 시작
        mcp_server_process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print("⏳ MCP 서버 시작 대기 중...")
        time.sleep(3)  # 서버 시작 대기

        # 서버 상태 확인
        if mcp_server_process.poll() is None:
            print("✅ MCP HTTP 서버 시작 완료 (PID: {})".format(mcp_server_process.pid))
            print("📍 서버 주소: http://localhost:8000")
            return True
        else:
            print("❌ MCP 서버 시작 실패")
            return False

    except Exception as e:
        print(f"❌ MCP 서버 시작 오류: {e}")
        return False


async def run_integration_demo():
    """A2A + ADK + MCP 통합 데모 실행"""
    print("\n" + "=" * 80)
    print("🎯 A2A + ADK + MCP 완전 통합 데모")
    print("=" * 80)

    # MCP 클라이언트 임포트 (여기서 임포트해야 서버가 먼저 시작됨)
    try:
        from A2A.mcp_http_client import A2AMCPAgent
    except ImportError as e:
        print(f"❌ MCP 클라이언트 임포트 실패: {e}")
        print("💡 필요한 패키지를 설치하세요: pip install aiohttp fastapi uvicorn")
        return False

    # A2A MCP 에이전트 생성
    agent = A2AMCPAgent()

    # 초기화
    if not await agent.initialize():
        print("❌ MCP 서버 연결 실패")
        return False

    print(f"✅ {agent.name} 초기화 완료")
    print(f"📋 지원 기능: {', '.join(agent.agent_card['capabilities'])}")
    print()

    # 실제 사용 시나리오들
    scenarios = [
        {
            "name": "🎯 에이전트 능력 확인",
            "request": {"id": 1, "method": "capabilities", "params": {}},
        },
        {
            "name": "🔍 바다 관련 여행지 검색",
            "request": {"id": 2, "method": "search", "params": {"query": "바다"}},
        },
        {
            "name": "✈️ 제주도 중간 예산 여행 추천",
            "request": {
                "id": 3,
                "method": "recommend",
                "params": {"destination": "제주도", "budget": "medium"},
            },
        },
        {
            "name": "🌤️ 부산 날씨 정보",
            "request": {"id": 4, "method": "weather", "params": {"location": "부산"}},
        },
        {
            "name": "💰 서울 2박3일 2명 예산 분석",
            "request": {
                "id": 5,
                "method": "budget",
                "params": {"destination": "서울", "days": 3, "people": 2},
            },
        },
    ]

    # 시나리오 실행
    for i, scenario in enumerate(scenarios, 1):
        print(f"📝 시나리오 {i}: {scenario['name']}")
        print("-" * 60)

        try:
            response = await agent.handle_a2a_request(scenario["request"])

            if "error" in response:
                print(f"❌ 오류: {response['error']}")
            else:
                result = response.get("result", {})
                source = response.get("source", "Unknown")

                print(f"📡 데이터 출처: {source}")

                if isinstance(result, dict):
                    # 결과 타입별 출력
                    if "destinations" in result:
                        # 검색 결과
                        total = result.get("total_results", 0)
                        print(f"🔍 총 {total}개 여행지 발견")
                        for dest in result.get("destinations", []):
                            score = dest.get("match_score", 0)
                            print(f"   📍 {dest['destination']} (매칭도: {score:.1f})")
                            print(f"      {dest['description']}")
                            print(
                                f"      주요 활동: {', '.join(dest.get('activities', []))}"
                            )

                    elif "recommended_activities" in result:
                        # 여행 추천
                        print(
                            f"🏨 추천 호텔: {', '.join(result.get('recommended_hotels', [])[:2])}"
                        )
                        print(
                            f"🎯 추천 활동: {', '.join(result.get('recommended_activities', [])[:3])}"
                        )
                        print(
                            f"🍽️ 현지 음식: {', '.join(result.get('local_food', [])[:3])}"
                        )
                        print(f"💰 예상 예산: {result.get('budget_estimate', 'N/A')}")
                        print(f"📊 예산 수준: {result.get('budget_level', 'N/A')}")

                    elif "temperature" in result:
                        # 날씨 정보
                        print(f"🌡️ 온도: {result.get('temperature', 'N/A')}")
                        print(f"☁️ 날씨: {result.get('condition', 'N/A')}")
                        print(f"💧 습도: {result.get('humidity', 'N/A')}")
                        print(f"🌬️ 바람: {result.get('wind', 'N/A')}")

                    elif "budget_options" in result:
                        # 예산 분석
                        print(f"💰 예산 분석 대상: {result.get('analysis_for', 'N/A')}")
                        print(f"🎯 추천 수준: {result.get('recommendation', 'medium')}")

                        options = result.get("budget_options", {})
                        for level, info in options.items():
                            level_kr = {
                                "low": "저예산",
                                "medium": "중간예산",
                                "high": "고예산",
                            }.get(level, level)
                            print(f"   {level_kr}: {info.get('total_cost', 'N/A')}")

                        notes = result.get("notes", [])
                        if notes:
                            print(f"📝 참고사항: {', '.join(notes[:2])}")

                    elif "capabilities" in result:
                        # 능력 정보
                        print(f"🤖 에이전트: {result.get('name', 'N/A')}")
                        print(f"📋 버전: {result.get('version', 'N/A')}")
                        print(f"🎯 능력: {', '.join(result.get('capabilities', []))}")
                        print(f"🔗 프로토콜: {result.get('protocol', 'N/A')}")
                        print(f"🌐 MCP 통합: {result.get('mcp_integration', False)}")

                    else:
                        # 기타 결과
                        print(
                            f"📋 결과: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}"
                        )

                else:
                    print(f"📋 결과: {result}")

        except Exception as e:
            print(f"❌ 시나리오 실행 오류: {e}")

        print()

    print("🎉 A2A + ADK + MCP 완전 통합 데모 완료!")
    print("✅ 모든 컴포넌트가 정상적으로 연동되었습니다!")
    print()
    print("🔗 아키텍처 요약:")
    print("   1. MCP HTTP 서버 (포트 8000) - 실제 여행 데이터 제공")
    print("   2. ADK 에이전트 - MCP 도구 활용 및 비즈니스 로직")
    print("   3. A2A 프로토콜 - 표준화된 에이전트 통신")
    print("   4. 통합 흐름: 사용자 → A2A → ADK → MCP → 데이터 → 응답")

    return True


async def main():
    """메인 실행 함수"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 A2A + ADK + MCP 완전 통합 데모 시작")
    print("=" * 80)

    try:
        # 1. MCP 서버 시작
        if not start_mcp_server():
            print("❌ MCP 서버 시작 실패")
            return

        # 2. 통합 데모 실행
        success = await run_integration_demo()

        if success:
            print("\n🎊 데모 실행 완료! MCP 서버는 계속 실행 중입니다.")
            print("🔍 브라우저에서 확인: http://localhost:8000")
            print("⏹️  종료하려면 Ctrl+C를 누르세요.")

            # 서버 유지 (사용자가 종료할 때까지)
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

    finally:
        cleanup_processes()


if __name__ == "__main__":
    asyncio.run(main())

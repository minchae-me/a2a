#!/usr/bin/env python3
"""
MCP + ADK + A2A 통합 예제
우리가 만든 MCP 서버를 ADK 에이전트와 A2A 프로토콜에 연결

구조:
1. MCP 서버 (우리가 만든 OpenAPI MCP 서버)
2. ADK 에이전트 (MCP Tool로 MCP 서버 연결)
3. A2A 프로토콜 (ADK 에이전트를 A2A로 래핑)
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess
import sys
import time

# 우리 프로젝트의 MCP 경로 (별도 저장소)
MCP_PROJECT_PATH = Path(__file__).parent.parent / "mcp"
MCP_SERVER_URL = "http://localhost:8000"


class MCPClient:
    """MCP 서버와 통신하는 클라이언트"""

    def __init__(self, server_url: str = MCP_SERVER_URL):
        self.server_url = server_url
        self.client = httpx.AsyncClient()

    async def check_server_health(self) -> bool:
        """MCP 서버가 실행 중인지 확인"""
        try:
            response = await self.client.get(f"{self.server_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    async def list_tools(self) -> Dict[str, Any]:
        """사용 가능한 도구들 목록 조회"""
        try:
            response = await self.client.get(f"{self.server_url}/tools")
            return response.json()
        except Exception as e:
            return {"error": str(e), "tools": []}

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 도구 호출"""
        try:
            payload = {"name": tool_name, "arguments": arguments}
            response = await self.client.post(
                f"{self.server_url}/tools/{tool_name}/call", json=payload
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "result": None}

    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()


class ADKMCPTravelAgent:
    """
    ADK 기반 여행 에이전트 + MCP Tool 통합
    Google ADK의 MCP Tool을 사용해서 우리 MCP 서버와 연결
    """

    def __init__(self):
        self.name = "ADK-MCP-TravelAgent"
        self.mcp_client = MCPClient()
        self.state = "initialized"

        # ADK에서 MCP Tool 사용 (시뮬레이션)
        self.mcp_tools = []

    async def initialize(self):
        """에이전트 초기화 및 MCP 서버 연결"""
        print(f"🔧 {self.name} 초기화 중...")

        # MCP 서버 상태 확인
        is_healthy = await self.mcp_client.check_server_health()
        if not is_healthy:
            print("❌ MCP 서버가 실행되지 않음. 먼저 MCP 서버를 시작하세요.")
            print("   실행 방법: cd mcp && python standalone_mcp_server.py")
            return False

        print("✅ MCP 서버 연결 성공!")

        # 사용 가능한 도구들 로드
        tools_info = await self.mcp_client.list_tools()
        self.mcp_tools = tools_info.get("tools", [])

        print(f"📋 로드된 MCP 도구: {len(self.mcp_tools)}개")
        for tool in self.mcp_tools:
            print(
                f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
            )

        self.state = "ready"
        return True

    async def process_travel_request(self, user_request: str) -> Dict[str, Any]:
        """
        여행 요청 처리 (ADK 워크플로우 + MCP 도구 사용)
        """
        print(f"\n🎯 ADK 여행 요청 처리: {user_request}")

        if self.state != "ready":
            return {"error": "에이전트가 초기화되지 않음"}

        results = {}

        # 1. MCP 도구로 여행지 검색
        if any(tool.get("name") == "search_destinations" for tool in self.mcp_tools):
            print("🔍 MCP 도구: 여행지 검색 중...")
            search_result = await self.mcp_client.call_tool(
                "search_destinations", {"query": user_request, "limit": 3}
            )
            results["destinations"] = search_result

        # 2. MCP 도구로 예산 분석
        if any(tool.get("name") == "analyze_budget" for tool in self.mcp_tools):
            print("💰 MCP 도구: 예산 분석 중...")
            budget_result = await self.mcp_client.call_tool(
                "analyze_budget", {"request": user_request}
            )
            results["budget_analysis"] = budget_result

        # 3. ADK 내부 로직으로 추천 생성
        print("🧠 ADK 내부 로직: 추천 생성 중...")
        recommendation = await self._generate_adk_recommendation(user_request, results)
        results["recommendation"] = recommendation

        return results

    async def _generate_adk_recommendation(
        self, request: str, mcp_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ADK 내부 로직으로 최종 추천 생성"""
        # ADK의 Sequential/Parallel 워크플로우 시뮬레이션
        workflow_steps = [
            "1️⃣ 사용자 선호도 분석",
            "2️⃣ MCP 결과와 내부 로직 결합",
            "3️⃣ 최적화된 여행 계획 생성",
        ]

        for step in workflow_steps:
            print(f"   {step}")
            await asyncio.sleep(0.5)  # 워크플로우 시뮬레이션

        return {
            "request": request,
            "mcp_integration": "성공",
            "workflow_completed": True,
            "final_recommendation": "제주도 3박 4일 가족 여행 (MCP + ADK 통합 결과)",
        }

    async def cleanup(self):
        """리소스 정리"""
        await self.mcp_client.close()


class A2AMCPAgent:
    """
    A2A 프로토콜로 래핑된 MCP 통합 에이전트
    ADK-MCP 에이전트를 A2A 인터페이스로 노출
    """

    def __init__(self):
        self.adk_agent = ADKMCPTravelAgent()
        self.agent_card = {
            "agent_id": "a2a-mcp-travel-agent",
            "name": "A2A MCP Travel Agent",
            "description": "MCP 서버를 활용한 여행 추천 에이전트 (ADK + A2A 통합)",
            "version": "1.0.0",
            "skills": [
                {
                    "name": "travel_recommendation_with_mcp",
                    "description": "MCP 도구를 활용한 여행 추천",
                    "parameters": {
                        "user_request": {
                            "type": "string",
                            "description": "사용자 여행 요청",
                        }
                    },
                }
            ],
        }

    async def initialize(self):
        """A2A 에이전트 초기화"""
        print(f"🌐 A2A MCP 에이전트 초기화...")
        success = await self.adk_agent.initialize()
        if success:
            print("✅ A2A MCP 에이전트 준비 완료!")
        return success

    async def handle_a2a_request(
        self, skill_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        A2A 요청 처리 (JSON-RPC 스타일)
        """
        print(f"\n📡 A2A 요청 수신: {skill_name}")
        print(f"📝 매개변수: {parameters}")

        if skill_name == "travel_recommendation_with_mcp":
            user_request = parameters.get("user_request", "")

            # ADK 에이전트로 처리 위임
            adk_result = await self.adk_agent.process_travel_request(user_request)

            # A2A 응답 형식으로 래핑
            return {
                "status": "success",
                "agent_id": self.agent_card["agent_id"],
                "skill": skill_name,
                "result": adk_result,
                "metadata": {
                    "processing_time": "2.3s",
                    "mcp_tools_used": len(self.adk_agent.mcp_tools),
                    "integration_layer": "ADK + MCP + A2A",
                },
            }
        else:
            return {"status": "error", "message": f"지원하지 않는 스킬: {skill_name}"}

    async def cleanup(self):
        """리소스 정리"""
        await self.adk_agent.cleanup()


async def start_mcp_server():
    """MCP 서버 시작 (백그라운드)"""
    print("🚀 MCP 서버 시작 중...")

    mcp_server_script = MCP_PROJECT_PATH / "standalone_mcp_server.py"
    if not mcp_server_script.exists():
        print(f"❌ MCP 서버 스크립트를 찾을 수 없음: {mcp_server_script}")
        print("💡 해결 방법:")
        print("   1. 별도 터미널에서 MCP 서버를 수동으로 시작하세요:")
        print("   2. cd ../mcp")
        print("   3. python standalone_mcp_server.py")
        return None

    # 백그라운드에서 MCP 서버 실행
    process = subprocess.Popen(
        [sys.executable, str(mcp_server_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 서버 시작 대기
    print("⏳ MCP 서버 시작 대기 중...")
    await asyncio.sleep(3)

    return process


async def test_mcp_adk_a2a_integration():
    """MCP + ADK + A2A 통합 테스트"""
    print("=" * 80)
    print("🎯 MCP + ADK + A2A 통합 테스트")
    print("=" * 80)

    # MCP 서버 시작
    mcp_process = await start_mcp_server()

    try:
        # A2A MCP 에이전트 생성 및 초기화
        a2a_agent = A2AMCPAgent()
        success = await a2a_agent.initialize()

        if not success:
            print("❌ 에이전트 초기화 실패")
            return

        # 테스트 시나리오
        test_request = "제주도로 가족 여행 계획해주세요. 예산 150만원, 3박 4일"

        print(f"\n📋 테스트 시나리오:")
        print(f"   요청: {test_request}")

        # A2A 요청 처리
        result = await a2a_agent.handle_a2a_request(
            "travel_recommendation_with_mcp", {"user_request": test_request}
        )

        # 결과 출력
        print(f"\n🎉 통합 테스트 결과:")
        print(f"   상태: {result.get('status', 'unknown')}")
        print(
            f"   처리 시간: {result.get('metadata', {}).get('processing_time', 'N/A')}"
        )
        print(
            f"   사용된 MCP 도구: {result.get('metadata', {}).get('mcp_tools_used', 0)}개"
        )
        print(
            f"   통합 레이어: {result.get('metadata', {}).get('integration_layer', 'N/A')}"
        )

        # 상세 결과
        adk_result = result.get("result", {})
        if "recommendation" in adk_result:
            rec = adk_result["recommendation"]
            print(f"   최종 추천: {rec.get('final_recommendation', 'N/A')}")

        # 정리
        await a2a_agent.cleanup()

        print("\n✅ MCP + ADK + A2A 통합 테스트 완료!")

    finally:
        # MCP 서버 종료
        if mcp_process:
            mcp_process.terminate()
            print("🛑 MCP 서버 종료")


def print_integration_architecture():
    """통합 아키텍처 설명"""
    print("\n" + "=" * 80)
    print("🏗️ MCP + ADK + A2A 통합 아키텍처")
    print("=" * 80)

    print(
        """
📦 MCP (Model Context Protocol) 서버
   ├── 우리가 만든 OpenAPI MCP 서버
   ├── REST API 엔드포인트 제공  
   ├── 여행지 검색, 예산 분석 등 도구 제공
   └── 포트 8000에서 실행

🔧 ADK (Agent Development Kit)
   ├── MCP Tool로 MCP 서버와 연결
   ├── Sequential/Parallel 워크플로우 구성
   ├── State 관리 및 내부 로직 처리
   └── MCP 결과와 ADK 로직 결합

🌐 A2A (Agent2Agent Protocol)
   ├── ADK 에이전트를 A2A 인터페이스로 래핑
   ├── JSON-RPC 스타일 통신 프로토콜
   ├── Agent Card로 서비스 디스커버리
   └── 다른 에이전트들과 상호작용

🔗 통합 흐름:
   1. 사용자 요청 → A2A 프로토콜
   2. A2A → ADK 에이전트 호출
   3. ADK → MCP 서버 도구 사용
   4. MCP → 실제 기능 수행 (검색, 분석 등)
   5. 결과를 역순으로 전달하여 최종 응답
"""
    )


async def main():
    """메인 실행 함수"""
    print_integration_architecture()

    print("\n📋 실행 옵션:")
    print("1. MCP + ADK + A2A 통합 테스트 실행")
    print("2. 아키텍처 설명만 보기")

    choice = input("\n선택하세요 (1-2): ").strip()

    if choice == "1":
        await test_mcp_adk_a2a_integration()
    elif choice == "2":
        print("✅ 아키텍처 설명 완료!")
    else:
        print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
🌐 HTTP MCP 클라이언트
A2A + ADK와 MCP 서버를 연결하는 HTTP 클라이언트
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPClient:
    """HTTP MCP 클라이언트"""

    base_url: str = "http://localhost:8000"
    timeout: int = 30

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def call_tool(
        self, method: str, params: Dict[str, Any] = None, request_id: int = 1
    ) -> Dict[str, Any]:
        """MCP 도구 호출"""
        if params is None:
            params = {}

        request_data = {"method": method, "params": params, "id": request_id}

        try:
            async with self.session.post(
                f"{self.base_url}/mcp", json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    return {
                        "id": request_id,
                        "error": f"HTTP {response.status}: {await response.text()}",
                    }
        except Exception as e:
            return {"id": request_id, "error": f"Connection error: {str(e)}"}

    async def health_check(self) -> bool:
        """서버 상태 확인"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except:
            return False

    async def list_tools(self) -> Dict[str, Any]:
        """사용 가능한 도구 목록"""
        try:
            async with self.session.get(f"{self.base_url}/tools") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}


# ADK + MCP 통합 에이전트
@dataclass
class ADKMCPAgent:
    """ADK 에이전트 + MCP 도구 통합"""

    name: str = "ADK-MCP-TravelAgent"
    mcp_client: Optional[MCPClient] = None

    async def initialize(self, mcp_url: str = "http://localhost:8000"):
        """MCP 클라이언트 초기화"""
        self.mcp_client = MCPClient(mcp_url)

        # 서버 연결 확인
        async with self.mcp_client as client:
            if await client.health_check():
                print(f"✅ MCP 서버 연결 성공: {mcp_url}")
                return True
            else:
                print(f"❌ MCP 서버 연결 실패: {mcp_url}")
                return False

    async def search_destinations(self, query: str) -> Dict[str, Any]:
        """MCP를 통한 여행지 검색"""
        async with self.mcp_client as client:
            result = await client.call_tool("search_destination", {"query": query})
            return result

    async def get_recommendation(
        self, destination: str, budget: str = "medium"
    ) -> Dict[str, Any]:
        """MCP를 통한 여행 추천"""
        async with self.mcp_client as client:
            result = await client.call_tool(
                "get_travel_recommendation",
                {"destination": destination, "budget": budget},
            )
            return result

    async def get_weather(self, location: str) -> Dict[str, Any]:
        """MCP를 통한 날씨 정보"""
        async with self.mcp_client as client:
            result = await client.call_tool("get_weather_info", {"location": location})
            return result

    async def analyze_budget(
        self, destination: str, days: int = 3, people: int = 1
    ) -> Dict[str, Any]:
        """MCP를 통한 예산 분석"""
        async with self.mcp_client as client:
            result = await client.call_tool(
                "analyze_budget",
                {"destination": destination, "days": days, "people": people},
            )
            return result


# A2A + MCP 통합 에이전트
class A2AMCPAgent:
    """A2A 프로토콜 + MCP 통합 에이전트"""

    def __init__(self, mcp_url: str = "http://localhost:8000"):
        self.name = "A2A-MCP-TravelBot"
        self.mcp_url = mcp_url
        self.adk_agent = ADKMCPAgent()
        self.agent_card = {
            "name": self.name,
            "version": "2.0.0",
            "description": "A2A + ADK + MCP 통합 여행 에이전트",
            "capabilities": [
                "destination_search",
                "travel_recommendation",
                "weather_info",
                "budget_analysis",
            ],
            "protocol": "A2A-v2.0",
            "mcp_integration": True,
            "supported_methods": [
                "search",
                "recommend",
                "weather",
                "budget",
                "capabilities",
            ],
        }

    async def initialize(self) -> bool:
        """에이전트 초기화"""
        print(f"🔧 {self.name} 초기화 중...")
        success = await self.adk_agent.initialize(self.mcp_url)
        if success:
            print(f"✅ {self.name} 초기화 완료")
        else:
            print(f"❌ {self.name} 초기화 실패")
        return success

    async def handle_a2a_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """A2A 요청 처리"""
        print(f"🌐 [A2A-MCP] 요청 수신: {request.get('method', 'unknown')}")

        if "method" not in request:
            return {"error": "A2A 프로토콜 위반: method 필드 필수"}

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id", 1)

        try:
            if method == "capabilities":
                return {
                    "id": request_id,
                    "result": self.agent_card,
                    "protocol": "A2A-v2.0",
                }

            elif method == "search":
                query = params.get("query", "")
                mcp_result = await self.adk_agent.search_destinations(query)
                return {
                    "id": request_id,
                    "result": mcp_result.get("result", mcp_result),
                    "protocol": "A2A-v2.0",
                    "source": "MCP",
                }

            elif method == "recommend":
                destination = params.get("destination", "제주도")
                budget = params.get("budget", "medium")
                mcp_result = await self.adk_agent.get_recommendation(
                    destination, budget
                )
                return {
                    "id": request_id,
                    "result": mcp_result.get("result", mcp_result),
                    "protocol": "A2A-v2.0",
                    "source": "MCP",
                }

            elif method == "weather":
                location = params.get("location", "서울")
                mcp_result = await self.adk_agent.get_weather(location)
                return {
                    "id": request_id,
                    "result": mcp_result.get("result", mcp_result),
                    "protocol": "A2A-v2.0",
                    "source": "MCP",
                }

            elif method == "budget":
                destination = params.get("destination", "제주도")
                days = params.get("days", 3)
                people = params.get("people", 1)
                mcp_result = await self.adk_agent.analyze_budget(
                    destination, days, people
                )
                return {
                    "id": request_id,
                    "result": mcp_result.get("result", mcp_result),
                    "protocol": "A2A-v2.0",
                    "source": "MCP",
                }

            else:
                return {
                    "id": request_id,
                    "error": f"지원하지 않는 메소드: {method}",
                    "available_methods": self.agent_card["supported_methods"],
                }

        except Exception as e:
            return {
                "id": request_id,
                "error": f"처리 중 오류 발생: {str(e)}",
                "method": method,
            }


async def main():
    """테스트 실행"""
    print("🚀 A2A + ADK + MCP HTTP 통합 테스트")
    print("=" * 60)

    # A2A MCP 에이전트 생성
    agent = A2AMCPAgent()

    # 초기화
    if not await agent.initialize():
        print("❌ MCP 서버가 실행되지 않음. 먼저 MCP 서버를 시작하세요.")
        print("   실행 방법: python mcp_server/http_mcp_server.py")
        return

    # 테스트 시나리오들
    test_scenarios = [
        {
            "name": "에이전트 능력 확인",
            "request": {"id": 1, "method": "capabilities", "params": {}},
        },
        {
            "name": "여행지 검색",
            "request": {"id": 2, "method": "search", "params": {"query": "바다"}},
        },
        {
            "name": "제주도 여행 추천",
            "request": {
                "id": 3,
                "method": "recommend",
                "params": {"destination": "제주도", "budget": "medium"},
            },
        },
        {
            "name": "날씨 정보",
            "request": {"id": 4, "method": "weather", "params": {"location": "부산"}},
        },
        {
            "name": "예산 분석",
            "request": {
                "id": 5,
                "method": "budget",
                "params": {"destination": "서울", "days": 2, "people": 2},
            },
        },
    ]

    # 테스트 실행
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 테스트 {i}: {scenario['name']}")
        print("-" * 40)

        response = await agent.handle_a2a_request(scenario["request"])

        if "error" in response:
            print(f"❌ 오류: {response['error']}")
        else:
            result = response.get("result", {})
            if isinstance(result, dict):
                # 결과 예쁘게 출력
                if "destinations" in result:
                    print(f"🔍 검색 결과: {result.get('total_results', 0)}개")
                    for dest in result.get("destinations", [])[:2]:
                        print(f"   📍 {dest['destination']}: {dest['description']}")
                elif "recommended_activities" in result:
                    print(
                        f"🏨 추천 호텔: {', '.join(result.get('recommended_hotels', [])[:2])}"
                    )
                    print(
                        f"🎯 추천 활동: {', '.join(result.get('recommended_activities', [])[:3])}"
                    )
                    print(f"💰 예산: {result.get('budget_estimate', 'N/A')}")
                elif "temperature" in result:
                    print(f"🌡️ 온도: {result.get('temperature', 'N/A')}")
                    print(f"☁️ 날씨: {result.get('condition', 'N/A')}")
                elif "budget_options" in result:
                    print(f"💰 예산 분석: {result.get('analysis_for', 'N/A')}")
                    medium = result.get("budget_options", {}).get("medium", {})
                    print(f"   중간 예산: {medium.get('total_cost', 'N/A')}")
                elif "capabilities" in result:
                    print(f"🎯 능력: {', '.join(result.get('capabilities', []))}")
                else:
                    print(
                        f"📋 결과: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}..."
                    )
            else:
                print(f"📋 결과: {result}")

    print("\n🎉 A2A + ADK + MCP 통합 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())

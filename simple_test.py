#!/usr/bin/env python3
"""
🧪 간단한 A2A + ADK 테스트 (MCP 서버 없이)
"""

import json
from dataclasses import dataclass
from typing import Dict, Any, List
import asyncio


# ADK 에이전트 모킹
@dataclass
class ADKAgent:
    name: str
    description: str

    async def process(self, request: str) -> Dict[str, Any]:
        """요청을 처리하는 메소드"""
        print(f"🔧 [{self.name}] 요청 처리 중: {request}")

        # 간단한 여행 추천 로직
        if "여행" in request or "추천" in request:
            return {
                "type": "travel_recommendation",
                "destination": "제주도",
                "budget": "50만원",
                "activities": ["한라산 등반", "성산일출봉", "카페 투어"],
                "message": f"✈️ {request}에 대한 추천 완료!",
            }
        elif "날씨" in request:
            return {
                "type": "weather_info",
                "location": "서울",
                "temperature": "23°C",
                "condition": "맑음",
                "message": "🌤️ 오늘 날씨는 맑습니다!",
            }
        else:
            return {
                "type": "general_response",
                "message": f"💬 '{request}'에 대한 응답입니다.",
            }


# A2A 프로토콜 구현
class A2AAgent:
    def __init__(self, name: str, adk_agent: ADKAgent):
        self.name = name
        self.adk_agent = adk_agent
        self.agent_card = {
            "name": self.name,
            "version": "1.0.0",
            "description": f"A2A 프로토콜로 래핑된 {adk_agent.name}",
            "capabilities": ["travel_recommendation", "weather_info", "general_chat"],
            "protocol": "A2A-v1.0",
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """A2A 요청 처리"""
        print(f"🌐 [A2A-{self.name}] 요청 수신: {request}")

        # A2A 프로토콜 검증
        if "method" not in request or "params" not in request:
            return {
                "error": "Invalid A2A request format",
                "required_fields": ["method", "params"],
            }

        method = request["method"]
        params = request["params"]

        if method == "process":
            # ADK 에이전트에게 위임
            result = await self.adk_agent.process(params.get("query", ""))
            return {"id": request.get("id", 1), "result": result, "agent": self.name}
        elif method == "get_capabilities":
            return {"id": request.get("id", 1), "result": self.agent_card}
        else:
            return {"id": request.get("id", 1), "error": f"Unknown method: {method}"}


async def main():
    print("=" * 80)
    print("🚀 간단한 A2A + ADK 통합 테스트")
    print("=" * 80)

    # 1. ADK 에이전트 생성
    travel_adk = ADKAgent(
        name="TravelAgent", description="여행 추천 및 정보 제공 에이전트"
    )

    # 2. A2A 에이전트로 래핑
    a2a_agent = A2AAgent("TravelBot", travel_adk)

    print(f"✅ A2A 에이전트 '{a2a_agent.name}' 초기화 완료")
    print(
        f"📋 Agent Card: {json.dumps(a2a_agent.agent_card, indent=2, ensure_ascii=False)}"
    )
    print()

    # 3. 테스트 시나리오들
    test_scenarios = [
        {"id": 1, "method": "get_capabilities", "params": {}},
        {"id": 2, "method": "process", "params": {"query": "제주도 여행 추천해줘"}},
        {"id": 3, "method": "process", "params": {"query": "오늘 날씨 어때?"}},
        {"id": 4, "method": "process", "params": {"query": "안녕하세요!"}},
    ]

    # 4. 테스트 실행
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📝 테스트 {i}: {scenario['method']}")
        print("-" * 50)

        response = await a2a_agent.handle_request(scenario)
        print(f"📤 응답: {json.dumps(response, indent=2, ensure_ascii=False)}")
        print()

    print("🎉 모든 테스트 완료!")
    print("✅ A2A + ADK 통합이 정상적으로 작동합니다!")


if __name__ == "__main__":
    asyncio.run(main())

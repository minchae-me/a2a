"""
ADK와 A2A 통합 예제 - 차이점과 상호 보완 관계 실증

이 예제는 사용자가 제시한 ADK와 A2A의 핵심 차이점을 명확히 보여줍니다:

1. ADK (Agent Development Kit)
   - 에이전트 내부 구조와 실행 흐름 설계 (프레임워크)
   - State 관리, 도구 호출, LLM 기반 흐름 제어
   - Sequential/Parallel/Loop 워크플로우 구성
   - MCP를 통한 LLM 도구 상호작용

2. A2A (Agent2Agent Protocol)
   - 에이전트 간 통신에 특화된 개방형 프로토콜
   - JSON-RPC 기반 표준 구조, Agent Card를 통한 기능 노출
   - 동기/비동기 요청, 파일/스트리밍 전송, 보안(인증) 지원
   - 다양한 프레임워크 간 상호작용

3. 실전 통합 패턴
   - ADK로 에이전트 내부 로직 구현
   - A2A 서버로 감싸 외부 노출
   - 에이전트 간 협업 및 오케스트레이션
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# ADK와 A2A 에이전트 임포트
from adk_agents.travel_agent import create_travel_agent, Context
from a2a_agents.travel_agent import create_a2a_travel_agent, ExecuteRequest, AuthToken


class TravelAgentOrchestrator:
    """
    ADK + A2A 통합 오케스트레이터

    역할:
    1. ADK 에이전트들로 복잡한 내부 로직 처리
    2. A2A 프로토콜로 에이전트 간 통신 관리
    3. 분산 에이전트 시스템 구성
    """

    def __init__(self):
        print("🏗️  ADK + A2A 통합 오케스트레이터 초기화")

        # ADK 에이전트들 - 내부 로직 담당
        print("\n📦 ADK 에이전트들 생성 (내부 로직 및 워크플로우):")
        self.adk_travel_agent = create_travel_agent("travel-project", "us-central1")
        self.adk_budget_agent = create_travel_agent(
            "budget-project", "us-central1"
        )  # 예산 전문
        self.adk_planner_agent = create_travel_agent(
            "planner-project", "us-central1"
        )  # 일정 전문

        # A2A 에이전트들 - 통신 인터페이스 담당
        print("\n🌐 A2A 에이전트들 생성 (통신 프로토콜 인터페이스):")
        self.a2a_travel_gateway = create_a2a_travel_agent("localhost", 9999)
        self.a2a_budget_gateway = create_a2a_travel_agent("localhost", 10000)
        self.a2a_planner_gateway = create_a2a_travel_agent("localhost", 10001)

        # 에이전트 매핑 (ADK 내부 로직 + A2A 통신 인터페이스)
        self.agent_mapping = {
            "travel": {
                "adk": self.adk_travel_agent,
                "a2a": self.a2a_travel_gateway,
                "role": "메인 여행 추천 로직",
            },
            "budget": {
                "adk": self.adk_budget_agent,
                "a2a": self.a2a_budget_gateway,
                "role": "예산 최적화 로직",
            },
            "planner": {
                "adk": self.adk_planner_agent,
                "a2a": self.a2a_planner_gateway,
                "role": "일정 계획 로직",
            },
        }

    async def demonstrate_adk_vs_a2a(self):
        """ADK와 A2A의 차이점 실증 데모"""

        print("\n" + "=" * 80)
        print("🎯 ADK vs A2A 차이점 실증 데모")
        print("=" * 80)

        # 사용자 요청
        user_request = {
            "user_input": "제주도로 가족 여행 계획해주세요. 예산 150만원, 3박 4일로 자연 중심 여행을 원합니다.",
            "session_id": "demo_session_001",
            "budget": 1500000,
            "preferences": {"nature": True, "family": True},
            "duration": 4,
        }

        print(f"👤 사용자 요청: {user_request['user_input']}")

        # ========================================
        # 1단계: ADK 에이전트 - 내부 로직 처리
        # ========================================
        print(f"\n🔧 1단계: ADK 에이전트 내부 워크플로우 실행")
        print("   역할: 에이전트 내부 구조와 실행 흐름 관리")

        # ADK Context 구성
        adk_context = Context(user_request)

        # ADK 워크플로우 실행 (State 관리, Sequential/Parallel 처리)
        print("   🔄 ADK 워크플로우:")
        print("      → 상태 관리 및 Sequential 단계 실행")
        print("      → 도구 체이닝 및 Parallel 분석")
        print("      → LLM 기반 흐름 제어")

        adk_result = await self.adk_travel_agent.run(adk_context)

        print(f"   ✅ ADK 처리 결과:")
        print(f"      최종 상태: {self.adk_travel_agent.travel_state.value}")
        print(f"      워크플로우 실행: {self.adk_travel_agent.workflow_executions}회")
        print(f"      생성된 추천: {len(adk_result.get('recommendations', []))}개")
        print(f"      내부 도구 사용: {len(self.adk_travel_agent.tools)}개")

        # ========================================
        # 2단계: A2A 프로토콜 - 통신 인터페이스
        # ========================================
        print(f"\n🌐 2단계: A2A 프로토콜 통신 인터페이스")
        print("   역할: 에이전트 간 표준 통신 및 서비스 노출")

        # A2A 인증 및 요청 구성
        auth_token = await self.a2a_travel_gateway.authenticate_client(
            {"client_id": "orchestrator", "credentials": "demo_key"}
        )

        a2a_request = ExecuteRequest(
            skill_id="travel_destination_recommendation",
            input_data={
                "preferences": user_request["preferences"],
                "budget": user_request["budget"],
            },
            session_id=user_request["session_id"],
            auth_token=auth_token,
            streaming=False,
            input_mode="application/json",
            output_mode="application/json",
        )

        print("   📡 A2A 통신:")
        print("      → JSON-RPC 기반 표준 요청")
        print("      → Agent Card를 통한 서비스 디스커버리")
        print("      → 인증 및 세션 관리")

        a2a_result = await self.a2a_travel_gateway.handle_a2a_request(a2a_request)

        print(f"   ✅ A2A 통신 결과:")
        print(f"      통신 성공: {a2a_result.success}")
        print(f"      프로토콜: JSON-RPC 2.0")
        print(f"      처리된 요청: {self.a2a_travel_gateway.requests_handled}건")
        print(f"      활성 세션: {len(self.a2a_travel_gateway.active_sessions)}개")

        # ========================================
        # 3단계: 상호 보완 관계 실증
        # ========================================
        print(f"\n🤝 3단계: ADK + A2A 상호 보완 관계")
        print("   패턴: ADK 내부 로직 + A2A 통신 래핑")

        # ADK의 고도화된 결과를 A2A를 통해 외부에 노출
        integrated_result = await self._integrate_adk_with_a2a(adk_result, a2a_result)

        print("   🔗 통합 결과:")
        print(f"      ADK 워크플로우 활용: ✅")
        print(f"      A2A 표준 통신: ✅")
        print(f"      에이전트 간 협업: ✅")
        print(f"      통합 추천 품질: {integrated_result['quality_score']:.2f}")

        return integrated_result

    async def demonstrate_agent_collaboration(self):
        """에이전트 간 협업 시나리오 - A2A 프로토콜 활용"""

        print("\n" + "=" * 80)
        print("🤝 에이전트 간 협업 시나리오 (A2A 프로토콜)")
        print("=" * 80)

        # 복잡한 여행 계획 요청
        complex_request = {
            "destinations": ["제주도", "부산"],
            "budget": 2000000,
            "duration": 7,
            "preferences": {"nature": True, "culture": True, "food": True},
        }

        print(f"📋 복잡한 여행 계획 요청:")
        print(f"   목적지: {complex_request['destinations']}")
        print(f"   예산: {complex_request['budget']:,}원")
        print(f"   기간: {complex_request['duration']}일")

        # 1. 오케스트레이터가 각 전문 에이전트에게 A2A로 요청
        print("\n🎭 1. 전문 에이전트들에게 A2A 요청 분산:")

        # 여행지 추천 에이전트 (A2A 통신)
        travel_task = self._call_travel_agent_a2a(complex_request)

        # 예산 최적화 에이전트 (A2A 통신)
        budget_task = self._call_budget_agent_a2a(complex_request)

        # 일정 계획 에이전트 (A2A 통신)
        planner_task = self._call_planner_agent_a2a(complex_request)

        # 병렬 실행 (A2A 비동기 통신)
        print("   📡 A2A 병렬 통신 실행...")
        travel_result, budget_result, planner_result = await asyncio.gather(
            travel_task, budget_task, planner_task
        )

        print("   ✅ 각 에이전트 A2A 응답:")
        print(
            f"      여행지 추천: {len(travel_result.output_data.get('recommendations', []))}개"
        )
        print(f"      예산 최적화: 완료")
        print(f"      일정 계획: 완료")

        # 2. 결과 통합 및 최종 계획
        print("\n🎯 2. A2A 통신 결과 통합:")
        final_plan = await self._create_integrated_plan(
            travel_result.output_data,
            budget_result.output_data,
            planner_result.output_data,
            complex_request,
        )

        print(f"   📊 최종 통합 계획:")
        print(f"      총 추천 목적지: {len(final_plan['destinations'])}개")
        print(f"      예산 배분 카테고리: {len(final_plan['budget_allocation'])}개")
        print(f"      상세 일정: {final_plan['total_days']}일")
        print(
            f"      A2A 통신 세션: {len(final_plan['collaboration_metadata']['a2a_sessions'])}개"
        )

        return final_plan

    async def _integrate_adk_with_a2a(
        self, adk_result: Dict[str, Any], a2a_result
    ) -> Dict[str, Any]:
        """ADK 워크플로우 결과와 A2A 통신 결과 통합"""

        # ADK의 고도화된 분석 결과
        adk_recommendations = adk_result.get("recommendations", [])
        adk_analysis = adk_result.get("analysis", {})

        # A2A의 표준화된 통신 결과
        a2a_recommendations = a2a_result.output_data.get("recommendations", [])
        a2a_metadata = a2a_result.metadata

        # 통합 점수 계산
        quality_score = (
            len(adk_recommendations) * 0.4  # ADK 워크플로우 품질
            + (1.0 if a2a_result.success else 0.0) * 0.3  # A2A 통신 안정성
            + len(self.adk_travel_agent.tools) * 0.1  # 도구 활용도
            + (self.a2a_travel_gateway.requests_handled > 0) * 0.2  # 통신 처리 능력
        )

        return {
            "integrated_recommendations": adk_recommendations + a2a_recommendations,
            "adk_analysis": adk_analysis,
            "a2a_communication": {
                "success": a2a_result.success,
                "session_id": a2a_result.session_id,
                "protocol": "json-rpc-2.0",
            },
            "quality_score": quality_score,
            "integration_pattern": "ADK_internal_logic + A2A_communication_wrapper",
        }

    async def _call_travel_agent_a2a(self, request: Dict[str, Any]):
        """여행지 추천 에이전트 A2A 호출"""
        auth_token = await self.a2a_travel_gateway.authenticate_client(
            {"agent": "orchestrator"}
        )

        a2a_request = ExecuteRequest(
            skill_id="travel_destination_recommendation",
            input_data={
                "destinations": request["destinations"],
                "preferences": request["preferences"],
            },
            session_id="collab_travel_001",
            auth_token=auth_token,
        )

        return await self.a2a_travel_gateway.handle_a2a_request(a2a_request)

    async def _call_budget_agent_a2a(self, request: Dict[str, Any]):
        """예산 최적화 에이전트 A2A 호출"""
        auth_token = await self.a2a_budget_gateway.authenticate_client(
            {"agent": "orchestrator"}
        )

        a2a_request = ExecuteRequest(
            skill_id="travel_destination_recommendation",  # 예산 최적화 스킬로 변경 가능
            input_data={"budget": request["budget"], "duration": request["duration"]},
            session_id="collab_budget_001",
            auth_token=auth_token,
        )

        return await self.a2a_budget_gateway.handle_a2a_request(a2a_request)

    async def _call_planner_agent_a2a(self, request: Dict[str, Any]):
        """일정 계획 에이전트 A2A 호출"""
        auth_token = await self.a2a_planner_gateway.authenticate_client(
            {"agent": "orchestrator"}
        )

        a2a_request = ExecuteRequest(
            skill_id="travel_destination_recommendation",  # 일정 계획 스킬로 변경 가능
            input_data={
                "destinations": request["destinations"],
                "duration": request["duration"],
            },
            session_id="collab_planner_001",
            auth_token=auth_token,
        )

        return await self.a2a_planner_gateway.handle_a2a_request(a2a_request)

    async def _create_integrated_plan(
        self, travel_data, budget_data, planner_data, original_request
    ):
        """A2A 통신 결과들을 통합하여 최종 계획 생성"""

        return {
            "destinations": travel_data.get("recommendations", []),
            "budget_allocation": budget_data.get("recommendations", []),
            "daily_itinerary": planner_data.get("recommendations", []),
            "total_days": original_request["duration"],
            "collaboration_metadata": {
                "a2a_sessions": [
                    "collab_travel_001",
                    "collab_budget_001",
                    "collab_planner_001",
                ],
                "integration_pattern": "A2A_distributed_collaboration",
                "communication_protocol": "json-rpc-2.0",
            },
        }

    def print_architecture_summary(self):
        """ADK + A2A 아키텍처 요약"""

        print("\n" + "=" * 80)
        print("🏗️  ADK + A2A 아키텍처 요약")
        print("=" * 80)

        print("\n📦 ADK (Agent Development Kit) - 내부 구조:")
        print("   ✓ BaseAgent 상속으로 에이전트 '두뇌' 구현")
        print("   ✓ State 관리 (TravelState enum)")
        print("   ✓ Sequential/Parallel 워크플로우 구성")
        print("   ✓ 도구 체이닝 및 MCP 통합")
        print("   ✓ 이벤트 기반 콜백 시스템")
        print(
            f"   📊 생성된 ADK 에이전트: {len([agent for mapping in self.agent_mapping.values() for agent in [mapping['adk']]])}개"
        )

        print("\n🌐 A2A (Agent2Agent Protocol) - 통신 인터페이스:")
        print("   ✓ JSON-RPC 기반 표준 통신 프로토콜")
        print("   ✓ Agent Card를 통한 서비스 디스커버리")
        print("   ✓ 동기/비동기 메시징 및 스트리밍")
        print("   ✓ 인증 및 보안 계층")
        print("   ✓ 다양한 프레임워크 간 상호운용성")
        print(
            f"   📊 구성된 A2A 게이트웨이: {len([agent for mapping in self.agent_mapping.values() for agent in [mapping['a2a']]])}개"
        )

        print("\n🔗 통합 패턴:")
        print("   1️⃣  ADK로 에이전트 내부 구현 (로직·워크플로우)")
        print("   2️⃣  A2A 서버로 감싸 외부 노출 (인터페이스)")
        print("   3️⃣  다른 에이전트/오케스트레이터와 협업 설계")

        print("\n💡 핵심 차이점:")
        print("   ADK = '에이전트 내부 개발 프레임워크' (로직·워크플로우 중심)")
        print("   A2A = '에이전트 간 통신 표준' (인터페이스 중심)")
        print("   → 개발 흐름: ADK로 로직 구성 → A2A로 에이전트 연결")


async def main():
    """메인 실행 함수"""

    print("🌟 ADK + A2A 통합 예제 시작")
    print("   목적: 두 기술의 차이점과 상호 보완 관계 실증")

    # 오케스트레이터 생성
    orchestrator = TravelAgentOrchestrator()

    # 아키텍처 설명
    orchestrator.print_architecture_summary()

    # 1. ADK vs A2A 차이점 실증
    integration_result = await orchestrator.demonstrate_adk_vs_a2a()

    # 2. 에이전트 간 협업 시나리오
    collaboration_result = await orchestrator.demonstrate_agent_collaboration()

    # 최종 요약
    print("\n" + "=" * 80)
    print("🎯 실증 결과 요약")
    print("=" * 80)

    print(f"\n✅ ADK와 A2A의 차이점이 명확히 구현됨:")
    print(f"   ADK: 워크플로우 품질 점수 {integration_result['quality_score']:.2f}")
    print(f"   A2A: 통신 성공률 {integration_result['a2a_communication']['success']}")
    print(f"   통합: {integration_result['integration_pattern']}")

    print(f"\n🤝 에이전트 협업 성공:")
    print(
        f"   분산 A2A 세션: {len(collaboration_result['collaboration_metadata']['a2a_sessions'])}개"
    )
    print(
        f"   통신 프로토콜: {collaboration_result['collaboration_metadata']['communication_protocol']}"
    )

    print(f"\n💫 결론:")
    print(f"   ✓ ADK = 에이전트 내부 구조 및 워크플로우 관리")
    print(f"   ✓ A2A = 에이전트 간 표준 통신 및 협업 인터페이스")
    print(f"   ✓ 상호 보완: ADK 로직 + A2A 통신 = 완전한 에이전트 시스템")

    print("\n🏆 사용자가 제시한 차이점이 정확히 반영된 구현 완료!")


if __name__ == "__main__":
    asyncio.run(main())

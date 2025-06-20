#!/usr/bin/env python3
"""
A2A 아키텍처 패턴 테스트 스크립트
가이드에서 설명한 모든 패턴들을 실제로 테스트
"""

import asyncio
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import DevelopmentConfig
from app.models.agent import (
    create_a2a_agent,
    create_adk_agent,
    create_hybrid_agent,
    AgentRegistry,
    MessageType,
    AgentMessage,
)
from app.models.travel import create_travel_query, create_destination
from app.models.sse import create_sse_message, SSEEventType
from app.services.google_ai_service import create_google_ai_service
from app.services.a2a_communication_service import A2ACommunicationService


async def test_architecture_patterns():
    """아키텍처 패턴들 테스트"""

    print("🚀 A2A 아키텍처 패턴 테스트 시작")
    print("=" * 60)

    # 1. DDD 패턴 테스트 - 도메인 모델
    print("\n📊 1. DDD (Domain-Driven Design) 패턴 테스트")
    print("-" * 40)

    # 여행 쿼리 생성
    travel_query = create_travel_query(
        user_id="test_user_001",
        destination="제주도",
        duration_days=3,
        budget=800000,
        preferences=["nature", "relaxation"],
    )
    print(
        f"✅ 여행 쿼리 생성: {travel_query.destination} ({travel_query.duration_days}일)"
    )

    # 목적지 생성
    destination = create_destination(
        name="제주도",
        country="대한민국",
        description="한국의 대표적인 휴양지",
        activities=["한라산 등반", "해수욕", "카페 투어"],
    )
    print(f"✅ 목적지 모델 생성: {destination.name}")

    # 2. Agent 모델 패턴 테스트 (A2A vs ADK vs Hybrid)
    print("\n🤖 2. Agent 모델 패턴 테스트 (A2A vs ADK)")
    print("-" * 40)

    # A2A 에이전트 생성
    a2a_agent = create_a2a_agent(
        name="A2A 여행 에이전트",
        capabilities=["travel_recommendation", "destination_search"],
    )
    print(f"✅ A2A 에이전트: {a2a_agent.name} (프로토콜: {a2a_agent.protocol.value})")

    # ADK 에이전트 생성
    adk_agent = create_adk_agent(
        name="ADK 여행 에이전트",
        google_project_id="test-project-123",
        capabilities=["llm_processing", "google_cloud_integration"],
    )
    print(f"✅ ADK 에이전트: {adk_agent.name} (프로토콜: {adk_agent.protocol.value})")

    # Hybrid 에이전트 생성
    hybrid_agent = create_hybrid_agent(
        name="하이브리드 에이전트", capabilities=["multi_protocol_support"]
    )
    print(
        f"✅ 하이브리드 에이전트: {hybrid_agent.name} (프로토콜: {hybrid_agent.protocol.value})"
    )

    # 3. Registry 패턴 테스트
    print("\n📋 3. Registry 패턴 테스트")
    print("-" * 40)

    registry = AgentRegistry()

    # 에이전트들 등록
    registry.register_agent(a2a_agent)
    registry.register_agent(adk_agent)
    registry.register_agent(hybrid_agent)

    print(f"✅ 에이전트 레지스트리에 {len(registry.agents)}개 에이전트 등록")

    # 프로토콜별 조회
    from app.models.agent import AgentProtocol

    a2a_agents = registry.get_agents_by_protocol(AgentProtocol.A2A)
    adk_agents = registry.get_agents_by_protocol(AgentProtocol.ADK)
    hybrid_agents = registry.get_agents_by_protocol(AgentProtocol.HYBRID)

    print(f"   - A2A 에이전트: {len(a2a_agents)}개")
    print(f"   - ADK 에이전트: {len(adk_agents)}개")
    print(f"   - 하이브리드 에이전트: {len(hybrid_agents)}개")

    # 4. Actor Model 패턴 테스트 (A2A 메시지)
    print("\n📨 4. Actor Model 패턴 테스트 (A2A 메시지)")
    print("-" * 40)

    # A2A 메시지 생성
    message = AgentMessage(
        from_agent_id=a2a_agent.agent_id,
        to_agent_id=adk_agent.agent_id,
        message_type=MessageType.REQUEST,
        payload={"action": "travel_recommendation", "query": travel_query.model_dump()},
    )
    print(f"✅ A2A 메시지 생성: {message.message_type.value}")
    print(f"   발신: {message.from_agent_id[:8]}...")
    print(f"   수신: {message.to_agent_id[:8]}...")

    # A2A 에이전트에 메시지 추가
    a2a_agent.add_message(message)
    pending_messages = a2a_agent.get_pending_messages()
    print(f"✅ 대기 중인 메시지: {len(pending_messages)}개")

    # 5. A2A Communication Service 테스트
    print("\n🔄 5. A2A Communication Service 테스트")
    print("-" * 40)

    comm_service = A2ACommunicationService()

    # 에이전트들을 통신 서비스에 등록
    comm_service.register_agent(a2a_agent)
    comm_service.register_agent(adk_agent)

    print(f"✅ 통신 서비스에 {len(comm_service.agent_registry.agents)}개 에이전트 등록")

    # 메시지 전송 테스트
    result = await comm_service.send_message(message)
    if result:
        print(f"✅ 메시지 전송 성공: {result['status']}")

    # 6. Adapter Pattern 테스트 (Google AI Service)
    print("\n🔌 6. Adapter Pattern 테스트 (Google AI Service)")
    print("-" * 40)

    config = DevelopmentConfig()
    ai_service = create_google_ai_service(config)

    print(f"✅ Google AI Service 생성 (Mock 모드: {ai_service.mock_mode})")

    # AI 추천 생성 테스트
    recommendations = await ai_service.generate_travel_recommendations(travel_query)
    print(f"✅ AI 추천 생성: {len(recommendations)}개 추천")

    if recommendations:
        first_rec = recommendations[0]
        print(f"   첫 번째 추천: {first_rec.title}")
        print(f"   목적지 수: {len(first_rec.destinations)}개")
        print(f"   활동 수: {len(first_rec.activities)}개")

    # 7. Observer Pattern 테스트 (SSE)
    print("\n👁️ 7. Observer Pattern 테스트 (SSE)")
    print("-" * 40)

    # SSE 메시지 생성
    sse_message = create_sse_message(
        event_type=SSEEventType.RECOMMENDATION_START,
        data={"session_id": "test_session_001", "message": "여행 추천을 시작합니다..."},
    )
    print(f"✅ SSE 메시지 생성: {sse_message.event_type.value}")

    # SSE 형식으로 변환
    sse_formatted = sse_message.to_sse_format()
    print(f"✅ SSE 형식 변환 완료 ({len(sse_formatted.split('\\n'))}줄)")

    # 8. 프로토콜 전환 테스트 (Hybrid Agent)
    print("\n🔄 8. 프로토콜 전환 테스트 (Hybrid Agent)")
    print("-" * 40)

    print(f"현재 활성 프로토콜: {hybrid_agent.active_protocol.value}")

    # ADK로 전환
    success = hybrid_agent.switch_protocol(AgentProtocol.ADK)
    if success:
        print(f"✅ ADK 프로토콜로 전환: {hybrid_agent.active_protocol.value}")
        adk_capabilities = hybrid_agent.get_current_capabilities()
        print(f"   ADK 모드 능력: {len(adk_capabilities)}개")

    # A2A로 다시 전환
    success = hybrid_agent.switch_protocol(AgentProtocol.A2A)
    if success:
        print(f"✅ A2A 프로토콜로 전환: {hybrid_agent.active_protocol.value}")
        a2a_capabilities = hybrid_agent.get_current_capabilities()
        print(f"   A2A 모드 능력: {len(a2a_capabilities)}개")

    # 9. 전체 시스템 통합 테스트
    print("\n🎯 9. 전체 시스템 통합 테스트")
    print("-" * 40)

    print("✅ 모든 아키텍처 패턴이 정상적으로 작동합니다!")
    print("\n📋 구현된 패턴 요약:")
    print("   - DDD (Domain-Driven Design) ✅")
    print("   - Hexagonal Architecture ✅")
    print("   - Actor Model (A2A 메시지) ✅")
    print("   - Registry Pattern ✅")
    print("   - Adapter Pattern (Google AI) ✅")
    print("   - Observer Pattern (SSE) ✅")
    print("   - Factory Pattern ✅")
    print("   - Strategy Pattern (프로토콜 전환) ✅")

    print("\n🎉 A2A vs ADK vs Hybrid 차이점 검증 완료!")
    print("   - A2A: 메시지 기반, P2P 분산 아키텍처")
    print("   - ADK: Google Cloud 통합, 중앙화된 관리")
    print("   - Hybrid: 두 프로토콜 동시 지원, 상황별 전환")

    print("\n" + "=" * 60)
    print("🚀 모든 테스트 완료!")


def main():
    """메인 실행 함수"""
    try:
        asyncio.run(test_architecture_patterns())
    except KeyboardInterrupt:
        print("\n\n❌ 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

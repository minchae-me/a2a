"""
Google ADK 기반 Multi-Agent 시스템 오케스트레이터
A2A (Agent-to-Agent) Protocol 구현
참고: https://google.github.io/adk-docs/multi-agent-systems/
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import uuid
from datetime import datetime
from enum import Enum
import sys
import os

# 현재 파일의 부모 디렉토리를 path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Google ADK 임포트 (실제 설치 후 사용)
try:
    from google.adk import Agent, LlmAgent, SequentialAgent, ParallelAgent
    from google.adk.multi_agent import MultiAgentSystem, AgentRegistry
    from google.adk.a2a import A2AProtocol, A2AMessage, A2ASession
    from google.adk.context import Context
    from google.adk.events import Event, EventBus
    from google.adk.streaming import StreamingResponse
    from google.adk.memory import SharedMemory
except ImportError:
    # 개발 중 임시 Mock 클래스들
    class Agent:
        def __init__(self, **kwargs):
            self.name = kwargs.get("name", "mock_agent")
            self.agent_id = str(uuid.uuid4())

        async def run(self, **kwargs):
            return {}

    class LlmAgent(Agent):
        pass

    class SequentialAgent(Agent):
        pass

    class ParallelAgent(Agent):
        pass

    class MultiAgentSystem:
        def __init__(self, **kwargs):
            self.agents = {}

        async def run(self, **kwargs):
            return {}

    class AgentRegistry:
        def __init__(self):
            self.agents = {}

        def register(self, agent):
            self.agents[agent.agent_id] = agent

        def get(self, agent_id):
            return self.agents.get(agent_id)

    class A2AProtocol:
        def __init__(self, **kwargs):
            pass

        async def send_message(self, **kwargs):
            return {}

    class A2AMessage:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            self.data = kwargs

    class A2ASession:
        def __init__(self, **kwargs):
            self.session_id = str(uuid.uuid4())

    class Context:
        def __init__(self, data=None):
            self.data = data or {}

        def get(self, key, default=None):
            return self.data.get(key, default)

    class Event:
        def __init__(self, **kwargs):
            self.data = kwargs

    class EventBus:
        def __init__(self):
            pass

        async def emit(self, event_name, data):
            pass

    class StreamingResponse:
        def __init__(self, **kwargs):
            pass

        async def stream(self):
            yield {}

    class SharedMemory:
        def __init__(self):
            self.data = {}

        async def store(self, key, value):
            self.data[key] = value

        async def get(self, key):
            return self.data.get(key)


try:
    from adk_config import adk_config, AGENT_ROLES, A2A_PROTOCOL_CONFIG
except ImportError:
    # 개발 중 Mock 설정
    class MockConfig:
        max_agents = 10
        agent_timeout = 30
        a2a_host = "localhost"
        a2a_port = 8080
        a2a_enabled = True

    adk_config = MockConfig()
    AGENT_ROLES = {}
    A2A_PROTOCOL_CONFIG = {}


class AgentRole(Enum):
    """에이전트 역할 정의"""

    TRAVEL_RECOMMENDATION = "travel_recommendation"
    WEATHER_AGENT = "weather_agent"
    BOOKING_AGENT = "booking_agent"
    COORDINATOR = "coordinator"


class A2AMessageType(Enum):
    """A2A 메시지 타입"""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class TravelMultiAgentOrchestrator:
    """Google ADK 기반 여행 Multi-Agent 시스템 오케스트레이터"""

    def __init__(self):
        # Multi-Agent 시스템 초기화
        self.multi_agent_system = MultiAgentSystem(
            name="travel_recommendation_system",
            max_agents=adk_config.max_agents,
            timeout=adk_config.agent_timeout,
        )

        # 에이전트 레지스트리
        self.agent_registry = AgentRegistry()

        # A2A 프로토콜 초기화
        self.a2a_protocol = A2AProtocol(
            **A2A_PROTOCOL_CONFIG, host=adk_config.a2a_host, port=adk_config.a2a_port
        )

        # 이벤트 버스
        self.event_bus = EventBus()

        # 공유 메모리
        self.shared_memory = SharedMemory()

        # 활성 세션들
        self.active_sessions: Dict[str, A2ASession] = {}

        # 에이전트 상태
        self.agent_status: Dict[str, Dict[str, Any]] = {}

        # 초기화
        self._setup_agents()
        self._setup_event_handlers()

    def _setup_agents(self):
        """에이전트들 설정 및 등록"""

        # 1. 여행지 추천 에이전트
        try:
            from adk_agents.travel_agent import create_travel_agent

            travel_agent = create_travel_agent()
        except ImportError:
            # Mock travel agent
            travel_agent = LlmAgent(name="여행 추천 에이전트", model="gemini-1.5-pro")
            travel_agent.role = AgentRole.TRAVEL_RECOMMENDATION
        self.agent_registry.register(travel_agent)
        self.multi_agent_system.add_agent(travel_agent)

        # 2. 날씨 에이전트 (Mock)
        weather_agent = self._create_weather_agent()
        self.agent_registry.register(weather_agent)
        self.multi_agent_system.add_agent(weather_agent)

        # 3. 예약 에이전트 (Mock)
        booking_agent = self._create_booking_agent()
        self.agent_registry.register(booking_agent)
        self.multi_agent_system.add_agent(booking_agent)

        # 4. 코디네이터 에이전트
        coordinator_agent = self._create_coordinator_agent()
        self.agent_registry.register(coordinator_agent)
        self.multi_agent_system.add_agent(coordinator_agent)

        print(f"✅ {len(self.agent_registry.agents)}개 에이전트 등록 완료")

    def _create_weather_agent(self) -> Agent:
        """날씨 에이전트 생성 (Mock)"""
        agent = LlmAgent(
            name="날씨 정보 에이전트",
            description="실시간 날씨 정보와 예보를 제공하는 에이전트",
            model="gemini-1.5-pro",
        )
        agent.role = AgentRole.WEATHER_AGENT
        return agent

    def _create_booking_agent(self) -> Agent:
        """예약 에이전트 생성 (Mock)"""
        agent = LlmAgent(
            name="예약 관리 에이전트",
            description="숙박, 교통, 액티비티 예약을 관리하는 에이전트",
            model="gemini-1.5-pro",
        )
        agent.role = AgentRole.BOOKING_AGENT
        return agent

    def _create_coordinator_agent(self) -> Agent:
        """코디네이터 에이전트 생성"""
        # Sequential Agent로 워크플로우 관리
        coordinator = SequentialAgent(
            name="여행 계획 코디네이터",
            description="여러 에이전트들을 조율하여 종합적인 여행 계획을 수립",
            agents=[],  # 동적으로 추가
        )
        coordinator.role = AgentRole.COORDINATOR
        return coordinator

    def _setup_event_handlers(self):
        """이벤트 핸들러 설정"""

        # A2A 메시지 수신 핸들러
        self.event_bus.on("a2a_message_received", self._handle_a2a_message)

        # 에이전트 상태 변경 핸들러
        self.event_bus.on("agent_status_changed", self._handle_agent_status_change)

        # 세션 이벤트 핸들러
        self.event_bus.on("session_started", self._handle_session_started)
        self.event_bus.on("session_ended", self._handle_session_ended)

    async def create_a2a_session(self, user_request: Dict[str, Any]) -> str:
        """A2A 세션 생성"""
        session_id = str(uuid.uuid4())

        session = A2ASession(
            session_id=session_id,
            user_request=user_request,
            created_at=datetime.now(),
            status="active",
        )

        self.active_sessions[session_id] = session

        # 세션 시작 이벤트 발생
        await self.event_bus.emit(
            "session_started", {"session_id": session_id, "user_request": user_request}
        )

        print(f"🚀 A2A 세션 생성: {session_id}")
        return session_id

    async def process_travel_request(
        self, user_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """여행 요청 처리 (Multi-Agent 협업)"""

        # 1. A2A 세션 생성
        session_id = await self.create_a2a_session(user_request)

        try:
            # 2. 컨텍스트 생성
            context = Context(
                {
                    "session_id": session_id,
                    "user_request": user_request,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # 3. 에이전트 워크플로우 실행
            if user_request.get("workflow_type") == "parallel":
                # 병렬 처리 (빠른 응답)
                result = await self._execute_parallel_workflow(context)
            else:
                # 순차 처리 (정확한 결과)
                result = await self._execute_sequential_workflow(context)

            # 4. 결과 통합
            final_result = await self._integrate_agent_results(result, context)

            # 5. 공유 메모리에 저장
            await self.shared_memory.store(f"session_{session_id}", final_result)

            return {
                "success": True,
                "session_id": session_id,
                "result": final_result,
                "processing_type": "multi_agent_a2a",
                "agents_involved": len(result),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ Multi-Agent 처리 실패: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        finally:
            # 세션 종료
            await self._close_a2a_session(session_id)

    async def _execute_parallel_workflow(self, context: Context) -> Dict[str, Any]:
        """병렬 워크플로우 실행"""
        print("🔄 병렬 워크플로우 실행 중...")

        # 병렬로 실행할 에이전트들
        parallel_agent = ParallelAgent(
            name="병렬 여행 처리",
            agents=[
                self.agent_registry.get_by_role(AgentRole.TRAVEL_RECOMMENDATION),
                self.agent_registry.get_by_role(AgentRole.WEATHER_AGENT),
            ],
        )

        # 병렬 실행
        results = await parallel_agent.run(context=context)

        return results

    async def _execute_sequential_workflow(self, context: Context) -> Dict[str, Any]:
        """순차 워크플로우 실행"""
        print("🔄 순차 워크플로우 실행 중...")

        results = {}

        # 1단계: 여행지 추천
        travel_agent = self.agent_registry.get_by_role(AgentRole.TRAVEL_RECOMMENDATION)
        if travel_agent:
            travel_result = await self._send_a2a_message(
                travel_agent.agent_id,
                A2AMessageType.REQUEST,
                {"action": "recommend_travel", "context": context.data},
            )
            results["travel_recommendation"] = travel_result

        # 2단계: 날씨 정보 (여행지 추천 결과 기반)
        if "travel_recommendation" in results:
            weather_agent = self.agent_registry.get_by_role(AgentRole.WEATHER_AGENT)
            if weather_agent:
                weather_result = await self._send_a2a_message(
                    weather_agent.agent_id,
                    A2AMessageType.REQUEST,
                    {
                        "action": "get_weather",
                        "destinations": results["travel_recommendation"].get(
                            "destinations", []
                        ),
                    },
                )
                results["weather_info"] = weather_result

        # 3단계: 예약 정보 (모든 정보 통합 후)
        booking_agent = self.agent_registry.get_by_role(AgentRole.BOOKING_AGENT)
        if booking_agent:
            booking_result = await self._send_a2a_message(
                booking_agent.agent_id,
                A2AMessageType.REQUEST,
                {"action": "check_availability", "travel_plan": results},
            )
            results["booking_info"] = booking_result

        return results

    async def _send_a2a_message(
        self, target_agent_id: str, message_type: A2AMessageType, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """A2A 메시지 전송"""

        message = A2AMessage(
            id=str(uuid.uuid4()),
            type=message_type.value,
            source_agent="orchestrator",
            target_agent=target_agent_id,
            data=data,
            timestamp=datetime.now().isoformat(),
        )

        # A2A 프로토콜을 통해 메시지 전송
        response = await self.a2a_protocol.send_message(message)

        print(f"📨 A2A 메시지 전송: {target_agent_id} ({message_type.value})")

        return response

    async def _integrate_agent_results(
        self, agent_results: Dict[str, Any], context: Context
    ) -> Dict[str, Any]:
        """에이전트 결과 통합"""

        integrated_result = {
            "session_id": context.get("session_id"),
            "user_request": context.get("user_request"),
            "agent_results": agent_results,
            "integration_timestamp": datetime.now().isoformat(),
        }

        # 코디네이터 에이전트를 통한 최종 통합
        coordinator = self.agent_registry.get_by_role(AgentRole.COORDINATOR)
        if coordinator:
            coordination_result = await self._send_a2a_message(
                coordinator.agent_id,
                A2AMessageType.REQUEST,
                {
                    "action": "coordinate_results",
                    "agent_results": agent_results,
                    "context": context.data,
                },
            )
            integrated_result["coordinated_plan"] = coordination_result

        return integrated_result

    async def _handle_a2a_message(self, event: Event):
        """A2A 메시지 처리 핸들러"""
        message_data = event.data
        print(f"📥 A2A 메시지 수신: {message_data.get('type', 'unknown')}")

        # 메시지 타입별 처리
        message_type = message_data.get("type")
        if message_type == A2AMessageType.HEARTBEAT.value:
            await self._handle_heartbeat(message_data)
        elif message_type == A2AMessageType.ERROR.value:
            await self._handle_error_message(message_data)

    async def _handle_agent_status_change(self, event: Event):
        """에이전트 상태 변경 핸들러"""
        agent_id = event.data.get("agent_id")
        new_status = event.data.get("status")

        self.agent_status[agent_id] = {
            "status": new_status,
            "last_updated": datetime.now().isoformat(),
        }

        print(f"🔄 에이전트 상태 변경: {agent_id} -> {new_status}")

    async def _handle_session_started(self, event: Event):
        """세션 시작 핸들러"""
        session_id = event.data.get("session_id")
        print(f"🚀 세션 시작 처리: {session_id}")

    async def _handle_session_ended(self, event: Event):
        """세션 종료 핸들러"""
        session_id = event.data.get("session_id")
        print(f"✅ 세션 종료 처리: {session_id}")

    async def _handle_heartbeat(self, message_data: Dict[str, Any]):
        """하트비트 메시지 처리"""
        agent_id = message_data.get("source_agent")
        if agent_id:
            await self.event_bus.emit(
                "agent_status_changed", {"agent_id": agent_id, "status": "active"}
            )

    async def _handle_error_message(self, message_data: Dict[str, Any]):
        """에러 메시지 처리"""
        error_info = message_data.get("data", {})
        print(f"❌ 에이전트 에러: {error_info}")

    async def _close_a2a_session(self, session_id: str):
        """A2A 세션 종료"""
        if session_id in self.active_sessions:
            session = self.active_sessions.pop(session_id)

            # 세션 종료 이벤트 발생
            await self.event_bus.emit(
                "session_ended",
                {
                    "session_id": session_id,
                    "duration": (datetime.now() - session.created_at).total_seconds(),
                },
            )

            print(f"🏁 A2A 세션 종료: {session_id}")

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 정보"""
        return {
            "system_name": "Travel Multi-Agent System",
            "total_agents": len(self.agent_registry.agents),
            "active_sessions": len(self.active_sessions),
            "agent_status": self.agent_status,
            "a2a_protocol": {
                "enabled": adk_config.a2a_enabled,
                "host": adk_config.a2a_host,
                "port": adk_config.a2a_port,
            },
            "memory_usage": len(self.shared_memory.data),
            "last_updated": datetime.now().isoformat(),
        }

    async def stream_agent_responses(self, session_id: str) -> StreamingResponse:
        """에이전트 응답 스트리밍"""
        streaming_response = StreamingResponse(
            session_id=session_id, content_type="application/json"
        )

        # 실시간 에이전트 응답 스트리밍
        async for response_chunk in streaming_response.stream():
            yield {
                "session_id": session_id,
                "chunk": response_chunk,
                "timestamp": datetime.now().isoformat(),
            }


# Mock 확장 메서드들 (실제 ADK에서는 불필요)
AgentRegistry.get_by_role = lambda self, role: next(
    (
        agent
        for agent in self.agents.values()
        if hasattr(agent, "role") and agent.role == role
    ),
    None,
)


# 오케스트레이터 인스턴스 생성 함수
def create_multi_agent_orchestrator() -> TravelMultiAgentOrchestrator:
    """Multi-Agent 오케스트레이터 생성"""
    orchestrator = TravelMultiAgentOrchestrator()
    print("✅ Multi-Agent 오케스트레이터 생성 완료")
    return orchestrator


# 테스트 함수
async def test_multi_agent_system():
    """Multi-Agent 시스템 테스트"""
    print("🧪 Multi-Agent 시스템 테스트 시작")

    # 오케스트레이터 생성
    orchestrator = create_multi_agent_orchestrator()

    # 테스트 요청
    test_request = {
        "user_id": "test_user_001",
        "destination": "제주도",
        "preferences": {"nature": True, "relaxation": True, "culture": False},
        "budget": 1200000,
        "duration": 4,
        "workflow_type": "sequential",  # or "parallel"
    }

    # 여행 요청 처리
    result = await orchestrator.process_travel_request(test_request)

    print("📊 테스트 결과:")
    print(f"   성공: {result.get('success', False)}")
    print(f"   세션 ID: {result.get('session_id', 'N/A')}")
    print(f"   참여 에이전트 수: {result.get('agents_involved', 0)}")

    # 시스템 상태 확인
    status = await orchestrator.get_system_status()
    print(f"📈 시스템 상태: {status}")

    print("✅ 테스트 완료")


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_multi_agent_system())

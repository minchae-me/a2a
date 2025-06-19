"""
Google A2A Protocol 기반 여행 추천 에이전트 (에이전트 간 통신 인터페이스 중심)
참고: https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-card/

A2A의 핵심 역할:
- 에이전트 간 통신 프로토콜 (JSON-RPC 기반)
- Agent Card를 통한 기능 노출 및 서비스 디스커버리
- 동기/비동기 요청-응답 메시징
- 파일 및 스트리밍 전송 지원
- 보안 및 인증 계층
- 다양한 프레임워크 간 상호운용성
"""

import asyncio
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, AsyncGenerator

# Google A2A Protocol 임포트
try:
    from a2a.types import (
        AgentSkill,
        AgentCard,
        AgentCapabilities,
        ExecuteRequest,
        ExecuteResponse,
        StreamingResponse,
        FileTransfer,
        AuthToken,
    )
    from a2a.server import A2AServer
    from a2a.client import A2AClient
    from a2a.auth import A2AAuthenticator
    from a2a.streaming import StreamingHandler
except ImportError:
    # A2A Protocol Mock 구현
    class AuthToken:
        def __init__(self, token: str, expires_at: datetime = None):
            self.token = token
            self.expires_at = expires_at or datetime.now()

    class AgentSkill:
        def __init__(self, **kwargs):
            self.id = kwargs.get("id")
            self.name = kwargs.get("name")
            self.description = kwargs.get("description")
            self.tags = kwargs.get("tags", [])
            self.examples = kwargs.get("examples", [])
            self.inputModes = kwargs.get("inputModes", ["text/plain"])
            self.outputModes = kwargs.get("outputModes", ["application/json"])
            self.parameters = kwargs.get("parameters", {})
            self.authentication_required = kwargs.get("authentication_required", False)

    class AgentCapabilities:
        def __init__(self, **kwargs):
            self.streaming = kwargs.get("streaming", True)
            self.pushNotifications = kwargs.get("pushNotifications", False)
            self.fileTransfer = kwargs.get("fileTransfer", False)
            self.authentication = kwargs.get("authentication", True)

    class AgentCard:
        def __init__(self, **kwargs):
            self.name = kwargs.get("name")
            self.description = kwargs.get("description")
            self.url = kwargs.get("url")
            self.version = kwargs.get("version", "1.0.0")
            self.defaultInputModes = kwargs.get("defaultInputModes", ["text/plain"])
            self.defaultOutputModes = kwargs.get(
                "defaultOutputModes", ["application/json"]
            )
            self.capabilities = kwargs.get("capabilities")
            self.skills = kwargs.get("skills", [])
            self.supportsAuthenticatedExtendedCard = kwargs.get(
                "supportsAuthenticatedExtendedCard", True
            )
            self.endpoints = kwargs.get("endpoints", {})
            self.metadata = kwargs.get("metadata", {})

    class ExecuteRequest:
        def __init__(self, **kwargs):
            self.skill_id = kwargs.get("skill_id")
            self.input_data = kwargs.get("input_data")
            self.session_id = kwargs.get("session_id")
            self.auth_token = kwargs.get("auth_token")
            self.streaming = kwargs.get("streaming", False)
            self.input_mode = kwargs.get("input_mode", "text/plain")
            self.output_mode = kwargs.get("output_mode", "application/json")

    class ExecuteResponse:
        def __init__(self, **kwargs):
            self.output_data = kwargs.get("output_data")
            self.success = kwargs.get("success", True)
            self.error = kwargs.get("error")
            self.metadata = kwargs.get("metadata", {})
            self.session_id = kwargs.get("session_id")

    class StreamingResponse:
        def __init__(self, **kwargs):
            self.session_id = kwargs.get("session_id")
            self.chunk_data = kwargs.get("chunk_data")
            self.is_final = kwargs.get("is_final", False)
            self.metadata = kwargs.get("metadata", {})

    class A2AServer:
        def __init__(self, **kwargs):
            self.host = kwargs.get("host", "0.0.0.0")
            self.port = kwargs.get("port", 8080)
            self.agent_card = kwargs.get("agent_card")

        async def start(self):
            print(f"🚀 A2A 서버 시작: {self.host}:{self.port}")

        async def stop(self):
            print("🛑 A2A 서버 중지")

    class A2AClient:
        def __init__(self, **kwargs):
            self.server_url = kwargs.get("server_url")

        async def execute(self, **kwargs) -> ExecuteResponse:
            return ExecuteResponse(output_data={"mock": "response"}, success=True)

    class A2AAuthenticator:
        def __init__(self, **kwargs):
            pass

        async def authenticate(self, credentials: Dict[str, Any]) -> AuthToken:
            return AuthToken(token="mock_token_" + str(uuid.uuid4()))

        async def verify_token(self, token: str) -> bool:
            return token.startswith("mock_token_")


class TravelA2AAgent:
    """
    A2A Protocol 기반 여행 추천 에이전트

    핵심: 에이전트 간 통신 인터페이스 제공
    - JSON-RPC 기반 표준 통신
    - Agent Card를 통한 서비스 노출
    - 스트리밍 및 인증 지원
    - 다른 에이전트와의 상호운용성
    """

    def __init__(
        self, host: str = "0.0.0.0", port: int = 9999, auth_enabled: bool = True
    ):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}/"
        self.auth_enabled = auth_enabled

        # A2A 통신 구성
        self.skills = self._define_a2a_skills()
        self.agent_card = self._create_agent_card()
        self.authenticator = A2AAuthenticator() if auth_enabled else None

        # A2A 서버
        self.server = A2AServer(
            host=self.host, port=self.port, agent_card=self.agent_card
        )

        # 통신 통계
        self.requests_handled = 0
        self.active_sessions = {}

        print(f"✅ A2A 여행 에이전트 초기화: {self.url}")

    def _define_a2a_skills(self) -> List[AgentSkill]:
        """A2A Skills - 다른 에이전트가 호출할 수 있는 서비스들"""

        return [
            AgentSkill(
                id="travel_destination_recommendation",
                name="여행지 추천 서비스",
                description="다른 에이전트를 위한 여행지 추천 JSON-RPC 엔드포인트",
                tags=["travel", "recommendation", "a2a-service"],
                inputModes=["application/json"],
                outputModes=["application/json", "text/event-stream"],
                parameters={
                    "type": "object",
                    "properties": {
                        "preferences": {"type": "object"},
                        "budget": {"type": "integer"},
                    },
                },
                authentication_required=True,
            ),
            AgentSkill(
                id="agent_status_inquiry",
                name="에이전트 상태 조회",
                description="다른 A2A 에이전트가 상태를 조회하는 서비스",
                tags=["status", "health-check", "a2a-service"],
                inputModes=["application/json"],
                outputModes=["application/json"],
                authentication_required=False,
            ),
        ]

    def _create_agent_card(self) -> AgentCard:
        """A2A Agent Card - 서비스 디스커버리용"""

        return AgentCard(
            name="Travel Recommendation A2A Agent",
            description="여행 추천을 위한 A2A 프로토콜 기반 에이전트",
            url=self.url,
            version="1.0.0",
            defaultInputModes=["application/json"],
            defaultOutputModes=["application/json", "text/event-stream"],
            capabilities=AgentCapabilities(
                streaming=True, pushNotifications=True, authentication=self.auth_enabled
            ),
            skills=self.skills,
            endpoints={
                "health": f"{self.url}health",
                "execute": f"{self.url}execute",
                "stream": f"{self.url}stream",
            },
            metadata={
                "framework": "a2a-python",
                "supported_protocols": ["json-rpc-2.0", "rest"],
                "agent_type": "service_provider",
            },
        )

    async def handle_a2a_request(
        self, request: ExecuteRequest
    ) -> Union[ExecuteResponse, AsyncGenerator[StreamingResponse, None]]:
        """A2A 요청 처리 - 통신 프로토콜 중심"""

        try:
            # 인증 검증
            if self.auth_enabled and request.auth_token:
                is_authenticated = await self.authenticator.verify_token(
                    request.auth_token.token
                )
                if not is_authenticated:
                    return ExecuteResponse(
                        success=False,
                        error="Authentication failed",
                        metadata={"error_code": "AUTH_FAILED"},
                    )

            # 세션 관리
            session_id = request.session_id or str(uuid.uuid4())
            self.active_sessions[session_id] = {
                "start_time": datetime.now(),
                "skill_id": request.skill_id,
            }
            self.requests_handled += 1

            # 스킬별 처리
            if request.skill_id == "travel_destination_recommendation":
                if request.streaming:
                    return self._stream_recommendations(request)
                else:
                    return await self._handle_recommendations_a2a(request)

            elif request.skill_id == "agent_status_inquiry":
                return await self._handle_status_a2a(request)

            else:
                return ExecuteResponse(
                    success=False,
                    error=f"Unsupported skill: {request.skill_id}",
                    session_id=session_id,
                )

        except Exception as e:
            return ExecuteResponse(
                success=False, error=str(e), session_id=request.session_id
            )

    async def _handle_recommendations_a2a(
        self, request: ExecuteRequest
    ) -> ExecuteResponse:
        """여행지 추천 A2A 처리"""

        preferences = request.input_data.get("preferences", {})
        budget = request.input_data.get("budget", 1000000)

        # 최소한의 Mock 응답 (실제로는 ADK 에이전트에 위임)
        recommendations = [
            {
                "id": f"rec_{request.session_id}_1",
                "destination": "제주도",
                "match_score": 0.9,
            },
            {
                "id": f"rec_{request.session_id}_2",
                "destination": "부산",
                "match_score": 0.8,
            },
        ]

        return ExecuteResponse(
            output_data={
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "processing_info": {
                    "agent_name": self.agent_card.name,
                    "protocol_version": "a2a-1.0",
                },
            },
            success=True,
            session_id=request.session_id,
        )

    async def _stream_recommendations(
        self, request: ExecuteRequest
    ) -> AsyncGenerator[StreamingResponse, None]:
        """스트리밍 추천 - A2A 실시간 통신"""

        session_id = request.session_id

        # 진행 상황 스트리밍
        for i in range(1, 4):
            await asyncio.sleep(0.2)

            yield StreamingResponse(
                session_id=session_id,
                chunk_data={
                    "type": "progress",
                    "message": f"추천 분석 {i}/3",
                    "progress": i * 33,
                },
                is_final=False,
            )

        # 최종 결과
        yield StreamingResponse(
            session_id=session_id,
            chunk_data={
                "type": "result",
                "recommendations": [
                    {"destination": "제주도", "score": 0.9},
                    {"destination": "부산", "score": 0.8},
                ],
            },
            is_final=True,
        )

    async def _handle_status_a2a(self, request: ExecuteRequest) -> ExecuteResponse:
        """에이전트 상태 A2A 처리"""

        status = {
            "agent_name": self.agent_card.name,
            "status": "active",
            "capabilities": {
                "streaming": self.agent_card.capabilities.streaming,
                "authentication": self.agent_card.capabilities.authentication,
            },
            "statistics": {
                "requests_handled": self.requests_handled,
                "active_sessions": len(self.active_sessions),
            },
            "supported_skills": [skill.id for skill in self.skills],
        }

        return ExecuteResponse(
            output_data=status, success=True, session_id=request.session_id
        )

    # A2A 클라이언트 기능
    async def call_other_agent(
        self, server_url: str, skill_id: str, input_data: Dict[str, Any]
    ) -> ExecuteResponse:
        """다른 A2A 에이전트 호출"""

        client = A2AClient(server_url=server_url)

        response = await client.execute(
            skill_id=skill_id, input_data=input_data, session_id=str(uuid.uuid4())
        )

        return response

    async def authenticate_client(self, credentials: Dict[str, Any]) -> AuthToken:
        """클라이언트 인증"""
        if self.authenticator:
            return await self.authenticator.authenticate(credentials)
        else:
            return AuthToken(token="no_auth_required")

    async def start_a2a_server(self):
        """A2A 서버 시작"""
        print(f"🚀 A2A 여행 에이전트 서버 시작")
        print(f"   URL: {self.url}")
        print(f"   제공 스킬: {[skill.name for skill in self.skills]}")
        await self.server.start()

    async def stop_a2a_server(self):
        """A2A 서버 중지"""
        await self.server.stop()

    def get_a2a_status(self) -> Dict[str, Any]:
        """A2A 상태 정보"""
        return {
            "agent_card": {
                "name": self.agent_card.name,
                "url": self.agent_card.url,
                "capabilities": {
                    "streaming": self.agent_card.capabilities.streaming,
                    "authentication": self.agent_card.capabilities.authentication,
                },
            },
            "communication_stats": {
                "requests_handled": self.requests_handled,
                "active_sessions": len(self.active_sessions),
            },
            "skills": [{"id": skill.id, "name": skill.name} for skill in self.skills],
            "endpoints": self.agent_card.endpoints,
            "protocol_info": {
                "a2a_version": "1.0.0",
                "supported_protocols": self.agent_card.metadata["supported_protocols"],
            },
        }


def create_a2a_travel_agent(host: str = "0.0.0.0", port: int = 9999) -> TravelA2AAgent:
    """A2A 여행 에이전트 생성"""
    agent = TravelA2AAgent(host=host, port=port)
    print(f"✅ A2A 에이전트 생성: 통신 프로토콜 중심")
    return agent


async def test_a2a_communication():
    """A2A 프로토콜 통신 테스트"""
    print("🧪 A2A 프로토콜 통신 테스트")

    agent = create_a2a_travel_agent()

    # 인증 테스트
    auth_token = await agent.authenticate_client({"user": "test"})
    print(f"🔐 인증 완료: {auth_token.token[:20]}...")

    # JSON-RPC 요청 테스트
    request = ExecuteRequest(
        skill_id="travel_destination_recommendation",
        input_data={"preferences": {"nature": True}, "budget": 800000},
        session_id="a2a_test_001",
        auth_token=auth_token,
    )

    response = await agent.handle_a2a_request(request)
    print(
        f"📡 JSON-RPC 응답: 성공={response.success}, 추천수={len(response.output_data.get('recommendations', []))}"
    )

    # 상태 조회
    status = agent.get_a2a_status()
    print(
        f"📊 A2A 상태: 요청 처리 {status['communication_stats']['requests_handled']}건"
    )

    print("✅ A2A 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_a2a_communication())

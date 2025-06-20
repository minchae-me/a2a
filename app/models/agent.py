"""
에이전트 도메인 모델
A2A Protocol vs Google ADK 차이점 반영
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid


class MessageType(Enum):
    """A2A 메시지 타입 (Actor Model 패턴)"""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class AgentStatus(Enum):
    """에이전트 상태"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentProtocol(Enum):
    """에이전트 프로토콜 타입"""

    A2A = "a2a"  # 기존 Agent-to-Agent Protocol
    ADK = "adk"  # Google Agent Development Kit
    HYBRID = "hybrid"  # A2A + ADK 통합


class AgentMessage(BaseModel):
    """
    A2A 메시지 모델 (Actor Model 패턴)
    참고: Carl Hewitt의 Actor Model
    """

    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="메시지 고유 ID"
    )
    from_agent_id: str = Field(..., description="발신 에이전트 ID")
    to_agent_id: str = Field(..., description="수신 에이전트 ID")
    message_type: MessageType = Field(..., description="메시지 타입")
    payload: Dict[str, Any] = Field(default_factory=dict, description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.now, description="전송 시간")
    correlation_id: Optional[str] = Field(None, description="연관 메시지 ID")
    ttl: Optional[int] = Field(300, description="메시지 유효시간(초)")


class Agent(BaseModel):
    """
    에이전트 기본 모델
    A2A vs ADK 차이점:
    - A2A: 메시지 기반 통신, 분산 아키텍처
    - ADK: Google Cloud 통합, 중앙화된 관리
    """

    agent_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="에이전트 고유 ID"
    )
    name: str = Field(..., description="에이전트 이름")
    description: Optional[str] = Field(None, description="에이전트 설명")
    protocol: AgentProtocol = Field(AgentProtocol.A2A, description="사용 프로토콜")
    status: AgentStatus = Field(AgentStatus.INITIALIZING, description="현재 상태")
    capabilities: List[str] = Field(default_factory=list, description="에이전트 능력")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="추가 메타데이터"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    last_heartbeat: Optional[datetime] = Field(None, description="마지막 하트비트")

    # A2A 전용 속성
    message_queue: List[AgentMessage] = Field(
        default_factory=list, description="메시지 큐"
    )
    peer_agents: List[str] = Field(
        default_factory=list, description="연결된 피어 에이전트들"
    )

    # ADK 전용 속성
    adk_config: Optional[Dict[str, Any]] = Field(None, description="ADK 설정")
    google_project_id: Optional[str] = Field(None, description="Google 프로젝트 ID")
    adk_session_id: Optional[str] = Field(None, description="ADK 세션 ID")


class A2AAgent(Agent):
    """
    A2A Protocol 전용 에이전트
    특징:
    - 메시지 기반 통신 (Actor Model)
    - P2P 분산 아키텍처
    - 자율적 의사결정
    """

    protocol: AgentProtocol = Field(AgentProtocol.A2A, description="A2A 프로토콜 고정")

    def add_message(self, message: AgentMessage) -> None:
        """메시지 큐에 추가"""
        queue = list(self.message_queue)
        queue.append(message)
        self.message_queue = queue

    def get_pending_messages(self) -> List[AgentMessage]:
        """대기 중인 메시지 조회"""
        return [
            msg for msg in self.message_queue if msg.message_type == MessageType.REQUEST
        ]

    def update_heartbeat(self) -> None:
        """하트비트 업데이트"""
        self.last_heartbeat = datetime.now()
        self.status = AgentStatus.ACTIVE

    def connect_peer(self, peer_agent_id: str) -> None:
        """피어 에이전트 연결"""
        peers = list(self.peer_agents)
        if peer_agent_id not in peers:
            peers.append(peer_agent_id)
            self.peer_agents = peers


class ADKAgent(Agent):
    """
    Google ADK 전용 에이전트
    특징:
    - Google Cloud 통합
    - 중앙화된 관리
    - LLM 기반 처리
    """

    protocol: AgentProtocol = Field(AgentProtocol.ADK, description="ADK 프로토콜 고정")

    def __init__(self, **data):
        super().__init__(**data)
        # ADK 기본 설정
        if not self.adk_config:
            self.adk_config = {
                "model": "gemini-1.5-pro",
                "temperature": 0.7,
                "max_tokens": 2048,
            }

    def set_google_project(self, project_id: str) -> None:
        """Google 프로젝트 설정"""
        self.google_project_id = project_id
        if self.adk_config:
            self.adk_config["project_id"] = project_id

    def start_adk_session(self) -> str:
        """ADK 세션 시작"""
        self.adk_session_id = str(uuid.uuid4())
        self.status = AgentStatus.ACTIVE
        return self.adk_session_id

    def get_adk_capabilities(self) -> List[str]:
        """ADK 전용 능력 조회"""
        base_capabilities = list(self.capabilities)
        adk_capabilities = [
            "llm_processing",
            "google_cloud_integration",
            "sequential_workflow",
            "parallel_workflow",
            "context_management",
        ]
        return base_capabilities + adk_capabilities


class HybridAgent(Agent):
    """
    A2A + ADK 통합 에이전트
    특징:
    - 두 프로토콜 동시 지원
    - 상황에 따른 프로토콜 선택
    - 최대 호환성
    """

    protocol: AgentProtocol = Field(
        AgentProtocol.HYBRID, description="하이브리드 프로토콜"
    )
    active_protocol: AgentProtocol = Field(
        AgentProtocol.A2A, description="현재 활성 프로토콜"
    )

    def switch_protocol(self, target_protocol: AgentProtocol) -> bool:
        """프로토콜 전환"""
        if target_protocol in [AgentProtocol.A2A, AgentProtocol.ADK]:
            self.active_protocol = target_protocol
            return True
        return False

    def get_current_capabilities(self) -> List[str]:
        """현재 프로토콜 기준 능력 조회"""
        if self.active_protocol == AgentProtocol.A2A:
            return self.capabilities + ["message_routing", "peer_communication"]
        elif self.active_protocol == AgentProtocol.ADK:
            return self.capabilities + ["llm_processing", "google_cloud_integration"]
        else:
            return self.capabilities


class AgentRegistry(BaseModel):
    """
    에이전트 레지스트리 (Registry Pattern)
    """

    agents: Dict[str, Agent] = Field(
        default_factory=dict, description="등록된 에이전트들"
    )

    def register_agent(self, agent: Agent) -> bool:
        """에이전트 등록"""
        agents_dict = dict(self.agents)
        if agent.agent_id not in agents_dict:
            agents_dict[agent.agent_id] = agent
            self.agents = agents_dict
            return True
        return False

    def unregister_agent(self, agent_id: str) -> bool:
        """에이전트 등록 해제"""
        agents_dict = dict(self.agents)
        if agent_id in agents_dict:
            del agents_dict[agent_id]
            self.agents = agents_dict
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """에이전트 조회"""
        return dict(self.agents).get(agent_id)

    def get_agents_by_protocol(self, protocol: AgentProtocol) -> List[Agent]:
        """프로토콜별 에이전트 조회"""
        return [
            agent for agent in dict(self.agents).values() if agent.protocol == protocol
        ]

    def get_active_agents(self) -> List[Agent]:
        """활성 에이전트 조회"""
        return [
            agent
            for agent in dict(self.agents).values()
            if agent.status == AgentStatus.ACTIVE
        ]


# 팩토리 함수들
def create_a2a_agent(name: str, capabilities: List[str] = None) -> A2AAgent:
    """A2A 에이전트 생성"""
    return A2AAgent(
        name=name, capabilities=capabilities or [], protocol=AgentProtocol.A2A
    )


def create_adk_agent(
    name: str, google_project_id: str, capabilities: List[str] = None
) -> ADKAgent:
    """ADK 에이전트 생성"""
    agent = ADKAgent(
        name=name, capabilities=capabilities or [], protocol=AgentProtocol.ADK
    )
    agent.set_google_project(google_project_id)
    return agent


def create_hybrid_agent(name: str, capabilities: List[str] = None) -> HybridAgent:
    """하이브리드 에이전트 생성"""
    return HybridAgent(
        name=name, capabilities=capabilities or [], protocol=AgentProtocol.HYBRID
    )

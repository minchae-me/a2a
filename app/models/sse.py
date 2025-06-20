"""
SSE (Server-Sent Events) 도메인 모델
실시간 통신 패턴 적용
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid


class SSEEventType(Enum):
    """SSE 이벤트 타입"""

    RECOMMENDATION_START = "recommendation_start"
    RECOMMENDATION_PROGRESS = "recommendation_progress"
    RECOMMENDATION_COMPLETE = "recommendation_complete"
    RECOMMENDATION_ERROR = "recommendation_error"
    AGENT_MESSAGE = "agent_message"
    HEARTBEAT = "heartbeat"
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_CLOSED = "connection_closed"


class SSEMessage(BaseModel):
    """SSE 메시지 모델"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: SSEEventType
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    retry: Optional[int] = None  # 재연결 대기 시간(ms)

    def to_sse_format(self) -> str:
        """SSE 형식으로 변환"""
        lines = []
        lines.append(f"id: {self.event_id}")
        lines.append(f"event: {self.event_type.value}")
        lines.append(f"data: {self.json()}")
        if self.retry:
            lines.append(f"retry: {self.retry}")
        lines.append("")  # 빈 줄로 메시지 종료
        return "\n".join(lines)


class SSEConnection(BaseModel):
    """SSE 연결 정보"""

    connection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    subscribed_events: List[SSEEventType] = Field(default_factory=list)

    def update_activity(self) -> None:
        """활동 시간 업데이트"""
        self.last_activity = datetime.now()

    def subscribe_to_event(self, event_type: SSEEventType) -> None:
        """이벤트 구독"""
        if event_type not in self.subscribed_events:
            self.subscribed_events.append(event_type)

    def unsubscribe_from_event(self, event_type: SSEEventType) -> None:
        """이벤트 구독 해제"""
        if event_type in self.subscribed_events:
            self.subscribed_events.remove(event_type)


class SSEEvent(BaseModel):
    """SSE 이벤트 모델 (Observer Pattern)"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: SSEEventType
    source: str  # 이벤트 발생 소스 (agent_id, service_name 등)
    target_connections: List[str] = Field(default_factory=list)  # connection_id 목록
    payload: Dict[str, Any] = Field(default_factory=dict)
    broadcast: bool = False  # 모든 연결에 브로드캐스트 여부
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class RecommendationProgress(BaseModel):
    """추천 진행상황 모델"""

    session_id: str
    step: str
    progress_percentage: int = Field(ge=0, le=100)
    current_task: Optional[str] = None
    estimated_remaining_time: Optional[int] = None  # 초 단위
    details: Dict[str, Any] = Field(default_factory=dict)

    def to_sse_message(self) -> SSEMessage:
        """SSE 메시지로 변환"""
        return SSEMessage(
            event_type=SSEEventType.RECOMMENDATION_PROGRESS,
            data={
                "session_id": self.session_id,
                "step": self.step,
                "progress": self.progress_percentage,
                "current_task": self.current_task,
                "estimated_remaining_time": self.estimated_remaining_time,
                "details": self.details,
            },
        )


# 팩토리 함수들
def create_sse_message(
    event_type: SSEEventType, data: Dict[str, Any] = None, retry: int = None
) -> SSEMessage:
    """SSE 메시지 생성"""
    return SSEMessage(event_type=event_type, data=data or {}, retry=retry)


def create_sse_connection(
    user_id: str = None,
    session_id: str = None,
    client_ip: str = None,
    user_agent: str = None,
) -> SSEConnection:
    """SSE 연결 생성"""
    return SSEConnection(
        user_id=user_id,
        session_id=session_id,
        client_ip=client_ip,
        user_agent=user_agent,
    )


def create_heartbeat_message() -> SSEMessage:
    """하트비트 메시지 생성"""
    return SSEMessage(
        event_type=SSEEventType.HEARTBEAT,
        data={"timestamp": datetime.now().isoformat()},
        retry=30000,  # 30초 후 재연결
    )


def create_recommendation_start_message(
    session_id: str, query_info: Dict[str, Any]
) -> SSEMessage:
    """추천 시작 메시지 생성"""
    return SSEMessage(
        event_type=SSEEventType.RECOMMENDATION_START,
        data={
            "session_id": session_id,
            "query_info": query_info,
            "message": "여행 추천을 시작합니다...",
        },
    )


def create_recommendation_complete_message(
    session_id: str, recommendations: List[Dict[str, Any]]
) -> SSEMessage:
    """추천 완료 메시지 생성"""
    return SSEMessage(
        event_type=SSEEventType.RECOMMENDATION_COMPLETE,
        data={
            "session_id": session_id,
            "recommendations": recommendations,
            "message": "여행 추천이 완료되었습니다!",
        },
    )


def create_agent_message_event(
    agent_id: str, message_content: str, session_id: str = None
) -> SSEMessage:
    """에이전트 메시지 이벤트 생성"""
    return SSEMessage(
        event_type=SSEEventType.AGENT_MESSAGE,
        data={
            "agent_id": agent_id,
            "message": message_content,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
        },
    )

"""
SSE (Server-Sent Events) 서비스
Observer Pattern 적용
"""

import asyncio
from typing import Dict, List, Optional
from ..models.sse import SSEConnection, SSEMessage, create_heartbeat_message


class SSEService:
    """SSE 서비스 클래스"""

    def __init__(self):
        self.connections: Dict[str, SSEConnection] = {}

    def add_connection(self, connection: SSEConnection) -> None:
        """연결 추가"""
        self.connections[connection.connection_id] = connection

    def remove_connection(self, connection_id: str) -> None:
        """연결 제거"""
        if connection_id in self.connections:
            del self.connections[connection_id]

    async def broadcast_message(self, message: SSEMessage) -> None:
        """모든 연결에 메시지 브로드캐스트"""
        for connection in self.connections.values():
            if connection.is_active:
                # 실제 구현에서는 여기서 메시지 전송
                pass

    async def send_heartbeat(self) -> None:
        """하트비트 전송"""
        heartbeat = create_heartbeat_message()
        await self.broadcast_message(heartbeat)

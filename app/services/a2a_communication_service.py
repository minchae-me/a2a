"""
A2A 통신 서비스
Agent-to-Agent 메시지 처리
"""

import asyncio
from typing import Dict, List, Optional, Callable
from ..models.agent import Agent, AgentMessage, MessageType, AgentRegistry


class A2ACommunicationService:
    """A2A 통신 서비스 클래스"""

    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}

    def register_agent(self, agent: Agent) -> bool:
        """에이전트 등록"""
        return self.agent_registry.register_agent(agent)

    def unregister_agent(self, agent_id: str) -> bool:
        """에이전트 등록 해제"""
        return self.agent_registry.unregister_agent(agent_id)

    async def send_message(self, message: AgentMessage) -> Optional[Dict]:
        """메시지 전송"""
        target_agent = self.agent_registry.get_agent(message.to_agent_id)
        if target_agent:
            # 실제 메시지 처리 로직
            return {"status": "sent", "message_id": message.message_id}
        return None

    async def broadcast_message(self, message: AgentMessage) -> List[Dict]:
        """메시지 브로드캐스트"""
        results = []
        for agent in self.agent_registry.get_active_agents():
            if hasattr(agent, "agent_id"):
                message.to_agent_id = agent["agent_id"]
                result = await self.send_message(message)
                if result:
                    results.append(result)
        return results

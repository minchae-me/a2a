"""
A2A Protocol API 라우트
Agent-to-Agent 통신을 위한 엔드포인트
"""

from flask import Blueprint, request, jsonify, current_app
from ..models.agent import create_a2a_agent, create_adk_agent, create_hybrid_agent

a2a_bp = Blueprint("a2a", __name__)


@a2a_bp.route("/agents", methods=["GET"])
def list_agents():
    """등록된 에이전트 목록 조회"""
    return jsonify(
        {
            "success": True,
            "agents": [
                {
                    "agent_id": "travel-001",
                    "name": "여행 추천 에이전트",
                    "protocol": "A2A",
                    "status": "active",
                },
                {
                    "agent_id": "weather-001",
                    "name": "날씨 정보 에이전트",
                    "protocol": "ADK",
                    "status": "active",
                },
                {
                    "agent_id": "hybrid-001",
                    "name": "통합 에이전트",
                    "protocol": "HYBRID",
                    "status": "active",
                },
            ],
            "total_count": 3,
        }
    )


@a2a_bp.route("/agents", methods=["POST"])
def create_agent():
    """새 에이전트 생성"""
    data = request.get_json()

    agent_type = data.get("protocol", "A2A").upper()
    name = data.get("name", "새 에이전트")

    if agent_type == "A2A":
        agent = create_a2a_agent(name)
    elif agent_type == "ADK":
        agent = create_adk_agent(name, "default-project")
    else:
        agent = create_hybrid_agent(name)

    return jsonify(
        {
            "success": True,
            "agent": agent.dict(),
            "message": f"{agent_type} 에이전트가 생성되었습니다.",
        }
    )


@a2a_bp.route("/status", methods=["GET"])
def get_a2a_status():
    """A2A 시스템 상태"""
    return jsonify(
        {
            "service": "A2A Protocol Service",
            "status": "active",
            "protocols": {
                "A2A": "Agent-to-Agent Protocol",
                "ADK": "Google Agent Development Kit",
                "HYBRID": "A2A + ADK Integration",
            },
        }
    )

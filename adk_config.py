"""
Google ADK 설정 파일
ADK 에이전트들을 위한 전역 설정
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ADKConfig:
    """ADK 전역 설정"""

    project_id: str = "demo-project"
    location: str = "us-central1"
    memory_enabled: bool = True
    max_memory_size: int = 1000
    enable_search_tool: bool = True

    # 추가 설정들
    max_concurrent_workflows: int = 5
    default_timeout: int = 30
    logging_level: str = "INFO"


# 전역 설정 인스턴스
adk_config = ADKConfig()


# 에이전트 역할 정의
AGENT_ROLES = {
    "travel_recommendation": {
        "name": "TravelRecommendationAgent",
        "description": "여행지 추천 및 일정 계획 전문 ADK 에이전트",
        "capabilities": ["recommendation", "analysis", "workflow"],
    },
    "budget_optimization": {
        "name": "BudgetOptimizationAgent",
        "description": "여행 예산 최적화 전문 ADK 에이전트",
        "capabilities": ["optimization", "calculation", "analysis"],
    },
    "itinerary_planning": {
        "name": "ItineraryPlanningAgent",
        "description": "여행 일정 계획 전문 ADK 에이전트",
        "capabilities": ["planning", "scheduling", "coordination"],
    },
}


def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """특정 에이전트 타입의 설정 반환"""
    return AGENT_ROLES.get(agent_type, AGENT_ROLES["travel_recommendation"])

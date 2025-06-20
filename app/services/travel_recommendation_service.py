"""
여행 추천 서비스
비즈니스 로직 레이어
"""

from typing import List, Dict, Any
from ..models.travel import TravelQuery, TravelRecommendation
from .google_ai_service import GoogleAIService


class TravelRecommendationService:
    """여행 추천 서비스 클래스"""

    def __init__(self, ai_service: GoogleAIService):
        self.ai_service = ai_service

    async def generate_recommendations(
        self, query: TravelQuery
    ) -> List[TravelRecommendation]:
        """여행 추천 생성"""
        return await self.ai_service.generate_travel_recommendations(query)

    async def get_weather_info(self, location: str) -> Dict[str, Any]:
        """날씨 정보 조회"""
        return await self.ai_service.get_weather_info(location)

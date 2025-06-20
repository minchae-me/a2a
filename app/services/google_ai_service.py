"""
Google AI Platform 연동 서비스
Adapter Pattern 적용
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Google Cloud AI Platform 임포트 시도
try:
    import google.cloud.aiplatform as aiplatform
    from google.cloud.aiplatform.gapic.schema import predict
    from google.protobuf import json_format
    from google.protobuf.struct_pb2 import Value

    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("⚠️ Google Cloud AI Platform이 설치되지 않았습니다. Mock 모드로 실행됩니다.")

from ..config import Config
from ..models.travel import TravelQuery, TravelRecommendation, Destination


class GoogleAIService:
    """
    Google AI Platform 연동 서비스
    참고: Adapter Pattern, Google Cloud AI Documentation
    """

    def __init__(self, config: Config):
        self.config = config
        self.project_id = config.GOOGLE_PROJECT_ID
        self.location = config.GOOGLE_LOCATION
        self.credentials_path = config.GOOGLE_CREDENTIALS_PATH

        # Mock 모드 확인
        self.mock_mode = not GOOGLE_AI_AVAILABLE or not self._validate_credentials()

        if not self.mock_mode:
            self._initialize_ai_platform()
        else:
            print("🤖 Google AI Service가 Mock 모드로 실행됩니다.")

    def _validate_credentials(self) -> bool:
        """Google Cloud 자격증명 검증"""
        if self.credentials_path and os.path.exists(self.credentials_path):
            return True
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            return True
        elif self.project_id != "your-project-id":
            return True
        return False

    def _initialize_ai_platform(self) -> None:
        """AI Platform 초기화"""
        try:
            if self.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path

            aiplatform.init(project=self.project_id, location=self.location)
            print(f"✅ Google AI Platform 초기화 완료: {self.project_id}")
        except Exception as e:
            print(f"❌ Google AI Platform 초기화 실패: {e}")
            self.mock_mode = True

    async def generate_travel_recommendations(
        self, query: TravelQuery, max_recommendations: int = 5
    ) -> List[TravelRecommendation]:
        """
        여행 추천 생성
        """
        if self.mock_mode:
            return await self._generate_mock_recommendations(query, max_recommendations)

        try:
            # 프롬프트 생성
            prompt = self._create_travel_prompt(query)

            # AI 호출
            recommendations = await self._call_generative_ai(
                prompt, max_recommendations
            )

            # 결과 파싱
            parsed_recommendations = self._parse_ai_response(
                recommendations, query.query_id
            )

            return parsed_recommendations

        except Exception as e:
            print(f"❌ AI 추천 생성 실패: {e}")
            return await self._generate_mock_recommendations(query, max_recommendations)

    def _create_travel_prompt(self, query: TravelQuery) -> str:
        """여행 추천용 프롬프트 생성"""
        prompt_parts = [
            "당신은 전문 여행 가이드입니다. 다음 조건에 맞는 여행 추천을 제공해주세요:",
            "",
            f"목적지: {query.destination or '미정'}",
            f"여행 기간: {query.duration_days or '미정'}일",
            f"예산: {query.budget or '미정'}원",
            f"선호사항: {', '.join([p.value for p in query.preferences]) if query.preferences else '없음'}",
            f"인원: {query.party_size or 1}명",
            "",
            "다음 형식으로 JSON 응답을 제공해주세요:",
            "{",
            '  "recommendations": [',
            "    {",
            '      "title": "추천 제목",',
            '      "description": "상세 설명",',
            '      "destinations": [{"name": "목적지명", "description": "설명"}],',
            '      "estimated_budget": {"total": 금액, "breakdown": {...}},',
            '      "hotels": [{"name": "호텔명", "price": 가격}],',
            '      "activities": [{"name": "활동명", "description": "설명"}],',
            '      "restaurants": [{"name": "음식점명", "cuisine": "요리종류"}],',
            '      "tips": ["팁1", "팁2"]',
            "    }",
            "  ]",
            "}",
        ]

        return "\n".join(prompt_parts)

    async def _call_generative_ai(
        self, prompt: str, max_recommendations: int
    ) -> Dict[str, Any]:
        """Generative AI 호출"""
        if self.mock_mode:
            await asyncio.sleep(1)  # 실제 API 호출 시뮬레이션
            return self._get_mock_ai_response()

        try:
            # 실제 Google AI 호출 (향후 구현)
            # endpoint = aiplatform.Endpoint(endpoint_name=...)
            # prediction = endpoint.predict(instances=[...])

            # 현재는 Mock 응답 반환
            await asyncio.sleep(2)  # 실제 API 호출 시뮬레이션
            return self._get_mock_ai_response()

        except Exception as e:
            print(f"❌ AI API 호출 실패: {e}")
            return self._get_mock_ai_response()

    def _get_mock_ai_response(self) -> Dict[str, Any]:
        """Mock AI 응답 생성"""
        return {
            "recommendations": [
                {
                    "title": "제주도 자연 힐링 여행",
                    "description": "제주도의 아름다운 자연을 만끽할 수 있는 3박 4일 힐링 여행 코스입니다.",
                    "destinations": [
                        {
                            "name": "제주도",
                            "description": "한국의 대표적인 휴양지로 자연경관이 아름다운 섬",
                        }
                    ],
                    "estimated_budget": {
                        "total": 800000,
                        "breakdown": {
                            "accommodation": 300000,
                            "food": 200000,
                            "activities": 200000,
                            "transportation": 100000,
                        },
                    },
                    "hotels": [
                        {"name": "제주신라호텔", "price": 150000},
                        {"name": "파라다이스호텔제주", "price": 120000},
                    ],
                    "activities": [
                        {
                            "name": "한라산 등반",
                            "description": "제주도 최고봉 한라산 백록담 등반",
                        },
                        {
                            "name": "성산일출봉",
                            "description": "UNESCO 세계자연유산 일출명소",
                        },
                        {"name": "만장굴 탐험", "description": "용암동굴 탐험 체험"},
                    ],
                    "restaurants": [
                        {"name": "흑돼지골목", "cuisine": "제주 흑돼지"},
                        {"name": "해녀의집", "cuisine": "제주 해물요리"},
                        {"name": "카페 더클리프", "cuisine": "카페"},
                    ],
                    "tips": [
                        "제주도는 렌터카 이용이 편리합니다",
                        "한라산 등반시 날씨 확인 필수",
                        "제주 특산품 한라봉, 감귤 꼭 드셔보세요",
                    ],
                }
            ]
        }

    def _parse_ai_response(
        self, ai_response: Dict[str, Any], query_id: str
    ) -> List[TravelRecommendation]:
        """AI 응답을 TravelRecommendation 객체로 변환"""
        recommendations = []

        for rec_data in ai_response.get("recommendations", []):
            # Destination 객체들 생성
            destinations = []
            for dest_data in rec_data.get("destinations", []):
                destination = Destination(
                    name=dest_data.get("name", ""),
                    description=dest_data.get("description", ""),
                )
                destinations.append(destination)

            # TravelRecommendation 객체 생성
            recommendation = TravelRecommendation(
                query_id=query_id,
                title=rec_data.get("title", ""),
                description=rec_data.get("description", ""),
                destinations=destinations,
                estimated_budget=rec_data.get("estimated_budget"),
                hotels=rec_data.get("hotels", []),
                activities=rec_data.get("activities", []),
                restaurants=rec_data.get("restaurants", []),
                tips=rec_data.get("tips", []),
            )

            recommendations.append(recommendation)

        return recommendations

    async def _generate_mock_recommendations(
        self, query: TravelQuery, max_recommendations: int
    ) -> List[TravelRecommendation]:
        """Mock 추천 생성"""
        await asyncio.sleep(1)  # 비동기 처리 시뮬레이션

        mock_response = self._get_mock_ai_response()
        return self._parse_ai_response(mock_response, query.query_id)

    async def get_weather_info(self, location: str) -> Dict[str, Any]:
        """날씨 정보 조회 (Mock)"""
        await asyncio.sleep(0.5)

        return {
            "location": location,
            "current_temp": 22.5,
            "description": "맑음",
            "humidity": 65,
            "wind_speed": 3.2,
            "forecast": [
                {
                    "date": "2024-01-15",
                    "temp_high": 25,
                    "temp_low": 18,
                    "description": "맑음",
                },
                {
                    "date": "2024-01-16",
                    "temp_high": 23,
                    "temp_low": 16,
                    "description": "구름 많음",
                },
                {
                    "date": "2024-01-17",
                    "temp_high": 20,
                    "temp_low": 14,
                    "description": "비",
                },
            ],
        }

    async def analyze_destination_sentiment(self, destination: str) -> Dict[str, Any]:
        """목적지 감정 분석 (향후 구현)"""
        await asyncio.sleep(0.3)

        return {
            "destination": destination,
            "sentiment_score": 0.8,
            "positive_keywords": ["아름다운", "평화로운", "힐링"],
            "negative_keywords": [],
            "overall_sentiment": "매우 긍정적",
        }


# 서비스 팩토리 함수
def create_google_ai_service(config: Config) -> GoogleAIService:
    """Google AI 서비스 생성"""
    return GoogleAIService(config)

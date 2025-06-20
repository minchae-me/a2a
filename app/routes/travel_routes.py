"""
여행 추천 API 라우트
Flask Blueprint 패턴 적용
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
import asyncio

from ..models.travel import create_travel_query
from ..services.google_ai_service import create_google_ai_service


travel_bp = Blueprint("travel", __name__)


@travel_bp.route("/recommend", methods=["POST"])
def recommend_travel():
    """
    여행 추천 API
    POST /api/travel/recommend
    """
    try:
        # 요청 데이터 파싱
        data = request.get_json()

        if not data:
            return (
                jsonify(
                    {"error": "Invalid request", "message": "JSON 데이터가 필요합니다."}
                ),
                400,
            )

        # 필수 필드 검증
        required_fields = ["user_id"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return (
                jsonify(
                    {
                        "error": "Missing required fields",
                        "missing_fields": missing_fields,
                    }
                ),
                400,
            )

        # TravelQuery 객체 생성
        travel_query = create_travel_query(
            user_id=data["user_id"],
            destination=data.get("destination"),
            duration_days=data.get("duration_days"),
            budget=data.get("budget"),
            preferences=data.get("preferences", []),
        )

        # Google AI 서비스 생성
        ai_service = create_google_ai_service(current_app.config)

        # 비동기 추천 생성 (동기적으로 실행)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            recommendations = loop.run_until_complete(
                ai_service.generate_travel_recommendations(travel_query)
            )
        finally:
            loop.close()

        # 응답 데이터 구성
        response_data = {
            "success": True,
            "query_id": travel_query.query_id,
            "recommendations": [rec.dict() for rec in recommendations],
            "total_count": len(recommendations),
            "generated_by": "A2A Travel System",
        }

        return jsonify(response_data)

    except Exception as e:
        current_app.logger.error(f"여행 추천 생성 실패: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "여행 추천 생성 중 오류가 발생했습니다.",
                    "details": str(e) if current_app.debug else None,
                }
            ),
            500,
        )


@travel_bp.route("/destinations", methods=["GET"])
def get_popular_destinations():
    """
    인기 여행지 조회 API
    GET /api/travel/destinations
    """
    try:
        # Mock 인기 여행지 데이터
        popular_destinations = [
            {
                "name": "제주도",
                "country": "대한민국",
                "description": "한국의 대표적인 휴양지",
                "best_season": "봄, 가을",
                "average_budget": {"low": 300000, "medium": 600000, "high": 1000000},
                "popular_activities": ["한라산 등반", "해수욕", "카페 투어"],
                "tags": ["자연", "힐링", "해변"],
            },
            {
                "name": "부산",
                "country": "대한민국",
                "description": "해안 도시의 매력과 문화가 어우러진 곳",
                "best_season": "봄, 여름",
                "average_budget": {"low": 200000, "medium": 400000, "high": 700000},
                "popular_activities": ["해운대 해수욕", "감천문화마을", "자갈치시장"],
                "tags": ["해변", "문화", "음식"],
            },
            {
                "name": "서울",
                "country": "대한민국",
                "description": "전통과 현대가 공존하는 수도",
                "best_season": "봄, 가을",
                "average_budget": {"low": 150000, "medium": 350000, "high": 600000},
                "popular_activities": ["궁궐 투어", "쇼핑", "한강 공원"],
                "tags": ["도시", "문화", "쇼핑"],
            },
        ]

        return jsonify(
            {
                "success": True,
                "destinations": popular_destinations,
                "total_count": len(popular_destinations),
            }
        )

    except Exception as e:
        current_app.logger.error(f"인기 여행지 조회 실패: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "인기 여행지 조회 중 오류가 발생했습니다.",
                }
            ),
            500,
        )


@travel_bp.route("/weather/<location>", methods=["GET"])
def get_weather(location: str):
    """
    날씨 정보 조회 API
    GET /api/travel/weather/<location>
    """
    try:
        # Google AI 서비스를 통한 날씨 조회
        ai_service = create_google_ai_service(current_app.config)

        # 비동기 날씨 정보 조회
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            weather_info = loop.run_until_complete(
                ai_service.get_weather_info(location)
            )
        finally:
            loop.close()

        return jsonify({"success": True, "weather": weather_info})

    except Exception as e:
        current_app.logger.error(f"날씨 정보 조회 실패: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": f"{location}의 날씨 정보 조회 중 오류가 발생했습니다.",
                }
            ),
            500,
        )


@travel_bp.route("/status", methods=["GET"])
def get_service_status():
    """
    여행 서비스 상태 조회 API
    GET /api/travel/status
    """
    return jsonify(
        {
            "service": "Travel Recommendation Service",
            "status": "active",
            "version": "1.0.0",
            "features": {
                "ai_recommendations": True,
                "weather_info": True,
                "destination_search": True,
            },
            "protocols": {
                "a2a_enabled": current_app.config.get("A2A_ENABLED", False),
                "adk_enabled": current_app.config.get("ADK_ENABLED", False),
            },
        }
    )

#!/usr/bin/env python3
"""
🌐 HTTP 모드 MCP 서버
A2A 통합을 위한 HTTP 포트 기반 MCP 서버
"""

import asyncio
import json
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel


# 요청/응답 모델
class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any] = {}
    id: int = 1


class MCPResponse(BaseModel):
    id: int
    result: Any = None
    error: str = None


# FastAPI 앱 생성
app = FastAPI(
    title="MCP HTTP Server",
    description="HTTP 기반 Model Context Protocol 서버",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 여행 데이터베이스 (모킹)
TRAVEL_DB = {
    "destinations": {
        "제주도": {
            "description": "아름다운 섬, 한라산과 해변으로 유명",
            "activities": ["한라산 등반", "성산일출봉", "카페 투어", "해변 산책"],
            "hotels": ["제주신라호텔", "파라다이스호텔", "롯데호텔제주"],
            "food": ["흑돼지", "해물라면", "한라봉", "갈치조림"],
            "budget": {
                "low": "30만원 (게스트하우스, 대중교통)",
                "medium": "50만원 (호텔, 렌터카)",
                "high": "100만원 (리조트, 프리미엄 투어)",
            },
        },
        "서울": {
            "description": "대한민국의 수도, 전통과 현대가 공존",
            "activities": ["경복궁", "명동쇼핑", "한강공원", "N서울타워"],
            "hotels": ["롯데호텔", "신라호텔", "그랜드하얏트"],
            "food": ["김치찌개", "불고기", "치킨", "떡볶이"],
            "budget": {
                "low": "20만원 (모텔, 지하철)",
                "medium": "40만원 (호텔, 택시)",
                "high": "80만원 (특급호텔, 프리미엄 식당)",
            },
        },
        "부산": {
            "description": "바다와 산이 어우러진 항구도시",
            "activities": ["해운대해수욕장", "감천문화마을", "자갈치시장", "태종대"],
            "hotels": ["파라다이스호텔부산", "롯데호텔부산", "해운대그랜드호텔"],
            "food": ["돼지국밥", "밀면", "회", "씨앗호떡"],
            "budget": {
                "low": "25만원 (게스트하우스, 버스)",
                "medium": "45만원 (호텔, 택시)",
                "high": "90만원 (오션뷰 호텔, 고급 해산물)",
            },
        },
    },
    "weather": {
        "제주도": {
            "temp": "24°C",
            "condition": "맑음",
            "humidity": "60%",
            "wind": "남풍 3m/s",
        },
        "서울": {
            "temp": "23°C",
            "condition": "흐림",
            "humidity": "70%",
            "wind": "서풍 2m/s",
        },
        "부산": {
            "temp": "26°C",
            "condition": "비",
            "humidity": "80%",
            "wind": "남동풍 4m/s",
        },
    },
}


# MCP 도구 구현
async def search_destination(query: str) -> Dict[str, Any]:
    """여행지 검색"""
    results = []
    query_lower = query.lower()

    for dest, info in TRAVEL_DB["destinations"].items():
        if query_lower in dest.lower() or query_lower in info["description"].lower():
            results.append(
                {
                    "destination": dest,
                    "description": info["description"],
                    "activities": info["activities"][:3],  # 상위 3개만
                    "match_score": 1.0 if query_lower in dest.lower() else 0.7,
                }
            )

    return {
        "query": query,
        "total_results": len(results),
        "destinations": sorted(results, key=lambda x: x["match_score"], reverse=True),
    }


async def get_travel_recommendation(
    destination: str, budget: str = "medium"
) -> Dict[str, Any]:
    """여행 추천"""
    dest_lower = destination.lower()

    # 목적지 찾기
    matched_dest = None
    for dest, info in TRAVEL_DB["destinations"].items():
        if dest_lower in dest.lower():
            matched_dest = dest
            break

    if not matched_dest:
        return {
            "error": f"'{destination}' 정보를 찾을 수 없습니다",
            "available_destinations": list(TRAVEL_DB["destinations"].keys()),
        }

    info = TRAVEL_DB["destinations"][matched_dest]
    budget_key = (
        budget.lower() if budget.lower() in ["low", "medium", "high"] else "medium"
    )

    return {
        "destination": matched_dest,
        "description": info["description"],
        "recommended_activities": info["activities"],
        "recommended_hotels": info["hotels"],
        "local_food": info["food"],
        "budget_estimate": info["budget"][budget_key],
        "budget_level": budget_key,
        "total_activities": len(info["activities"]),
        "total_hotels": len(info["hotels"]),
    }


async def get_weather_info(location: str) -> Dict[str, Any]:
    """날씨 정보"""
    location_lower = location.lower()

    # 위치 찾기
    matched_location = None
    for loc in TRAVEL_DB["weather"].keys():
        if location_lower in loc.lower():
            matched_location = loc
            break

    if not matched_location:
        return {
            "error": f"'{location}' 날씨 정보를 찾을 수 없습니다",
            "available_locations": list(TRAVEL_DB["weather"].keys()),
        }

    weather = TRAVEL_DB["weather"][matched_location]
    return {
        "location": matched_location,
        "temperature": weather["temp"],
        "condition": weather["condition"],
        "humidity": weather["humidity"],
        "wind": weather["wind"],
        "status": "current",
    }


async def analyze_budget(
    destination: str, days: int = 3, people: int = 1
) -> Dict[str, Any]:
    """예산 분석"""
    dest_lower = destination.lower()

    # 목적지 찾기
    matched_dest = None
    for dest in TRAVEL_DB["destinations"].keys():
        if dest_lower in dest.lower():
            matched_dest = dest
            break

    if not matched_dest:
        return {"error": f"'{destination}' 예산 정보를 찾을 수 없습니다"}

    info = TRAVEL_DB["destinations"][matched_dest]

    # 예산 계산 (간단한 로직)
    base_costs = {
        "low": 30000,  # 3만원/일
        "medium": 50000,  # 5만원/일
        "high": 100000,  # 10만원/일
    }

    budget_breakdown = {}
    for level, daily_cost in base_costs.items():
        total_cost = daily_cost * days * people
        budget_breakdown[level] = {
            "daily_cost_per_person": f"{daily_cost:,}원",
            "total_cost": f"{total_cost:,}원",
            "description": info["budget"][level],
        }

    return {
        "destination": matched_dest,
        "analysis_for": f"{people}명, {days}일",
        "budget_options": budget_breakdown,
        "recommendation": "medium" if people <= 2 else "high",
        "notes": [
            "항공료/교통비 별도",
            "성수기/비수기에 따라 변동",
            "개인 쇼핑/액티비티 비용 별도",
        ],
    }


# MCP 메소드 매핑
MCP_TOOLS = {
    "search_destination": search_destination,
    "get_travel_recommendation": get_travel_recommendation,
    "get_weather_info": get_weather_info,
    "analyze_budget": analyze_budget,
}


@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "server": "MCP HTTP Server",
        "status": "running",
        "version": "1.0.0",
        "available_tools": list(MCP_TOOLS.keys()),
        "total_destinations": len(TRAVEL_DB["destinations"]),
        "endpoints": {"mcp": "/mcp", "health": "/health", "tools": "/tools"},
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "tools_available": len(MCP_TOOLS)}


@app.get("/tools")
async def list_tools():
    """사용 가능한 도구 목록"""
    return {
        "tools": [
            {
                "name": "search_destination",
                "description": "여행지 검색",
                "parameters": ["query"],
            },
            {
                "name": "get_travel_recommendation",
                "description": "여행 추천",
                "parameters": ["destination", "budget?"],
            },
            {
                "name": "get_weather_info",
                "description": "날씨 정보",
                "parameters": ["location"],
            },
            {
                "name": "analyze_budget",
                "description": "예산 분석",
                "parameters": ["destination", "days?", "people?"],
            },
        ]
    }


@app.post("/mcp")
async def handle_mcp_request(request: MCPRequest) -> MCPResponse:
    """MCP 요청 처리"""
    try:
        method = request.method
        params = request.params

        if method not in MCP_TOOLS:
            return MCPResponse(
                id=request.id,
                error=f"Unknown method: {method}. Available: {list(MCP_TOOLS.keys())}",
            )

        # 도구 실행
        tool_func = MCP_TOOLS[method]
        result = await tool_func(**params)

        return MCPResponse(id=request.id, result=result)

    except Exception as e:
        return MCPResponse(
            id=request.id, error=f"Error executing {request.method}: {str(e)}"
        )


if __name__ == "__main__":
    print("🚀 MCP HTTP 서버 시작 중...")
    print("📍 http://localhost:8000")
    print("🔧 도구:", list(MCP_TOOLS.keys()))
    print("📋 엔드포인트: /mcp (POST), /tools (GET), /health (GET)")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

"""
여행 도메인 모델
DDD (Domain-Driven Design) 패턴 적용
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid


class TravelPreferenceType(Enum):
    """여행 선호도 타입"""

    NATURE = "nature"
    CULTURE = "culture"
    FOOD = "food"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    ADVENTURE = "adventure"
    NIGHTLIFE = "nightlife"


class TravelBudgetLevel(Enum):
    """여행 예산 수준"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LUXURY = "luxury"


class RecommendationStatus(Enum):
    """추천 상태"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TravelQuery(BaseModel):
    """여행 쿼리 모델"""

    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    budget: Optional[int] = None
    budget_level: Optional[TravelBudgetLevel] = None
    preferences: List[TravelPreferenceType] = Field(default_factory=list)
    travel_dates: Optional[str] = None
    party_size: Optional[int] = 1
    raw_query: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class Destination(BaseModel):
    """목적지 모델"""

    destination_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 37.5665, "lng": 126.9780}
    best_season: Optional[str] = None
    average_budget: Optional[Dict[str, int]] = (
        None  # {"low": 50000, "medium": 100000, "high": 200000}
    )
    popular_activities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class TravelRecommendation(BaseModel):
    """여행 추천 모델"""

    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str
    title: str
    description: str
    destinations: List[Destination] = Field(default_factory=list)
    suggested_itinerary: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_budget: Optional[Dict[str, Any]] = None
    hotels: List[Dict[str, Any]] = Field(default_factory=list)
    activities: List[Dict[str, Any]] = Field(default_factory=list)
    restaurants: List[Dict[str, Any]] = Field(default_factory=list)
    transportation: List[Dict[str, Any]] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    status: RecommendationStatus = RecommendationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class TravelPlan(BaseModel):
    """여행 계획 모델"""

    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    query_id: str
    recommendation_id: str
    title: str
    final_destinations: List[Destination]
    detailed_itinerary: List[Dict[str, Any]]
    confirmed_bookings: List[Dict[str, Any]] = Field(default_factory=list)
    total_budget: int
    budget_breakdown: Dict[str, int] = Field(default_factory=dict)
    notes: Optional[str] = None
    is_confirmed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None


class WeatherInfo(BaseModel):
    """날씨 정보 모델"""

    location: str
    current_temp: Optional[float] = None
    description: Optional[str] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    forecast: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


# 팩토리 함수들
def create_travel_query(
    user_id: str,
    destination: str = None,
    duration_days: int = None,
    budget: int = None,
    preferences: List[str] = None,
) -> TravelQuery:
    """여행 쿼리 생성"""
    preference_enums = []
    if preferences:
        for pref in preferences:
            try:
                preference_enums.append(TravelPreferenceType(pref.lower()))
            except ValueError:
                continue

    return TravelQuery(
        user_id=user_id,
        destination=destination,
        duration_days=duration_days,
        budget=budget,
        preferences=preference_enums,
    )


def create_destination(
    name: str,
    country: str = None,
    description: str = None,
    activities: List[str] = None,
) -> Destination:
    """목적지 생성"""
    return Destination(
        name=name,
        country=country,
        description=description,
        popular_activities=activities or [],
    )


def create_travel_recommendation(
    query_id: str, title: str, description: str, destinations: List[Destination] = None
) -> TravelRecommendation:
    """여행 추천 생성"""
    return TravelRecommendation(
        query_id=query_id,
        title=title,
        description=description,
        destinations=destinations or [],
    )

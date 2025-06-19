"""
Google ADK 기반 여행지 추천 에이전트 (내부 로직 및 워크플로우 중심)
참고: https://google.github.io/adk-docs/agents/

ADK의 핵심 역할:
- 에이전트 내부 실행 구조 설계
- State 관리, 도구 호출, LLM 기반 흐름 제어
- Sequential / Parallel / Loop 워크플로우 구성
- MCP를 통한 LLM 도구 상호작용
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
from datetime import datetime
from enum import Enum

# Google ADK 임포트 (실제 설치 후 사용)
try:
    from google.adk import BaseAgent, LlmAgent, SequentialAgent, ParallelAgent
    from google.adk.tools import SearchTool, FunctionTool, Tool
    from google.adk.memory import Memory
    from google.adk.context import Context
    from google.adk.events import Event
    from google.adk.workflows import Workflow, Step
    from google.adk.state import AgentState
    from google.adk.callbacks import Callback
    from google.adk.mcp import MCPClient  # Model Context Protocol
except ImportError:
    # 개발 중 임시 Mock 클래스들 - ADK의 핵심 추상화 구현
    class AgentState:
        def __init__(self):
            self.data = {}
            self.history = []

        def update(self, key: str, value: Any):
            self.data[key] = value
            self.history.append(
                {"key": key, "value": value, "timestamp": datetime.now()}
            )

        def get(self, key: str, default=None):
            return self.data.get(key, default)

    class BaseAgent:
        def __init__(self, name: str, **kwargs):
            self.name = name
            self.state = AgentState()
            self.tools = []
            self.workflows = []
            self.callbacks = {}

        def add_tool(self, tool):
            self.tools.append(tool)

        def add_workflow(self, workflow):
            self.workflows.append(workflow)

        def add_callback(self, event_name: str, callback):
            self.callbacks[event_name] = callback

        async def run(self, context: "Context") -> Dict[str, Any]:
            pass

    class LlmAgent(BaseAgent):
        def __init__(self, name: str, model: str = "gemini-1.5-pro", **kwargs):
            super().__init__(name, **kwargs)
            self.model = model

    class SequentialAgent(BaseAgent):
        def __init__(self, name: str, steps: List["Step"], **kwargs):
            super().__init__(name, **kwargs)
            self.steps = steps

        async def run(self, context: "Context") -> Dict[str, Any]:
            results = []
            for step in self.steps:
                result = await step.execute(context)
                results.append(result)
                context.update("last_result", result)
            return {"sequential_results": results}

    class ParallelAgent(BaseAgent):
        def __init__(self, name: str, agents: List[BaseAgent], **kwargs):
            super().__init__(name, **kwargs)
            self.agents = agents

        async def run(self, context: "Context") -> Dict[str, Any]:
            # Mock 병렬 결과 생성 (실제로는 각 에이전트 실행)
            mock_results = [
                {
                    "scores": [0.9, 0.8, 0.7],
                    "matching_factors": ["자연 선호도 일치", "높은 인기도"],
                },
                {
                    "total_budget": context.get("budget", 1000000),
                    "allocation": {
                        "accommodation": 350000,
                        "transportation": 250000,
                        "food": 250000,
                        "activities": 100000,
                        "shopping": 50000,
                    },
                },
                {
                    "itineraries": [
                        {"day_1": "자연 탐방", "day_2": "문화 체험", "day_3": "휴식"},
                        {"day_1": "도시 투어", "day_2": "맛집 탐방", "day_3": "쇼핑"},
                    ]
                },
            ]
            return {"parallel_results": mock_results}

    class Step:
        def __init__(self, name: str, func, **kwargs):
            self.name = name
            self.func = func
            self.kwargs = kwargs

        async def execute(self, context: "Context") -> Any:
            return await self.func(context, **self.kwargs)

    class Workflow:
        def __init__(self, name: str, steps: List[Step]):
            self.name = name
            self.steps = steps

    class Tool:
        def __init__(self, name: str, description: str, func):
            self.name = name
            self.description = description
            self.func = func

    class SearchTool(Tool):
        def __init__(self, name: str, description: str, **kwargs):
            super().__init__(name, description, self._search)

        async def _search(self, query: str) -> Dict[str, Any]:
            return {"query": query, "results": ["mock_result"]}

    class FunctionTool(Tool):
        def __init__(self, name: str, description: str, func):
            super().__init__(name, description, func)

    class Memory:
        def __init__(self, enabled: bool = True, max_size: int = 1000):
            self.enabled = enabled
            self.data = []
            self.max_size = max_size

        async def store(self, data: Dict[str, Any]):
            if self.enabled:
                self.data.append(data)
                if len(self.data) > self.max_size:
                    self.data.pop(0)

    class Context:
        def __init__(self, data: Dict[str, Any] = None):
            self.data = data or {}

        def get(self, key: str, default=None):
            return self.data.get(key, default)

        def update(self, key: str, value: Any):
            self.data[key] = value

    class Event:
        def __init__(self, name: str, data: Dict[str, Any] = None):
            self.name = name
            self.data = data or {}

    class MCPClient:
        def __init__(self, **kwargs):
            pass


class TravelState(Enum):
    """여행 추천 프로세스 상태"""

    INITIALIZED = "initialized"
    ANALYZING_PREFERENCES = "analyzing_preferences"
    SEARCHING_DESTINATIONS = "searching_destinations"
    MATCHING_PREFERENCES = "matching_preferences"
    OPTIMIZING_BUDGET = "optimizing_budget"
    GENERATING_ITINERARY = "generating_itinerary"
    FINALIZING_RECOMMENDATIONS = "finalizing_recommendations"
    COMPLETED = "completed"
    ERROR = "error"


class TravelRecommendationAgent(LlmAgent):
    """
    Google ADK 기반 여행지 추천 에이전트

    ADK의 핵심 특징:
    1. BaseAgent 상속으로 내부 구조 정의
    2. State 관리 (TravelState)
    3. 워크플로우 구성 (Sequential/Parallel)
    4. 도구 체이닝 및 MCP 통합
    5. 이벤트 기반 콜백 시스템
    """

    def __init__(self, project_id: str, location: str = "us-central1"):
        # ADK LlmAgent 초기화 - 에이전트의 "두뇌" 역할
        super().__init__(
            name="TravelRecommendationAgent",
            model="gemini-1.5-pro",
            project_id=project_id,
            location=location,
        )

        # 여행 추천 전용 상태 관리
        self.travel_state = TravelState.INITIALIZED

        # ADK 메모리 시스템
        self.memory = Memory(enabled=True, max_size=1000)

        # MCP 클라이언트 (Model Context Protocol)
        self.mcp_client = MCPClient()

        # 도구들 설정 - ADK 도구 체이닝
        self._setup_tools()

        # 워크플로우 구성 - ADK의 핵심
        self._setup_workflows()

        # 콜백 시스템 설정
        self._setup_callbacks()

        # 통계
        self.recommendations_count = 0
        self.workflow_executions = 0

    def _setup_tools(self):
        """ADK 도구 체이닝 구성"""

        # 1. 선호도 분석 도구
        self.preference_analyzer = FunctionTool(
            name="analyze_user_preferences",
            description="사용자 입력에서 여행 선호도를 추출하고 분석",
            func=self._analyze_user_preferences,
        )
        self.add_tool(self.preference_analyzer)

        # 2. 목적지 검색 도구 (MCP 통합)
        self.destination_searcher = SearchTool(
            name="search_destinations",
            description="여행지 데이터베이스에서 후보 목적지 검색",
        )
        self.add_tool(self.destination_searcher)

        # 3. 매칭 엔진 도구
        self.matching_engine = FunctionTool(
            name="match_destinations",
            description="사용자 선호도와 목적지 데이터를 매칭",
            func=self._match_destinations,
        )
        self.add_tool(self.matching_engine)

        # 4. 예산 최적화 도구
        self.budget_optimizer = FunctionTool(
            name="optimize_travel_budget",
            description="여행 예산을 카테고리별로 최적 배분",
            func=self._optimize_travel_budget,
        )
        self.add_tool(self.budget_optimizer)

        # 5. 일정 생성 도구
        self.itinerary_generator = FunctionTool(
            name="generate_itinerary",
            description="최종 선택된 목적지의 상세 일정 생성",
            func=self._generate_itinerary,
        )
        self.add_tool(self.itinerary_generator)

    def _setup_workflows(self):
        """ADK 워크플로우 구성 - Sequential/Parallel 조합"""

        # 메인 여행 추천 워크플로우 (Sequential)
        self.main_workflow = Workflow(
            name="travel_recommendation_workflow",
            steps=[
                Step("analyze_preferences", self._step_analyze_preferences),
                Step("search_destinations", self._step_search_destinations),
                Step("parallel_analysis", self._step_parallel_analysis),
                Step("generate_recommendations", self._step_generate_recommendations),
            ],
        )
        self.add_workflow(self.main_workflow)

        # 병렬 분석 서브-에이전트들
        self.parallel_analyzer = ParallelAgent(
            name="parallel_destination_analyzer",
            agents=[
                LlmAgent("preference_matcher", model="gemini-1.5-pro"),
                LlmAgent("budget_analyzer", model="gemini-1.5-pro"),
                LlmAgent("itinerary_planner", model="gemini-1.5-pro"),
            ],
        )

    def _setup_callbacks(self):
        """ADK 이벤트 기반 콜백 시스템"""

        self.add_callback("on_state_change", self._on_state_change)
        self.add_callback("on_workflow_start", self._on_workflow_start)
        self.add_callback("on_workflow_complete", self._on_workflow_complete)
        self.add_callback("on_tool_executed", self._on_tool_executed)
        self.add_callback("on_error", self._on_error)

    async def run(self, context: Context) -> Dict[str, Any]:
        """
        ADK 에이전트 메인 실행 함수
        상태 관리와 워크플로우 실행을 통합
        """
        try:
            # 상태 초기화
            await self._update_state(TravelState.INITIALIZED, context)

            # 워크플로우 실행 시작
            await self._emit_event(
                "on_workflow_start",
                {"workflow": "travel_recommendation", "context": context.data},
            )

            # 메인 워크플로우 실행
            workflow_result = await self._execute_main_workflow(context)

            # 최종 상태 업데이트
            await self._update_state(TravelState.COMPLETED, context)

            # 완료 이벤트
            await self._emit_event(
                "on_workflow_complete",
                {
                    "result": workflow_result,
                    "recommendations_count": len(
                        workflow_result.get("recommendations", [])
                    ),
                },
            )

            return workflow_result

        except Exception as e:
            await self._update_state(TravelState.ERROR, context)
            await self._emit_event("on_error", {"error": str(e)})
            raise

    async def _execute_main_workflow(self, context: Context) -> Dict[str, Any]:
        """메인 워크플로우 실행 - ADK의 핵심 워크플로우 패턴"""

        results = {}

        # Step 1: 선호도 분석 (Sequential)
        await self._update_state(TravelState.ANALYZING_PREFERENCES, context)
        preferences = await self._step_analyze_preferences(context)
        results["preferences"] = preferences

        # Step 2: 목적지 검색 (Sequential)
        await self._update_state(TravelState.SEARCHING_DESTINATIONS, context)
        destinations = await self._step_search_destinations(context, preferences)
        results["destinations"] = destinations

        # Step 3: 병렬 분석 (Parallel)
        await self._update_state(TravelState.MATCHING_PREFERENCES, context)
        parallel_results = await self._step_parallel_analysis(
            context, destinations, preferences
        )
        results["analysis"] = parallel_results

        # Step 4: 최종 추천 생성 (Sequential)
        await self._update_state(TravelState.FINALIZING_RECOMMENDATIONS, context)
        recommendations = await self._step_generate_recommendations(context, results)
        results["recommendations"] = recommendations

        return results

    async def _step_analyze_preferences(self, context: Context) -> Dict[str, Any]:
        """Step 1: 사용자 선호도 분석"""
        user_input = context.get("user_input", "")

        # 도구 실행
        preferences = await self.preference_analyzer.func(user_input, context)

        # 상태 업데이트
        self.state.update("preferences", preferences)

        # 메모리 저장
        await self.memory.store(
            {
                "step": "analyze_preferences",
                "input": user_input,
                "output": preferences,
                "timestamp": datetime.now().isoformat(),
            }
        )

        await self._emit_event(
            "on_tool_executed", {"tool": "preference_analyzer", "result": preferences}
        )

        return preferences

    async def _step_search_destinations(
        self, context: Context, preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Step 2: 목적지 검색"""
        search_query = self._build_search_query(preferences)

        # 검색 도구 실행
        search_results = await self.destination_searcher._search(search_query)

        # 결과 처리
        destinations = self._process_search_results(search_results, preferences)

        self.state.update("destinations", destinations)

        await self._emit_event(
            "on_tool_executed",
            {
                "tool": "destination_searcher",
                "query": search_query,
                "results_count": len(destinations),
            },
        )

        return destinations

    async def _step_parallel_analysis(
        self,
        context: Context,
        destinations: List[Dict[str, Any]],
        preferences: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Step 3: 병렬 분석 실행"""

        # 병렬 분석 컨텍스트 구성
        analysis_context = Context(
            {
                "destinations": destinations,
                "preferences": preferences,
                "budget": context.get("budget", 1000000),
            }
        )

        # 병렬 에이전트 실행
        parallel_results = await self.parallel_analyzer.run(analysis_context)

        # 결과 통합
        integrated_analysis = {
            "preference_matching": parallel_results["parallel_results"][0],
            "budget_optimization": parallel_results["parallel_results"][1],
            "itinerary_planning": parallel_results["parallel_results"][2],
        }

        self.state.update("analysis", integrated_analysis)

        return integrated_analysis

    async def _step_generate_recommendations(
        self, context: Context, workflow_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Step 4: 최종 추천 생성"""

        recommendations = []
        destinations = workflow_results.get("destinations", [])
        analysis = workflow_results.get("analysis", {})

        # 안전한 분석 결과 추출
        preference_matching = analysis.get("preference_matching", {})
        budget_optimization = analysis.get("budget_optimization", {})
        itinerary_planning = analysis.get("itinerary_planning", {})

        for i, destination in enumerate(destinations[:3]):  # 상위 3개
            # 안전한 점수 추출
            scores = preference_matching.get("scores", [0.8, 0.7, 0.6])
            match_score = scores[i] if i < len(scores) else 0.8

            # 안전한 일정 추출
            itineraries = itinerary_planning.get("itineraries", [{}])
            itinerary = itineraries[i] if i < len(itineraries) else {}

            recommendation = {
                "id": f"rec_{context.get('session_id', 'unknown')}_{i+1}",
                "destination": destination.get("name", "알 수 없는 목적지"),
                "title": f"{destination.get('name', '여행지')} 여행",
                "description": destination.get("description", "아름다운 여행지입니다."),
                "match_score": match_score,
                "budget_breakdown": budget_optimization,
                "itinerary": itinerary,
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.85 - (i * 0.05),  # 상위일수록 높은 신뢰도
            }
            recommendations.append(recommendation)

        self.state.update("recommendations", recommendations)
        self.recommendations_count += len(recommendations)

        return recommendations

    # ADK 도구 함수들
    async def _analyze_user_preferences(
        self, user_input: str, context: Context
    ) -> Dict[str, Any]:
        """사용자 선호도 분석 도구"""
        # 실제로는 LLM을 통한 고도화된 분석
        preferences = {
            "nature": "자연" in user_input or "힐링" in user_input,
            "culture": "문화" in user_input or "역사" in user_input,
            "food": "맛집" in user_input or "음식" in user_input,
            "budget_conscious": "저렴" in user_input or "절약" in user_input,
            "luxury": "럭셔리" in user_input or "고급" in user_input,
            "family": "가족" in user_input,
            "solo": "혼자" in user_input or "솔로" in user_input,
            "extracted_budget": self._extract_budget(user_input),
            "extracted_duration": self._extract_duration(user_input),
        }
        return preferences

    async def _match_destinations(
        self, destinations: List[Dict[str, Any]], preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """목적지 매칭 도구"""
        matches = []
        for dest in destinations:
            score = self._calculate_match_score(dest, preferences)
            matches.append(
                {
                    "destination": dest,
                    "match_score": score,
                    "matching_factors": self._get_matching_factors(dest, preferences),
                }
            )

        # 점수순 정렬
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "matches": matches,
            "total_analyzed": len(destinations),
            "scores": [m["match_score"] for m in matches],
        }

    async def _optimize_travel_budget(
        self, budget: int, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """예산 최적화 도구"""
        base_allocation = {
            "accommodation": 0.35,
            "transportation": 0.25,
            "food": 0.25,
            "activities": 0.10,
            "shopping": 0.05,
        }

        # 선호도에 따른 배분 조정
        if preferences.get("food"):
            base_allocation["food"] += 0.05
            base_allocation["shopping"] -= 0.05

        if preferences.get("luxury"):
            base_allocation["accommodation"] += 0.10
            base_allocation["activities"] -= 0.10

        return {
            "total_budget": budget,
            "allocation": {k: int(budget * v) for k, v in base_allocation.items()},
            "optimization_strategy": "preference_based",
        }

    async def _generate_itinerary(
        self, destination: Dict[str, Any], duration: int
    ) -> Dict[str, Any]:
        """일정 생성 도구"""
        # 간단한 일정 템플릿
        return {
            "destination": destination["name"],
            "duration": duration,
            "daily_plan": [
                {"day": i + 1, "activities": [f"Activity {j+1}" for j in range(3)]}
                for i in range(duration)
            ],
        }

    # 상태 관리 및 이벤트 시스템
    async def _update_state(self, new_state: TravelState, context: Context):
        """상태 업데이트"""
        old_state = self.travel_state
        self.travel_state = new_state

        await self._emit_event(
            "on_state_change",
            {
                "old_state": old_state.value,
                "new_state": new_state.value,
                "context": context.data,
            },
        )

    async def _emit_event(self, event_name: str, data: Dict[str, Any]):
        """이벤트 발생"""
        if event_name in self.callbacks:
            event = Event(event_name, data)
            await self.callbacks[event_name](event)

    # 콜백 함수들
    async def _on_state_change(self, event: Event):
        print(f"🔄 상태 변경: {event.data['old_state']} → {event.data['new_state']}")

    async def _on_workflow_start(self, event: Event):
        self.workflow_executions += 1
        print(
            f"🚀 워크플로우 시작: {event.data['workflow']} (실행 횟수: {self.workflow_executions})"
        )

    async def _on_workflow_complete(self, event: Event):
        print(f"✅ 워크플로우 완료: {event.data['recommendations_count']}개 추천 생성")

    async def _on_tool_executed(self, event: Event):
        print(f"🔧 도구 실행: {event.data['tool']}")

    async def _on_error(self, event: Event):
        print(f"❌ 오류 발생: {event.data['error']}")

    # 유틸리티 함수들
    def _build_search_query(self, preferences: Dict[str, Any]) -> str:
        query_parts = []
        if preferences.get("nature"):
            query_parts.append("자연 경관")
        if preferences.get("culture"):
            query_parts.append("문화 관광")
        return " ".join(query_parts) if query_parts else "인기 여행지"

    def _process_search_results(
        self, search_results: Dict[str, Any], preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Mock 목적지 데이터
        destinations = [
            {"name": "제주도", "category": "nature", "popularity": 9.5},
            {"name": "부산", "category": "city", "popularity": 8.7},
            {"name": "경주", "category": "culture", "popularity": 8.2},
            {"name": "강릉", "category": "nature", "popularity": 8.0},
        ]
        return destinations

    def _calculate_match_score(
        self, destination: Dict[str, Any], preferences: Dict[str, Any]
    ) -> float:
        score = 0.5  # 기본 점수

        if preferences.get("nature") and destination["category"] == "nature":
            score += 0.3
        if preferences.get("culture") and destination["category"] == "culture":
            score += 0.3

        # 인기도 반영
        score += destination.get("popularity", 5.0) / 10.0 * 0.2

        return min(score, 1.0)

    def _get_matching_factors(
        self, destination: Dict[str, Any], preferences: Dict[str, Any]
    ) -> List[str]:
        factors = []
        if preferences.get("nature") and destination["category"] == "nature":
            factors.append("자연 선호도 일치")
        if destination.get("popularity", 0) > 8.0:
            factors.append("높은 인기도")
        return factors

    def _extract_budget(self, text: str) -> int:
        import re

        match = re.search(r"(\d+)만원", text)
        return int(match.group(1)) * 10000 if match else 1000000

    def _extract_duration(self, text: str) -> int:
        import re

        match = re.search(r"(\d+)박\s*(\d+)일", text)
        return int(match.group(2)) if match else 3

    def get_agent_status(self) -> Dict[str, Any]:
        """ADK 에이전트 상태 정보"""
        return {
            "agent_name": self.name,
            "agent_type": "ADK_LlmAgent",
            "current_state": self.travel_state.value,
            "state_history": [entry for entry in self.state.history[-10:]],  # 최근 10개
            "tools_count": len(self.tools),
            "workflows_count": len(self.workflows),
            "workflow_executions": self.workflow_executions,
            "recommendations_generated": self.recommendations_count,
            "memory_size": len(self.memory.data),
            "capabilities": [
                "sequential_workflow",
                "parallel_analysis",
                "state_management",
                "tool_chaining",
            ],
            "last_updated": datetime.now().isoformat(),
        }


# 팩토리 함수
def create_travel_agent(
    project_id: str, location: str = "us-central1"
) -> TravelRecommendationAgent:
    """ADK 기반 여행 추천 에이전트 생성"""
    agent = TravelRecommendationAgent(project_id=project_id, location=location)
    print(f"✅ ADK 여행 추천 에이전트 생성: {agent.name}")
    print(f"   상태 관리: {agent.travel_state.value}")
    print(f"   도구 수: {len(agent.tools)}")
    print(f"   워크플로우 수: {len(agent.workflows)}")
    return agent


# 테스트 함수
async def test_adk_travel_agent():
    """ADK 여행 추천 에이전트 워크플로우 테스트"""
    print("🧪 ADK 여행 추천 에이전트 워크플로우 테스트")

    # 에이전트 생성
    agent = create_travel_agent("test-project", "us-central1")

    # 테스트 컨텍스트
    test_context = Context(
        {
            "session_id": "adk_test_001",
            "user_input": "제주도로 가족 여행을 계획하고 있어요. 100만원 예산으로 자연 중심 3박 4일 여행을 원합니다.",
            "budget": 1000000,
            "user_id": "test_user",
        }
    )

    # ADK 워크플로우 실행
    print(f"\n🚀 ADK 워크플로우 실행 시작")
    result = await agent.run(test_context)

    # 결과 출력
    print(f"\n📊 ADK 워크플로우 결과:")
    print(f"   최종 상태: {agent.travel_state.value}")
    print(f"   추천 수: {len(result.get('recommendations', []))}")
    print(f"   워크플로우 실행 횟수: {agent.workflow_executions}")

    for i, rec in enumerate(result.get("recommendations", [])[:2]):
        print(f"   추천 {i+1}: {rec['title']} (매칭점수: {rec['match_score']:.2f})")

    # 상태 정보
    status = agent.get_agent_status()
    print(f"\n📈 ADK 에이전트 상태:")
    print(f"   능력: {status['capabilities']}")
    print(f"   상태 히스토리 크기: {len(status['state_history'])}")

    print("✅ ADK 테스트 완료")


if __name__ == "__main__":
    # ADK 워크플로우 테스트 실행
    asyncio.run(test_adk_travel_agent())

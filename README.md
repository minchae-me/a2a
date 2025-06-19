# 🤖 ADK + A2A 통합 여행 추천 에이전트 시스템

> **Google ADK(Agent Development Kit)**와 **A2A(Agent2Agent Protocol)**의 차이점을 실증하고 상호 보완 관계를 구현한 여행 추천 시스템

## 🎯 프로젝트 목적

이 프로젝트는 Google의 두 가지 에이전트 기술의 **핵심 차이점**을 명확히 구현하여 보여줍니다:

- **ADK (Agent Development Kit)**: 에이전트 내부 구조와 워크플로우 설계 프레임워크
- **A2A (Agent2Agent Protocol)**: 에이전트 간 통신에 특화된 개방형 프로토콜

## 🏗️ 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                    통합 에이전트 시스템                            │
├─────────────────────────────────────────────────────────────────┤
│  🧠 ADK (내부 구조)          │  📡 A2A (통신 인터페이스)      │
│  ─────────────────────       │  ──────────────────────        │
│  • BaseAgent 상속            │  • JSON-RPC 프로토콜           │
│  • State 관리 (enum)         │  • Agent Card 서비스           │
│  • Sequential/Parallel       │  • 인증 & 세션 관리            │
│  • 도구 체이닝 & MCP         │  • 스트리밍 지원               │
│  • 이벤트 기반 콜백          │  • 분산 에이전트 협업          │
└─────────────────────────────────────────────────────────────────┘
```

## 📂 프로젝트 구조

```
A2A/
├── 📦 adk_agents/              # ADK 기반 에이전트 (내부 로직)
│   ├── travel_agent.py         # ADK 여행 추천 에이전트
│   └── multi_agent_orchestrator.py
├── 🌐 a2a_agents/              # A2A 기반 에이전트 (통신 인터페이스)
│   ├── __init__.py
│   └── travel_agent.py         # A2A 여행 통신 에이전트
├── 🔧 adk_config.py            # ADK 설정
├── 🤝 integration_example.py   # ADK + A2A 통합 데모
├── 📋 requirements.txt         # 통합 의존성
├── 📚 README.md               # 프로젝트 문서
└── 📖 A2A_개발_레퍼런스_가이드.md
```

## 🚀 빠른 시작

### 🌟 권장: UV 사용 (최신, 초고속!)

```bash
# UV 설치 (한번만)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 실행
python uv_run.py
```

### 기존 방법 (호환성 유지)

#### 1. 의존성 설치

```bash
cd A2A
pip install -r requirements.txt
```

#### 2. 통합 데모 실행

```bash
# ADK + A2A 차이점 실증 데모
python integration_example.py
```

#### 3. 개별 테스트

```bash
# ADK 에이전트 테스트 (내부 워크플로우)
python adk_agents/travel_agent.py

# A2A 에이전트 테스트 (통신 프로토콜)
python a2a_agents/travel_agent.py

# MCP + ADK + A2A 통합 테스트 (최신!)
# 방법 1: 자동 통합 실행 (권장)
python run_with_mcp.py

# 방법 2: 수동 실행
# 터미널 1: cd ../mcp && python standalone_mcp_server.py
# 터미널 2: python mcp_integration.py
```

## 🎯 핵심 차이점 실증

### 🧠 ADK (Agent Development Kit)
**역할**: 에이전트 내부 개발 프레임워크

```python
# ADK: 내부 구조와 워크플로우 중심
class TravelRecommendationAgent(LlmAgent):
    def __init__(self, project_id: str):
        super().__init__(name="TravelAgent", model="gemini-1.5-pro")
        self.travel_state = TravelState.INITIALIZED
        self._setup_tools()        # 도구 체이닝
        self._setup_workflows()    # Sequential/Parallel 워크플로우
        self._setup_callbacks()    # 이벤트 기반 콜백
    
    async def run(self, context: Context):
        # 상태 관리 + 워크플로우 실행
        return await self._execute_main_workflow(context)
```

**ADK 특징**:
- ✅ State 관리 (TravelState enum)
- ✅ Sequential/Parallel 워크플로우 구성
- ✅ 도구 체이닝 및 MCP 통합
- ✅ 이벤트 기반 콜백 시스템
- ✅ LLM 기반 흐름 제어

### 📡 A2A (Agent2Agent Protocol)
**역할**: 에이전트 간 통신 표준

```python
# A2A: 통신 프로토콜과 인터페이스 중심
class TravelA2AAgent:
    def __init__(self, host="0.0.0.0", port=9999):
        self.skills = self._define_a2a_skills()      # 서비스 정의
        self.agent_card = self._create_agent_card()  # 서비스 디스커버리
        self.server = A2AServer(agent_card=self.agent_card)
    
    async def handle_a2a_request(self, request: ExecuteRequest):
        # JSON-RPC 기반 표준 통신 처리
        return await self._process_skill_request(request)
```

**A2A 특징**:
- ✅ JSON-RPC 기반 표준 통신 프로토콜
- ✅ Agent Card를 통한 서비스 디스커버리
- ✅ 동기/비동기 요청-응답 메시징
- ✅ 파일 및 스트리밍 전송 지원
- ✅ 보안 및 인증 계층

## 🤝 통합 패턴

```python
# 통합 패턴: ADK 내부 + A2A 외부
class TravelAgentOrchestrator:
    def __init__(self):
        # 1. ADK로 내부 로직 구현
        self.adk_agent = create_travel_agent("project-id")
        
        # 2. A2A로 통신 인터페이스 구성
        self.a2a_agent = create_a2a_travel_agent()
    
    async def demonstrate_adk_vs_a2a(self):
        # ADK: 내부 워크플로우 실행
        adk_result = await self.adk_agent.run(context)
        
        # A2A: 외부 통신 처리
        a2a_result = await self.a2a_agent.handle_a2a_request(request)
        
        return {"adk_logic": adk_result, "a2a_communication": a2a_result}
```

## 📊 실행 결과 예시

```
🎯 ADK vs A2A 차이점 실증 데모
================================================================================
👤 사용자 요청: 제주도로 가족 여행 계획해주세요. 예산 150만원, 3박 4일

🔧 1단계: ADK 에이전트 내부 워크플로우 실행
   🔄 상태 관리: initialized → analyzing_preferences → completed
   🔧 도구 실행: preference_analyzer, destination_searcher
   ✅ ADK 결과: 3개 추천 생성, 워크플로우 1회 실행

🌐 2단계: A2A 프로토콜 통신 인터페이스  
   📡 JSON-RPC 통신: travel_destination_recommendation 스킬 호출
   🔐 인증 완료: mock_token_abc123...
   ✅ A2A 결과: 통신 성공, 1건 처리, 1개 활성 세션

🤝 3단계: ADK + A2A 상호 보완 관계
   패턴: ADK 내부 로직 + A2A 통신 래핑
   ✅ 통합 결과: 완전한 분산 에이전트 시스템 구현
```

## 💡 핵심 학습 포인트

### 🎯 **개발 흐름의 차이**
1. **ADK 먼저**: 에이전트 내부 로직과 워크플로우 구현
2. **A2A 나중에**: 완성된 에이전트를 A2A 프로토콜로 감싸서 외부 노출
3. **통합 결과**: `ADK_internal_logic + A2A_communication_wrapper`

### 🔄 **상호 보완 관계**
- **MCP**: "외부 도구와 어떻게 연결할 것인가?" (How to Connect Tools)
- **ADK**: "에이전트를 어떻게 만들 것인가?" (How to Build)
- **A2A**: "에이전트들을 어떻게 연결할 것인가?" (How to Connect Agents)
- **결과**: MCP 도구 + ADK 로직 + A2A 통신 = 완전한 에이전트 생태계

## 🛠️ 고급 기능

### 1. **분산 에이전트 협업**
```python
# 여러 A2A 에이전트 간 병렬 통신
async def collaborative_planning():
    tasks = [
        agent1.call_other_agent("http://agent2:9999", "analyze_budget", data),
        agent2.call_other_agent("http://agent3:10000", "plan_itinerary", data),
    ]
    results = await asyncio.gather(*tasks)
```

### 2. **실시간 스트리밍**
```python
# A2A 스트리밍 응답
async def stream_recommendations():
    async for chunk in agent.handle_streaming_request(request):
        yield chunk  # 실시간 추천 업데이트
```

### 3. **상태 기반 워크플로우**
```python
# ADK 상태 관리
class TravelState(Enum):
    ANALYZING_PREFERENCES = "analyzing"
    SEARCHING_DESTINATIONS = "searching"  
    FINALIZING_RECOMMENDATIONS = "finalizing"
```

## 🏆 프로젝트 성과

✅ **ADK와 A2A 차이점 명확 구현**
- 내부 구조 vs 통신 인터페이스 역할 분리
- 실행 가능한 코드로 개념 실증

✅ **분산 에이전트 시스템 기반**
- MLOps 파이프라인 구축 준비
- 확장 가능한 아키텍처 설계

✅ **실무 적용 가능한 패턴**
- Mock 클래스로 학습 지원
- 한국어 주석으로 이해도 향상

## 📚 추가 자료

- [Google ADK 공식 문서](https://google.github.io/adk-docs/agents/)
- [A2A Protocol 사양](https://google-a2a.github.io/A2A/latest/)
- [A2A 개발 레퍼런스 가이드](./A2A_개발_레퍼런스_가이드.md)

---

**© 2025 ADK + A2A 통합 여행 추천 시스템**  
*Google ADK와 A2A Protocol의 차이점과 상호 보완 관계 실증 프로젝트* 
# 🤖 A2A (Agent2Agent Protocol) + ADK 통합 프로젝트

A2A 프로토콜과 ADK(Agent Development Kit)를 통합한 차세대 AI 에이전트 시스템입니다.

## 📖 프로젝트 개요

이 프로젝트는 **A2A(Agent2Agent Protocol)**와 **ADK(Agent Development Kit)**를 결합하여 확장 가능한 AI 에이전트 생태계를 구축합니다.

### 🎯 핵심 아키텍처
- **A2A Protocol**: 에이전트 간 표준화된 통신 프로토콜
- **ADK**: Google의 차세대 에이전트 개발 프레임워크  
- **MCP Integration**: Model Context Protocol 연동 (개발 중)

## 🚀 빠른 시작

### ✅ **완전히 작동하는 실행** (추천)

```bash
# 🎯 완전한 A2A + ADK 데모 (가장 추천!)
python final_demo.py

# 🧪 간단한 통합 테스트
python simple_test.py

# 📡 A2A 에이전트 단독 테스트
python a2a_agents/travel_agent.py

# ⚙️ ADK 에이전트 단독 테스트  
python adk_agents/travel_agent.py
```

### ⚠️ **개발 중인 기능들**

```bash
# 🚧 MCP 서버 연결 이슈로 현재 작업 중
# python run_with_mcp.py      # <- 현재 실행 안됨
# python mcp_integration.py   # <- 현재 실행 안됨

# 🔧 기타 개발 중인 스크립트들
python integration_example.py  # 기본 작동하나 final_demo.py가 더 좋음
python run_demo.py             # 기본 작동하나 simple_test.py가 더 좋음
```

### UV 사용 (권장)

이 프로젝트는 **UV**(Ultra-fast Python package installer)를 지원합니다:

```bash
# UV 설치 (한 번만)
curl -LsSf https://astral.sh/uv/install.sh | sh

# UV로 실행 (빠름!)
uv run python final_demo.py

# 또는 편리한 스크립트 사용
python uv_run.py
```

## 📋 실행 결과 예시

### `final_demo.py` 실행 결과:
```
🚀 A2A + ADK 최종 통합 데모 시작
================================================================================
🔧 컴포넌트 초기화...
✅ ADK-TravelAgent 초기화 완료
✅ A2A-TravelBot 초기화 완료

📝 시나리오 1: 제주도 여행 추천
🏨 호텔: 제주신라호텔, 파라다이스호텔
🎯 활동: 한라산 등반, 성산일출봉, 카페거리
🍽️ 음식: 흑돼지, 해물라면, 한라봉
💰 비용: 항공료 15만원 + 숙박 20만원 + 식사 10만원

🎉 A2A + ADK 최종 통합 데모 완료!
✅ 모든 기능이 정상적으로 작동합니다!
```

## 📁 핵심 파일 구조

```
A2A/
├── final_demo.py           # ✅ 완전한 A2A + ADK 데모 (최고 추천)
├── simple_test.py          # ✅ 간단한 통합 테스트  
├── a2a_agents/             # A2A 프로토콜 에이전트들
│   └── travel_agent.py     # ✅ A2A 여행 에이전트
├── adk_agents/             # ADK 에이전트들
│   └── travel_agent.py     # ✅ ADK 여행 에이전트
├── run_with_mcp.py         # 🚧 MCP 통합 (개발 중)
├── mcp_integration.py      # 🚧 MCP 통합 (개발 중)
├── pyproject.toml          # ✅ UV 프로젝트 설정
└── uv_run.py              # ✅ UV 실행 스크립트
```

## 🎯 기능별 실행 가이드

### 1. 여행 추천 시스템 체험
```bash
python final_demo.py
# → 제주도/서울 여행 추천, 날씨 정보, 오류 처리까지 완전한 데모
```

### 2. A2A 프로토콜 이해
```bash
python simple_test.py  
# → A2A 프로토콜의 기본 통신 방식 학습
```

### 3. 개별 에이전트 테스트
```bash
python a2a_agents/travel_agent.py   # A2A 방식
python adk_agents/travel_agent.py   # ADK 방식
```

## 🔧 기술 스택

- **Python 3.12+**
- **A2A Protocol**: 에이전트 간 통신 표준
- **Google ADK**: 에이전트 개발 프레임워크
- **UV**: 초고속 패키지 관리자 (선택사항)
- **MCP**: Model Context Protocol (개발 중)

## 📚 주요 개념

### A2A (Agent2Agent Protocol)
- JSON-RPC 스타일의 에이전트 통신 표준
- Agent Card를 통한 서비스 디스커버리
- 표준화된 요청/응답 형식

### ADK (Agent Development Kit)
- Google의 차세대 에이전트 개발 프레임워크
- Sequential/Parallel 워크플로우 지원
- 내장된 상태 관리와 도구 통합

### 통합 아키텍처
```
사용자 요청 → A2A Protocol → ADK Agent → 비즈니스 로직 → 응답
```

## 🛠️ 개발 상태

| 기능 | 상태 | 실행 파일 |
|------|------|-----------|
| A2A + ADK 통합 | ✅ 완료 | `final_demo.py` |
| 간단한 테스트 | ✅ 완료 | `simple_test.py` |
| A2A 에이전트 | ✅ 완료 | `a2a_agents/travel_agent.py` |
| ADK 에이전트 | ✅ 완료 | `adk_agents/travel_agent.py` |
| UV 지원 | ✅ 완료 | `uv_run.py` |
| MCP 통합 | 🚧 개발 중 | `run_with_mcp.py` (실행 안됨) |

## 🔮 향후 계획

1. **MCP 서버 연동 문제 해결** - STDIO vs HTTP 통신 방식 정리
2. **실제 API 연동** - Google AI, 날씨 API 등
3. **웹 인터페이스** - FastAPI 기반 REST API
4. **다중 에이전트 협업** - 복수 에이전트 간 협업 시나리오

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 GitHub Issues를 활용해 주세요.

---
**⚡ 빠른 시작**: `python final_demo.py` 실행하면 모든 기능을 체험할 수 있습니다! 
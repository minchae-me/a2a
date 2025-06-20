# 🤖 A2A (Agent2Agent Protocol) + ADK + MCP 통합 프로젝트

A2A 프로토콜, ADK(Agent Development Kit), MCP(Model Context Protocol)를 완전 통합한 차세대 AI 에이전트 시스템입니다.

## 📖 프로젝트 개요

이 프로젝트는 **A2A + ADK + MCP** 3개 기술을 완전 통합하여 확장 가능한 AI 에이전트 생태계를 구축합니다.

### 🎯 핵심 아키텍처
- **A2A Protocol**: 에이전트 간 표준화된 통신 프로토콜
- **ADK**: Google의 차세대 에이전트 개발 프레임워크  
- **MCP Integration**: Model Context Protocol HTTP 서버 완전 연동 ✅

## 🚀 빠른 시작

### ✅ **완전히 작동하는 실행** (추천)

```bash
# 🎯 A2A + ADK + MCP 완전 통합 데모 (최고 추천!)
python run_full_demo.py

# 🧪 A2A + ADK 기본 데모 (MCP 없이)
python final_demo.py

# 🔍 간단한 통합 테스트
python simple_test.py

# 📡 A2A 에이전트 단독 테스트
python a2a_agents/travel_agent.py

# ⚙️ ADK 에이전트 단독 테스트  
python adk_agents/travel_agent.py
```

### 🌐 **MCP HTTP 서버 별도 실행**

```bash
# MCP 서버만 실행하고 싶을 때
python mcp_server/http_mcp_server.py

# MCP 클라이언트 테스트
python mcp_http_client.py
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

### `run_full_demo.py` 실행 결과 (A2A + ADK + MCP 완전 통합):
```
🚀 A2A + ADK + MCP 완전 통합 데모 시작
================================================================================
🌐 MCP HTTP 서버 시작 중... (포트 8000)
✅ MCP HTTP 서버 시작 완료 (PID: 48195)
🤖 A2A-MCP-TravelBot 초기화 완료

📝 시나리오 1: 에이전트 능력 확인
✅ 사용 가능한 도구: search_destinations, recommend_travel, get_weather, analyze_budget

📝 시나리오 2: 바다 관련 여행지 검색
🌊 검색 결과: 부산 - 해운대 해수욕장과 광안리 해변으로 유명한 해안 도시

📝 시나리오 3: 제주도 중간예산 여행 추천
🏨 호텔: 제주 오션스위트호텔, 제주 파라다이스호텔
🎯 활동: 한라산 국립공원, 성산일출봉, 만장굴
🍽️ 음식: 제주 흑돼지, 갈치조림, 한라봉 디저트
💰 총 예산: 약 35-45만원 (2박3일 기준)

📝 시나리오 4: 부산 날씨 정보
🌤️ 현재 날씨: 맑음, 기온 18°C, 습도 65%, 바람 약함

📝 시나리오 5: 서울 2박3일 2명 예산 분석
💰 저예산: 25-30만원 | 중예산: 40-50만원 | 고예산: 70-80만원

🎉 A2A + ADK + MCP 완전 통합 데모 완료!
✅ 모든 기능이 정상적으로 작동합니다!
```

## 📁 핵심 파일 구조

```
A2A/
├── run_full_demo.py        # ✅ A2A + ADK + MCP 완전 통합 (최고 추천!)
├── final_demo.py           # ✅ A2A + ADK 기본 데모 (MCP 없이)
├── simple_test.py          # ✅ 간단한 통합 테스트  
├── mcp_http_client.py      # ✅ MCP HTTP 클라이언트
├── mcp_server/             # MCP 서버 폴더
│   └── http_mcp_server.py  # ✅ MCP HTTP 서버 (포트 8000)
├── a2a_agents/             # A2A 프로토콜 에이전트들
│   └── travel_agent.py     # ✅ A2A 여행 에이전트
├── adk_agents/             # ADK 에이전트들
│   └── travel_agent.py     # ✅ ADK 여행 에이전트
├── pyproject.toml          # ✅ UV 프로젝트 설정
└── uv_run.py              # ✅ UV 실행 스크립트
```

## 🎯 기능별 실행 가이드

### 1. 완전 통합 시스템 체험 (최고 추천!)
```bash
python run_full_demo.py
# → A2A + ADK + MCP 완전 통합, 실제 여행 데이터 제공
# → 여행지 검색, 추천, 날씨, 예산 분석까지 모든 기능
```

### 2. 기본 여행 추천 시스템 (MCP 없이)
```bash
python final_demo.py
# → A2A + ADK 기본 통합, 시뮬레이션 데이터 사용
```

### 3. A2A 프로토콜 이해
```bash
python simple_test.py  
# → A2A 프로토콜의 기본 통신 방식 학습
```

### 4. 개별 컴포넌트 테스트
```bash
python a2a_agents/travel_agent.py   # A2A 방식
python adk_agents/travel_agent.py   # ADK 방식
python mcp_server/http_mcp_server.py # MCP 서버만
python mcp_http_client.py           # MCP 클라이언트만
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
사용자 요청 → A2A Protocol → ADK Agent → MCP HTTP Server → 실제 데이터 → 응답
```

### MCP 통합 플로우
1. **MCP HTTP 서버** (포트 8000) - 여행 데이터 제공
2. **ADK 에이전트** - MCP 도구 활용 및 비즈니스 로직  
3. **A2A 프로토콜** - 표준화된 에이전트 통신
4. **통합 실행** - 자동 서버 시작/종료 및 프로세스 관리

## 🛠️ 개발 상태

| 기능 | 상태 | 실행 파일 |
|------|------|-----------|
| **A2A + ADK + MCP 완전 통합** | ✅ **완료** | `run_full_demo.py` |
| A2A + ADK 기본 통합 | ✅ 완료 | `final_demo.py` |
| MCP HTTP 서버 | ✅ 완료 | `mcp_server/http_mcp_server.py` |
| MCP HTTP 클라이언트 | ✅ 완료 | `mcp_http_client.py` |
| A2A 에이전트 | ✅ 완료 | `a2a_agents/travel_agent.py` |
| ADK 에이전트 | ✅ 완료 | `adk_agents/travel_agent.py` |
| 간단한 테스트 | ✅ 완료 | `simple_test.py` |
| UV 지원 | ✅ 완료 | `uv_run.py` |

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 GitHub Issues를 활용해 주세요.

---
**⚡ 빠른 시작**: `python run_full_demo.py` 실행하면 **A2A + ADK + MCP 완전 통합**을 체험할 수 있습니다! 
# ⚡ 빠른 시작 가이드

> ADK + A2A 통합 여행 추천 에이전트 시스템을 즉시 실행해보세요!

## 🚀 원클릭 실행

### 1. 빠른 데모 (권장)
```bash
cd A2A
python run_demo.py
```
**결과**: ADK와 A2A의 차이점을 즉시 확인 (약 10초 소요)

### 2. 대화형 메뉴
```bash
python main.py
```
**결과**: 메뉴를 통해 원하는 테스트 선택 실행

## 📋 실행 옵션

### Option 1: 통합 데모 (차이점 실증)
```bash
python integration_example.py
```
- ✅ ADK 내부 워크플로우 실행
- ✅ A2A 통신 프로토콜 테스트  
- ✅ 두 기술의 상호 보완 관계 실증

### Option 2: ADK 에이전트 (내부 로직)
```bash
python adk_agents/travel_agent.py
```
- 🧠 상태 관리 (TravelState)
- 🔄 Sequential/Parallel 워크플로우
- 🔧 도구 체이닝 및 콜백 시스템

### Option 3: A2A 에이전트 (통신 인터페이스)
```bash
python a2a_agents/travel_agent.py
```
- 📡 JSON-RPC 프로토콜
- 🔐 인증 및 세션 관리
- 🃏 Agent Card 서비스 디스커버리

## 🎯 기대 결과

### 성공적인 실행 시:
```
✅ ADK 처리 결과:
   최종 상태: completed
   워크플로우 실행: 1회
   생성된 추천: 3개

✅ A2A 통신 결과:
   통신 성공: True
   프로토콜: JSON-RPC 2.0
   처리된 요청: 1건

🏆 결론: ADK_internal_logic + A2A_communication_wrapper
```

## 🔧 문제 해결

### 실행 오류 시:
1. **Python 버전 확인**: Python 3.8+ 필요
2. **의존성 설치**: `pip install -r requirements.txt`
3. **경로 확인**: A2A 폴더 내에서 실행

### 개별 테스트:
```bash
# ADK만 테스트
python adk_agents/travel_agent.py

# A2A만 테스트  
python a2a_agents/travel_agent.py
```

## 📚 더 알아보기

- 📖 **상세 문서**: [README.md](./README.md)
- 📋 **개발 가이드**: [A2A_개발_레퍼런스_가이드.md](./A2A_개발_레퍼런스_가이드.md)
- 🔧 **설정 파일**: [adk_config.py](./adk_config.py)

---

**🎉 5분 안에 ADK와 A2A의 차이점을 직접 체험해보세요!** 
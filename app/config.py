"""
애플리케이션 설정 클래스
환경별 설정 분리 패턴 적용
"""

import os
from typing import Dict, Any


class Config:
    """기본 설정 클래스"""

    # Flask 기본 설정
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-a2a-system"

    # Google AI Platform 설정
    GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID") or "your-project-id"
    GOOGLE_LOCATION = os.environ.get("GOOGLE_LOCATION") or "us-central1"
    GOOGLE_CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH")

    # A2A Protocol 설정 (기존 방식)
    A2A_ENABLED = True
    A2A_HOST = os.environ.get("A2A_HOST") or "localhost"
    A2A_PORT = int(os.environ.get("A2A_PORT") or 8080)
    A2A_MAX_AGENTS = int(os.environ.get("A2A_MAX_AGENTS") or 10)

    # Google ADK 설정 (새로운 방식)
    ADK_ENABLED = True
    ADK_PROJECT_ID = os.environ.get("ADK_PROJECT_ID") or GOOGLE_PROJECT_ID
    ADK_REGION = os.environ.get("ADK_REGION") or "us-central1"
    ADK_MAX_AGENTS = int(os.environ.get("ADK_MAX_AGENTS") or 5)
    ADK_TIMEOUT = int(os.environ.get("ADK_TIMEOUT") or 300)

    # MCP 설정 (통합 레이어)
    MCP_ENABLED = True
    MCP_HOST = os.environ.get("MCP_HOST") or "localhost"
    MCP_PORT = int(os.environ.get("MCP_PORT") or 8000)

    # SSE 설정
    SSE_ENABLED = True
    SSE_HEARTBEAT_INTERVAL = 30
    SSE_MAX_CONNECTIONS = 100

    # 로깅 설정
    LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"


class DevelopmentConfig(Config):
    """개발 환경 설정"""

    DEBUG = True
    A2A_HOST = "localhost"
    ADK_ENABLED = False  # 개발 중에는 Mock 사용


class ProductionConfig(Config):
    """운영 환경 설정"""

    DEBUG = False
    A2A_HOST = os.environ.get("A2A_HOST") or "0.0.0.0"
    ADK_ENABLED = True  # 운영에서는 실제 ADK 사용


class TestingConfig(Config):
    """테스트 환경 설정"""

    TESTING = True
    A2A_ENABLED = False
    ADK_ENABLED = False
    MCP_ENABLED = False


# 설정 매핑
config_class: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

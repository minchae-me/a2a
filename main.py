"""
A2A (Agent-to-Agent) 시스템 메인 애플리케이션
Flask 애플리케이션 팩토리 패턴 + 헥사고날 아키텍처 구현
"""

import os
import sys
from flask import Flask, jsonify

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app import create_app
from app.config import config_class


def main():
    """메인 실행 함수"""
    # 환경 설정
    config_name = os.environ.get("FLASK_CONFIG", "development")

    # Flask 앱 생성
    app = create_app(config_name)

    # 기본 라우트
    @app.route("/")
    def index():
        return jsonify(
            {
                "service": "A2A Travel Recommendation System",
                "version": "1.0.0",
                "architecture": "Hexagonal Architecture + DDD",
                "protocols": {
                    "a2a": "Agent-to-Agent Protocol",
                    "adk": "Google Agent Development Kit",
                    "mcp": "Model Context Protocol",
                },
                "endpoints": {
                    "travel": "/api/travel",
                    "a2a": "/api/a2a",
                    "sse": "/api/sse",
                },
                "status": "active",
            }
        )

    @app.route("/health")
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "config": config_name,
                "features": {
                    "a2a_enabled": app.config.get("A2A_ENABLED", False),
                    "adk_enabled": app.config.get("ADK_ENABLED", False),
                    "mcp_enabled": app.config.get("MCP_ENABLED", False),
                    "sse_enabled": app.config.get("SSE_ENABLED", False),
                },
            }
        )

    # 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "요청하신 리소스를 찾을 수 없습니다.",
                    "available_endpoints": ["/api/travel", "/api/a2a", "/api/sse"],
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "서버 내부 오류가 발생했습니다.",
                }
            ),
            500,
        )

    # 개발 서버 실행
    if __name__ == "__main__":
        print("🚀 A2A Travel Recommendation System 시작")
        print(f"📋 환경: {config_name}")
        print(f"🏗️ 아키텍처: Hexagonal + DDD")
        print(f"🔗 프로토콜: A2A + ADK + MCP")

        app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))

    return app


if __name__ == "__main__":
    app = main()

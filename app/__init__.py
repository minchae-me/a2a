"""
A2A (Agent-to-Agent) 시스템 애플리케이션 패키지
헥사고날 아키텍처와 DDD 패턴 적용
"""

from flask import Flask
from .config import config_class
from .routes.travel_routes import travel_bp
from .routes.a2a_routes import a2a_bp
from .routes.sse_routes import sse_bp


def create_app(config_name="development"):
    """
    Flask 애플리케이션 팩토리 패턴
    참고: Flask Official Documentation
    """
    app = Flask(__name__)
    app.config.from_object(config_class[config_name])

    # 블루프린트 등록
    app.register_blueprint(travel_bp, url_prefix="/api/travel")
    app.register_blueprint(a2a_bp, url_prefix="/api/a2a")
    app.register_blueprint(sse_bp, url_prefix="/api/sse")

    # CORS 설정
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    return app

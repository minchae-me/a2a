"""
SSE (Server-Sent Events) API 라우트
실시간 통신을 위한 엔드포인트
"""

from flask import Blueprint, Response, jsonify
from ..models.sse import create_heartbeat_message, create_sse_connection

sse_bp = Blueprint("sse", __name__)


@sse_bp.route("/connect")
def sse_connect():
    """SSE 연결 엔드포인트"""

    def generate():
        # 연결 확인 메시지
        yield 'data: {"type": "connection_established", "message": "SSE 연결이 설정되었습니다."}\n\n'

        # 하트비트 메시지 (실제로는 별도 스레드에서 주기적 전송)
        heartbeat = create_heartbeat_message()
        yield f"data: {heartbeat.json()}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@sse_bp.route("/status")
def sse_status():
    """SSE 서비스 상태"""
    return jsonify(
        {
            "service": "SSE Service",
            "status": "active",
            "features": {
                "real_time_updates": True,
                "heartbeat": True,
                "recommendation_progress": True,
            },
        }
    )

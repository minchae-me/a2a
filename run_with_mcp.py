#!/usr/bin/env python3
"""
MCP + A2A 통합 실행 스크립트
별도 저장소로 분리된 MCP와 A2A를 쉽게 연동해서 실행
"""

import subprocess
import sys
import time
import asyncio
from pathlib import Path
import signal
import os

# 프로젝트 경로들
A2A_ROOT = Path(__file__).parent
MCP_ROOT = A2A_ROOT.parent / "mcp"


def check_mcp_project():
    """MCP 프로젝트가 존재하는지 확인"""
    if not MCP_ROOT.exists():
        print("❌ MCP 프로젝트를 찾을 수 없습니다!")
        print(f"   예상 경로: {MCP_ROOT}")
        print("\n💡 해결 방법:")
        print("   1. MCP 저장소를 클론하세요:")
        print("   2. git clone https://github.com/minchae-me/mcp.git")
        print("   3. 또는 MCP 프로젝트를 올바른 위치로 이동하세요")
        return False

    mcp_server = MCP_ROOT / "standalone_mcp_server.py"
    if not mcp_server.exists():
        print(f"❌ MCP 서버 스크립트를 찾을 수 없습니다: {mcp_server}")
        return False

    print(f"✅ MCP 프로젝트 발견: {MCP_ROOT}")
    return True


def start_mcp_server():
    """MCP 서버를 백그라운드에서 시작"""
    print("🚀 MCP 서버 시작 중...")

    mcp_server_script = MCP_ROOT / "standalone_mcp_server.py"

    # MCP 디렉토리에서 서버 실행
    process = subprocess.Popen(
        [sys.executable, "standalone_mcp_server.py"],
        cwd=str(MCP_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("⏳ MCP 서버 시작 대기 중...")
    time.sleep(5)  # 더 오래 기다리기

    # 서버가 실제로 시작되었는지 확인
    try:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", 8000))
        sock.close()

        if result == 0:
            print("✅ MCP 서버가 성공적으로 시작되었습니다!")
        else:
            print("❌ MCP 서버 시작 실패 - 포트 8000에 연결할 수 없습니다")
    except Exception as e:
        print(f"❌ MCP 서버 상태 확인 실패: {e}")

    return process


def run_a2a_integration():
    """A2A MCP 통합 테스트 실행"""
    print("🎯 A2A MCP 통합 테스트 실행 중...")

    # A2A 디렉토리에서 통합 스크립트 실행
    result = subprocess.run(
        [sys.executable, "mcp_integration.py"],
        cwd=str(A2A_ROOT),
        input="1\n",  # 자동으로 옵션 1 선택
        text=True,
    )

    return result.returncode == 0


def cleanup_processes(processes):
    """프로세스들 정리"""
    print("\n🛑 프로세스 정리 중...")
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    print("✅ 정리 완료")


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("🔗 MCP + A2A 통합 실행 스크립트")
    print("=" * 70)

    # MCP 프로젝트 확인
    if not check_mcp_project():
        return

    processes = []

    try:
        # MCP 서버 시작
        mcp_process = start_mcp_server()
        if mcp_process:
            processes.append(mcp_process)

        # A2A 통합 테스트 실행
        success = run_a2a_integration()

        if success:
            print("\n🎉 MCP + A2A 통합 실행 성공!")
        else:
            print("\n❌ 통합 실행 중 오류 발생")

    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단됨")

    finally:
        cleanup_processes(processes)


if __name__ == "__main__":
    main()

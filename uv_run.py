#!/usr/bin/env python3
"""
UV 기반 A2A 프로젝트 실행기
UV의 장점을 활용한 모던한 Python 프로젝트 관리
"""

import subprocess
import sys
import os
from pathlib import Path


def check_uv_installed():
    """UV가 설치되어 있는지 확인"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV가 설치되어 있습니다: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def install_uv():
    """UV 설치"""
    print("🚀 UV를 설치합니다...")
    if sys.platform.startswith("win"):
        # Windows
        install_cmd = 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
    else:
        # macOS/Linux
        install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"

    print(f"실행 명령어: {install_cmd}")
    print("수동으로 터미널에서 위 명령어를 실행해주세요.")
    return False


def run_with_uv():
    """UV로 프로젝트 실행"""
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("🎯 UV로 A2A 프로젝트를 실행합니다!")
    print()

    # pyproject.toml이 있는지 확인
    if not (project_root / "pyproject.toml").exists():
        print("❌ pyproject.toml 파일이 없습니다!")
        return False

    print("📋 사용 가능한 명령어:")
    print("1. uv sync          - 의존성 동기화")
    print("2. uv run main.py   - 대화형 메뉴 실행")
    print("3. uv run run_demo.py - 원클릭 데모 실행")
    print("4. uv run integration_example.py - 통합 예제 실행")
    print()

    choice = input("실행할 명령을 선택하세요 (1-4): ").strip()

    commands = {
        "1": ["uv", "sync"],
        "2": ["uv", "run", "main.py"],
        "3": ["uv", "run", "run_demo.py"],
        "4": ["uv", "run", "integration_example.py"],
    }

    if choice in commands:
        print(f"🚀 실행 중: {' '.join(commands[choice])}")
        try:
            subprocess.run(commands[choice], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ 실행 실패: {e}")
            return False
    else:
        print("❌ 잘못된 선택입니다.")
        return False

    return True


def main():
    """메인 함수"""
    print("=" * 60)
    print("🚀 UV 기반 A2A 프로젝트 실행기")
    print("=" * 60)
    print()

    # UV 설치 확인
    if not check_uv_installed():
        print("❌ UV가 설치되어 있지 않습니다.")
        install_uv()
        return

    # UV로 실행
    run_with_uv()


if __name__ == "__main__":
    main()

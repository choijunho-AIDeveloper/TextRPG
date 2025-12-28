"""Game Engine for Text RPG"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from model_handler import ModelHandler


class GameEngine:
    def __init__(self, model_handler: ModelHandler, max_history_turns: int = 5):
        """
        Initialize the game engine
        """
        self.model_handler = model_handler
        self.states_file = "states.md"
        self.world_info_file = "world_info.md"
        self.game_active = False

    def initialize_game(self, world_setting: str) -> str:
        """
        Initialize a new game with world settings
        """
        # Create world_info.md
        world_content = f"""# 세계관 정보

        ## 기본 설정
        {world_setting}

        ## 게임 시작 시간
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        ## 게임 상태
        - 진행 중: True
        - 턴 수: 0
        """
        self._save_file(self.world_info_file, world_content)

        # Create initial states.md
        states_content = """# 플레이어 상태

## 기본 정보
- 이름: 미정
- 레벨: 1

## 인벤토리
- 소지금: 없음
- 아이템: 없음

## 현재 위치
- 미정 (게임 시작 위치)

## 퀘스트
- 없음
"""
        self._save_file(self.states_file, states_content)

        self.game_active = True

        # Generate initial game introduction
        system_prompt = self._build_system_prompt()
        user_message = """게임을 시작합니다.

        다음을 수행하세요:
        1. 플레이어에게 이 세계관을 간결하게 소개 (2-3문단)
        2. 플레이어의 초기 상황 (이름, 직업, 시작 위치) 설정
        3. 몰입감 있게 게임 시작 상황 서술
        """

        introduction = self.model_handler.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
        )

        # Process initial state updates
        self._process_state_update(introduction)

        return introduction

    def process_player_action(self, player_input: str) -> Tuple[str, bool]:
        """
        Process player's action and generate response
        """
        if not self.game_active:
            return "게임이 활성화되지 않았습니다. 먼저 세계관을 설정하고 게임을 시작해주세요.", True

        # Build system prompt with current context
        system_prompt = self._build_system_prompt()

        # Create user message with validation request
        user_message = f"""
        플레이어 행동: "{player_input}"
        """

        # Generate response
        response = self.model_handler.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
        )

        # Process state updates (always try to extract and update)
        self._process_state_update(response)

        # Increment turn counter
        self._increment_turn()

        # Check for ending
        game_continues = True
        if "[ENDING:" in response:
            self.game_active = False
            game_continues = False

        return response, game_continues

    def _build_system_prompt(self) -> str:
        """Build system prompt with current game context and recent conversation history"""
        world_info = self._load_file(self.world_info_file)
        player_states = self._load_file(self.states_file)

        system_prompt = f"""
        당신은 텍스트 RPG의 게임 마스터입니다.
        **현재 게임 정보:**

        세계관 정보: {world_info}

        플레이어 상태: {player_states}

        **핵심 원칙:**
        1. **현실성**: 플레이어의 행동이 세계관 정보와 플레이어 상태를 비교했을 때 비현실적이면 거부하세요.
        2. **성공과 실패**: 모든 행동은 세계관 정보와 플레이어 상태를 비교하여 성공과 실패를 결정해주세요.
        3. **공정성**: 현재 능력치, 상태, 장비를 정확히 고려하세요.
        4. **결과의 무게**: 잘못된 선택은 부상, 죽음 등 초래 가능합니다.
        5. **간결성**: 내부 판단 과정을 보여주지 말고, 결과만 간결하게 서술하세요. (2-3문단)

        **출력 시 다음을 꼭 지켜주세요.**

        1. 스토리 서술 (2-4문단, 몰입감 있게)
        2. 매 턴마다 반드시 다음 세계관 정보, 플레이어 상태를 바탕으로 게임 상태를 업데이트하세요(플레이어의 행동에 따라 추가 또는 삭제를 업데이트 해주세요., 게임 상태 업데이트 등의 제목이 아닌 [STATES_UPDATE]를 바로 출력해주세요.):

        [STATES_UPDATE]
        {world_info}
        [/STATES_UPDATE]

        [WORLD_UPDATE]
        {player_states}
        [/WORLD_UPDATE]

        3. 게임 종료 시에만: [ENDING: 타입]

        **중요:**
        - 판단 과정 숨기기
        - 매 턴 반드시 STATES_UPDATE와 WORLD_UPDATE를 markdown 형식으로 출력
        """
        return system_prompt

    def _process_state_update(self, response: str):
        """Extract and apply state updates from response (Markdown format)"""
        try:
            # Extract STATES_UPDATE section
            if "[STATES_UPDATE]" in response and "[/STATES_UPDATE]" in response:
                start = response.find("[STATES_UPDATE]") + len("[STATES_UPDATE]")
                end = response.find("[/STATES_UPDATE]")
                states = response[start:end].strip()

                self._save_file(self.states_file, states)

            # Extract WORLD_UPDATE section
            if "[WORLD_UPDATE]" in response and "[/WORLD_UPDATE]" in response:
                start = response.find("[WORLD_UPDATE]") + len("[WORLD_UPDATE]")
                end = response.find("[/WORLD_UPDATE]")
                world = response[start:end].strip()

                # Update world_info.md
                self._save_file(self.world_info_file, world)
        except Exception as e:
            print(f"State update error: {e}")

    def _increment_turn(self):
        """Increment turn counter in world_info"""
        world_info = self._load_file(self.world_info_file)

        # Simple turn increment
        if "턴 수:" in world_info:
            lines = world_info.split("\n")
            for i, line in enumerate(lines):
                if "턴 수:" in line:
                    try:
                        current_turn = int(line.split(":")[-1].strip())
                        lines[i] = f"- 턴 수: {current_turn + 1}"
                    except:
                        lines[i] = "- 턴 수: 1"
            world_info = "\n".join(lines)
            self._save_file(self.world_info_file, world_info)

    def _save_file(self, filename: str, content: str):
        """Save content to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def _load_file(self, filename: str) -> str:
        """Load content from a file"""
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def get_current_states(self) -> str:
        """Get current player states"""
        return self._load_file(self.states_file)

    def get_world_info(self) -> str:
        """Get current world info"""
        return self._load_file(self.world_info_file)

    def reset_game(self):
        """Reset the game"""
        self.game_active = False
        # Clear in-memory conversation history
        self.conversation_history = []
        # Remove game state files
        if os.path.exists(self.states_file):
            os.remove(self.states_file)
        if os.path.exists(self.world_info_file):
            os.remove(self.world_info_file)

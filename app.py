"""Text RPG with AI - Streamlit Application"""

import streamlit as st
import os
from model_handler import ModelHandler
from game_engine import GameEngine


# Page configuration
st.set_page_config(
    page_title="AI Text RPG",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "model_loaded" not in st.session_state:
        st.session_state.model_loaded = False
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_handler" not in st.session_state:
        st.session_state.model_handler = None
    if "game_engine" not in st.session_state:
        st.session_state.game_engine = None


def load_model():
    """Load the AI model"""
    with st.spinner("AI 모델을 로딩 중입니다..."):
        try:
            model_handler = ModelHandler(model_name="Qwen/Qwen3-4B-Instruct-2507", max_new_tokens=4092)
            model_handler.load_model()
            st.session_state.model_handler = model_handler
            st.session_state.game_engine = GameEngine(model_handler)
            st.session_state.model_loaded = True
            st.success("모델 로딩 완료!")
        except Exception as e:
            st.error(f"모델 로딩 실패: {str(e)}")


def start_game(world_setting: str):
    """Start a new game with the given world setting"""
    if not st.session_state.model_loaded:
        st.error("먼저 AI 모델을 로드해주세요!")
        return

    with st.spinner("게임을 시작하는 중..."):
        try:
            introduction = st.session_state.game_engine.initialize_game(world_setting)
            filtered_introduction = introduction
            if "[STATES_UPDATE]" in introduction:
                start = introduction.find("[STATES_UPDATE]")
                filtered_introduction = introduction[:start]
            st.session_state.game_started = True
            st.session_state.messages = [
                {"role": "assistant", "content": filtered_introduction}
            ]
            st.rerun()
        except Exception as e:
            st.error(f"게임 시작 실패: {str(e)}")


def process_action(player_input: str):
    """Process player action"""
    if not st.session_state.game_started:
        st.error("먼저 게임을 시작해주세요!")
        return

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": player_input})

    with st.spinner("게임 마스터가 생각 중..."):
        try:
            response, game_continues = st.session_state.game_engine.process_player_action(player_input)

            filtered_response = response
            if "[STATES_UPDATE]" in response:
                start = response.find("[STATES_UPDATE]")
                filtered_response = response[:start]

            # Add assistant response to chat
            st.session_state.messages.append({"role": "assistant", "content": filtered_response})

            if not game_continues:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "🎭 **게임이 종료되었습니다!** 사이드바에서 '게임 재시작'을 눌러 새 게임을 시작할 수 있습니다."
                })

        except Exception as e:
            st.error(f"오류 발생: {str(e)}")


def main():
    """Main application"""
    initialize_session_state()

    # Title
    st.title("🎮 AI Text RPG")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ 게임 설정")

        # Model loading section
        st.subheader("1. AI 모델 로드")
        if not st.session_state.model_loaded:
            if st.button("🤖 AI 모델 로드", type="primary", use_container_width=True):
                load_model()
        else:
            st.success("✅ 모델 로드 완료")

        st.markdown("---")

        # Game start section
        st.subheader("2. 게임 시작")
        if st.session_state.model_loaded and not st.session_state.game_started:
            st.markdown("**세계관을 입력하세요:**")
            world_setting = st.text_area(
                "세계관 설정",
                placeholder="이름 등 캐릭터의 정보와 세계관 정보를 작성해주세요!",
                height=150,
                label_visibility="collapsed"
            )

            if st.button("🎲 게임 시작", type="primary", use_container_width=True):
                if world_setting.strip():
                    start_game(world_setting)
                else:
                    st.error("세계관을 입력해주세요!")

        elif st.session_state.game_started:
            st.success("✅ 게임 진행 중")

            if st.button("🔄 게임 재시작", use_container_width=True):
                st.session_state.game_engine.reset_game()
                st.session_state.game_started = False
                st.session_state.messages = []
                st.rerun()

        st.markdown("---")

        # Game info section
        if st.session_state.game_started:
            st.subheader("📊 게임 정보")

            with st.expander("📜 플레이어 상태", expanded=False):
                states = st.session_state.game_engine.get_current_states()
                st.markdown(states)

            with st.expander("🌍 세계관 정보", expanded=False):
                world_info = st.session_state.game_engine.get_world_info()
                st.markdown(world_info)

    # Main content area
    if not st.session_state.model_loaded:
        st.info("👈 왼쪽 사이드바에서 AI 모델을 먼저 로드해주세요.")

    elif not st.session_state.game_started:
        st.info("👈 왼쪽 사이드바에서 세계관을 설정하고 게임을 시작해주세요.")

    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("행동을 입력하세요..."):
            process_action(prompt)
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        AI Text RPG | Made by junhochoi
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

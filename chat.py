import os

import openai
import streamlit as st
from dotenv import load_dotenv

API = {
    "model": "gpt-4o-mini",  # 🔌 OpenAI 모델 (Chat Completions API)
}

SYSTEM_PROMPT = "당신은 친절한 AI 어시스턴트입니다. 한국어로 간결하게 답해 주세요."


def stream_reply(client, messages):
    """OpenAI에 대화를 보내고 답변 조각(글자)을 하나씩 내보낸다."""
    stream = client.chat.completions.create(  # 🔌 API 호출
        model=API["model"],
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        stream=True,
        timeout=30,
    )
    for chunk in stream:
        if chunk.choices:
            yield chunk.choices[0].delta.content or ""  # chunk.choices[0].delta.content = 방금 도착한 글자 조각


def main():
    st.set_page_config(page_title="챗봇", page_icon="🤖")
    st.title("🤖 챗봇")
    st.caption(f"모델: {API['model']} · OpenAI")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("`.env`에 OPENAI_API_KEY가 없어요. `.env.example`을 보고 채워 주세요.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.sidebar.button("🗑️ 대화 지우기"):
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("메시지를 입력하세요")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = openai.OpenAI(api_key=api_key)
    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(stream_reply(client, st.session_state.messages))
        except openai.AuthenticationError:
            st.error("OpenAI 키가 틀렸어요.")
        except openai.RateLimitError:
            st.error("요청이 너무 많거나 사용 한도를 넘었어요. 잠시 뒤에 다시 해 주세요.")
        except openai.APIConnectionError:
            st.error("네트워크 오류로 답변을 받지 못했어요.")
        except openai.APIError:
            st.error("OpenAI에서 답변을 가져오지 못했어요.")
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            return

    # 실패하면 방금 질문을 지워서 다음 질문이 이어서 가능하게 한다
    st.session_state.messages.pop()


main()

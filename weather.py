import json
import os
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st

API_URL = "https://api.openweathermap.org/data/2.5/weather"
CITY = "Seoul"


def load_env(path=".env"):
    """같은 폴더의 .env 파일에서 KEY=VALUE를 읽어 환경 변수에 넣는다."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@st.cache_data(ttl=60)
def fetch_weather(api_key):
    params = urllib.parse.urlencode(
        {"q": CITY, "appid": api_key, "units": "metric", "lang": "kr"}
    )
    with urllib.request.urlopen(f"{API_URL}?{params}", timeout=10) as res:
        return json.load(res)


def main():
    st.set_page_config(page_title="서울 날씨", page_icon="🌤️")
    st.title("🌤️ 서울 현재 날씨")

    load_env()
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        st.error("`.env` 파일에 OPENWEATHER_API_KEY를 설정해 주세요.")
        st.stop()

    if st.button("새로고침"):
        fetch_weather.clear()

    try:
        data = fetch_weather(api_key)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            st.error("API 키가 올바르지 않거나 아직 활성화되지 않았습니다.")
        else:
            st.error(f"날씨 정보를 가져오지 못했습니다. (HTTP {e.code})")
        st.stop()
    except urllib.error.URLError as e:
        st.error(f"네트워크 오류: {e.reason}")
        st.stop()

    main_info = data["main"]
    col1, col2, col3 = st.columns(3)
    col1.metric("기온", f"{main_info['temp']:.1f}°C")
    col2.metric("체감 온도", f"{main_info['feels_like']:.1f}°C")
    col3.metric("습도", f"{main_info['humidity']}%")
    st.subheader(f"날씨: {data['weather'][0]['description']}")


main()

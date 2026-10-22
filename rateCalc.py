import os
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

import requests
import streamlit as st
from dotenv import load_dotenv

API = {
    "rates": "https://v6.exchangerate-api.com/v6/latest/USD",  # 🔌 환율 (USD 기준 전체 통화)
}

KST = timezone(timedelta(hours=9))
DEFAULT_CURRENCY = "JPY"

# 자주 쓰는 통화: 코드 -> (깃발, 한국어 이름)
CURRENCY_INFO = {
    "JPY": ("🇯🇵", "일본 엔"),
    "USD": ("🇺🇸", "미국 달러"),
    "EUR": ("🇪🇺", "유로"),
    "CNY": ("🇨🇳", "중국 위안"),
    "GBP": ("🇬🇧", "영국 파운드"),
    "AUD": ("🇦🇺", "호주 달러"),
    "CAD": ("🇨🇦", "캐나다 달러"),
    "CHF": ("🇨🇭", "스위스 프랑"),
    "HKD": ("🇭🇰", "홍콩 달러"),
    "SGD": ("🇸🇬", "싱가포르 달러"),
    "THB": ("🇹🇭", "태국 바트"),
    "VND": ("🇻🇳", "베트남 동"),
    "TWD": ("🇹🇼", "대만 달러"),
    "PHP": ("🇵🇭", "필리핀 페소"),
}

ERROR_MESSAGES = {
    "invalid-key": "환율 키가 틀렸어요.",
    "inactive-account": "환율 사이트 가입 인증 메일을 확인해 주세요.",
    "quota-reached": "이번 달 무료 사용량(1,500번)을 다 썼어요.",
}

CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 25%, #a1c4fd 60%, #c2e9fb 100%);
}
.rc-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ff512f, #f09819, #56ab2f, #2193b0, #8e2de2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.rc-sub { text-align: center; color: #444; margin-bottom: 1.5rem; }
.rc-card {
    border-radius: 20px;
    padding: 24px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
.rc-card .label { font-size: 1rem; opacity: 0.9; }
.rc-card .value { font-size: 2.2rem; font-weight: 800; margin: 6px 0; }
.rc-card .note { font-size: 0.9rem; opacity: 0.9; }
.rc-pink { background: linear-gradient(135deg, #ff6a88, #ff99ac); }
.rc-blue { background: linear-gradient(135deg, #36d1dc, #5b86e5); }
.rc-green { background: linear-gradient(135deg, #43e97b, #38b36b); }
.rc-foot { text-align: center; color: #333; font-size: 0.85rem; margin-top: 1.5rem; }
</style>
"""


class RateError(Exception):
    """화면에 그대로 보여 줘도 되는 한국어 한 줄 에러."""


@st.cache_data(ttl=3600)
def fetch_rates(api_key):
    try:
        res = requests.get(  # 🔌 API 호출
            API["rates"],
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        data = res.json()
    except requests.exceptions.RequestException:
        raise RateError("네트워크 오류로 환율을 가져오지 못했어요.") from None
    except ValueError:
        raise RateError("환율 응답을 읽지 못했어요.") from None

    if data.get("result") != "success":  # data["result"] = 성공 여부 ("success" / "error")
        error_type = data.get("error-type", "")  # data["error-type"] = 실패 이유
        raise RateError(ERROR_MESSAGES.get(error_type, "환율을 가져오지 못했어요."))
    return data


def currency_label(code):
    flag, name = CURRENCY_INFO.get(code, ("🏳️", code))
    return f"{flag} {code} · {name}"


def card(color, label, value, note=""):
    return (
        f'<div class="rc-card {color}"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="note">{note}</div></div>'
    )


def main():
    st.set_page_config(page_title="환율 계산기", page_icon="💱")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="rc-title">💱 환율 계산기</div>', unsafe_allow_html=True)
    st.markdown('<div class="rc-sub">외화 ↔ 원화, 한 번에 계산해요</div>', unsafe_allow_html=True)

    load_dotenv()
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    if not api_key:
        st.error("`.env`에 EXCHANGERATE_API_KEY가 없어요. `.env.example`을 보고 채워 주세요.")
        st.stop()

    if st.button("🔄 새로 불러오기"):
        st.cache_data.clear()

    try:
        data = fetch_rates(api_key)
    except RateError as e:
        st.error(str(e))
        st.stop()

    rates = data["conversion_rates"]  # data["conversion_rates"] = 1달러가 각 통화로 얼마인지
    krw_per_usd = rates["KRW"]  # rates["KRW"] = 1달러가 몇 원인지

    codes = [c for c in CURRENCY_INFO if c in rates]
    codes += sorted(c for c in rates if c not in CURRENCY_INFO and c != "KRW")
    default_index = codes.index(DEFAULT_CURRENCY) if DEFAULT_CURRENCY in codes else 0

    col_a, col_b = st.columns(2)
    code = col_a.selectbox("통화", codes, index=default_index, format_func=currency_label)
    amount = col_b.number_input("금액", min_value=0.0, value=100.0, step=10.0)

    krw_per_one = krw_per_usd / rates[code]  # 1단위 외화가 몇 원인지 (USD 기준 환율로 교차 계산)
    to_krw = amount * krw_per_one
    from_krw = amount / krw_per_one

    flag, name = CURRENCY_INFO.get(code, ("🏳️", code))
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        card("rc-pink", f"{flag} {amount:,.2f} {code} →", f"₩ {to_krw:,.0f}", "원화로 바꾸면"),
        unsafe_allow_html=True,
    )
    c2.markdown(
        card("rc-blue", f"🇰🇷 {amount:,.2f} KRW →", f"{from_krw:,.2f} {code}", f"{name}로 바꾸면"),
        unsafe_allow_html=True,
    )
    c3.markdown(
        card("rc-green", "📈 현재 환율", f"₩ {krw_per_one:,.2f}", f"1 {code} 기준"),
        unsafe_allow_html=True,
    )

    updated = parsedate_to_datetime(data["time_last_update_utc"]).astimezone(KST)  # data["time_last_update_utc"] = 환율 기준 시각
    st.markdown(
        f'<div class="rc-foot">환율: ExchangeRate-API · 기준 시각 {updated:%Y-%m-%d %H:%M} (한국 시간)<br>'
        "무료 플랜은 하루 한 번 갱신돼요.</div>",
        unsafe_allow_html=True,
    )


main()

import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="Research Assistant Agent",
    page_icon="🔍",
    layout="centered"
)

st.title("Research Assistant Agent")
st.caption("Nhap cau hoi bat ky - agent se tu tim kiem web va tong hop bao cao")

st.markdown("---")

question = st.text_input(
    label="cau hoi",
    placeholder="Vi du: Vector database la gi?",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_btn = st.button("Nghien cuu", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("Xoa", use_container_width=True)

if clear_btn:
    st.rerun()

if run_btn and question:
    st.markdown("---")
    with st.spinner("Agent dang lam viec... vui long cho 20-30 giay"):
        report = run_agent(question)
    st.success("Hoan thanh!")
    st.markdown("---")
    st.subheader("Bao cao")
    st.markdown(report)
    st.markdown("---")
    st.download_button(
        label="Tai bao cao",
        data=report,
        file_name="report.txt",
        mime="text/plain"
    )
elif run_btn and not question:
    st.warning("Vui long nhap cau hoi!")

st.markdown("---")
st.caption("Built with Groq - Tavily - Streamlit")
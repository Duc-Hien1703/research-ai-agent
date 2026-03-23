import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="Research Assistant Agent",
    page_icon="🔍",
    layout="centered"
)

st.title("Research Assistant Agent")
st.caption(" Hỏi tự do - Trả lời mình lo !!")

st.markdown("---")

question = st.text_input(
    label=" Điều cậu muốn biết ",
    placeholder="Vi du: Manchester United là vô đối phải không? ",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_btn = st.button("Let's go bro", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("Tẩy não !", use_container_width=True)

if clear_btn:
    st.rerun()

if run_btn and question:
    st.markdown("---")
    with st.spinner("Đợi một tí vì tớ miễn phí ...."):
        report = run_agent(question)
    st.success("Tìm ra rồi nha!")
    st.markdown("---")
    st.subheader("Final Answer ")
    st.markdown(report)
    st.markdown("---")
    st.download_button(
        label="Save answer",
        data=report,
        file_name="report.txt",
        mime="text/plain"
    )
elif run_btn and not question:
    st.warning("Hỏi đi ngại chi !")

st.markdown("---")
st.caption("Không đúng - không trách - không tốn tiền !!!")

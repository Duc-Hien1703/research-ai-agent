import streamlit as st
from agent import run_agent
from memory import get_all_memories, clear_memory

st.set_page_config(
    page_title="Research Assistant Agent",
    page_icon="🔍",
    layout="wide"   # đổi thành wide để có chỗ cho sidebar
)

# Sidebar hiển thị long-term memory
with st.sidebar:
    st.subheader("Long-term Memory")
    st.caption("Những gì tôi nhớ về bạn")

    if st.button("Tẩy não toàn phần !!!", use_container_width=True):
        clear_memory()
        st.success("Tẩy thành công!")
        st.rerun()

    memories = get_all_memories()
    if memories:
        st.caption(f"Dang co {len(memories)} ky uc")
        for mem in memories[:10]:  # hiện 10 memory gần nhất
            with st.expander(mem["question"][:50] + "..."):
                st.write(mem["answer"][:200] + "...")
                st.caption(mem["timestamp"][:10])
    else:
        st.caption("Chưa có tí kí ức nào , hỏi gì cho tui đi!")

# Main UI giữ nguyên như cũ
st.title("Research Assistant Agent")
st.caption("Hỏi tự do - Tớ tự lo !!")

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.messages:
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Tẩy não!", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        asked = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.caption(f"Hỏi {asked} câu trong lần này rồi nha !")

st.markdown("---")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**{msg['content']}**")
    else:
        with st.chat_message("assistant"):
            st.success("Tim ra roi nha!")
            st.markdown("---")
            st.subheader("Final Answer")
            st.markdown(msg["content"])
            st.markdown("---")
            st.download_button(
                label="Save answer",
                data=msg["content"],
                file_name="report.txt",
                mime="text/plain",
                key=f"dl_{st.session_state.messages.index(msg)}"
            )

question = st.chat_input("Manchester United là vô đối nhể? / Hỏi gì ghi dô đây nha !")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(f"**{question}**")

    with st.chat_message("assistant"):
        with st.spinner("Đợi một tí vì tớ miễn phí...."):
            report = run_agent(question, chat_history=st.session_state.messages)
        st.success("Trùi ui thấy rùi!")
        st.markdown("---")
        st.subheader("Final Answer")
        st.markdown(report)
        st.markdown("---")
        st.download_button(
            label="Save answer",
            data=report,
            file_name="report.txt",
            mime="text/plain",
            key=f"dl_new_{len(st.session_state.messages)}"
        )

    st.session_state.messages.append({"role": "assistant", "content": report})
    st.rerun()

st.markdown("---")
st.caption("Không đúng - không trách - không tốn tiền!!!")
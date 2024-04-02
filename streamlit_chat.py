import streamlit as st
from streamlit_chat import message
from chatglm3 import ChatGLM3

st.title("Chat Demo")

chat_glm = ChatGLM3()

# 使用streamlit的session_state来存储聊天历史
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 在侧边栏添加一个按钮，用于清除聊天历史
if st.sidebar.button("Clear chat history"):
    st.session_state.chat_history = []

# 遍历聊天历史并显示消息
for chat in st.session_state.chat_history:
    message(chat["content"], is_user=(chat["role"] == "user"))

# 用户输入并提交消息
user_input = st.text_input("Enter your message")

if st.button("Submit"):
    # 使用ChatGLM模型生成回复
    reply = chat_glm.chat(user_input)

    # 更新聊天历史
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # 重新运行应用以更新聊天界面
    st.experimental_rerun()

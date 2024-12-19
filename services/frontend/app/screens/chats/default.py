import streamlit as st
from screens.chats.state import get_chat_client, get_chat_response

def chat_sidebar():
    with st.sidebar:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.button("", icon=":material/add:", use_container_width=True)
        with col2:
            with st.popover("", icon=":material/settings:", use_container_width=True):
                st.page_link("screens/sources/catalog.py", label="Sources")

        for chat in range(20):
            st.link_button(f"chat-{chat}", f"/chat/{chat}", use_container_width=True)

def chat_header():
    title_col, save_col, trash_col, fave_col, share_col, fork_col, more_col = st.columns([4,1,1,1,1,1,1], vertical_alignment="bottom")

    with title_col:
        st.header("Chat")
    with save_col:
        st.button("", "save-chat", icon=":material/save:", use_container_width=True)
    with trash_col:
        st.button("", "trash-chat", icon=":material/delete:", use_container_width=True)
    with fave_col:
        st.button("", "fave-chat", icon=":material/star:", use_container_width=True)
    with share_col:
        st.button("", "share-chat", icon=":material/share:", use_container_width=True)
    with fork_col:
        st.button("", "fork-chat", icon=":material/alt_route:", use_container_width=True)
    with more_col:
        st.button("", "more-chat", icon=":material/more_vert:", use_container_width=True)

def chat_message(message):
    with st.chat_message(message['role']):
        st.markdown(message['content'])

def chat_history():
    for message in st.session_state.messages:
        chat_message(message)

def chat_entry():
    user_content = st.chat_input("Chat")
    if user_content:
        user_message = {"role": "user", "content": user_content}
        st.session_state.messages.append(user_message)
        chat_message(user_message)

        ai_message = get_chat_response(client, st.session_state.messages)
        st.session_state.messages.append(ai_message)
        chat_message(ai_message)


client = get_chat_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

chat_sidebar()

chat_header()

chat_history()

chat_entry()


    

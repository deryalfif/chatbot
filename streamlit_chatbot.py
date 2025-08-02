import streamlit as st
import openai
from datetime import datetime
import os
import json

# Load environment variables

# Page configuration
st.set_page_config(
    page_title="Intelligo Chatbot Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ChatAgent:
    def __init__(self, api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = """Kamu adalah AI Assistant chatbot Data Science & AI di Intelligo ID. Kamu membantu siswa dengan pertanyaan teknis dan administrasi terkait bootcamp. Gunakan bahasa Indonesia yang friendly dan profesional."""
    
    def get_response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_message_history(self, conversations):
        messages = [{"role": "system", "content": self.system_prompt}]
        for conv in conversations:
            messages.append({"role": "user", "content": conv["user"]})
            messages.append({"role": "assistant", "content": conv["assistant"]})
        return messages

def initialize_session_state():
    """Initialize session state variables"""
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False

def sidebar_config():
    """Configure sidebar with settings"""
    st.sidebar.title("⚙️ Configuration")

    # Agent personality
    personality = st.sidebar.selectbox(
        "Assistant Personality",
        ["Mintell Bot", "Student Mentor"],
        help="Choose the assistant's personality"
    )
    
    if personality:
        if st.sidebar.button("Initialize Agent"):
            try:
                st.session_state.agent = ChatAgent()
                st.session_state.api_key_set = True
                
                # Set personality-based system prompt
                personality_prompts = {
                    "Mintell Bot": "Kamu adalah AI Assistant chatbot Data Science & AI di Intelligo ID. Tugas kamu hanya menjawab seputar administari bootcamp di Intelligo ID, apabila user menanyakan seputar materi arahkan menggunakan model Student Mentor, Dan jangan menjawab selain yang berkaitan dengan Intelligo ID. Gunakan bahasa Indonesia yang friendly dan profesional.",
                    "Student Mentor": "Kamu adalah AI Assistant chatbot Data Science & AI di Intelligo ID. Kamu membantu siswa untuk mentoring hanya seputar Data Science dan AI, apabila user menanyakan administari bootcamp arahkan menggunakan model Mintell Bot, dan jangan menjawab selain Data Science dan AI. Gunakan bahasa Indonesia yang friendly dan profesional.",
                    "Creative Writer": "You are a creative writing AI assistant. You help with storytelling, creative writing, and imaginative content creation.",
                    "Data Analyst": "You are a data analyst AI assistant. You help with data analysis, visualization insights, and statistical interpretations."
                }
                st.session_state.agent.system_prompt = personality_prompts[personality]
                st.sidebar.success("Agent initialized successfully!")
            except Exception as e:
                st.sidebar.error(f"Error initializing agent: {str(e)}")
    
    # Chat controls
    st.sidebar.markdown("---")
    st.sidebar.title("💬 Chat Controls")
    
    if st.sidebar.button("Clear Chat History"):
        st.session_state.conversations = []
        st.rerun()
    
    if st.sidebar.button("Export Chat"):
        if st.session_state.conversations:
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "conversations": st.session_state.conversations
            }
            st.sidebar.download_button(
                "Download Chat History",
                data=json.dumps(chat_data, indent=2),
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def main_chat_interface():
    """Main chat interface"""
    st.title("🤖 Intelligo Chatbot Assistant")
    st.markdown("Welcome to your AI chatbot assistant! Start a conversation below.")
    
    # Check if agent is initialized
    if not st.session_state.api_key_set or st.session_state.agent is None:
        st.warning("Please configure your OpenAI API key in the sidebar to start chatting.")
        return
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, conv in enumerate(st.session_state.conversations):
            # User message
            with st.chat_message("user"):
                st.write(conv["user"])
                st.caption(f"🕒 {conv['timestamp']}")
            
            # Assistant message
            with st.chat_message("assistant"):
                st.write(conv["assistant"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)
            st.caption(f"🕒 {timestamp}")
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare message history
                message_history = st.session_state.agent.create_message_history(
                    st.session_state.conversations
                )
                message_history.append({"role": "user", "content": user_input})
                
                # Get response
                response = st.session_state.agent.get_response(message_history)
                
                # Display response
                st.write(response)
        
        # Add to conversation history
        st.session_state.conversations.append({
            "user": user_input,
            "assistant": response,
            "timestamp": timestamp
        })
        
        # Rerun to update the interface
        st.rerun()

def main():
    """Main application function"""
    initialize_session_state()
    sidebar_config()
    main_chat_interface()

if __name__ == "__main__":
    main()
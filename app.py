import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Study Buddy", page_icon="📚", layout="wide")

st.markdown("""
    <style>
        .stButton > button { width: 100%; background-color: #4285F4; color: white; font-size: 16px; padding: 10px; border: none; border-radius: 8px; }
        .stButton > button:hover { background-color: #3367d6; }
        .output-box { background-color: black; padding: 20px; border-radius: 10px; border-left: 5px solid #4285F4; font-size: 15px; line-height: 1.7; }
    </style>
""", unsafe_allow_html=True)

st.title("📚 AI Study Buddy")


# ---------------- API KEY SETUP ----------------
DEFAULT_API_KEY = st.secrets["API_KEY"]

def test_api_key(api_key):
    try:
        client = OpenAI(
           api_key=api_key,
           base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

        client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception:
        return False

# Try default key first
working_key = None

if DEFAULT_API_KEY and test_api_key(DEFAULT_API_KEY):
    working_key = DEFAULT_API_KEY
    st.sidebar.success("✅ Using default OpenAI API key")
else:
    st.sidebar.warning("Default API key unavailable")

    user_key = st.sidebar.text_input(
        "Enter OpenAI API Key",
        type="password",
        placeholder="Paste your OpenAI API key here"
    )

    if not user_key:
        st.info("👈 Default key failed. Please enter your OpenAI API key.")
        st.stop()

    if test_api_key(user_key):
        working_key = user_key
        st.sidebar.success("✅ API key accepted")
    else:
        st.error("❌ Invalid OpenAI API key")
        st.stop()



# ---------------- GEMINI VIA OPENAI CLIENT ----------------
client = OpenAI(
    api_key=working_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ---------------- ASK AI ----------------
def ask_ai(prompt, system="You are a helpful AI study tutor. Answer clearly in 2-3 line."):
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- PDF EXTRACT ----------------
def extract_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text[:4000].rsplit('. ', 1)[0] + '.'

# ---------------- SIDEBAR MENU ----------------
st.sidebar.markdown("---")
st.sidebar.title("📖 Features")
menu = st.sidebar.radio(
    "Choose a feature",
    ["🔍 Explain Topic", "📝 Summarize Notes", "❓ Generate Quiz", "🃏 Flashcards", "📄 PDF Assistant", "💬 Chat with AI"]
)

st.sidebar.markdown("---")

# ---------------- EXPLAIN TOPIC ----------------
if menu == "🔍 Explain Topic":
    st.subheader("🔍 Explain a Topic")
    topic = st.text_input("Enter a topic", placeholder="e.g. Artificial Intelligence, Photosynthesis, Newton's Laws")

    if st.button("Explain"):
        if topic.strip():
            with st.spinner("Generating explanation..."):
                prompt = (
                    f"Explain '{topic}' in detail for a student. Include:\n"
                    f"1. What it is (definition)\n"
                    f"2. How it works\n"
                    f"3. A simple real-world example\n"
                    f"4. Why it is important\n"
                    f"Use simple, clear language."
                )
                result = ask_ai(prompt)
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a topic.")

# ---------------- SUMMARIZE NOTES ----------------
elif menu == "📝 Summarize Notes":
    st.subheader("📝 Summarize Your Notes")
    notes = st.text_area("Paste your notes here", height=200, placeholder="Paste lecture notes, paragraphs, or any text...")
    style = st.radio("Summary style", ["Bullet points", "Short paragraph", "Key points only"])

    if st.button("Summarize"):
        if notes.strip():
            with st.spinner("Summarizing..."):
                prompt = f"Summarize the following notes as {style.lower()} for a student. Be clear and concise:\n\n{notes}"
                result = ask_ai(prompt)
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please paste some notes.")

# ---------------- GENERATE QUIZ ----------------
elif menu == "❓ Generate Quiz":
    st.subheader("❓ Generate Quiz Questions")
    topic = st.text_input("Enter a topic", placeholder="e.g. World War 2, Python Programming")
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of questions", 3, 10, 5)
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz"):
        if topic.strip():
            with st.spinner("Generating quiz..."):
                prompt = (
                    f"Create {num_questions} {difficulty.lower()} quiz questions with answers about '{topic}'. "
                    f"Format each as:\nQ1: [question]\nA1: [answer]\n\nNumber all questions clearly."
                )
                result = ask_ai(prompt)
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a topic.")

# ---------------- FLASHCARDS ----------------
elif menu == "🃏 Flashcards":
    st.subheader("🃏 Create Flashcards")
    topic = st.text_input("Enter a topic", placeholder="e.g. The Solar System, Algebra, French Revolution")
    num_cards = st.slider("Number of flashcards", 3, 10, 5)

    if st.button("Create Flashcards"):
        if topic.strip():
            with st.spinner("Creating flashcards..."):
                prompt = (
                    f"Create {num_cards} study flashcards about '{topic}'. "
                    f"Format strictly as:\nQ: [question]\nA: [answer]\n"
                    f"Separate each card with a blank line."
                )
                result = ask_ai(prompt)

            cards = result.strip().split("Q:")
            cards = [c for c in cards if c.strip()]

            if cards:
                st.success(f"Created {len(cards)} flashcards!")
                for i, card in enumerate(cards, 1):
                    parts = card.split("A:")
                    question = parts[0].strip() if parts else ""
                    answer = parts[1].strip() if len(parts) > 1 else ""
                    with st.expander(f"Card {i}: {question[:70]}"):
                        st.write(f"**Question:** {question}")
                        st.success(f"**Answer:** {answer}")
            else:
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a topic.")

# ---------------- PDF ASSISTANT ----------------
elif menu == "📄 PDF Assistant":
    st.subheader("📄 PDF Assistant")
    file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if file:
        with st.spinner("Reading PDF..."):
            text = extract_pdf(file)
        st.success(f"PDF loaded! ({len(text)} characters extracted)")
        st.text_area("Preview", text[:500] + "...", height=100, disabled=True)

        option = st.radio("What do you want to do?", [
            "Summarize", "Explain Simply", "Generate Quiz", "Key Takeaways"
        ])

        if st.button("Run"):
            with st.spinner("Processing PDF..."):
                prompts = {
                    "Summarize": f"Summarize this text clearly for a student:\n\n{text}",
                    "Explain Simply": f"Explain this text in very simple terms for a beginner:\n\n{text}",
                    "Generate Quiz": f"Generate 5 quiz questions with answers from this text:\n\n{text}",
                    "Key Takeaways": f"List the 5 most important key takeaways from this text:\n\n{text}"
                }
                result = ask_ai(prompts[option])
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)

# ---------------- CHAT WITH AI ----------------
elif menu == "💬 Chat with AI":
    st.subheader("💬 Chat with AI Tutor")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask me anything about your studies...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                messages = [{"role": "system", "content": "You are a helpful AI study tutor. Answer clearly for a student."}]
                messages += st.session_state.chat_history[-6:]
                try:
                    response = client.chat.completions.create(
                        model="gemini-2.5-flash",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    result = response.choices[0].message.content
                except Exception as e:
                    result = f"Error: {str(e)}"
                st.write(result)
                st.session_state.chat_history.append({"role": "assistant", "content": result})

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


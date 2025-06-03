import streamlit as st
import pandas as pd
import datetime
from openai import OpenAI


# === Config ===
st.set_page_config(page_title="MindMirror – Start Your Day", layout="centered")
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI key
DATA_FILE = "journal_entries.csv"

# === Session state init ===
if "started" not in st.session_state:
    st.session_state.started = False

if "show_affirmation" not in st.session_state:
    st.session_state.show_affirmation = False

if "show_mood" not in st.session_state:
    st.session_state.show_mood = False

if "show_gratitude" not in st.session_state:
    st.session_state.show_gratitude = False

if "show_reflection" not in st.session_state:
    st.session_state.show_reflection = False

# === Load or create journal log ===
def load_entries():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["date", "affirmation", "gratitude", "mood", "good_thing", "ai_response"])

entries = load_entries()
today = datetime.date.today().isoformat()

# === Welcome screen ===
if not st.session_state.started:
    st.title("🪞 MindMirror")
    st.markdown("Welcome to your daily self-check-in. Take 5 minutes for clarity, gratitude, and peace.")
    if st.button("🌅 Start Your Day"):
        st.session_state.started = True
    st.stop()

# === Daily flow begins ===
st.title(f"🧘‍♀️ MindMirror – {today}")

# --- Affirmation ---
if st.button("🪷 Write your daily affirmation"):
    st.session_state.show_affirmation = True

if st.session_state.show_affirmation:
    affirmation = st.text_input("What's your intention or mantra today?")
else:
    affirmation = ""

# --- Mood ---
if st.button("😊 Track your mood"):
    st.session_state.show_mood = True

if st.session_state.show_mood:
    mood = st.slider("How do you feel today (0 = rough, 10 = amazing)?", 0, 10, 5)
else:
    mood = ""

# --- Gratitude + Good Thing ---
if st.button("🙏 Write your gratitude"):
    st.session_state.show_gratitude = True

if st.session_state.show_gratitude:
    gratitude = st.text_area("List 3 things you're grateful for:")
    good_thing = st.text_area("What’s 1 good thing that happened today?")
else:
    gratitude = ""
    good_thing = ""

# --- AI Reflection ---
if st.button("🧠 Reflect with AI"):
    st.session_state.show_reflection = True

if st.session_state.show_reflection:
    with st.spinner("Reflecting..."):
        user_input = f"""
        Affirmation: {affirmation}
        Gratitude: {gratitude}
        Mood: {mood}/10
        Good thing: {good_thing}
        """

        prompt = f"You are a mindful, gentle AI self-coach. A user just wrote this reflection:\n{user_input}\nRespond with warmth and encouragement, and highlight any emotional patterns or insights."

        try:
            client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
ai_reply = response.choices[0].message.content

        except Exception as e:
            ai_reply = f"Error: {e}"

        st.markdown("### ✨ AI Reflection")
        st.write(ai_reply)

        # Save
        new_entry = pd.DataFrame([{
            "date": today,
            "affirmation": affirmation,
            "gratitude": gratitude,
            "mood": mood,
            "good_thing": good_thing,
            "ai_response": ai_reply
        }])
        updated = pd.concat([entries, new_entry], ignore_index=True)
        updated.to_csv(DATA_FILE, index=False)
        st.success("✅ Journal entry saved.")

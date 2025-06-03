import streamlit as st
import pandas as pd
import datetime
from openai import OpenAI

# === Config ===
st.set_page_config(page_title="MindMirror – Start Your Day", layout="centered")
client = OpenAI()
DATA_FILE = "journal_entries.csv"

# === Session state ===
if "started" not in st.session_state:
    st.session_state.started = False

for key in ["show_affirmation", "show_mood", "show_gratitude", "show_reflection"]:
    if key not in st.session_state:
        st.session_state[key] = False

# === Load or create journal log ===
def load_entries():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["date", "affirmation", "gratitude", "mood", "good_thing", "ai_response"])

entries = load_entries()
today = datetime.date.today().isoformat()

# === Start screen ===
if not st.session_state.started:
    st.title("🌞 MindMirror")
    st.markdown("Welcome to your daily self-check-in. Take 5 minutes for clarity, gratitude, and peace.")
    if st.button("📅 Start Your Day"):
        st.session_state.started = True
    st.stop()

# === Main UI ===
st.title(f"🧘‍♀️ MindMirror – {today}")

# --- Affirmation ---
if st.button("🌸 Write your daily affirmation"):
    st.session_state.show_affirmation = True

affirmation = st.text_input("What's your intention or mantra today?") if st.session_state.show_affirmation else ""

# --- Mood ---
if st.button("😊 Track your mood"):
    st.session_state.show_mood = True

mood = st.slider("How do you feel today (0 = rough, 10 = amazing)?", 0, 10, 5) if st.session_state.show_mood else None

# --- Gratitude ---
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

        prompt = f"You are a mindful and kind self-coach. A user just wrote their daily journal. Reflect with insight, encouragement, and gentle advice:\n{user_input}"

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_reply = response.choices[0].message.content
        except Exception as e:
            ai_reply = f"Error: {e}"

        st.markdown("### ✨ AI Reflection")
        st.write(ai_reply)

        # Save to file
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

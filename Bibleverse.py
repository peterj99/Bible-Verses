import google.generativeai as genai
import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure the generative AI model
genai.configure(api_key=api_key)

# Base prompt
base_prompt = """
You are an expert in creating comprehensive Christian spiritual content. 
Your task is to generate a JSON with these keys:
- daily_verse: A clear, readable Bible verse (not in JSON format). It should also contain the book and verse number
- daily_devotional: A short devotional based on the earlier verse generated(less than 60 words)
- prayer_guide: A prayer based on above generated content(less than 60 words)
- religious_insight: A meaningful insight about Christian tradition or history like saints feast days, liturgical seasons, christian festivals, historical events in christian history, biblical facts, christian symbols with meanings, christian traditions etc.

Ensure the content is:
- Theologically sound
- Personally meaningful
- Culturally sensitive
- Aligned with specific Christian traditions

Avoid:
- Generic content
- Controversial topics
- Repetitive structures

Output MUST be a valid JSON object.
"""

# Initialize the generative model
spiritual_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=base_prompt
)


# Function to generate spiritual content
def get_spiritual_content(denomination=None, bible_version=None, themes=None):
    # Get current date and day
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")

    # Construct prompt
    prompt = f"""
    Generate comprehensive spiritual content for a general Christian audience for {current_day}, {current_date}.
    """
    if denomination or bible_version or themes:
        prompt = f"""
        Generate comprehensive spiritual content for a {denomination or 'general'} Christian 
        using {bible_version or 'a standard Bible version'}, focusing on themes: {', '.join(themes or ['general spirituality'])}.
        Ensure it is aligned with {current_day}, {current_date}.
        """

    response = spiritual_model.generate_content(prompt)

    # Parse JSON response
    try:
        text = response.parts[0].text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        return json.loads(text)
    except Exception:
        return {
            "daily_verse": "Proverbs 3:5-6 - Trust in the Lord with all your heart and lean not on your own understanding.",
            "daily_devotional": "In times of uncertainty, remember that faith is your anchor. Reflect on God's unwavering love and guidance.",
            "prayer_guide": "Heavenly Father, guide my steps and fill my heart with your peace today.",
            "religious_insight": f"Today is {current_day}, {current_date}. We are reminded of the significance of steadfast faith in navigating life's challenges."
        }


# Load or initialize preferences
def load_preferences():
    return st.session_state.get("preferences", {"denomination": None, "bible_version": None, "themes": None})


def save_preferences(preferences):
    st.session_state["preferences"] = preferences


# Streamlit App
def main():
    st.title("Daily Grace")
    st.write("Discover inspiration, comfort, and guidance every day with Daily Grace. Begin each day with grace and grow in your walk with God.")

    # Load preferences
    preferences = load_preferences()

    # Generate initial content based on preferences or general content
    content = get_spiritual_content(
        denomination=preferences.get("denomination"),
        bible_version=preferences.get("bible_version"),
        themes=preferences.get("themes")
    )

    # Display Content Sections
    st.subheader("📖 Daily Bible Verse")
    st.write(content.get("daily_verse", "No verse available today."))

    st.subheader("💭 Daily Devotional")
    st.write(content.get("daily_devotional", "Today's devotional could not be generated."))

    st.subheader("🙏 Prayer Guide")
    st.write(content.get("prayer_guide", "A simple prayer for guidance."))

    st.subheader("🕊️ Religious Insight")
    st.write(content.get("religious_insight", "Each day is a gift from God."))

    # Hyperlink to open preferences in the sidebar
    st.markdown(
        '<a href="#preferences" style="text-decoration:none;color:blue;">Customize Your Spiritual Journey(Open Sidebar) →</a>',
        unsafe_allow_html=True
    )

    # Sidebar for Preferences
    with st.sidebar:
        st.header("Preferences")
        st.markdown('<div id="preferences"></div>', unsafe_allow_html=True)  # Anchor for scrolling

        denomination = st.selectbox(
            "Select Your Denomination",
            [
                "Catholic", "Baptist", "Methodist", "Lutheran",
                "Presbyterian", "Pentecostal", "Non-denominational",
                "Orthodox", "Anglican", "Other"
            ],
            index=0 if not preferences.get("denomination") else ["Catholic", "Baptist", "Methodist", "Lutheran",
                                                                 "Presbyterian", "Pentecostal", "Non-denominational",
                                                                 "Orthodox", "Anglican", "Other"].index(
                preferences["denomination"])
        )
        if denomination == "Other":
            denomination = st.text_input("Please specify your denomination",
                                         value=preferences.get("denomination") or "")

        bible_version = st.selectbox(
            "Preferred Bible Version",
            [
                "New International Version (NIV)",
                "King James Version (KJV)",
                "English Standard Version (ESV)",
                "New Living Translation (NLT)",
                "New American Standard Bible (NASB)",
                "The Message (MSG)",
                "Other"
            ],
            index=0 if not preferences.get("bible_version") else ["New International Version (NIV)",
                                                                  "King James Version (KJV)",
                                                                  "English Standard Version (ESV)",
                                                                  "New Living Translation (NLT)",
                                                                  "New American Standard Bible (NASB)",
                                                                  "The Message (MSG)", "Other"].index(
                preferences["bible_version"])
        )
        if bible_version == "Other":
            bible_version = st.text_input("Please specify your preferred Bible version",
                                          value=preferences.get("bible_version") or "")

        themes = st.multiselect(
            "Select Your Spiritual Themes",
            [
                "Strength", "Gratitude", "Forgiveness", "Love", "Hope",
                "Peace", "Courage", "Wisdom", "Joy", "Patience",
                "Humility", "Compassion", "Faith", "Mindfulness",
                "Purpose", "Healing", "Unity", "Growth",
                "Generosity", "Resilience"
            ],
            default=preferences.get("themes") or []
        )

        if st.button("Save Preferences"):
            preferences = {"denomination": denomination, "bible_version": bible_version, "themes": themes}
            save_preferences(preferences)
            st.success("Preferences saved! Refresh the app to see personalized content.")


# Run the app
if __name__ == "__main__":
    main()

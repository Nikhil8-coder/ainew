import streamlit as st
import pandas as pd
import json
import os
import random
import hashlib
import secrets
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================
APP_NAME = "Career Choice"
CURRENT_YEAR = 2026
USER_DB_FILE = "users_database.json"

# Set this as an environment variable before deploying — never hardcode it in
# real use. This fallback exists only so the app runs out of the box locally.
ADMIN_PASSWORD = os.environ.get("CAREER_CHOICE_ADMIN_PASSWORD", "change-me-now")

STREAMS = [
    "B.Tech / B.E. — Computer Science / IT",
    "B.Tech / B.E. — Electronics / Electrical",
    "B.Tech / B.E. — Mechanical Engineering",
    "B.Tech / B.E. — Civil Engineering",
    "B.Tech / B.E. — Chemical / Other Core Branch",
    "B.Sc. — Science Degree",
    "B.Com — Commerce Degree",
    "B.A. — Arts / Humanities Degree",
    "BBA / Management Degree",
    "Diploma / Polytechnic",
    "Civil Services Aspirant (UPSC / State PSC)",
    "Class 11–12 (School, stream not yet decided)",
    "Other",
]

# Maps the detailed stream a student picks at signup to the broader category
# the recommendation logic and knowledge base reason about.
STREAM_CATEGORY = {
    "B.Tech / B.E. — Computer Science / IT": "Engineering / CS",
    "B.Tech / B.E. — Electronics / Electrical": "Engineering / CS",
    "B.Tech / B.E. — Mechanical Engineering": "Engineering / CS",
    "B.Tech / B.E. — Civil Engineering": "Civil Engineering",
    "B.Tech / B.E. — Chemical / Other Core Branch": "Engineering / CS",
    "B.Sc. — Science Degree": "Science (PCM)",
    "B.Com — Commerce Degree": "Commerce",
    "B.A. — Arts / Humanities Degree": "Arts / Humanities",
    "BBA / Management Degree": "Commerce",
    "Diploma / Polytechnic": "Diploma / Polytechnic",
    "Civil Services Aspirant (UPSC / State PSC)": "Civil Services",
    "Class 11–12 (School, stream not yet decided)": "Other",
    "Other": "Other",
}

# ==============================================================================
# KNOWLEDGE BASE — production rules mapping trait combinations to careers.
# Each entry also lists which streams it's most relevant to, so the guidance
# flow can prioritise paths that fit the user's declared stream.
# ==============================================================================
KNOWLEDGE_BASE = {
    "software_engineering": {
        "title": "Software Engineering & Systems Development",
        "logic_expression": "Coding AND Analytical_Thinking AND NOT Visual_Art_Focus",
        "relevant_streams": ["Engineering / CS", "Science (PCM)", "Diploma / Polytechnic"],
        "prereqs": ["A programming language (Python/Java/C++)", "Data structures & algorithms", "Git & version control"],
        "if_taken": "Strong, transferable technical foundation; wide range of roles across almost every industry.",
        "if_avoided": "You'd rely on others to build technical systems for you, but keep more time for other strengths.",
        "if_alt_chosen": "If you lean toward a related-but-lighter path (e.g. QA, technical support), you can still pick up coding basics later without starting over.",
        "trend_now": "Heavy demand for cloud-native and AI-integrated backend systems.",
        "trend_10y": "Routine code generation is increasingly AI-assisted; human engineers focus more on system design, review, and safety/verification work."
    },
    "data_science_ai": {
        "title": "Data Science & Artificial Intelligence",
        "logic_expression": "Coding AND Advanced_Math AND High_Analytics_Interest",
        "relevant_streams": ["Engineering / CS", "Science (PCM)"],
        "prereqs": ["Statistics & linear algebra", "Python (pandas, NumPy, scikit-learn)", "Core ML concepts"],
        "if_taken": "Access to high-growth, high-paying roles in analytics, ML, and applied AI.",
        "if_avoided": "You skip a steep math learning curve, but close off roles that need it.",
        "if_alt_chosen": "If pure math feels heavy, data analytics (less theory-heavy) is a solid nearby alternative.",
        "trend_now": "Widespread use of fine-tuning and retrieval-augmented generation in production systems.",
        "trend_10y": "More autonomous, specialised AI agents; demand shifts toward people who can evaluate, govern, and apply these systems responsibly."
    },
    "ui_ux_design": {
        "title": "UI/UX & Product Design",
        "logic_expression": "Visual_Art_Focus AND Empathy_For_Users AND NOT Advanced_Math",
        "relevant_streams": ["Arts / Humanities", "Commerce", "Undergraduate (other)"],
        "prereqs": ["Design tools (Figma)", "Basic user research methods", "Prototyping"],
        "if_taken": "High creative control and direct influence on how products feel to use.",
        "if_avoided": "You stay out of visual/product decisions but may miss creative satisfaction in your day-to-day work.",
        "if_alt_chosen": "If you want more structure than pure design, product management blends design sense with strategy.",
        "trend_now": "Responsive, cross-device design systems and increasing use of AI-assisted prototyping.",
        "trend_10y": "More adaptive interfaces that personalise themselves; designers focus more on judgment and systems thinking than pixel-pushing."
    },
    "product_management": {
        "title": "Product Management & Strategy",
        "logic_expression": "High_Communication AND Strategy_Interest AND NOT Deep_Coding",
        "relevant_streams": ["Commerce", "Arts / Humanities", "Undergraduate (other)"],
        "prereqs": ["Agile/Scrum basics", "Market & user research", "Cross-team communication"],
        "if_taken": "Broad influence across engineering, design and business; strong long-term leadership path.",
        "if_avoided": "You stay closer to hands-on technical or creative work, with less cross-functional overhead.",
        "if_alt_chosen": "If you want the strategy side without full PM ownership, business analysis is a good adjacent role.",
        "trend_now": "Data-driven, experiment-led product growth is now standard practice.",
        "trend_10y": "AI tools handle more routine planning and reporting; PMs focus more on judgment calls, ethics, and long-term positioning."
    },
    "finance_analytics": {
        "title": "Finance & Business Analytics",
        "logic_expression": "Numbers_Comfort AND Structured_Thinking AND NOT Visual_Art_Focus",
        "relevant_streams": ["Commerce", "Science (PCM)"],
        "prereqs": ["Financial fundamentals", "Excel / SQL", "Basic statistics"],
        "if_taken": "Stable, in-demand skill set applicable across almost every industry.",
        "if_avoided": "You avoid heavier quantitative work but may need it eventually in most business-adjacent roles.",
        "if_alt_chosen": "If finance feels too narrow, general business analytics gives similar skills with more variety.",
        "trend_now": "Growing use of automation and dashboards for routine financial analysis.",
        "trend_10y": "Analysts spend less time compiling numbers and more time interpreting them and advising decisions."
    },
    "content_communication": {
        "title": "Content, Communication & Media",
        "logic_expression": "Language_Strength AND Creativity AND NOT Numbers_Comfort",
        "relevant_streams": ["Arts / Humanities", "Undergraduate (other)", "Other"],
        "prereqs": ["Strong writing/communication", "Basic SEO or media literacy", "Portfolio building"],
        "if_taken": "Flexible, creative career with growing digital and multimedia opportunities.",
        "if_avoided": "You avoid a competitive, often freelance-heavy field, but lose a natural strength if writing is one.",
        "if_alt_chosen": "If you want more stability, marketing or corporate communications applies similar skills in a structured role.",
        "trend_now": "Rising demand for short-form video and AI-assisted content workflows.",
        "trend_10y": "AI drafts routine content; human value shifts toward original ideas, judgment, and voice."
    },
    "civil_services": {
        "title": "Civil Services — Administrative, Police & Foreign Service (UPSC / State PSC)",
        "logic_expression": "Public_Service_Interest AND Strong_GK AND High_Communication",
        "relevant_streams": ["Civil Services", "Arts / Humanities", "Commerce"],
        "prereqs": [
            "Prelims syllabus: Polity, Economy, History, Geography, Environment",
            "Daily current-affairs reading (newspaper + monthly compilations)",
            "Mains answer-writing practice (structured, time-bound)",
            "Optional subject mastery + mock interviews for Personality Test",
        ],
        "if_taken": "Access to some of the most influential public-leadership roles in the country (IAS/IPS/IFS and allied services), with long-term job security and nationwide impact.",
        "if_avoided": "You keep flexibility to enter the private sector sooner, without the multi-year, high-competition preparation timeline this path usually needs.",
        "if_alt_chosen": "If the full UPSC track feels too long, State PSC exams or Public Sector Undertaking (PSU) recruitment offer a related, often shorter path with similar public-service value.",
        "trend_now": "Selection increasingly rewards structured, syllabus-aligned preparation over rote memorisation, with growing weight on ethics and current-affairs analysis.",
        "trend_10y": "Governance is steadily digitising — future officers are expected to be comfortable with data-driven policy tools alongside traditional administrative skills."
    },
    "civil_engineering": {
        "title": "Civil Engineering — Structural, Infrastructure & Construction Management",
        "logic_expression": "Coding_Optional AND Physical_Systems_Interest AND Structured_Thinking",
        "relevant_streams": ["Civil Engineering", "Diploma / Polytechnic"],
        "prereqs": [
            "Structural analysis & design fundamentals",
            "AutoCAD / civil design software (e.g. STAAD.Pro, Revit)",
            "Site execution & project management basics",
            "Relevant licensing/certification for your region",
        ],
        "if_taken": "Direct role in building the physical infrastructure — buildings, roads, water systems — with steady, widespread demand across both public and private projects.",
        "if_avoided": "You avoid site-heavy, often outdoor and physically demanding work, but move away from hands-on infrastructure creation.",
        "if_alt_chosen": "If pure structural design appeals more than site execution, specialising early toward structural or geotechnical engineering narrows the same degree into a more design-focused role.",
        "trend_now": "Rising use of Building Information Modelling (BIM) and sustainable/green construction practices.",
        "trend_10y": "Greater integration of smart-infrastructure sensors and AI-assisted design checks, with engineers focusing more on oversight, safety, and sustainability judgment."
    },
}

INSPIRATIONAL_QUOTES = [
    {"quote": "The best way to predict the future is to invent it.", "author": "Alan Kay"},
    {"quote": "Choose a job you love, and you will never have to work a day in your life.", "author": "Confucius"},
    {"quote": "Success is the sum of small efforts, repeated day in and day out.", "author": "Robert Collier"},
    {"quote": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"quote": "Your career is a marathon, not a sprint — pace yourself with purpose.", "author": "Unknown"},
]

VAGUE_ANSWERS = {"idk", "i don't know", "not sure", "dunno", "no idea", "maybe", "?"}

# ==============================================================================
# PAGE CONFIG & STYLING
# ==============================================================================
st.set_page_config(page_title=APP_NAME, page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Elegant deep slate/teal background — stays calm and readable whether
       the viewer's system is in light or dark mode. */
    .stApp {
        background: linear-gradient(160deg, #0f2027 0%, #203a43 45%, #2c5364 100%);
        color: #eef2f6;
    }
    h1, h2, h3 { color: #7dd3fc !important; font-weight: 700; }
    p, label, span, div { color: #eef2f6; }
    .quote-box {
        background: rgba(255,255,255,0.08);
        border-left: 5px solid #fb7185;
        border-radius: 10px;
        padding: 20px 24px;
        backdrop-filter: blur(4px);
        box-shadow: 0 4px 18px -6px rgba(0,0,0,0.4);
    }
    .hero-panel {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
        border-radius: 18px;
        padding: 34px;
        color: #f8fafc;
        text-align: center;
        box-shadow: 0 12px 28px -8px rgba(8,145,178,0.5);
    }
    .result-card {
        background: rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 22px 26px;
        margin-top: 10px;
        backdrop-filter: blur(4px);
        box-shadow: 0 6px 20px -8px rgba(0,0,0,0.4);
    }
    /* Keep Streamlit's own widgets (inputs, sidebar) readable on the dark base */
    section[data-testid="stSidebar"] { background: rgba(15,32,39,0.85); }
    .stTextInput input, .stTextInput>div>div, .stSelectbox>div>div {
        background: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #4b5563 !important;
    }
    .stTextInput input::placeholder { color: #9ca3af !important; }
    /* Streamlit's built-in show/hide-password eye icon — make it visible on black */
    .stTextInput button svg { fill: #ffffff !important; opacity: 0.9; }
    .stTextInput button:hover svg { opacity: 1; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# AUTH HELPERS — passwords are salted + hashed, never stored or shown in plain text
# ==============================================================================
def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()

def load_users() -> dict:
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_user(username: str, password: str, stream: str) -> None:
    users = load_users()
    salt = secrets.token_hex(8)
    users[username] = {
        "salt": salt,
        "password_hash": hash_password(password, salt),
        "stream": stream,
        "created": str(datetime.now()),
    }
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=2)

def verify_user(username: str, password: str, users: dict) -> bool:
    record = users.get(username)
    if not record:
        return False
    return hash_password(password, record["salt"]) == record["password_hash"]

# ==============================================================================
# SESSION STATE
# ==============================================================================
defaults = {
    "authenticated": False, "username": None, "user_stream": None,
    "dialogue_step": 0, "user_responses": {}, "free_question": "",
    "clarify_pending": False,
    "selected_quote": random.choice(INSPIRATIONAL_QUOTES),
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==============================================================================
# ADMIN VIEW — reachable only via an unlisted URL parameter (not linked anywhere
# in the UI), and additionally gated behind ADMIN_PASSWORD. The URL parameter
# alone is not sufficient to see any data — this avoids "security by obscurity".
# ==============================================================================
if st.query_params.get("access_scope") == "creator_admin_override":
    st.title("🛡️ Creator Admin View")
    st.caption("This view is not linked anywhere in the app and requires the admin password.")
    admin_pw = st.text_input("Admin password", type="password")
    if admin_pw == ADMIN_PASSWORD and admin_pw != "":
        users_data = load_users()
        rows = [
            {"Username": k, "Stream": v.get("stream", "—"), "Created": v.get("created", "N/A")}
            for k, v in users_data.items()
        ]
        st.subheader(f"Registered users ({len(rows)})")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.caption("Password hashes are intentionally not shown here — there's no legitimate reason to display them.")
    elif admin_pw:
        st.error("Incorrect admin password.")
    if st.button("Exit admin view"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# ==============================================================================
# LOGIN / SIGNUP
# ==============================================================================
if not st.session_state.authenticated:
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown(f"# Welcome to {APP_NAME}")
        st.markdown("*Find a career direction that fits how you think, backed by clear reasoning.*")
        st.markdown("""
            <div class="hero-panel">
                <div style="font-size:1.15rem; font-weight:300;">
                    "Good career choices come from quiet reflection, honest self-assessment,
                    and a clear look at where the world is heading."
                </div>
            </div>
        """, unsafe_allow_html=True)

        q = st.session_state.selected_quote
        st.markdown(f"""
        <div class="quote-box" style="margin-top:28px;">
            <div style="font-size:1.15rem; font-style:italic;">"{q['quote']}"</div>
            <div style="text-align:right; font-weight:bold; color:#0ea5e9; margin-top:8px;">— {q['author']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.subheader("🔐 Account Access")
        auth_action = st.radio("Choose an option", ["Log In", "Sign Up"])
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")

        if auth_action == "Sign Up":
            stream_input = st.selectbox("Your current stream / background", STREAMS)

        if auth_action == "Log In":
            if st.button("Log In ➔"):
                users_database = load_users()
                if verify_user(username_input, password_input, users_database):
                    st.session_state.authenticated = True
                    st.session_state.username = username_input
                    st.session_state.user_stream = users_database[username_input].get("stream")
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        else:
            if st.button("Create Account ➔"):
                users_database = load_users()
                if username_input in users_database:
                    st.error("That username is already taken.")
                elif len(username_input) < 3 or len(password_input) < 4:
                    st.warning("Username needs 3+ characters, password needs 4+ characters.")
                else:
                    save_user(username_input, password_input, stream_input)
                    st.success("Account created! Switch to 'Log In' above to sign in.")

# ==============================================================================
# LOGGED-IN DASHBOARD
# ==============================================================================
else:
    st.sidebar.markdown("### 🔮 Dashboard")
    st.sidebar.markdown(f"Signed in as **{st.session_state.username}**")
    st.sidebar.markdown(f"Stream: {st.session_state.user_stream or 'Not set'}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Sign Out"):
        for key in ["authenticated", "username", "user_stream", "dialogue_step", "user_responses", "free_question", "clarify_pending"]:
            st.session_state[key] = defaults[key]
        st.rerun()

    st.title("🧭 Career Guidance")

    # --- Free-text question with clarifying re-ask ---
    st.markdown("### 🤖 Ask a question")
    question = st.text_input("What's on your mind about your career?", value=st.session_state.free_question)
    if st.button("Ask"):
        st.session_state.free_question = question
        cleaned = question.strip().lower()
        if not cleaned or cleaned in VAGUE_ANSWERS or len(cleaned) < 8:
            st.session_state.clarify_pending = True
        else:
            st.session_state.clarify_pending = False

    if st.session_state.clarify_pending:
        st.info("Could you say a bit more? For example: what subject or type of work do you enjoy most right now?")
    elif st.session_state.free_question:
        st.success("Got it — use the guided questions below and I'll factor this in.")

    st.markdown("---")

    # --- Guided clarifying dialogue ---
    st.markdown("### 🧩 Guided assessment")
    dialogue_flow = {
        0: {
            "question": "Which describes you better?",
            "key": "logic_vs_visual",
            "options": [
                "I enjoy logical, structured problem-solving (coding, systems, numbers)",
                "I enjoy visual, creative, or people-facing work",
            ],
        },
        1: {
            "question": "How comfortable are you with heavy math/statistics?",
            "key": "math_comfort",
            "options": [
                "Very comfortable — I enjoy working with numbers and models",
                "Not very comfortable — I'd rather focus on strategy, people, or design",
            ],
        },
        2: {
            "question": "What matters more to you day to day?",
            "key": "comm_vs_focus",
            "options": [
                "Communicating, coordinating, and influencing others",
                "Deep, focused individual work on a specific craft",
            ],
        },
    }

    step = st.session_state.dialogue_step
    if step < len(dialogue_flow):
        st.caption(f"Question {step + 1} of {len(dialogue_flow)}")
        st.markdown(f"**{dialogue_flow[step]['question']}**")
        pick = st.radio("Choose one:", dialogue_flow[step]["options"], key=f"q_{step}")
        if st.button("Next ➔"):
            st.session_state.user_responses[dialogue_flow[step]["key"]] = pick
            st.session_state.dialogue_step += 1
            st.rerun()
    else:
        st.success("✅ Assessment complete.")
        if st.button("🔄 Restart assessment"):
            st.session_state.dialogue_step = 0
            st.session_state.user_responses = {}
            st.rerun()

        facts = st.session_state.user_responses
        coding = "logical, structured" in facts.get("logic_vs_visual", "")
        math_ok = "Very comfortable" in facts.get("math_comfort", "")
        comm = "Communicating" in facts.get("comm_vs_focus", "")

        if coding and math_ok:
            target_key = "data_science_ai"
        elif coding and not math_ok:
            target_key = "software_engineering"
        elif not coding and comm and not math_ok:
            target_key = "product_management"
        elif not coding and math_ok:
            target_key = "finance_analytics"
        elif not coding and not comm:
            target_key = "content_communication"
        else:
            target_key = "ui_ux_design"

        # Route students on a Civil Services or Civil Engineering track to the
        # field-specific path rather than the generic four-way split above.
        stream_category = STREAM_CATEGORY.get(st.session_state.user_stream, "Other")
        if stream_category == "Civil Services":
            target_key = "civil_services"
        elif stream_category == "Civil Engineering":
            target_key = "civil_engineering"

        # Nudge toward a stream-relevant path if the direct match doesn't fit their stream
        record = KNOWLEDGE_BASE[target_key]
        if stream_category and stream_category not in record["relevant_streams"]:
            alt = next((k for k, v in KNOWLEDGE_BASE.items() if stream_category in v["relevant_streams"]), None)
            if alt:
                st.caption(f"Note: this also draws on paths common for your stream ({st.session_state.user_stream}).")

        st.markdown("---")
        st.markdown(f"""
        <div class="result-card">
        <h4>🎯 Suggested direction: {record['title']}</h4>
        <p><b>Reasoning basis:</b> {record['logic_expression']}</p>
        <p>✅ <b>If you pursue this:</b> {record['if_taken']}</p>
        <p>⚠️ <b>If you avoid this:</b> {record['if_avoided']}</p>
        <p>🔁 <b>If you'd rather try something adjacent:</b> {record['if_alt_chosen']}</p>
        <p>🚀 <b>Path to achieving this:</b> If you deliberately build the skills listed below, you're on a realistic track to reach {record['title']}. If you continue without that extra effort, you'll more likely land in an adjacent, less specialised role rather than this one.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📊 Skill self-assessment")
        c1, c2 = st.columns(2)
        with c1:
            grade = st.slider("Current performance in relevant subjects (%)", 10, 100, 75)
            if grade < 60:
                st.warning("Foundational gaps detected — start with core fundamentals before advanced material.")
            elif grade < 85:
                st.info("Solid base — build real projects and get hands-on practice now.")
            else:
                st.success("Strong foundation — move toward advanced, specialised work and mentorship.")
        with c2:
            st.markdown("**Core skills to build:**")
            for skill in record["prereqs"]:
                st.markdown(f"- 🛠️ {skill}")

        st.markdown("### ⏳ Market outlook")
        t1, t2 = st.columns(2)
        with t1:
            st.info(f"**Now ({CURRENT_YEAR}):** {record['trend_now']}")
        with t2:
            st.success(f"**In 10 years (~{CURRENT_YEAR + 10}):** {record['trend_10y']}")

    st.markdown("---")
    st.caption(f"{APP_NAME} · v2.0")

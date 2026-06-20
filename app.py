import re
import streamlit as st
from google import genai
from google.genai import types


def md_to_html(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'(?m)^[\-\*]\s(.+)', r'<li>\1</li>', text)
    paragraphs = re.split(r'\n\s*\n', text)
    if len(paragraphs) > 1:
        return "".join(
            f"<p>{p.strip().replace(chr(10), '<br>')}</p>"
            for p in paragraphs if p.strip()
        )
    return text.replace("\n", "<br>")

# ============================================================
# 1. PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="El Defensor AI — La Albiceleste",
    page_icon="🇦🇷",
    layout="centered",
)

# ============================================================
# 2. LA CAMISETA CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

:root {
    --white: #FAFAFA;
    --sky-blue: #75AADB;
    --sky-blue-dark: #5A8FBF;
    --sky-blue-light: #B8D8F0;
    --navy: #1A365D;
    --navy-dark: #0F1F3A;
    --gold: #C9A84C;
    --gold-light: #DFC66A;
    --text: #1A1A2E;
    --text-light: #5A6B7C;
    --card-shadow: rgba(26, 54, 93, 0.1);
}

/* ── Base layout ── */
.stApp {
    background-color: var(--white);
    background-image: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 45px,
        rgba(117, 170, 219, 0.06) 45px,
        rgba(117, 170, 219, 0.06) 75px
    );
    background-attachment: fixed;
}

#MainMenu, .stDeployButton, header { display: none; }

.main > .block-container {
    max-width: 780px;
    padding: 0.5rem 1.5rem 2rem;
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif;
    color: var(--navy);
}

p, li, div, span, label {
    font-family: 'Lora', serif;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--white); }
::-webkit-scrollbar-thumb { background: var(--sky-blue); border-radius: 4px; }

/* ── Hero header ── */
.header-hero {
    text-align: center;
    padding: 2rem 1rem 0.5rem;
    margin-bottom: 0.3rem;
}

.header-hero .sun {
    display: block;
    margin: 0 auto 0.3rem;
    animation: sunGlow 3s ease-in-out infinite;
}

.header-hero .crest {
    display: block;
    margin: 0 auto 0.4rem;
}

.header-hero h1 {
    font-family: 'Playfair Display', serif;
    font-weight: 900;
    font-size: 2.8rem;
    color: var(--navy-dark);
    margin: 0;
    line-height: 1.1;
    letter-spacing: 3px;
}

.header-hero .divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 6px auto 2px;
    max-width: 280px;
}

.header-hero .divider::before,
.header-hero .divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--sky-blue), transparent);
}

.header-hero .divider-icon {
    color: var(--gold);
    font-size: 0.7rem;
    letter-spacing: 4px;
}

.header-hero .subtitle {
    font-family: 'Lora', serif;
    font-style: italic;
    color: var(--text-light);
    font-size: 1rem;
    margin: 4px 0 0;
    line-height: 1.4;
}

/* ── Chat container ── */
[data-testid="stChatMessage"] {
    border: none !important;
    background: transparent !important;
    padding: 0.2rem 0 !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
    font-size: 1.8rem !important;
    align-self: flex-start !important;
    padding-top: 0.3rem !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ── User bubble — sky blue ── */
.user-bubble {
    background: linear-gradient(135deg, var(--sky-blue) 0%, var(--sky-blue-dark) 100%);
    color: white !important;
    padding: 0.8rem 1rem;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(90, 143, 191, 0.2);
    margin-left: 2.5rem;
    font-size: 0.92rem;
    line-height: 1.6;
}

.user-bubble a { color: var(--gold-light); }
.user-bubble p { color: white; margin-bottom: 0.4rem; }
.user-bubble p:last-child { margin-bottom: 0; }
.user-bubble strong { color: white; }
.user-bubble em { color: rgba(255, 255, 255, 0.9); }

/* ── Assistant bubble — white card ── */
.assistant-bubble {
    background: white;
    color: var(--text) !important;
    padding: 0.8rem 1rem;
    border-radius: 10px;
    border: 1px solid rgba(117, 170, 219, 0.2);
    border-left: 3px solid var(--gold);
    box-shadow: 0 2px 10px rgba(26, 54, 93, 0.06);
    margin-right: 2.5rem;
    font-size: 0.92rem;
    line-height: 1.6;
}

.assistant-bubble p { margin-bottom: 0.4rem; }
.assistant-bubble p:last-child { margin-bottom: 0; }

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border: 1.5px solid rgba(117, 170, 219, 0.3) !important;
    border-radius: 10px !important;
    background: white !important;
    font-family: 'Lora', serif !important;
    color: var(--text) !important;
    box-shadow: 0 2px 8px rgba(26, 54, 93, 0.04) !important;
}

[data-testid="stChatInput"]:focus {
    border-color: var(--sky-blue) !important;
    box-shadow: 0 0 0 2px rgba(117, 170, 219, 0.15) !important;
}

[data-testid="stChatInput"] input::placeholder {
    color: var(--text-light);
    font-style: italic;
    opacity: 0.5;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    margin-top: 1.5rem;
}

.footer p {
    font-family: 'Playfair Display', serif;
    font-size: 0.8rem;
    color: var(--text-light);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
}

.footer .stars {
    color: var(--gold);
    font-size: 1rem;
    letter-spacing: 4px;
}

.footer .stripe {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--sky-blue), transparent);
    margin: 10px auto 8px;
}

/* ── Animations ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatMessage"] {
    animation: fadeSlideUp 0.35s ease-out;
}

@keyframes sunGlow {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.08); }
}

/* ── Loading spinner ── */
.stSpinner > div {
    border-color: var(--sky-blue) !important;
    border-top-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. SYSTEM INSTRUCTIONS
# ============================================================
SYSTEM_INSTRUCTION = """You are 'El Defensor', a fiercely loyal, intensely knowledgeable, and witty AI dedicated exclusively to defending the Argentina National Football Team (La Albiceleste).

You have an encyclopedic knowledge of football history, and you do not just defend—you counter-attack by bringing up historical facts that expose the flaws of other teams.

Your Tactical Playbook for Attacks & Defenses:

1. AGAINST BRAZIL:
   - If they boast about 5 World Cups, remind them they haven't won one since 2002 (nearly a quarter-century).
   - Bring up the absolute dominance: Argentina beat them 1-0 in the 2021 Copa América Final *at their own Maracanã*, and beat them 1-0 in Rio in 2023.
   - Point out that Argentina holds the absolute continental record with 16 Copa Américas, while Brazil only has 9.

2. AGAINST FRANCE:
   - The ultimate receipt is December 18, 2022. Argentina dominated them for 80 minutes, Messi lifted the trophy, and Emi Martínez danced his way into their nightmares.
   - Remind them that Argentina has 16 Copa Américas, while France has only 2 Euros. Broaden the trophy cabinet comparison.

3. AGAINST GERMANY:
   - If they bring up 2014, remind them that after that final, Germany completely collapsed on the world stage, suffering consecutive, embarrassing Group Stage exits in the 2018 and 2022 World Cups while Argentina rebuilt and conquered the world.

4. GENERAL DEFENSE (The GOAT & The Cabinet):
   - Lionel Messi is the undisputed GOAT: 8 Ballon d'Ors, most World Cup appearances, and back-to-back major international trophies.
   - Argentina won the 2024 Copa América (beating Colombia 1-0 via Lautaro Martínez), confirming their total global dominance.

Tone: Confident, fiercely passionate, witty, and mathematically undefeated. Use football slang like 'Muchachos', 'La Scaloneta', and 'Decime qué se siente'.

CRITICAL LANGUAGE RULE: You must always write your entire response in English. You may use short, iconic Spanish football catchphrases (like 'Muchachos' or 'La Scaloneta') for flavor, but the core arguments, facts, and sentences must absolutely be in English."""

# ============================================================
# 4. SESSION STATE
# ============================================================
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8,
        ),
    )

# ============================================================
# 5. MAIN HEADER
# ============================================================
st.markdown("""
<div class="header-hero">
    <svg class="sun" viewBox="0 0 44 44" width="34" height="34">
        <circle cx="22" cy="22" r="7" fill="#C9A84C"/>
        <path d="M22 1 L23.5 8 L20.5 8 Z M22 43 L23.5 36 L20.5 36 Z
                 M1 22 L8 23.5 L8 20.5 Z M43 22 L36 23.5 L36 20.5 Z
                 M7 7 L12 12 L11 13 L6 8 Z M37 37 L32 32 L33 31 L38 36 Z
                 M37 7 L32 12 L33 13 L38 8 Z M7 37 L12 32 L11 31 L6 36 Z"
              fill="#C9A84C"/>
        <circle cx="22" cy="22" r="4.5" fill="#F5D742"/>
    </svg>
    <svg class="crest" viewBox="0 0 90 60" width="74" height="49">
        <rect width="90" height="60" fill="#75AADB"/>
        <rect y="20" width="90" height="20" fill="#FFFFFF"/>
        <circle cx="45" cy="30" r="7" fill="#C9A84C"/>
        <circle cx="45" cy="30" r="4" fill="#F5D742"/>
    </svg>
    <h1>EL DEFENSOR</h1>
    <div class="divider">
        <span class="divider-icon">✦</span>
    </div>
    <p class="subtitle">La Albiceleste</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 6. CHAT HISTORY
# ============================================================
for message in st.session_state.messages:
    is_assistant = message["role"] == "assistant"
    avatar = "🇦🇷" if is_assistant else "🤬"
    bubble_class = "assistant-bubble" if is_assistant else "user-bubble"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(f"<div class='{bubble_class}'>{md_to_html(message['content'])}</div>", unsafe_allow_html=True)

# ============================================================
# 7. CHAT INPUT & STREAMING RESPONSE
# ============================================================
if user_prompt := st.chat_input("Try: 'Brazil is better than Argentina' or 'Messi is overrated'..."):
    with st.chat_message("user", avatar="🤬"):
        st.markdown(f"<div class='user-bubble'>{user_prompt}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant", avatar="🇦🇷"):
        stream = st.session_state.chat.send_message_stream(user_prompt)
        full_response = ""
        placeholder = st.empty()
        for chunk in stream:
            if chunk.text:
                full_response += chunk.text
                placeholder.markdown(
                    f"<div class='assistant-bubble'>{md_to_html(full_response)}</div>",
                    unsafe_allow_html=True,
                )

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ============================================================
# 8. FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <p class="stars">★ ★ ★</p>
    <p>Campeón del Mundo &bull; 1978 &bull; 1986 &bull; 2022</p>
    <p style="text-transform:none; letter-spacing:1px; font-family:'Lora',serif; font-size:0.75rem;">
        16 Copas América &bull; 3 Estrellas &bull; La Scaloneta
    </p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import base64
from pathlib import Path
from agent import analyze_skin, chat_with_bot


# PAGE CONFIG
st.set_page_config(
    page_title="AI Skincare Advisor",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# CUSTOM CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --cream:   #FAF6EF;
        --cream2:  #F3EBD8;
        --gold:    #C9A84C;
        --gold2:   #E8C97A;
        --charcoal:#2C2C2C;
        --muted:   #7A7065;
        --accent:  #8B5E3C;
        --white:   #FFFFFF;
        --card-bg: #FFFDF7;
        --border:  #E8D9B8;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--cream) !important;
        font-family: 'DM Sans', sans-serif;
        color: var(--charcoal);
    }
    [data-testid="stHeader"] { background: transparent !important; }
    section[data-testid="stMain"] > div { padding-top: 1rem !important; }

    /* ── Title ── */
    .app-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem; font-weight: 700;
        color: var(--charcoal);
        letter-spacing: 0.04em;
        margin-bottom: 0; line-height: 1.1;
    }
    .app-subtitle {
        font-size: 0.93rem; color: var(--muted);
        letter-spacing: 0.12em; text-transform: uppercase; margin-top: 0.2rem;
    }
    .gold-line {
        height: 3px;
        background: linear-gradient(90deg, var(--gold), var(--gold2), transparent);
        border: none; margin: 0.6rem 0 1.4rem 0; border-radius: 2px;
    }

    /* ── Panel card ── */
    .panel-card {
        background: var(--card-bg);
        border: 1.5px solid var(--border);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 16px rgba(201,168,76,0.07);
    }
    .panel-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem; font-weight: 600;
        color: var(--charcoal); margin-bottom: 0.12rem;
    }
    .panel-subtitle {
        font-size: 0.77rem; color: var(--muted);
        text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.85rem;
    }

    /* ── Result box ── */
    .result-box {
        background: linear-gradient(135deg, #FFF9EC, #FFF3D6);
        border: 1.5px solid var(--gold);
        border-radius: 14px; padding: 1.1rem 1.3rem; margin-top: 0.5rem;
    }
    .result-skin-name {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.55rem; font-weight: 700;
        color: var(--gold); margin-bottom: 0.4rem;
    }
    .result-description { font-size: 0.87rem; color: var(--charcoal); line-height: 1.65; }
    .conf-bar-bg {
        background: var(--cream2); border-radius: 20px; height: 7px;
        margin: 0.6rem 0 0; overflow: hidden; border: 1px solid var(--border);
    }
    .conf-bar-fill {
        height: 100%; border-radius: 20px;
        background: linear-gradient(90deg, var(--gold), var(--gold2));
    }
    .small-text { font-size: 0.77rem; color: var(--muted); }

    /* ── ALL buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, var(--gold), #B8962E) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: 30px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em !important;
        padding: 0.42rem 1.2rem !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 18px rgba(201,168,76,0.35) !important;
    }

    /* ── Checkbox-style question buttons — cream/gold look ── */
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] .stButton > button,
    .question-btn .stButton > button {
        background: var(--white) !important;
        color: var(--charcoal) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        text-align: left !important;
        font-size: 0.83rem !important;
        padding: 0.42rem 0.9rem !important;
        font-weight: 400 !important;
        letter-spacing: 0 !important;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        border-color: var(--gold) !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* ── Suggested question chips ── */
    .sq-row .stButton > button {
        background: var(--white) !important;
        color: var(--accent) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 30px !important;
        font-size: 0.79rem !important;
        padding: 0.3rem 0.8rem !important;
        font-weight: 400 !important;
        letter-spacing: 0 !important;
    }
    .sq-row .stButton > button:hover {
        border-color: var(--gold) !important;
        color: var(--gold) !important;
        box-shadow: none !important; transform: none !important;
    }

    /* ── Text input ── */
    .stTextInput > div > input {
        background: var(--white) !important;
        border-color: var(--border) !important;
        border-radius: 30px !important;
        font-family: 'DM Sans', sans-serif !important;
        color: var(--charcoal) !important;
        padding: 0.5rem 1rem !important;
    }
    .stTextInput > div > input:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
    }

    /* ── Chat bubbles ── */
    .chat-bubble-user {
        background: linear-gradient(135deg, var(--gold), var(--gold2));
        color: var(--charcoal);
        border-radius: 18px 18px 4px 18px;
        padding: 0.6rem 1rem;
        margin: 0.25rem 0 0.25rem 3rem;
        font-size: 0.84rem; line-height: 1.55;
    }
    .chat-bubble-bot {
        background: var(--white);
        border: 1.5px solid var(--border);
        border-radius: 18px 18px 18px 4px;
        padding: 0.6rem 1rem;
        margin: 0.25rem 3rem 0.25rem 0;
        font-size: 0.84rem; line-height: 1.55;
        color: var(--charcoal);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .chat-label {
        font-size: 0.65rem; color: var(--muted);
        text-transform: uppercase; letter-spacing: 0.07em;
    }
    .chat-messages {
        min-height: 0;              /* remove forced empty space */
        max-height: 360px;
        overflow-y: auto;
        padding: 0.2rem 0.2rem 0.4rem;
        margin-bottom: 0.7rem;
    }

    .chat-messages::-webkit-scrollbar { width: 4px; }
    .chat-messages::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    /* Context badges */
    .context-badge {
        background: linear-gradient(135deg,#FFF9EC,#FFF3D6);
        border: 1px solid var(--border); border-radius: 20px;
        padding: 0.28rem 0.85rem; font-size: 0.75rem;
        display: inline-block; margin-bottom: 0.65rem;
    }
    .context-badge-hint {
        background: #FFF8E8; border: 1px dashed var(--border);
        border-radius: 10px; padding: 0.45rem 0.85rem;
        font-size: 0.79rem; color: var(--muted);
        margin-bottom: 0.65rem; font-style: italic;
    }

    hr { border-color: var(--border) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)



# DATA: skin types with descriptions + questions
ASSETS = Path(__file__).parent / "assets"

SKIN_DATA = {
    "Dry": {
        "emoji": "",
        "file": "Dry_Skin.png",
        "description": (
            "Dry skin produces less sebum than normal, leaving it lacking the lipids needed to "
            "retain moisture and build a protective barrier. It often feels tight, rough, or flaky — "
            "especially after cleansing or in cold weather."
        ),
        "questions": [
            "My skin feels tight or uncomfortable after washing",
            "I often notice flaky or rough patches on my face",
            "My skin rarely looks shiny or oily",
            "I need to reapply moisturizer multiple times a day",
        ],
    },
    "Oily": {
        "emoji": "",
        "file": "Oily_Skin.jpg",
        "description": (
            "Oily skin is characterised by excess sebum production, giving the face a shiny or greasy "
            "appearance — especially across the T-zone. Pores tend to look enlarged, and this type is "
            "more prone to blackheads, whiteheads, and breakouts."
        ),
        "questions": [
            "My face looks noticeably shiny by midday",
            "I have visibly large or frequently clogged pores",
            "I get regular blackheads or whiteheads",
            "Makeup slides off or breaks down quickly on my skin",
        ],
    },
    "Combination": {
        "emoji": "",
        "file": "Combination_Skin.webp",
        "description": (
            "Combination skin features an oily T-zone (forehead, nose, chin) alongside dry or normal "
            "cheeks. It's the most common skin type and can be tricky to manage, as different areas "
            "need different levels of hydration and oil control."
        ),
        "questions": [
            "My T-zone is oily but my cheeks feel dry or tight",
            "Different areas of my face need different products",
            "I get occasional breakouts mainly in the T-zone",
            "My skin balance shifts with seasons or hormones",
        ],
    },
    "Sensitive": {
        "emoji": "",
        "file": "Sensitive_Skin.webp",
        "description": (
            "Sensitive skin reacts easily to external triggers — products, temperature, or stress — "
            "showing redness, itching, burning, or stinging. It often has a weakened skin barrier that "
            "allows irritants to penetrate more easily."
        ),
        "questions": [
            "My skin turns red or burns after applying products",
            "I react to fragrance, alcohol, or harsh ingredients",
            "My skin often feels itchy or irritated throughout the day",
            "I have visible redness, flushing, or rosacea-like patches",
        ],
    },
    "Acne-Prone": {
        "emoji": "",
        "file": "Acne_Skin.jpg",
        "description": (
            "Acne-prone skin is predisposed to breakouts — including pimples, cysts, blackheads, and "
            "whiteheads — due to excess oil, clogged pores, bacteria, or inflammation. It requires "
            "non-comedogenic, gentle care to prevent and treat blemishes without over-drying."
        ),
        "questions": [
            "I get regular pimples, papules, or cystic breakouts",
            "My pores clog easily even when I follow a routine",
            "I have post-acne marks or hyperpigmentation",
            "Stress, diet, or hormones visibly worsen my breakouts",
        ],
    },
}

SKIN_TYPES = list(SKIN_DATA.keys())


# HELPERS

def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        raw = base64.b64encode(f.read()).decode()
    ext = Path(path).suffix.lstrip(".").lower()
    mime = {"webp": "image/webp", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, f"image/{ext}")
    return f"data:{mime};base64,{raw}"


def init_session_state():
    defaults = {
        "selected_skin": None,
        "checked_questions": [],
        "analysis": None,
        "chat_history": [],
        "chat_display": [],
        "analyzed": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def send_chat(user_msg: str):
    """Send a message to GlowBot, save to histories, and rerun."""
    user_msg = user_msg.strip()
    if not user_msg:
        return

    skin_ctx = st.session_state.analysis if st.session_state.analyzed else {}

    # Pass history WITHOUT the new message — agent.py appends it internally
    with st.spinner("GlowBot is thinking..."):
        reply = chat_with_bot(user_msg, st.session_state.chat_history, skin_ctx)

    # Now save both turns to history and display
    st.session_state.chat_display.append({"role": "user",      "content": user_msg})
    st.session_state.chat_display.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append({"role": "user",      "content": user_msg})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()


# MAIN

def main():
    init_session_state()

    # Header
    st.markdown(
        '<h1 class="app-title">✨ AI Skincare Advisor</h1>'
        '<p class="app-subtitle"> · Personalized for your skin ·</p>'
        '<div class="gold-line"></div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.05, 0.95], gap="large")

    
    # LEFT PANEL
    with left_col:

        # Skin type image grid 
        st.markdown(
            '<div class="panel-card">'
            '<div class="panel-title">💆 What\'s your skin type?</div>'
            '<div class="panel-subtitle">Tap an image to select yours</div>',
            unsafe_allow_html=True,
        )

        # Layout: row of 3 + centred row of 2
        r1c1, r1c2, r1c3 = st.columns(3)
        _, r2c1, r2c2, _ = st.columns([0.5, 1, 1, 0.5])
        slots = [r1c1, r1c2, r1c3, r2c1, r2c2]

        for idx, name in enumerate(SKIN_TYPES):
            skin  = SKIN_DATA[name]
            img_p = ASSETS / skin["file"]
            b64   = img_to_base64(str(img_p)) if img_p.exists() else ""
            is_sel = st.session_state.selected_skin == name
            border = "3px solid #C9A84C" if is_sel else "2px solid #E8D9B8"
            bg     = "linear-gradient(135deg,#FFF9EC,#FFF3D6)" if is_sel else "#FFFFFF"
            shadow = "0 4px 16px rgba(201,168,76,0.28)" if is_sel else "none"
            tick   = "✅ " if is_sel else ""

            with slots[idx]:
                if b64:
                    st.markdown(
                        f'<div style="border:{border};border-radius:14px;padding:5px;'
                        f'background:{bg};box-shadow:{shadow};text-align:center;">'
                        f'<img src="{b64}" style="width:100%;height:86px;object-fit:cover;border-radius:10px;" />'
                        f'<div style="font-size:0.75rem;font-weight:500;color:#2C2C2C;margin-top:4px;">'
                        f'{tick}{skin["emoji"]} {name}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="border:{border};border-radius:14px;padding:10px;'
                        f'background:{bg};box-shadow:{shadow};text-align:center;height:105px;'
                        f'display:flex;flex-direction:column;align-items:center;justify-content:center;">'
                        f'<div style="font-size:1.8rem;">{skin["emoji"]}</div>'
                        f'<div style="font-size:0.75rem;font-weight:500;margin-top:4px;">'
                        f'{tick}{name}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                if st.button("Select", key=f"sel_{name}", use_container_width=True):
                    if st.session_state.selected_skin != name:
                        st.session_state.selected_skin = name
                        st.session_state.checked_questions = []
                        st.session_state.analyzed = False
                        st.session_state.analysis = None
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Dynamic follow-up questions
        # Questions change every time a different skin type is clicked
        if st.session_state.selected_skin:
            skin_name = st.session_state.selected_skin
            questions = SKIN_DATA[skin_name]["questions"]

            st.markdown(
                '<div class="panel-card">'
                f'<div class="panel-title">🔍 About your {skin_name} skin</div>'
                '<div class="panel-subtitle">Click all that apply to you</div>',
                unsafe_allow_html=True,
            )

            # Render each question as a full-width toggle button
            for q in questions:
                is_checked = q in st.session_state.checked_questions
                icon = "✅" if is_checked else "⬜"
                if st.button(f"{icon}  {q}", key=f"q_{skin_name}_{q[:18]}", use_container_width=True):
                    if is_checked:
                        st.session_state.checked_questions.remove(q)
                    else:
                        st.session_state.checked_questions.append(q)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Analyze / Regenerate buttons
            btn_l, btn_r = st.columns([2, 1])
            with btn_l:
                analyze_clicked = st.button("Analyze My Skin", key="analyze_btn", use_container_width=True)
            with btn_r:
                regen_clicked = st.button("🔄 Regenerate", key="regen_btn", use_container_width=True)

            if analyze_clicked or regen_clicked:
                concerns = (
                    "User confirmed these symptoms: " + "; ".join(st.session_state.checked_questions)
                    if st.session_state.checked_questions
                    else "No specific symptoms indicated"
                )
                with st.spinner("Analyzing your skin..."):
                    analysis = analyze_skin(
                        skin_type=skin_name,
                        concerns=concerns,
                        lifestyle="Not provided",
                    )
                st.session_state.analysis = analysis
                st.session_state.analyzed = True
                st.session_state.chat_history = []
                st.session_state.chat_display = []
                st.rerun()

        # Analysis result: name + description ONLY
        if st.session_state.analyzed and st.session_state.analysis:
            a = st.session_state.analysis
            skin_name = a.get("skin_type", st.session_state.selected_skin or "Unknown")
            conf = a.get("confidence", 80)
            description = SKIN_DATA.get(skin_name, {}).get(
                "description",
                "Your skin has been analyzed. Ask GlowBot for personalised advice and routines."
            )
            emoji = SKIN_DATA.get(skin_name, {}).get("emoji", "✨")

            st.markdown(
                '<div class="panel-card">'
                '<div class="panel-title">📋 Analysis Result</div>'
                '<div class="panel-subtitle">Your skin profile</div>'
                f'<div class="result-box">'
                f'<div class="result-skin-name">{emoji} {skin_name} Skin</div>'
                f'<div class="result-description">{description}</div>'
                f'<div class="small-text" style="margin-top:0.85rem;">Analysis confidence: {conf}%</div>'
                f'<div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{conf}%;"></div></div>'
                f'</div>'
                '<div style="font-size:0.79rem;color:#7A7065;margin-top:0.75rem;font-style:italic;">'
                '💬 Use GlowBot on the right for routines, ingredient advice, and deeper insights!'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # RIGHT PANEL — full chatbot
    with right_col:

        # Single card: title + context badge + chat history + input
        st.markdown(
            '<div class="panel-card">'
            '<div class="panel-title">💬 AI Chat Bot</div>'
            '<div class="panel-subtitle">GlowBot · Ask anything about skincare</div>',
            unsafe_allow_html=True,
        )

        # Context badge: shows the skin type currently loaded in the bot's context (if any)
        if st.session_state.analyzed and st.session_state.analysis:
            skin = st.session_state.analysis.get("skin_type", "–")
            st.markdown(
                f'<div class="context-badge">🧬 Context: <strong>{skin} Skin</strong> loaded</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="context-badge-hint">'
                '💡 Analyze your skin first for personalized answers, or just ask away!'
                '</div>',
                unsafe_allow_html=True,
            )

        # Chat message area
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

        if not st.session_state.chat_display:
            st.markdown(
                '<div style="text-align:center;padding:2.5rem 0.5rem;">'
                '<div style="font-size:2.6rem;margin-bottom:0.5rem;">✨</div>'
                '<div style="color:#7A7065;font-size:0.87rem;line-height:1.65;">'
                "Hi! I'm <strong>GlowBot</strong>.<br>"
                "Ask me about ingredients, routines,<br>or anything about your skin.</div>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.chat_display:
                if msg["role"] == "user":
                    st.markdown(
                        '<div class="chat-label" style="text-align:right;margin-top:0.5rem;">You</div>'
                        f'<div class="chat-bubble-user">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div class="chat-label" style="margin-top:0.5rem;">✨ GlowBot</div>'
                        f'<div class="chat-bubble-bot">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)  # close .chat-messages

        # Input row (still inside the same card)
        st.markdown("<hr/>", unsafe_allow_html=True)
        in_col, send_col, clear_col = st.columns([2.5, 0.8, 0.8])
        with in_col:
            user_msg = st.text_input(
                "msg",
                placeholder="e.g. What ingredients should I avoid?",
                key="chat_input",
                label_visibility="collapsed",
            )
        with send_col:
            send_clicked = st.button("Send 💬", key="send_btn", use_container_width=True)
        with clear_col:
            if st.button("Clear🗑️", key="clear_btn", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.chat_display = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # close .panel-card

        # Handle send
        if send_clicked and user_msg.strip():
            send_chat(user_msg)

        # Suggested Questions (only show to encourage users to try it out)
        st.markdown(
            '<div class="panel-card" style="padding:1rem 1.4rem;">'
            '<div class="panel-subtitle" style="margin-bottom:0.5rem;">💡 Suggested Questions</div>',
            unsafe_allow_html=True,
        )

        suggestions = [
            "What SPF should I use?",
            "Is niacinamide good for me?",
            "Give me a morning routine",
            "How often should I exfoliate?",
            "Best ingredients for my skin?",
            "What should I avoid in products?",
        ]

        sq_c1, sq_c2 = st.columns(2)
        for i, q in enumerate(suggestions):
            with (sq_c1 if i % 2 == 0 else sq_c2):
                if st.button(q, key=f"sq_{i}", use_container_width=True):
                    send_chat(q)

        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#B0A090;font-size:0.75rem;padding:0.4rem;">'
        "⚠️ For informational purposes only. Consult a dermatologist for medical concerns."
        " &nbsp;|&nbsp; AI Skincare Advisor · 2026"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

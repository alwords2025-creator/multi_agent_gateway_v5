# Copyright (c) 2026 AI Software Innovation Infotech And Hardware Enterprises. All Rights Reserved.
"""
Multi-Agent Gateway v5.0
Hinglish + AI Chat + Image Studio + Video Studio + Learning Agent + Web Research
"""

import streamlit as st
import json
import hashlib
import io
from pathlib import Path
from datetime import datetime
import asyncio

from gateway import APIGateway
from llm_client import chat_with_llm, has_any_llm_key, has_openrouter_key
from image_gen import generate_image_openai, has_openai_image_key, build_image_prompt

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ====================== PATHS ======================
DATA_FILE = Path("data/company_info.json")
USERS_FILE = Path("data/users.json")
LEARNING_FILE = Path("data/learning/memory.json")
IMG_DIR = Path("uploads/images")
VID_DIR = Path("uploads/videos")
ASSETS_DIR = Path("assets")
for d in [IMG_DIR, VID_DIR, ASSETS_DIR, LEARNING_FILE.parent]:
    d.mkdir(parents=True, exist_ok=True)

DEFAULT_USERS = {
    "ceo": {"password_hash": hashlib.sha256("AI Software Innovation Infotech And Hardware Enterprises@CEO2026".encode()).hexdigest(), "role": "Founder & CEO", "name": "Alex Rivera", "full_access": True},
    "priya": {"password_hash": hashlib.sha256("AI Software Innovation Infotech And Hardware Enterprises@CTO2026".encode()).hexdigest(), "role": "CTO", "name": "Priya Sharma", "full_access": True},
    "jordan": {"password_hash": hashlib.sha256("AI Software Innovation Infotech And Hardware Enterprises@Research2026".encode()).hexdigest(), "role": "Head of AI Research", "name": "Jordan Lee", "full_access": True},
    "sam": {"password_hash": hashlib.sha256("AI Software Innovation Infotech And Hardware Enterprises@Product2026".encode()).hexdigest(), "role": "Product Lead", "name": "Sam Patel", "full_access": True},
}

LANGUAGES = {
    "English": "en",
    "Hinglish": "hi-en",
    "Hindi (हिन्दी)": "hi",
    "Spanish": "es", "French": "fr", "German": "de",
    "Chinese": "zh", "Japanese": "ja", "Arabic": "ar",
    "Portuguese": "pt", "Russian": "ru", "Bengali": "bn",
    "Tamil": "ta", "Telugu": "te", "Marathi": "mr", "Gujarati": "gu",
}

SYSTEM_PROMPT = """You are AISIH Multi-Agent AI – smart, helpful, and practical.
You write emails, code, letters, summaries, image prompts, video scripts, and research answers.
If user writes in Hinglish, reply in natural Hinglish (Hindi+English mix).
Be clear and useful."""

def load_json(path, default):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_users():
    u = load_json(USERS_FILE, None)
    if u is None:
        save_json(USERS_FILE, DEFAULT_USERS)
        return DEFAULT_USERS
    return u

def load_company():
    return load_json(DATA_FILE, {})

def save_company(data):
    save_json(DATA_FILE, data)

def check_login(username, password):
    users = load_users()
    if username in users:
        if users[username]["password_hash"] == hashlib.sha256(password.encode()).hexdigest():
            return users[username]
    return None

def load_learning():
    return load_json(LEARNING_FILE, {"lessons": [], "improvements": [], "topics": []})

def save_learning(data):
    save_json(LEARNING_FILE, data)

def run_gateway_simulated(task: str, language: str = "English"):
    if language == "Hinglish":
        task = f"[Reply in natural Hinglish - Hindi English mix] {task}"
    elif language != "English":
        task = f"[Please respond in {language}] {task}"
    gateway = APIGateway()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(gateway.process(task))
        if response.success:
            return response.final_output, response
        return "Agents could not complete this request.", None
    finally:
        loop.close()

def get_ai_reply(user_text: str, history: list, provider: str, language: str) -> str:
    if has_any_llm_key() and provider != "simulated":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if language == "Hinglish":
            messages[0]["content"] += "\nAlways reply in natural Hinglish (Hindi + English mix)."
        elif language != "English":
            messages[0]["content"] += f"\nAlways reply in {language}."
        for m in history[-8:]:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_text})
        result = chat_with_llm(messages, provider=provider)
        if result and not str(result).startswith("[LLM Error"):
            return result
        if result:
            return result
    reply, _ = run_gateway_simulated(user_text, language)
    return reply

def tts_button(text: str, lang_code: str = "en"):
    code = "hi" if lang_code in ("hi", "hi-en") else lang_code
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("'", "\\'")[:600]
    st.components.v1.html(f"""
    <button onclick="speak()" style="background:linear-gradient(90deg,#7c3aed,#8b5cf6);color:white;border:none;border-radius:8px;padding:6px 14px;cursor:pointer;font-size:13px;">🔊 Speak</button>
    <script>
    function speak(){{
        if('speechSynthesis' in window){{
            window.speechSynthesis.cancel();
            const u=new SpeechSynthesisUtterance(`{safe}`);
            u.lang='{code}';
            window.speechSynthesis.speak(u);
        }}
    }}
    </script>
    """, height=40)

# ====================== UI SETUP ======================
st.set_page_config(page_title="AISIH Gateway v5.0 | Chat + Image + Video + Learning", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.main-header{background:linear-gradient(90deg,#0f172a,#1e1b4b);padding:1rem 1.4rem;border-radius:12px;margin-bottom:1rem;border:1px solid #8b5cf6;}
.stButton>button{background:linear-gradient(90deg,#7c3aed,#8b5cf6);color:white;border:none;border-radius:8px;}
.tool-card{background:#1e293b;padding:1rem;border-radius:10px;border:1px solid #334155;margin-bottom:0.8rem;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "Hinglish"
if "provider" not in st.session_state:
    st.session_state.provider = "auto"

# ====================== SIDEBAR ======================
with st.sidebar:
    try:
        st.image("assets/logo.svg", width=180)
    except Exception:
        st.markdown("### 🚀 AISIH")
    st.markdown("### AISIH Gateway **v5.0**")
    st.caption("Chat • Image • Video • Learning • Research")
    st.divider()

    menu = st.radio("Nav", [
        "🏠 Home (AI Chat)",
        "🖼️ Image Studio",
        "🎬 Video Studio",
        "🧠 Learning Agent",
        "🌐 Web Research",
        "🤖 Multi-Agent System",
        "📄 About Us",
        "🔐 Admin Login",
        "⚙️ Admin Panel",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**🌐 Language**")
    lang_name = st.selectbox("Lang", list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.language) if st.session_state.language in LANGUAGES else 1,
        label_visibility="collapsed")
    st.session_state.language = lang_name
    lang_code = LANGUAGES.get(lang_name, "en")

    st.markdown("**🧠 AI Provider**")
    st.session_state.provider = st.selectbox(
        "Provider",
        ["auto", "openrouter", "openai", "anthropic", "xai", "simulated"],
        help="OpenRouter free models: Secrets mein OPENROUTER_API_KEY daalo (sk-or-v1-...)"
    )

    if has_openrouter_key():
        st.success("✅ OpenRouter key found (free models OK)")
    elif has_any_llm_key():
        st.success("✅ LLM key found")
    else:
        st.warning("No API key → simulated mode. Free: OPENROUTER_API_KEY in Secrets")

    st.divider()
    if st.session_state.logged_in:
        st.success(st.session_state.user["name"])
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    else:
        st.caption("Admin login for full panel")

# ====================== HOME AI CHAT ======================
if menu == "🏠 Home (AI Chat)":
    company = load_company()
    st.markdown(f"""
    <div class="main-header">
        <h2 style="color:white;margin:0;">🚀 {company.get('company_name', 'AISIH Multi-Agent Gateway v5.0')}</h2>
        <p style="color:#a78bfa;margin:0.2rem 0 0 0;">AI Chat • Hinglish • Image • Video • Learning</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Language: **{st.session_state.language}** | Provider: **{st.session_state.provider}**")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                tts_button(msg["content"], lang_code)

    with st.expander("🎤 Voice Input"):
        audio = st.audio_input("Record")
        if audio:
            st.audio(audio)
            vt = st.text_input("Jo bola wo type/paste karo")
            if vt and st.button("Send Voice"):
                st.session_state.messages.append({"role": "user", "content": vt})
                reply = get_ai_reply(vt, st.session_state.messages[:-1], st.session_state.provider, st.session_state.language)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

    if prompt := st.chat_input("Hinglish / English mein kuch bhi poocho..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Soch raha hoon..."):
                reply = get_ai_reply(prompt, st.session_state.messages[:-1], st.session_state.provider, st.session_state.language)
                st.markdown(reply)
                tts_button(reply, lang_code)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    if st.session_state.messages and st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ====================== IMAGE STUDIO ======================
elif menu == "🖼️ Image Studio":
    st.header("🖼️ Image Studio")
    st.caption("Upload • Edit • AI Image Prompt / Create idea")

    tab1, tab2, tab3 = st.tabs(["Upload & Edit", "AI Image Create", "Gallery"])

    with tab1:
        up = st.file_uploader("Image upload karo (PNG/JPG)", type=["png", "jpg", "jpeg", "webp"])
        if up:
            if HAS_PIL:
                img = Image.open(up)
                st.image(img, caption="Original", use_container_width=True)
                c1, c2, c3 = st.columns(3)
                bright = c1.slider("Brightness", 0.5, 1.5, 1.0)
                contrast = c2.slider("Contrast", 0.5, 1.5, 1.0)
                blur = c3.slider("Blur", 0, 5, 0)
                edited = ImageEnhance.Brightness(img).enhance(bright)
                edited = ImageEnhance.Contrast(edited).enhance(contrast)
                if blur > 0:
                    edited = edited.filter(ImageFilter.GaussianBlur(blur))
                if st.checkbox("Grayscale"):
                    edited = ImageOps.grayscale(edited).convert("RGB")
                st.image(edited, caption="Edited", use_container_width=True)
                buf = io.BytesIO()
                edited.save(buf, format="PNG")
                st.download_button("⬇️ Download edited", buf.getvalue(), "edited.png", "image/png")
                if st.button("Save to uploads"):
                    path = IMG_DIR / f"edit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    edited.save(path)
                    st.success(f"Saved: {path}")
            else:
                st.image(up)
                st.warning("Pillow not installed – only preview")

    with tab2:
        st.subheader("AI Image Create (OpenAI DALL·E)")
        if has_openai_image_key():
            st.success("✅ OPENAI_API_KEY mil gaya – real image generate ho sakti hai")
        else:
            st.warning("⚠️ OPENAI_API_KEY nahi hai. Streamlit Secrets mein add karo. Abhi prompt + concept milenge.")

        idea = st.text_area("Kya image chahiye? (Hinglish / English OK)", placeholder="girl in school uniform, smiling, classroom background")
        style = st.selectbox("Style", ["Realistic", "Anime", "3D Render", "Oil Painting", "Sketch", "Product Photo", "Cinematic"])
        size = st.selectbox("Size", ["1024x1024", "1024x1792 (portrait)", "1792x1024 (landscape)"])
        size_api = size.split()[0]

        col_a, col_b = st.columns(2)
        with col_a:
            do_real = st.button("🎨 Generate REAL Image (DALL·E)", type="primary", disabled=not has_openai_image_key())
        with col_b:
            do_prompt = st.button("📝 Only make Prompt (free)")

        if do_prompt or (do_real and idea.strip()):
            final_prompt = build_image_prompt(idea.strip() or "a girl in school uniform", style)
            st.markdown("### Prompt used")
            st.code(final_prompt)

        if do_prompt and idea.strip():
            with st.spinner("Prompt bana raha hoon..."):
                out = get_ai_reply(
                    f"Create a detailed image generation prompt for: {idea}. Style: {style}. Make it ready for DALL-E or Midjourney. Output only the final prompt text.",
                    [], st.session_state.provider, st.session_state.language
                )
            st.markdown(out)
            tts_button(out, lang_code)

        if do_real and idea.strip() and has_openai_image_key():
            with st.spinner("DALL·E image bana raha hai... 10–30 sec lag sakte hain"):
                img_bytes, err = generate_image_openai(final_prompt, size=size_api)
            if err:
                st.error(f"Error: {err}")
            elif img_bytes:
                st.image(img_bytes, caption="AI Generated Image", use_container_width=True)
                st.download_button("⬇️ Download PNG", img_bytes, "ai_image.png", "image/png")
                # optional save
                from datetime import datetime as _dt
                path = IMG_DIR / f"ai_{_dt.now().strftime('%Y%m%d_%H%M%S')}.png"
                path.write_bytes(img_bytes)
                st.success(f"Saved to {path}")
            else:
                st.error("Image nahi bani")

    with tab3:
        files = list(IMG_DIR.glob("*"))
        if not files:
            st.write("Abhi koi saved image nahi.")
        else:
            for f in files[-12:]:
                try:
                    st.image(str(f), caption=f.name, width=200)
                except Exception:
                    st.write(f.name)

# ====================== VIDEO STUDIO ======================
elif menu == "🎬 Video Studio":
    st.header("🎬 Video Studio")
    st.caption("Upload • AI Video Script • YouTube Search helper • Ideas")

    t1, t2, t3, t4 = st.tabs(["Upload Video", "AI Video Content", "YouTube Search", "Download Tips"])

    with t1:
        vup = st.file_uploader("Video upload (mp4/mov/webm)", type=["mp4", "mov", "webm", "avi"])
        if vup:
            st.video(vup)
            path = VID_DIR / f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{vup.name}"
            if st.button("Save video to server"):
                with open(path, "wb") as f:
                    f.write(vup.getbuffer())
                st.success(f"Saved: {path}")
        st.caption("Full timeline video editor Streamlit pe limited hai – heavy editing ke liye CapCut/DaVinci use karo. Yahan AI script + ideas milte hain.")

    with t2:
        topic = st.text_input("Video topic", placeholder="AI se paise kaise kamaye 2026")
        length = st.selectbox("Length", ["15 sec (Reel)", "60 sec", "3 min", "8 min YouTube"])
        tone = st.selectbox("Tone", ["Educational", "Funny", "Motivational", "Professional", "Hinglish casual"])
        if st.button("🎥 AI Video Script + Shot List"):
            q = f"Write a complete video script and shot list for topic: {topic}. Length: {length}. Tone: {tone}. Include hook, body, CTA. Hinglish if needed."
            with st.spinner("Script bana raha hoon..."):
                out = get_ai_reply(q, [], st.session_state.provider, st.session_state.language)
            st.markdown(out)
            tts_button(out, lang_code)

    with t3:
        st.subheader("YouTube Search Helper")
        yt_q = st.text_input("Search keyword", placeholder="best AI tools 2026")
        if yt_q:
            link = f"https://www.youtube.com/results?search_query={yt_q.replace(' ', '+')}"
            st.markdown(f"**Open YouTube search:** [{yt_q}]({link})")
            st.info("Related topics AI se nikaalte hain:")
            if st.button("Related topics + content ideas"):
                out = get_ai_reply(f"Suggest 8 related YouTube video topics and short titles for: {yt_q}. Also 3 content ideas.", [], st.session_state.provider, st.session_state.language)
                st.markdown(out)

    with t4:
        st.markdown("""
        **Video download note:**  
        YouTube se direct download copyright / ToS issue ho sakta hai.  
        Apne videos upload/download yahan se kar sakte ho.  
        Public videos ke liye official apps / yt-dlp (local) use karo – Streamlit Cloud pe restricted.
        """)
        st.download_button("Sample placeholder note", "Use local tools for bulk YouTube download.", "note.txt")

# ====================== LEARNING AGENT ======================
elif menu == "🧠 Learning Agent":
    st.header("🧠 Learning AI Agent")
    st.caption("Sub-tasks seekhta hai • Notes save karta hai • Self-improvement list banata hai")

    mem = load_learning()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Lessons saved", len(mem.get("lessons", [])))
    with col2:
        st.metric("Improvement notes", len(mem.get("improvements", [])))

    lesson = st.text_area("Naya lesson / jo seekha", placeholder="User ko email formal tone mein likhna pasand hai")
    if st.button("💾 Save Lesson"):
        mem.setdefault("lessons", []).append({"text": lesson, "time": datetime.now().isoformat()})
        save_learning(mem)
        st.success("Lesson saved – agent next time use kar sakta hai")

    improve = st.text_input("Self-improvement note", placeholder="Zyada short answers do")
    if st.button("Add Improvement"):
        mem.setdefault("improvements", []).append({"text": improve, "time": datetime.now().isoformat()})
        save_learning(mem)
        st.success("Added")

    task = st.text_input("Learning task (sub-tasks banao)", placeholder="Blog post likhna seekho")
    if st.button("🧩 Break into sub-tasks + learn plan"):
        q = f"Break this learning goal into clear sub-tasks and a self-improvement plan: {task}. Reply in Hinglish if user prefers."
        out = get_ai_reply(q, [], st.session_state.provider, st.session_state.language)
        st.markdown(out)
        mem.setdefault("topics", []).append({"task": task, "plan": out[:500], "time": datetime.now().isoformat()})
        save_learning(mem)

    with st.expander("📚 Saved memory"):
        st.json(mem)

    st.info("True model fine-tuning continuous training cloud pe alag infrastructure maangta hai. Yahan memory + sub-task learning store hota hai jo prompts mein use ho sakta hai.")

# ====================== WEB RESEARCH ======================
elif menu == "🌐 Web Research":
    st.header("🌐 Web Research Agent")
    st.caption("Related topics • Info collection plan • Task complete karne ka structure")

    query = st.text_input("Research topic / task", placeholder="Best ways to deploy Streamlit apps 2026")
    if st.button("🔍 Research plan + related topics"):
        q = f"""For the topic/task: {query}
1. List 8 related search topics
2. Give a step-by-step information collection plan
3. Summarize what a good final answer should contain
4. Suggest sources types (docs, blogs, official sites)
Reply clearly. Hinglish OK if needed."""
        with st.spinner("Research plan bana raha hoon..."):
            out = get_ai_reply(q, [], st.session_state.provider, st.session_state.language)
        st.markdown(out)
        tts_button(out, lang_code)
        st.markdown("---")
        st.markdown(f"**Google search:** [Open](https://www.google.com/search?q={query.replace(' ', '+')})")
        st.caption("Live web scrape ke liye Serper/Google CSE API key add kar sakte ho. Abhi AI research plan + related topics milte hain.")

# ====================== MULTI-AGENT ======================
elif menu == "🤖 Multi-Agent System":
    st.header("🤖 Multi-Agent System")
    task = st.text_area("Task", height=100, placeholder="Email likho / code likho / research karo...")
    use_real = st.checkbox("Real LLM use karo (agar key hai)", value=has_any_llm_key())
    if st.button("🚀 Run"):
        if not task.strip():
            st.warning("Task likho")
        else:
            with st.spinner("Agents..."):
                if use_real and has_any_llm_key() and st.session_state.provider != "simulated":
                    out = get_ai_reply(task, [], st.session_state.provider, st.session_state.language)
                    st.markdown(out)
                else:
                    out, resp = run_gateway_simulated(task, st.session_state.language)
                    st.markdown(out)
                    if resp:
                        st.caption(f"Confidence: {resp.confidence:.0%} | {resp.total_time_ms:.0f} ms")

# ====================== ABOUT ======================
elif menu == "📄 About Us":
    company = load_company()
    st.markdown(f"""
    <div class="main-header"><h2 style="color:white;margin:0;">{company.get('company_name', 'AISIH')}</h2>
    <p style="color:#a78bfa;">{company.get('tagline', '')}</p></div>
    """, unsafe_allow_html=True)
    st.write(company.get("about", ""))
    ceo = company.get("founder_ceo", {})
    st.subheader("CEO")
    st.write(f"**{ceo.get('name', '')}** — {ceo.get('title', '')}")
    st.write(ceo.get("bio", ""))

# ====================== ADMIN ======================
elif menu == "🔐 Admin Login":
    st.header("Admin Login")
    if st.session_state.logged_in:
        st.success(st.session_state.user["name"])
    else:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = check_login(u, p)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Wrong credentials")
        st.caption("ceo / AI Software Innovation Infotech And Hardware Enterprises@CEO2026")

elif menu == "⚙️ Admin Panel":
    if not st.session_state.logged_in:
        st.warning("Login first")
        st.stop()
    st.header("Admin Panel")
    company = load_company()
    name = st.text_input("Company", value=company.get("company_name", ""))
    tag = st.text_input("Tagline", value=company.get("tagline", ""))
    about = st.text_area("About", value=company.get("about", ""))
    if st.button("Save"):
        company["company_name"] = name
        company["tagline"] = tag
        company["about"] = about
        save_company(company)
        st.success("Saved")

st.markdown("---")
st.caption("© 2026 AI Software Innovation Infotech And Hardware Enterprises | Gateway v5.0")

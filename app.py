import streamlit as st
from router import LLMRouter

# -------------------- PAGE CONFIG -------------------- #
st.set_page_config(
    page_title="Sentinel LLM Reliability Console",
    page_icon="🛰️",
    layout="wide"
)

# -------------------- GLOBAL STYLES -------------------- #
st.markdown(
    """
    <style>
        /* Global background */
        .main {
            background: radial-gradient(circle at top, #1f2937 0, #020617 55%, #000000 100%);
            color: #e5e7eb;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            max-width: 1100px;
        }
        /* Card look */
        .card {
            background: rgba(15,23,42,0.9);
            border-radius: 18px;
            padding: 1.25rem 1.4rem;
            border: 1px solid rgba(148,163,184,0.35);
            box-shadow: 0 18px 45px rgba(0,0,0,0.55);
        }
        .card-soft {
            background: rgba(15,23,42,0.7);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            border: 1px solid rgba(75,85,99,0.65);
        }
        .app-title {
            font-size: 1.9rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.03em;
        }
        .app-subtitle {
            font-size: 0.95rem;
            color: #9ca3af;
        }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: linear-gradient(120deg,#22d3ee,#6366f1);
            color: #020617;
        }
        .model-tag {
            display: inline-flex;
            align-items: center;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            background: rgba(31,41,55,0.9);
            border: 1px solid rgba(148,163,184,0.4);
            color: #e5e7eb;
        }
        .model-tag span {
            opacity: 0.9;
        }
        .metric-label {
            font-size: 0.75rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.15rem;
        }
        .metric-value {
            font-size: 1rem;
            font-weight: 600;
            color: #e5e7eb;
        }
        .routing-label {
            font-size: 0.8rem;
            color: #9ca3af;
            margin-bottom: 0.25rem;
        }
        /* Sidebar tweaks */
        section[data-testid="stSidebar"] {
            background: #020617;
            border-right: 1px solid rgba(55,65,81,0.7);
        }
        /* Chat tweaks (subtle) */
        [data-testid="stChatMessage"] {
            border-radius: 16px;
            padding: 0.8rem 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- ROUTER (CACHED) -------------------- #
@st.cache_resource
def get_router():
    return LLMRouter()

router = get_router()

# -------------------- MODEL NAME HELPERS -------------------- #
MODEL_PRETTY = {
    "groq/llama-3.3-70b-specdec": "Groq · Llama 3.3 70B",
    "groq/llama-3.1-8b-instant": "Groq · Llama 3.1 8B Instant",
    "gemini/gemini-1.5-flash": "Gemini · 1.5 Flash",
    "gemini/gemini-2.0-flash": "Gemini · 2.0 Flash",
    "gemini/gemini-2.0-pro": "Gemini · 2.0 Pro",
}

def pretty_model(model_id: str) -> str:
    return MODEL_PRETTY.get(model_id, model_id)

# -------------------- SIDEBAR: CONTROLS -------------------- #
st.sidebar.markdown("### 🛰️ Sentinel Console")
st.sidebar.caption("Operational controls for your fault-tolerant LLM gateway.")

# Routing mode selector
routing_mode = st.sidebar.selectbox(
    "Routing strategy",
    [
        "Auto · Failover (Primary → Backup)",
        "Primary only",
        "Backup only",
    ],
    help="Define how requests are routed between the two models."
)

st.sidebar.markdown("---")

temperature = st.sidebar.slider(
    "Temperature (creativity)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.05,
)

max_tokens = st.sidebar.number_input(
    "Max tokens",
    min_value=50,
    max_value=2000,
    value=500,
    step=50,
)

st.sidebar.markdown("---")

# Swap button – clearly named
if st.sidebar.button("↔️ Swap primary ↔ backup"):
    router.primary_model, router.backup_model = router.backup_model, router.primary_model
    st.sidebar.success("Roles updated: primary and backup have been swapped.")

st.sidebar.markdown("#### Model roles")

st.sidebar.markdown(
    f"""
    <div class="card-soft">
        <div class="metric-label">Primary</div>
        <div class="metric-value">{pretty_model(router.primary_model)}</div>
        <br>
        <div class="metric-label">Backup</div>
        <div class="metric-value">{pretty_model(router.backup_model)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.caption("Swap roles or tune temperature/max tokens to experiment with behavior.")

# -------------------- MAIN HEADER -------------------- #
top_col1, top_col2 = st.columns([0.68, 0.32])

with top_col1:
    st.markdown(
        """
        <div class="card">
            <div class="pill">Sentinel · Reliability Layer</div>
            <div style="margin-top:0.6rem;" class="app-title">
                Sentinel LLM Reliability Console
            </div>
            <div class="app-subtitle" style="margin-top:0.3rem;">
                A control plane for resilient inference — automatic retries, graceful failover,
                and transparent observability across your primary and backup LLMs.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_col2:
    st.markdown(
        f"""
        <div class="card">
            <div class="routing-label">Active routing strategy</div>
            <div style="margin-bottom:0.8rem;">
                <span class="model-tag">
                    <span>⚙️ {routing_mode}</span>
                </span>
            </div>
            <div class="routing-label">Current configuration</div>
            <div style="display:flex; flex-direction:column; gap:0.35rem;">
                <div>
                    <span class="model-tag"><span>Primary</span></span>
                    <span style="margin-left:0.4rem;">{pretty_model(router.primary_model)}</span>
                </div>
                <div>
                    <span class="model-tag"><span>Backup</span></span>
                    <span style="margin-left:0.4rem;">{pretty_model(router.backup_model)}</span>
                </div>
            </div>
            <div style="margin-top:0.9rem; display:flex; gap:1rem;">
                <div>
                    <div class="metric-label">Temperature</div>
                    <div class="metric-value">{temperature}</div>
                </div>
                <div>
                    <div class="metric-label">Max tokens</div>
                    <div class="metric-value">{max_tokens}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# -------------------- CHAT HISTORY INITIALIZATION -------------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------- CHAT HISTORY RENDER -------------------- #
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# -------------------- ROUTING HELPERS -------------------- #
def route_request(prompt: str):
    """
    Routes a prompt according to the selected routing mode.
    Returns a dict with keys: content, model_used, status.
    """
    messages = [{"role": "user", "content": prompt}]

    # Auto mode uses the router's built-in failover
    if routing_mode.startswith("Auto"):
        return router.generate_response(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # Primary only
    if routing_mode.startswith("Primary"):
        raw = router._call_llm(  # using the helper defined in LLMRouter
            router.primary_model,
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = raw["choices"][0]["message"]["content"]
        return {
            "content": content,
            "model_used": router.primary_model,
            "status": "success",
        }

    # Backup only
    raw = router._call_llm(
        router.backup_model,
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = raw["choices"][0]["message"]["content"]
    return {
        "content": content,
        "model_used": router.backup_model,
        "status": "success",
    }

# -------------------- CHAT INPUT + HANDLER -------------------- #
prompt = st.chat_input("Type a message to send through the Sentinel gateway…")

if prompt:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant slot
    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        status_placeholder = st.empty()

        with st.spinner("Coordinating with models via Sentinel…"):
            result = route_request(prompt)

        response_text = result["content"]
        msg_placeholder.markdown(response_text)

        used_model_pretty = pretty_model(result["model_used"])

        # Status line – clear & professional
        if result["status"] == "success" and routing_mode.startswith("Auto"):
            status_placeholder.markdown(
                f"✅ Served by **primary** model: `{used_model_pretty}`"
            )
        elif result["status"] == "success":
            status_placeholder.markdown(
                f"✅ Served by `{used_model_pretty}` "
                f"using strategy **{routing_mode}**"
            )
        elif result["status"] == "fallback_success":
            status_placeholder.markdown(
                f"🛡️ Failover engaged. Primary failed, response served by **backup** model: "
                f"`{used_model_pretty}`"
            )
        else:
            status_placeholder.error("❌ All routes failed. Both primary and backup models returned errors.")

        # Persist assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

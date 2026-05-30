"""
Prism AI — Multimodal Intelligence Platform
Claude.ai-style UI: dark sidebar + light chat area
"""

import streamlit as st
import streamlit.components.v1 as components
import os, base64, io, tempfile, json
import html as _html
from datetime import datetime, timezone
from pathlib import Path

st.set_page_config(
    page_title="Prism AI",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  PREMIUM CSS
# ─────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

:root {
  --sb-bg:        #1C1917;
  --sb-surface:   #292524;
  --sb-hover:     #333029;
  --sb-border:    rgba(255,255,255,0.07);
  --sb-text-hi:   #F5F5F4;
  --sb-text-md:   #A8A29E;
  --sb-text-lo:   #57534E;
  --main-bg:      #FAFAF8;
  --main-surface: #FFFFFF;
  --main-hover:   #F4F2EE;
  --main-border:  #E7E5E0;
  --main-border2: #D1CBC0;
  --accent:       #D4915A;
  --accent-dark:  #B5733A;
  --accent-light: #FDF0E6;
  --accent-glow:  rgba(212,145,90,0.18);
  --txt-hi:   #1C1917;
  --txt-md:   #57534E;
  --txt-lo:   #A8A29E;
  --txt-ph:   #C5BDB5;
  --green:    #22C55E;
  --red:      #EF4444;
  --font:  'DM Sans',  -apple-system, sans-serif;
  --mono:  'DM Mono',  monospace;
  --r2:4px; --r4:8px; --r6:12px; --r8:16px; --r10:20px; --rpill:999px;
  --sh1: 0 1px 4px rgba(0,0,0,0.08);
  --sh2: 0 4px 16px rgba(0,0,0,0.1);
  --sh3: 0 8px 32px rgba(0,0,0,0.13);
}

*, *::before, *::after { box-sizing: border-box; }
/* H-B2 fix: Apply DM Sans EXCEPT to Streamlit/Material icon spans.
   Recent Streamlit versions tag icons with data-testid="stIconMaterial"
   (not a class containing "material-symbols"), so the previous class-only
   selector didn't match and ligatures (`upload`, `keyboard_arrow_down`,
   etc.) kept leaking as raw text. Cover both naming conventions here. */
*:not([class*="material-symbols"]):not([class*="material-icons"]):not([data-testid*="Icon"]):not([data-testid*="Material"]) {
  font-family: var(--font) !important;
}
code, pre, kbd { font-family: var(--mono) !important; }

/* Re-assert the Material Symbols font on icon elements wherever Streamlit
   identifies them. Covers data-testid AND class-based variants. */
[class*="material-symbols"],
[class*="material-icons"],
[data-testid="stIconMaterial"],
[data-testid="stMaterialIcon"],
[data-testid="stIcon"],
.material-symbols-rounded,
.material-symbols-outlined,
.material-symbols-sharp,
.material-icons {
  font-family: 'Material Symbols Rounded', 'Material Icons' !important;
  font-feature-settings: 'liga' !important;
  -webkit-font-feature-settings: 'liga' !important;
  font-variant-ligatures: contextual !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
  font-weight: normal !important;
  font-style: normal !important;
  white-space: nowrap !important;
  direction: ltr !important;
}

/* H-B2 ultimate guard: unconditionally hide ALL icon-like elements inside
   the file uploader. Even if H-B2 (font-load) ever fails again — corporate
   proxy strips Google Fonts, ad-blocker, CSP — no ligature text can leak
   onto the Browse files button, because the icon element itself is gone.
   Trade-off: no cloud_upload glyph is shown, but the button text is
   self-explanatory and this guarantees the bug never resurfaces. */
[data-testid="stFileUploader"] [data-testid*="Icon"],
[data-testid="stFileUploader"] [data-testid*="Material"],
[data-testid="stFileUploaderDropzone"] [data-testid*="Icon"],
[data-testid="stFileUploaderDropzone"] [data-testid*="Material"],
[data-testid="stFileUploader"] [class*="material-symbols"],
[data-testid="stFileUploader"] [class*="material-icons"],
[data-testid="stFileUploaderDropzoneInstructions"] [data-testid*="Icon"],
[data-testid="stFileUploaderDropzoneInstructions"] [class*="material-symbols"],
section[data-testid="stFileUploaderDropzone"] > div > span:first-child {
  display: none !important;
}

#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton { display: none !important; }

/* ── Single-page lock (H-C fix) ─────────────────────────────
   Pin html/body/.stApp to the viewport so the document does not
   scroll. Sidebar and main column each scroll independently. */
html, body {
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}
.stApp {
  background: var(--main-bg) !important;
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}
[data-testid="stAppViewContainer"] {
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}
[data-testid="stMain"], .main {
  height: 100vh !important;
  max-height: 100vh !important;
  overflow-y: auto !important;
}
.main > .block-container {
  max-width: 820px !important;
  margin: 0 auto !important;
  /* Bottom padding clears the JS-pinned uploader (~100px tall at
     bottom:88px) AND the fixed chat input (~70px at bottom:0). */
  padding: 0.4rem 1.2rem 13rem !important;
}

/* ═══ INLINE-ATTACH MODE ═══
   The Cursor-style "paperclip inside the chat input" UX is built on top
   of the existing st.file_uploader widget for older Streamlit (<1.42)
   that doesn't expose accept_file on st.chat_input. Mechanics:
   1. The file_uploader itself is moved off-screen (it stays mounted, so
      its <input type="file"> is still in the DOM and triggerable via
      JS .click() — that's the call that opens the OS file picker).
   2. A paperclip <button> is created at <body> level and positioned via
      JS to visually sit inside the chat-input bar, just left of the send
      button. Clicking it calls .click() on the hidden file input.
   3. When a file is selected, Streamlit reruns and main() renders an
      attached-file chip (.inline-attach-chip) just above the chat input. */
[data-testid="stChatInput"] {
  z-index: 60 !important;
}
[data-testid="stFileUploader"] {
  /* Visually hidden but still functional (input.click() works). The
     ".sr-only" pattern: 1px box, hidden overflow, off-screen-friendly. */
  position: absolute !important;
  left: -10000px !important;
  top: 0 !important;
  width: 1px !important;
  height: 1px !important;
  overflow: hidden !important;
  z-index: -1 !important;
  opacity: 0 !important;
  pointer-events: none !important;
}
.inline-attach-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #FEF3C7;
  border: 1px solid #FCD34D;
  color: #92400E;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  margin: 6px 0 4px;
  max-width: 70%;
}
.inline-attach-chip .x {
  opacity: 0.6;
  font-size: 0.7rem;
}

/* Upload button glyph — outline tray + up-arrow per user-supplied design.
   Implemented as an inlined SVG background-image so the icon doesn't
   depend on any web font loading, doesn't get stripped by Streamlit's
   icon-hide rules, and isn't affected by the global DM Sans override.
   Notes from prior debug rounds:
     - The data URI mime is now `image/svg+xml,` (no `;utf8` parameter)
       because some browsers/proxies treated the non-standard `utf8`
       parameter as invalid and silently dropped the image.
     - Size is fixed to 18px (not em-based) so the icon is consistently
       visible regardless of the button's inherited font-size.
     - Vertical alignment uses `text-bottom` + a small translate so the
       icon's optical center matches the button text's optical center. */
section[data-testid="stFileUploaderDropzone"] button::before,
[data-testid="stFileUploaderDropzone"] button::before,
[data-testid="stFileUploader"] button[kind="secondary"]::before {
  content: '';
  display: inline-block;
  width: 18px;
  height: 18px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpolyline points='17 8 12 3 7 8'/%3E%3Cline x1='12' y1='3' x2='12' y2='15'/%3E%3C/svg%3E") !important;
  background-repeat: no-repeat !important;
  background-size: contain !important;
  background-position: center !important;
  margin-right: 8px;
  vertical-align: text-bottom;
  transform: translateY(-2px);
  flex-shrink: 0;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--main-border2); border-radius: 4px; }

/* ═══ SIDEBAR ════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--sb-bg) !important;
  border-right: 1px solid var(--sb-border) !important;
  width: 288px !important;
  min-width: 288px !important;
  max-width: 288px !important;
  transform: none !important;
  visibility: visible !important;
  display: flex !important;
  opacity: 1 !important;
  left: 0 !important;
}
[data-testid="stSidebarCollapseButton"],
button[title="Close sidebar"],
button[aria-label="Close sidebar"],
button[aria-label="Collapse sidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"] button {
  display: none !important;
  pointer-events: none !important;
}
[data-testid="stSidebar"] > div:first-child { width: 288px !important; min-width: 288px !important; }
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebarContent"] { padding: 0 !important; overflow-y: auto; height: 100%; }

/* Sidebar inputs */
[data-testid="stSidebar"] .stTextInput > div > div > input {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: var(--r4) !important;
  color: var(--sb-text-hi) !important;
  font-size: 0.83rem !important;
  padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
  outline: none !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
  color: var(--sb-text-lo) !important;
}
[data-testid="stSidebar"] .stTextInput > label {
  color: var(--sb-text-lo) !important;
  font-size: 0.63rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}

/* Sidebar sliders */
[data-testid="stSidebar"] [data-testid="stSlider"] label {
  color: var(--sb-text-lo) !important;
  font-size: 0.63rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
  background: var(--accent) !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] p {
  color: var(--sb-text-md) !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: var(--sb-text-md) !important;
  border-radius: var(--r4) !important;
  font-size: 0.77rem !important;
  font-weight: 500 !important;
  padding: 0.45rem 1rem !important;
  width: 100% !important;
  transition: all 0.18s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.09) !important;
  color: var(--sb-text-hi) !important;
  border-color: rgba(255,255,255,0.16) !important;
}
[data-testid="stSidebar"] [data-testid="stDownloadButton"] > button {
  background: rgba(212,145,90,0.12) !important;
  border: 1px solid rgba(212,145,90,0.25) !important;
  color: #F5C69A !important;
  font-size: 0.77rem !important;
  width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stDownloadButton"] > button:hover {
  background: rgba(212,145,90,0.2) !important;
}

/* ═══ CHAT INPUT ═════════════════════════════════════════════ */
[data-testid="stChatInput"] {
  background: var(--main-surface) !important;
  border: 1.5px solid var(--main-border2) !important;
  border-radius: var(--r10) !important;
  box-shadow: var(--sh2) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow), var(--sh2) !important;
}
[data-testid="stChatInput"] textarea {
  color: var(--txt-hi) !important;
  font-size: 0.94rem !important;
  background: transparent !important;
  caret-color: var(--accent) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--txt-ph) !important; }
[data-testid="stChatInput"] button[kind="primary"] {
  background: var(--accent) !important;
  border: none !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 8px rgba(212,145,90,0.4) !important;
}
[data-testid="stChatInput"] button[kind="primary"]:hover {
  background: var(--accent-dark) !important;
}

/* ═══ CHAT MESSAGES ══════════════════════════════════════════ */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 2px 0 !important;
  animation: fadeUp 0.2s cubic-bezier(.22,1,.36,1) !important;
}
@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0); }
}
[data-testid="stChatMessage"]:has([aria-label="assistant avatar"]) > div:nth-child(2) {
  background: var(--main-surface) !important;
  border: 1px solid var(--main-border) !important;
  border-radius: 4px 18px 18px 18px !important;
  padding: 14px 18px !important;
  box-shadow: var(--sh1) !important;
}
[data-testid="stChatMessage"] .stMarkdown p,
[data-testid="stChatMessage"] .stMarkdown li,
[data-testid="stChatMessage"] .stMarkdown span {
  /* Must match user-bubble inline font-size (0.92rem) so AI and user
     messages are visually the same size. line-height matches the user
     bubble (1.72) too — the previous 1.82 made AI lines feel taller. */
  color: var(--txt-hi) !important; line-height: 1.72 !important; font-size: 0.92rem !important;
}
[data-testid="stChatMessage"] .stMarkdown h1,
[data-testid="stChatMessage"] .stMarkdown h2,
[data-testid="stChatMessage"] .stMarkdown h3 {
  color: var(--txt-hi) !important; font-weight: 600 !important;
}
[data-testid="stChatMessage"] .stMarkdown code {
  background: #F0EDE8 !important; color: #92400E !important;
  border-radius: 4px !important; padding: 2px 6px !important;
  font-size: 0.84em !important; border: 1px solid var(--main-border) !important;
}
[data-testid="stChatMessage"] .stMarkdown pre {
  background: #F7F5F2 !important; border: 1px solid var(--main-border) !important;
  border-radius: var(--r6) !important; padding: 14px !important;
}
[data-testid="stChatMessage"] .stMarkdown pre code {
  background: transparent !important; color: var(--txt-hi) !important;
  border: none !important; padding: 0 !important;
}
[data-testid="stChatMessage"] .stMarkdown blockquote {
  border-left: 3px solid var(--accent) !important;
  padding: 8px 14px !important;
  background: var(--accent-light) !important;
  border-radius: 0 var(--r4) var(--r4) 0 !important;
  color: var(--txt-md) !important;
}
[data-testid="stChatMessage"] .stMarkdown a { color: var(--accent-dark) !important; }
[data-testid="stChatMessage"] .stMarkdown table { border-collapse: collapse !important; width: 100% !important; }
[data-testid="stChatMessage"] .stMarkdown th {
  background: var(--main-hover) !important; color: var(--txt-hi) !important;
  padding: 8px 12px !important; border: 1px solid var(--main-border) !important;
  font-weight: 600 !important;
}
[data-testid="stChatMessage"] .stMarkdown td {
  color: var(--txt-hi) !important; padding: 8px 12px !important;
  border: 1px solid var(--main-border) !important;
}

.stCaption, [data-testid="caption"] { color: var(--txt-lo) !important; font-size: 0.72rem !important; }
[data-testid="stAlert"] {
  background: #FEF2F2 !important; border: 1px solid #FCA5A5 !important;
  border-left: 3px solid var(--red) !important; border-radius: var(--r6) !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] div { color: #7F1D1D !important; }

/* AI alert text must match user-bubble font-size (0.92rem). Without this
   rule Streamlit's default stAlert paragraphs inherit ~1rem (16px), which
   makes the AI's "Groq API key required" warning look visibly larger than
   the user's typed message bubble (rendered at 0.92rem via inline style).
   Also covers stAlertContainer used in newer Streamlit versions. */
[data-testid="stChatMessage"] [data-testid="stAlert"],
[data-testid="stChatMessage"] [data-testid="stAlert"] p,
[data-testid="stChatMessage"] [data-testid="stAlert"] div,
[data-testid="stChatMessage"] [data-testid="stAlert"] span,
[data-testid="stChatMessage"] [data-testid="stAlertContainer"],
[data-testid="stChatMessage"] [data-testid="stAlertContainer"] p,
[data-testid="stChatMessage"] [data-testid="stAlertContainer"] div,
[data-testid="stChatMessage"] [data-testid="stAlertContainer"] span {
  font-size: 0.92rem !important;
  line-height: 1.72 !important;
}

[data-testid="stFileUploader"] {
  background: var(--main-surface) !important;
  border: 1.5px dashed var(--main-border2) !important;
  border-radius: var(--r6) !important; transition: all 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important; background: var(--accent-light) !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small { color: var(--txt-md) !important; font-size: 0.78rem !important; }
[data-testid="stFileUploader"] section { padding: 8px !important; }

[data-testid="stImage"] img {
  border-radius: var(--r6) !important; box-shadow: var(--sh2) !important;
  border: 1px solid var(--main-border) !important;
}
audio { border-radius: var(--r4) !important; width: 100% !important; }
hr { border: none !important; border-top: 1px solid var(--main-border) !important; margin: 4px 0 !important; }
[data-testid="column"] { padding: 0 3px !important; }

.mpill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 2px 11px 2px 9px; border-radius: var(--rpill);
  border: 1px solid rgba(212,145,90,0.28); background: var(--accent-light);
  color: var(--accent-dark); font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 8px;
}

/* ═══ ANIMATED LOGO ══════════════════════════════════════════ */
@keyframes prismFloat {
  0%, 100% {
    transform: translateY(0px) scale(1);
    box-shadow: 0 8px 32px rgba(212,145,90,0.38),
                inset 0 1px 0 rgba(255,255,255,0.25),
                0 0 0 0px rgba(212,145,90,0.0);
  }
  50% {
    transform: translateY(-7px) scale(1.03);
    box-shadow: 0 20px 52px rgba(212,145,90,0.58),
                inset 0 1px 0 rgba(255,255,255,0.3),
                0 0 0 8px rgba(212,145,90,0.10);
  }
}
@keyframes prismGradient {
  0%   { background-position: 0%   0%;   }
  25%  { background-position: 100% 0%;   }
  50%  { background-position: 100% 100%; }
  75%  { background-position: 0%   100%; }
  100% { background-position: 0%   0%;   }
}
@keyframes prismShield {
  0%, 100% { opacity: 0.88; }
  50%       { opacity: 1.0;  }
}
@keyframes prismDot {
  0%, 100% { r: 3; fill: #D4915A; }
  50%       { r: 3.8; fill: #E8A870; }
}
/* Sidebar logo animation */
.prism-logo-sb {
  animation: prismFloat 3.2s ease-in-out infinite,
             prismGradient 5s ease infinite;
  background: linear-gradient(135deg,#E8A870,#D4915A,#B5733A,#D4915A,#E8A870) !important;
  background-size: 300% 300% !important;
}
/* Welcome hero logo animation */
.prism-logo-hero {
  animation: prismFloat 3.2s ease-in-out infinite,
             prismGradient 5s ease infinite;
  background: linear-gradient(145deg,#E8A870,#D4915A,#B5733A,#C8834A,#E8A870) !important;
  background-size: 300% 300% !important;
}

@keyframes glow {
  0%,100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }
  50%      { box-shadow: 0 0 0 5px rgba(34,197,94,0); }
}
</style>
""", unsafe_allow_html=True)

    # Sidebar keep-open script — separate from CSS to avoid rendering issues
    st.markdown("""
<script>
(function keepSidebarOpen(){
  function enforce(){
    var sb = document.querySelector('[data-testid="stSidebar"]');
    if(sb){
      sb.style.cssText += 'transform:none!important;visibility:visible!important;display:flex!important;opacity:1!important;width:288px!important;min-width:288px!important;';
    }
    document.querySelectorAll('[data-testid="stSidebarCollapseButton"],button[title="Close sidebar"],button[aria-label="Collapse sidebar"],[data-testid="collapsedControl"]')
      .forEach(function(b){ b.style.display='none'; b.disabled=true; });
  }
  enforce();
  var mo = new MutationObserver(enforce);
  mo.observe(document.body, {childList:true, subtree:true, attributes:true});
})();
</script>
""", unsafe_allow_html=True)

    # NOTE: previous attempt to inject this JS via st.markdown(<script>) was
    # removed because recent Streamlit strips <script> from markdown.
    # The pin logic now lives inside `inject_uploader_pin_component()` which
    # uses streamlit.components.v1.html() — that mechanism is NOT stripped
    # and is guaranteed to execute. Called from main().


# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages":         [],
        "hf_key":           os.getenv("HUGGINGFACEHUB_API_TOKEN", ""),
        "or_key":           os.getenv("OPENROUTER_API_KEY", ""),
        "groq_key":         os.getenv("GROQ_API_KEY", ""),
        "gemini_key":       os.getenv("GOOGLE_API_KEY", ""),
        "temperature":      0.7,
        "max_tokens":       512,
        "upload_idx":       0,
        "active_model_key": "text",
        "show_keys":        False,
        "show_settings":    False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
#  SIDEBAR HTML HELPERS  (simplified — plain text, no inline CSS blobs)
# ─────────────────────────────────────────────────────────────
def _sb_divider(label):
    """Simple section divider using pure Streamlit — avoids raw-HTML CSS leaks."""
    st.markdown(
        f'<div style="padding:10px 14px 4px;">'
        f'<span style="color:#57534E;font-size:0.58rem;font-weight:700;'
        f'letter-spacing:0.18em;text-transform:uppercase;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

def _model_row(icon, name, badge, active=False):
    """Compact one-liner model row — minimal HTML, no complex nested styles."""
    dot_color   = "#22C55E" if active else "#3D3934"
    dot_shadow  = "box-shadow:0 0 7px rgba(34,197,94,0.7);" if active else ""
    bg          = "background:rgba(212,145,90,0.09);border:1px solid rgba(212,145,90,0.3);" if active else "background:transparent;border:1px solid transparent;"
    name_color  = "#F5F5F4" if active else "#78716C"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:7px 14px;'
        f'border-radius:9px;margin:1px 8px;{bg}">'
        f'<div style="width:7px;height:7px;border-radius:50%;background:{dot_color};flex-shrink:0;{dot_shadow}"></div>'
        f'<span style="font-size:0.73rem;font-weight:600;color:{name_color};flex:1;">{icon} {name}</span>'
        f'<span style="font-size:0.52rem;font-weight:800;letter-spacing:0.08em;'
        f'color:#A8A29E;padding:2px 6px;border-radius:3px;background:rgba(255,255,255,0.05);">{badge}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

def _key_dot(v): return "🟢" if v else "🔴"


# ─────────────────────────────────────────────────────────────
#  HANDLERS  (unchanged)
# ─────────────────────────────────────────────────────────────
def handle_text_to_text(prompt):
    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import SystemMessage, HumanMessage
        os.environ["GROQ_API_KEY"] = st.session_state.groq_key
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            max_tokens=st.session_state.max_tokens,
            temperature=st.session_state.temperature,
        )
        resp = llm.invoke([
            SystemMessage(content="You are Prism AI, a sharp multimodal AI assistant. Be insightful, concise. Use clean markdown."),
            HumanMessage(content=prompt),
        ])
        return resp.content
    except Exception as e:
        return f"❌ **Text error:** `{e}`"

def _hf_image(prompt):
    from huggingface_hub import InferenceClient
    llm = InferenceClient(api_key=st.session_state.hf_key)
    img = InferenceClient(api_key=st.session_state.hf_key, provider="fal-ai")
    ref = llm.chat_completion(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {"role":"system","content":"You are an expert FLUX prompt engineer. Output ONLY a single rich image prompt with lighting, mood, style, 4K quality tags. No preamble."},
            {"role":"user","content":prompt},
        ],
        max_tokens=160, temperature=0.75,
    )
    refined = ref.choices[0].message.content.strip()
    image = img.text_to_image(prompt=refined, model="black-forest-labs/FLUX.1-schnell")
    buf = io.BytesIO(); image.save(buf, format="PNG")
    return {"image_bytes":buf.getvalue(),"refined_prompt":refined,"source":"FLUX.1-schnell"}

def _gemini_image(prompt):
    """
    Generate an image via the Google AI Studio REST API using raw HTTP requests.

    WHY raw requests instead of the google-genai SDK:
      The google-genai SDK hard-routes ALL calls through the v1beta endpoint
      regardless of the model requested. Many image-generation models exist only
      on v1 or have been removed from v1beta entirely, which caused the repeated
      404 NOT_FOUND errors even when the model name was correct.

    WHY dynamic model discovery instead of a hardcoded name:
      Google deprecates and renames preview/exp models frequently. This function
      calls ListModels first, sorts results by image-generation likelihood, then
      tries each one — so the code keeps working across Google's model lifecycle
      without needing a code change every time a model is renamed.

    Previous failures explained:
      • imagen-3.0-generate-002 / imagen-3.0-fast-generate-001
            → Vertex AI / allowlist only; not reachable with a plain AI Studio key.
      • gemini-2.0-flash-preview-image-generation
            → "preview" model removed from v1beta; caused the second 404.
    """
    import requests as _req, base64 as _b64

    api_key  = st.session_state.gemini_key.strip()
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    headers  = {"Content-Type": "application/json"}

    # ── Step 1: Discover models available to this API key ────────────────────
    # ListModels returns everything the key can reach — no guessing required.
    try:
        lr   = _req.get(f"{base_url}/models?key={api_key}", timeout=10)
        raw  = lr.json().get("models", [])
        all_names = [m["name"].replace("models/", "") for m in raw]
    except Exception:
        # If discovery fails, fall back to a known-stable list
        all_names = [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
        ]

    # ── Step 2: Sort candidates by image-generation likelihood ───────────────
    # Priority: (a) any model whose name contains "image", non-preview first;
    #           (b) flash-exp models (known to support responseModalities);
    #           (c) flash stable; (d) everything else.
    def _rank(name: str) -> tuple:
        n = name.lower()
        has_image   = "image" in n
        is_preview  = "preview" in n
        is_flash    = "flash" in n
        is_exp      = "exp" in n or "experimental" in n
        return (
            not has_image,       # image-specific models first
            is_preview,          # non-preview before preview
            not (is_flash and is_exp),  # flash-exp next
            not is_flash,        # flash stable after
        )

    seen: set = set()
    candidates = []
    for name in sorted(all_names, key=_rank):
        if name not in seen:
            seen.add(name)
            candidates.append(name)

    # ── Step 3: Attempt image generation against each candidate ──────────────
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }

    errors: list = []
    for model in candidates[:8]:   # cap attempts; text-only models fail fast
        url = f"{base_url}/models/{model}:generateContent?key={api_key}"
        try:
            r    = _req.post(url, headers=headers, json=body, timeout=60)
            data = r.json()
            if r.status_code == 200:
                for cand in data.get("candidates", []):
                    for part in cand.get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            return {
                                "image_bytes":    _b64.b64decode(part["inlineData"]["data"]),
                                "refined_prompt": prompt,
                                "source":         f"Gemini {model}",
                            }
                # 200 but no image bytes → text-only model, skip silently
                errors.append(f"{model}: no image parts in response (text-only model?)")
            else:
                msg = data.get("error", {}).get("message", str(data))[:120]
                errors.append(f"{model}: HTTP {r.status_code} – {msg}")
        except Exception as exc:
            errors.append(f"{model}: {exc}")

    avail = ", ".join(candidates[:6]) or "none discovered"
    raise RuntimeError(
        f"No Gemini model returned an image.\n"
        f"Models tried (from your key's ListModels): [{avail}]\n"
        + "\n".join(errors)
    )

def handle_text_to_image(prompt):
    hf, gem = st.session_state.hf_key.strip(), st.session_state.gemini_key.strip()
    if hf:
        try: return _hf_image(prompt)
        except Exception as e:
            if gem:
                try: r = _gemini_image(prompt); r["fallback"]=str(e); return r
                except Exception as e2: return f"❌ HF: `{e}` | Gemini: `{e2}`"
            return f"❌ **Image error:** `{e}`"
    elif gem:
        try: return _gemini_image(prompt)
        except Exception as e: return f"❌ **Gemini error:** `{e}`"
    return "❌ **Image generation needs a HuggingFace token or Gemini API key.** Add in sidebar."

def handle_image_to_text(img_bytes, filename, prompt):
    import requests
    ext = Path(filename).suffix.lower().lstrip(".")
    mt  = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","gif":"image/gif","webp":"image/webp"}.get(ext,"image/jpeg")
    b64 = base64.b64encode(img_bytes).decode()
    q   = prompt.strip() or "Describe this image comprehensively and in detail."
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization":f"Bearer {st.session_state.or_key}","Content-Type":"application/json"},
            json={"model":"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                  "messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":f"data:{mt};base64,{b64}"}}]}],
                  "temperature":0.3},
            timeout=60,
        )
        m = r.json().get("choices",[{}])[0].get("message",{})
        return m.get("content") or m.get("reasoning") or f"❌ **API error:** {r.json()}"
    except Exception as e: return f"❌ **Vision error:** `{e}`"

def handle_audio_to_text(audio_bytes, filename):
    try:
        from groq import Groq
        client = Groq(api_key=st.session_state.groq_key)
        suffix = Path(filename).suffix or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes); p = tmp.name
        with open(p,"rb") as f:
            tx = client.audio.transcriptions.create(file=(filename,f.read()),model="whisper-large-v3",response_format="text")
        os.unlink(p); return str(tx)
    except Exception as e: return f"❌ **Transcription error:** `{e}`"

def handle_text_to_audio(prompt):
    try:
        from gtts import gTTS
        from langchain_groq import ChatGroq
        from langchain_core.messages import SystemMessage, HumanMessage
        os.environ["GROQ_API_KEY"] = st.session_state.groq_key
        llm = ChatGroq(model="openai/gpt-oss-120b", max_tokens=120, temperature=0.75)
        resp = llm.invoke([
            SystemMessage(content="Write a spoken voiceover script. Output ONLY spoken words, no labels, no stage directions. 60 words max."),
            HumanMessage(content=prompt),
        ])
        spoken = " ".join(resp.content.strip().split()[:60])
        if not spoken: return "❌ No script generated."
        tts = gTTS(text=spoken, lang="en", slow=False)
        buf = io.BytesIO(); tts.write_to_fp(buf); buf.seek(0)
        return {"audio_bytes": buf.getvalue()}
    except ImportError: return "❌ Install gTTS: `pip install gTTS`"
    except Exception as e: return f"❌ **TTS error:** `{e}`"

def handle_video_to_text(vid_bytes, filename, prompt):
    import requests
    try:
        import cv2
        from PIL import Image as PIL_Image
    except ImportError:
        return "❌ Install: `pip install opencv-python-headless Pillow`"
    try:
        suffix = Path(filename).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(vid_bytes); p = tmp.name
        cap = cv2.VideoCapture(p)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total//6); frames, idx = [], 0
        while cap.isOpened() and len(frames) < 6:
            ok, frame = cap.read()
            if not ok: break
            if idx % step == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil = PIL_Image.fromarray(rgb)
                w = 384; pil = pil.resize((w, int(w*pil.height/pil.width)), PIL_Image.Resampling.LANCZOS)
                buf = io.BytesIO(); pil.save(buf,format="JPEG",quality=60)
                frames.append(base64.b64encode(buf.getvalue()).decode())
            idx += 1
        cap.release(); os.unlink(p)
        q = prompt.strip() or "Describe what happens in this video. List key actions and objects."
        contents = [{"type":"text","text":q}]
        for fb64 in frames:
            contents.append({"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{fb64}"}})
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization":f"Bearer {st.session_state.or_key}","Content-Type":"application/json"},
            json={"model":"nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                  "messages":[{"role":"user","content":contents}],"temperature":0.2},
            timeout=90,
        )
        m = r.json().get("choices",[{}])[0].get("message",{})
        return m.get("content") or m.get("reasoning") or f"❌ **API error:** {r.json()}"
    except Exception as e: return f"❌ **Video error:** `{e}`"

# ─────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────
_IMG_KW = ["generate image","create image","draw ","make image","generate a photo","create a photo",
           "illustrate","paint a","paint me","sketch","render image","generate art","create art",
           "make a picture","image of ","photo of ","picture of ","scene of ","artwork of "]
_AUD_KW = ["generate audio","create audio","text to speech","convert to speech","speak this",
           "say this"," tts","make audio","narrate","read aloud","audio clip","audio ad","audio for"]

def _detect(t):
    t = t.lower()
    if any(k in t for k in _AUD_KW): return "text_to_audio"
    if any(k in t for k in _IMG_KW): return "text_to_image"
    if any(w in t for w in [" image"," photo"," picture","an image"]): return "text_to_image"
    return "text_to_text"

def _need_key(attr, label):
    if not st.session_state.get(attr,"").strip():
        return f"⚠️ **{label} API key required.** Add it in the sidebar under **🔑 API Keys**."
    return None

def process_request(user_text, file):
    ts = datetime.now().strftime("%I:%M %p")

    if file is not None:
        ft, fb, fn = file.type or "", file.getvalue(), file.name

        if ft.startswith("video/"):
            st.session_state.active_model_key = "video"
            e = _need_key("or_key","OpenRouter")
            if e: return _err(e,"🎬 Video → Text",ts)
            return _txt(handle_video_to_text(fb,fn,user_text),"🎬 Video → Text",ts)

        if ft.startswith("audio/"):
            st.session_state.active_model_key = "audio_stt"
            e = _need_key("groq_key","Groq")
            if e: return _err(e,"🎵 Audio → Text",ts)
            return _txt(handle_audio_to_text(fb,fn),"🎵 Audio → Text",ts)

        if ft.startswith("image/"):
            st.session_state.active_model_key = "vision"
            e = _need_key("or_key","OpenRouter")
            if e: return _err(e,"🖼️ Image → Text",ts)
            return _txt(handle_image_to_text(fb,fn,user_text),"🖼️ Image → Text",ts)

    intent = _detect(user_text)

    if intent == "text_to_image":
        st.session_state.active_model_key = "image_gen"
        if not st.session_state.hf_key.strip() and not st.session_state.gemini_key.strip():
            return _err("⚠️ **Image generation needs a HuggingFace token or Gemini API key.** Add in sidebar.","✨ Text → Image",ts)
        res = handle_text_to_image(user_text)
        if isinstance(res, dict):
            return {"role":"assistant","type":"image",
                    "image_b64":base64.b64encode(res["image_bytes"]).decode(),
                    "caption":res["refined_prompt"],"img_source":res.get("source","FLUX"),
                    "modality":"✨ Text → Image","timestamp":ts}
        return _err(res,"✨ Text → Image",ts)

    if intent == "text_to_audio":
        st.session_state.active_model_key = "tts"
        e = _need_key("groq_key","Groq")
        if e: return _err(e,"🔊 Text → Audio",ts)
        res = handle_text_to_audio(user_text)
        if isinstance(res, dict):
            return {"role":"assistant","type":"audio",
                    "audio_b64":base64.b64encode(res["audio_bytes"]).decode(),
                    "modality":"🔊 Text → Audio","timestamp":ts}
        return _err(res,"🔊 Text → Audio",ts)

    st.session_state.active_model_key = "text"
    e = _need_key("groq_key","Groq")
    if e: return _err(e,"💬 Text → Text",ts)
    return _txt(handle_text_to_text(user_text),"💬 Text → Text",ts)

def _txt(c,m,ts): return {"role":"assistant","type":"text","content":c,"modality":m,"timestamp":ts}
def _err(c,m,ts): return {"role":"assistant","type":"error","content":c,"modality":m,"timestamp":ts}


# ─────────────────────────────────────────────────────────────
#  SIDEBAR  (simplified markup — no inline CSS style blobs)
# ─────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:

        # ── Brand header (animated logo) ──────────────────
        # IMPORTANT: no blank lines and no 4-space indentation inside the HTML —
        # otherwise CommonMark treats the indented lines as a code block and the
        # raw markup leaks into the sidebar as visible text. See H-A bugfix.
        st.markdown(
            '<div style="padding:22px 16px 18px;border-bottom:1px solid rgba(255,255,255,0.06);">'
            '<div style="display:flex;align-items:center;gap:12px;">'
            '<div style="position:relative;flex-shrink:0;">'
            '<div class="prism-logo-sb" style="width:40px;height:40px;border-radius:12px;'
            'display:flex;align-items:center;justify-content:center;">'
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
            '<path d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z" '
            'fill="rgba(255,255,255,0.9)"/>'
            '<path d="M9 12l2 2 4-4" stroke="#B5733A" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
            '</div>'
            '<div style="position:absolute;bottom:-2px;right:-2px;width:10px;height:10px;'
            'border-radius:50%;background:#22C55E;box-shadow:0 0 6px rgba(34,197,94,0.9);'
            'border:2px solid #1C1917;"></div>'
            '</div>'
            '<div>'
            '<div style="color:#F5F5F4;font-size:1.05rem;font-weight:700;'
            'letter-spacing:-0.025em;line-height:1.1;">Prism AI</div>'
            '<div style="color:#57534E;font-size:0.56rem;font-weight:600;'
            'letter-spacing:0.18em;text-transform:uppercase;margin-top:1px;">'
            'Multimodal Platform</div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Active Engine ─────────────────────────────────
        _sb_divider("⚙ Active Engine")

        akey = st.session_state.get("active_model_key", "text")
        models = [
            ("💬", "gpt-oss-120b",        "text",      "TEXT"),
            ("✨", "FLUX / Imagen 3",      "image_gen", "IMAGE"),
            ("🖼️", "Nemotron-Omni-30B",    "vision",    "VISION"),
            ("🎵", "Whisper Large v3",     "audio_stt", "AUDIO"),
            ("🎬", "Nemotron-Omni-30B",    "video",     "VIDEO"),
            ("🔊", "gpt-oss-120b → gTTS",  "tts",       "TTS"),
        ]
        for icon, name, key, badge in models:
            _model_row(icon, name, badge, active=(akey == key))

        # Coming soon
        st.markdown("""
<div style="margin:8px 10px 4px;padding:11px 13px;border-radius:10px;
            background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);">
  <div style="display:flex;align-items:center;gap:7px;margin-bottom:4px;">
    <span style="background:linear-gradient(135deg,#D4915A,#0EA5E9);color:white;
                 font-size:0.52rem;font-weight:800;letter-spacing:0.1em;
                 padding:2px 7px;border-radius:4px;">COMING SOON</span>
    <div style="width:6px;height:6px;border-radius:50%;background:#22D3EE;
                box-shadow:0 0 8px rgba(34,211,238,0.9);"></div>
  </div>
  <div style="color:#57534E;font-size:0.66rem;line-height:1.55;">
    <span style="color:#A8A29E;font-weight:600;">Text → Video</span> via
    <span style="color:#7DD3FC;font-weight:600;">Google Veo 3.1</span>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── API Keys (toggle) ─────────────────────────────
        arr_k = "▲" if st.session_state.show_keys else "▼"
        if st.button(f"🔑  API Keys  {arr_k}", key="toggle_keys", use_container_width=True):
            st.session_state.show_keys = not st.session_state.show_keys
            st.rerun()
        if st.session_state.show_keys:
            st.session_state.groq_key   = st.text_input("Groq Key",    value=st.session_state.groq_key,   type="password", placeholder="gsk_••••",   help="Text chat, TTS, Whisper STT.")
            st.session_state.hf_key     = st.text_input("HuggingFace", value=st.session_state.hf_key,     type="password", placeholder="hf_••••",    help="FLUX.1-schnell via fal-ai.")
            st.session_state.or_key     = st.text_input("OpenRouter",  value=st.session_state.or_key,     type="password", placeholder="sk-or-••••", help="Vision, video, PDF.")
            st.session_state.gemini_key = st.text_input("Gemini",      value=st.session_state.gemini_key, type="password", placeholder="AIza••••",   help="Imagen 3 fallback for image gen.")
            st.markdown(
                f'<div style="font-size:0.7rem;color:#57534E;line-height:2.1;padding:2px 0 4px;">'
                f'{_key_dot(st.session_state.groq_key)} Groq &nbsp;·&nbsp;'
                f'{_key_dot(st.session_state.hf_key)} HF &nbsp;·&nbsp;'
                f'{_key_dot(st.session_state.or_key)} OR &nbsp;·&nbsp;'
                f'{_key_dot(st.session_state.gemini_key)} Gemini</div>',
                unsafe_allow_html=True,
            )

        # ── Settings (toggle) ─────────────────────────────
        arr_s = "▲" if st.session_state.show_settings else "▼"
        if st.button(f"⚙️  Settings  {arr_s}", key="toggle_settings", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()
        if st.session_state.show_settings:
            st.session_state.temperature = st.slider("Temperature", 0.0, 2.0, float(st.session_state.temperature), 0.05)
            st.session_state.max_tokens  = st.slider("Max Tokens",   64, 2048, int(st.session_state.max_tokens),    64)

        # ── Session controls ──────────────────────────────
        _sb_divider("Session")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🆕 New", use_container_width=True):
                st.session_state.messages = []; st.session_state.upload_idx += 1; st.rerun()
        with c2:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.messages = []; st.session_state.upload_idx += 1; st.rerun()

        if st.session_state.messages:
            exportable = [
                {"role":m["role"],"type":m.get("type","text"),
                 "content":m.get("content",""),"modality":m.get("modality",""),"time":m.get("timestamp","")}
                for m in st.session_state.messages if m.get("type") not in ("image","audio")
            ]
            st.download_button("💾 Export Chat",
                data=json.dumps(exportable, indent=2),
                file_name=f"prism_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json", use_container_width=True)

        # Footer
        st.markdown("""
<div style="padding:14px;border-top:1px solid rgba(255,255,255,0.05);
            color:#44403C;font-size:0.62rem;text-align:center;line-height:2.1;margin-top:10px;">
  <div style="color:#D4915A;font-weight:700;font-size:0.78rem;margin-bottom:2px;">
    Prism AI · v1.0</div>
  <div>Multimodal Demo · Open Source</div>
  <div style="color:#292524;margin-top:2px;">Groq · HuggingFace · OpenRouter · Gemini</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  HEADER BAR
# ─────────────────────────────────────────────────────────────
def render_header():
    now = datetime.now(timezone.utc).strftime("UTC %Y-%m-%d  %H:%M")
    akey = st.session_state.get("active_model_key","text")
    model_names = {
        "text":"gpt-oss-120b","image_gen":"FLUX / Imagen 3","vision":"Nemotron-Omni",
        "audio_stt":"Whisper v3","tts":"gpt-oss → gTTS","video":"Nemotron-Omni","pdf":"Nemotron-Omni",
    }
    active_name = model_names.get(akey, "gpt-oss-120b")
    st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid #E7E5E0;border-radius:14px;
            padding:7px 14px;margin-bottom:0.7rem;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);
            display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="display:flex;align-items:center;gap:6px;
                background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.22);
                border-radius:999px;padding:4px 13px;">
      <div style="width:6px;height:6px;border-radius:50%;background:#22C55E;
                  box-shadow:0 0 6px rgba(34,197,94,0.7);"></div>
      <span style="color:#16A34A;font-size:0.67rem;font-weight:700;letter-spacing:0.04em;">
        Pipeline Active</span>
    </div>
    <span style="color:#C5BDB5;font-size:0.71rem;">{now}</span>
  </div>
  <div style="background:rgba(212,145,90,0.08);border:1px solid rgba(212,145,90,0.22);
              border-radius:999px;padding:5px 14px;">
    <span style="color:#92400E;font-size:0.71rem;font-weight:700;">
      Active: {active_name}</span>
  </div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  WELCOME SCREEN  (no chip buttons — hero + capability pills only)
# ─────────────────────────────────────────────────────────────
def render_welcome():
    st.markdown("""
<div style="text-align:center;padding:0.4rem 1rem 0.6rem;max-width:660px;margin:0 auto;"><div class="prism-logo-hero" style="width:48px;height:48px;border-radius:12px;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(212,145,90,0.3);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z" fill="rgba(255,255,255,0.92)"/><circle cx="12" cy="12" r="3" fill="#D4915A"/></svg></div><h1 style="color:#1C1917;font-size:1.35rem;font-weight:700;letter-spacing:-0.035em;line-height:1.12;margin-bottom:4px;">Prism AI Multimodal Platform</h1><p style="color:#78716C;font-size:0.82rem;line-height:1.5;margin-bottom:4px;">One unified intelligence. Every modality.<br>Type a message below, or attach a file to get started.</p><div style="display:flex;flex-wrap:wrap;justify-content:center;gap:5px;margin:8px 0 0;">
    <span style="background:#F0FDF4;border:1px solid #BBF7D0;color:#166534;font-size:0.61rem;font-weight:600;padding:3px 11px;border-radius:999px;">💬 Chat</span>
    <span style="background:#FDF2F8;border:1px solid #FBCFE8;color:#9D174D;font-size:0.61rem;font-weight:600;padding:3px 11px;border-radius:999px;">✨ Image Gen</span>
    <span style="background:#F5F3FF;border:1px solid #DDD6FE;color:#5B21B6;font-size:0.61rem;font-weight:600;padding:3px 11px;border-radius:999px;">🖼️ Vision</span>
    <span style="background:#FFFBEB;border:1px solid #FDE68A;color:#92400E;font-size:0.61rem;font-weight:600;padding:3px 11px;border-radius:999px;">🎵 STT</span>
    <span style="background:#F0F9FF;border:1px solid #BAE6FD;color:#075985;font-size:0.61rem;font-weight:600;padding:3px 11px;border-radius:999px;">🔊 TTS</span>
    <span style="background:#F0FDF4;border:1px solid #86EFAC;color:#14532D;font-size:0.61rem;font-weight:600;padding:3px 11px;border-radius:999px;">🎬 Video</span>
  </div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  RENDER MESSAGES
# ─────────────────────────────────────────────────────────────
def render_messages():
    for msg in st.session_state.messages:

        if msg["role"] == "user":
            text   = _html.escape(msg.get("content",""))
            fname  = msg.get("file_name","")
            ts     = msg.get("timestamp","")
            attach = (f'<div style="font-size:0.7rem;color:#A8A29E;margin-top:3px;">'
                      f'📎 {_html.escape(fname)}</div>') if fname else ""
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;align-items:flex-start;'
                f'margin:6px 0;gap:9px;">'
                f'<div style="max-width:72%;">'
                f'<div style="background:#E9E3DA;border:1px solid rgba(196,149,106,0.2);'
                f'border-radius:18px 18px 4px 18px;padding:11px 16px;'
                f'color:#1C1917;font-size:0.92rem;line-height:1.72;">{text}</div>'
                f'{attach}'
                f'<div style="font-size:0.67rem;color:#C5BDB5;margin-top:2px;text-align:right;">{ts}</div>'
                f'</div>'
                f'<div style="width:32px;height:32px;border-radius:50%;background:#44403C;'
                f'flex-shrink:0;display:flex;align-items:center;justify-content:center;'
                f'font-size:11px;margin-top:2px;color:#F5F5F4;font-weight:600;">YOU</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        else:
            modality = msg.get("modality","")
            mtype    = msg.get("type","text")
            ts       = msg.get("timestamp","")

            with st.chat_message("assistant", avatar="🔷"):
                if modality:
                    st.markdown(f'<div class="mpill">{modality}</div>', unsafe_allow_html=True)

                if mtype == "text":
                    st.markdown(msg.get("content",""))

                elif mtype == "image":
                    img_bytes = base64.b64decode(msg["image_b64"]) if msg.get("image_b64") else msg.get("image_bytes")
                    if img_bytes:
                        st.image(img_bytes, use_container_width=True)
                    src = msg.get("img_source","FLUX.1-schnell")
                    cap = msg.get("caption","")
                    note = f" · *{cap[:150]}{'…' if len(cap)>150 else ''}*" if cap else ""
                    st.caption(f"✨ {src}{note}")

                elif mtype == "audio":
                    audio_data = msg.get("audio_b64") or msg.get("audio_bytes")
                    if isinstance(audio_data, str):
                        audio_data = base64.b64decode(audio_data)
                    if audio_data:
                        st.audio(audio_data, format="audio/mpeg")
                    st.caption("🔊 gTTS · MP3")

                elif mtype == "error":
                    st.error(msg.get("content","An error occurred."), icon="⚠️")

                if ts:
                    st.caption(ts)


# ─────────────────────────────────────────────────────────────
#  FILE UPLOADER
# ─────────────────────────────────────────────────────────────
def render_attached_chip(uploaded):
    """
    Visible chip rendered above the chat input when a file is attached.
    Needed because the underlying st.file_uploader is hidden off-screen
    (.inline-attach mode), which would otherwise also hide its built-in
    file preview/name UI. Icon is picked from the MIME-type prefix.
    """
    if not uploaded:
        return
    ft = (uploaded.type or "").lower()
    if   ft.startswith("image/"): icon = "🖼️"
    elif ft.startswith("audio/"): icon = "🎵"
    elif ft.startswith("video/"): icon = "🎬"
    else:                          icon = "📄"
    st.markdown(
        f'<div class="inline-attach-chip">'
        f'<span>{icon}</span>'
        f'<span>{_html.escape(uploaded.name)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_uploader():
    # Accepted types narrowed per user request — drops gif/webp/wav/m4a/ogg
    # /avi/mov/mkv/webm/pdf. The chips of supported types shown by Streamlit
    # underneath the dropzone come directly from this list, so trimming here
    # automatically removes the highlighted file-type words.
    uploaded = st.file_uploader(
        "📎 Attach a file — Image · Audio · Video",
        type=["png", "jpg", "jpeg", "mp3", "mp4"],
        key=f"up_{st.session_state.upload_idx}",
    )
    if uploaded:
        ft = uploaded.type or ""
        if ft.startswith("image/"):
            st.image(uploaded, width=260, caption=f"📎 {uploaded.name}")
        elif ft.startswith("audio/"):
            st.audio(uploaded); st.caption(f"📎 {uploaded.name}")
        else:
            sz  = len(uploaded.getvalue())
            szs = f"{sz/1024:.1f} KB" if sz < 1_048_576 else f"{sz/1_048_576:.1f} MB"
            ico = "🎬" if ft.startswith("video/") else "📄"
            st.markdown(
                f'<div style="background:rgba(212,145,90,0.06);border:1px solid rgba(212,145,90,0.18);'
                f'border-radius:10px;padding:9px 13px;display:flex;align-items:center;gap:10px;">'
                f'<span style="font-size:1.4rem;">{ico}</span>'
                f'<div><div style="color:#1C1917;font-size:0.84rem;font-weight:600;">{uploaded.name}</div>'
                f'<div style="color:#A8A29E;font-size:0.7rem;">{ft} · {szs}</div></div></div>',
                unsafe_allow_html=True,
            )
    return uploaded


def _add_user(text, file=None):
    ts  = datetime.now().strftime("%I:%M %p")
    msg = {"role":"user","type":"text","content":text,"timestamp":ts}
    if file: msg["file_name"] = file.name; msg["file_type"] = file.type
    st.session_state.messages.append(msg)


# ─────────────────────────────────────────────────────────────
#  UPLOADER PIN — components.html iframe (NOT strippable by Streamlit)
# ─────────────────────────────────────────────────────────────
def inject_uploader_pin_component():
    """
    Cursor-style inline-attach widget (Streamlit <1.42 fallback).
    Replaces the previous "pin uploader above chat input" rig.

    What this Component does inside its same-origin iframe:
      1. Collapses its own host slot to 0×0 so no flow space is reserved.
      2. Creates a single paperclip <button> at the parent <body> level
         and positions it via getBoundingClientRect to visually sit inside
         the chat-input bar, just left of Streamlit's built-in send button.
      3. Wires the paperclip's click to call .click() on the hidden
         st.file_uploader's <input type="file">. That opens the native OS
         file picker. The hidden uploader is moved off-screen by CSS in
         inject_css(), so its input element is still in the DOM and
         triggerable but the widget itself is invisible.
      4. Re-positions on every Streamlit mutation + window resize so the
         paperclip stays glued to the chat-input bar across reruns.

    The selected file flows back through Streamlit's normal file_uploader
    state pipe; render_attached_chip() draws the visible filename pill
    above the chat input on the next rerun.
    """
    components.html(
        """
<!DOCTYPE html><html><head><style>
  html,body{margin:0;padding:0;background:transparent;}
  #s{display:none !important;}
</style></head><body><div id="s"></div><script>
(function(){
  var doc;
  try { doc = window.parent.document; } catch(e){ return; }
  if(!doc) return;

  // Collapse this iframe's host slot to 0×0 so it doesn't reserve space.
  function collapseHost(){
    try {
      var f = window.frameElement;
      if(!f) return;
      var host = f.parentElement, probe = host;
      for(var i=0;i<6 && probe && probe !== doc.body; i++){
        if(probe.getAttribute && (probe.getAttribute('data-testid')||'').indexOf('stIFrame')>=0){
          host = probe; break;
        }
        probe = probe.parentElement;
      }
      ['position:fixed','top:0','left:0','right:auto','width:0','height:0',
       'min-height:0','margin:0','padding:0','overflow:hidden','z-index:9999',
       'pointer-events:none','visibility:hidden'].forEach(function(kv){
        var i = kv.indexOf(':');
        host.style.setProperty(kv.slice(0,i), kv.slice(i+1), 'important');
      });
      f.style.setProperty('width','0','important');
      f.style.setProperty('height','0','important');
      f.style.setProperty('border','0','important');
    } catch(e){}
  }
  collapseHost();

  // Paperclip SVG (Lucide-style), rendered using currentColor so the
  // button's `color:` CSS controls the icon tint.
  var PAPERCLIP = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '+
    'width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" '+
    'stroke-linecap="round" stroke-linejoin="round">'+
    '<path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>'+
    '</svg>';

  // Single body-level paperclip button. Body parent means no transformed
  // ancestor can break position:fixed, and clicks fire normally (we use
  // a real button + native click, no React event delegation needed).
  function ensureButton(){
    var btn = doc.querySelector('button[data-prism-attach="1"]');
    if(btn) return btn;
    btn = doc.createElement('button');
    btn.type = 'button';
    btn.setAttribute('data-prism-attach','1');
    btn.setAttribute('aria-label','Attach a file');
    btn.title = 'Attach a file';
    btn.innerHTML = PAPERCLIP;
    var s = btn.style;
    ['position:fixed','background:transparent','border:0','padding:6px',
     'margin:0','cursor:pointer','color:#57534E','display:flex',
     'align-items:center','justify-content:center','border-radius:6px',
     'z-index:100'].forEach(function(kv){
      var i = kv.indexOf(':');
      s.setProperty(kv.slice(0,i), kv.slice(i+1), 'important');
    });
    btn.addEventListener('mouseenter', function(){
      btn.style.setProperty('background','rgba(212,145,90,0.10)','important');
    });
    btn.addEventListener('mouseleave', function(){
      btn.style.setProperty('background','transparent','important');
    });
    btn.addEventListener('click', function(e){
      e.preventDefault(); e.stopPropagation();
      // Open the OS file picker by programmatically clicking the hidden
      // st.file_uploader's <input type="file">. The .click() call is
      // synchronous inside this real user-gesture handler, so browsers
      // allow it (no security pop-up suppression).
      var hidden = doc.querySelector('[data-testid="stFileUploader"] input[type="file"]');
      if(hidden){ hidden.click(); }
    });
    doc.body.appendChild(btn);
    return btn;
  }

  function position(){
    var btn = ensureButton();
    var chat = doc.querySelector('[data-testid="stChatInput"]')
            || doc.querySelector('[data-testid="stBottom"]')
            || doc.querySelector('[data-testid="stBottomBlockContainer"]');
    if(!chat){ btn.style.setProperty('display','none','important'); return; }
    btn.style.setProperty('display','flex','important');
    var r = chat.getBoundingClientRect();
    // Center vertically within the chat-input bar; place ~56px from the
    // right edge so we sit just left of Streamlit's built-in send button.
    var topPx  = Math.round(r.top + (r.height - 32) / 2);
    var leftPx = Math.round(r.right - 56);
    btn.style.setProperty('top',    topPx + 'px',  'important');
    btn.style.setProperty('left',   leftPx + 'px', 'important');
    btn.style.setProperty('bottom', 'auto',        'important');
    btn.style.setProperty('right',  'auto',        'important');
    btn.style.setProperty('width',  '32px',        'important');
    btn.style.setProperty('height', '32px',        'important');
  }

  position();
  try {
    var mo = new window.parent.MutationObserver(function(){ position(); });
    mo.observe(doc.body, {childList:true, subtree:true, attributes:true});
  } catch(e){}
  window.parent.addEventListener('resize', position);
})();
</script></body></html>
        """,
        height=0,
        width=0,
    )


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
def _native_chat_attach_supported():
    """
    Returns True iff st.chat_input supports accept_file (Streamlit ≥ 1.42).
    We check the actual function signature instead of parsing __version__
    so a backport or future rename still works correctly.
    """
    try:
        import inspect
        sig = inspect.signature(st.chat_input)
        return "accept_file" in sig.parameters
    except Exception:
        return False


def main():
    # #region agent log — log path is resolved relative to THIS script so
    # it works regardless of CWD or which folder Streamlit is run from.
    try:
        import time as _t, os as _os
        _logp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "debug-07747d.log")
        with open(_logp, "a", encoding="utf-8") as _f:
            _f.write(json.dumps({
                "sessionId":"07747d","runId":"r-chat-attach",
                "hypothesisId":"H-Old-Streamlit",
                "location":"app.py:main",
                "message":"main() invoked",
                "data":{
                    "build":"chat-attach-v2",
                    "logPath": _logp,
                    "scriptPath": _os.path.abspath(__file__),
                    "streamlitVersion": getattr(st, "__version__", "unknown"),
                    "nativeChatAttach": _native_chat_attach_supported(),
                },
                "timestamp": int(_t.time()*1000),
            }) + "\n")
    except Exception:
        pass
    # #endregion

    init_state()
    inject_css()
    render_sidebar()
    # render_header() removed — user requested no top status bar.
    # render_header function is preserved below in case it's needed later.

    if not st.session_state.messages:
        render_welcome()

    render_messages()

    # Use the native chat-with-attachment widget ONLY if this Streamlit
    # version exposes the `accept_file` kwarg (≥1.42, Feb 2025). Otherwise
    # fall back to the previous rig that worked here: a separate
    # st.file_uploader panel pinned above the chat input via a Component.
    if _native_chat_attach_supported():
        chat_in = st.chat_input(
            "Message Prism AI — or attach a file with the paperclip…",
            accept_file=True,
            file_type=["png", "jpg", "jpeg", "mp3", "mp4"],
        )
        if chat_in:
            prompt_text = (chat_in.text or "").strip()
            uploaded    = chat_in.files[0] if chat_in.files else None
            if prompt_text or uploaded:
                _add_user(prompt_text, file=uploaded)
                with st.spinner("Prism AI is thinking…"):
                    resp = process_request(prompt_text, uploaded)
                st.session_state.messages.append(resp)
                st.session_state.upload_idx += 1
                st.rerun()
    else:
        # Fallback for Streamlit <1.42: hand-rolled Cursor-style inline
        # attach. render_uploader() mounts the file_uploader (hidden via
        # CSS), render_attached_chip() shows the visible filename pill,
        # and inject_uploader_pin_component() draws a paperclip button
        # inside the chat-input bar.
        uploaded = render_uploader()
        render_attached_chip(uploaded)
        inject_uploader_pin_component()
        if prompt := st.chat_input("Message Prism AI — type your message or paperclip to attach…"):
            _add_user(prompt, file=uploaded)
            with st.spinner("Prism AI is thinking…"):
                resp = process_request(prompt, uploaded)
            st.session_state.messages.append(resp)
            st.session_state.upload_idx += 1
            st.rerun()

if __name__ == "__main__":
    main()
<div align="center">

<!-- Replace with your actual banner image once you have one -->
<!-- <img src="assets/banner.png" alt="Prism AI" width="100%" /> -->

# 🔷 Prism AI

### One unified intelligence. Every modality.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Inference-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FLUX-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

<br/>

**Prism AI** is a multimodal intelligence platform that lets you chat, generate images,<br/>
transcribe audio, analyze video, and synthesize speech — all from a single, premium interface.

</div>

---

## 📹 Demo

<!-- ─────────────────────────────────────────────────────────────────────────
     REPLACE: paste your Loom / YouTube link below, or drop a GIF into assets/
     ───────────────────────────────────────────────────────────────────────── -->
> 🎬 Full walkthrough video — all 6 modalities in action.

[![Prism AI Demo](https://img.shields.io/badge/▶%20Watch%20Demo-000000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/your-video-id)

---

## 🗺️ Highlevel Overview

![Highlevel](assets/highlevel.png)

---

## ✨ Capabilities

Prism AI automatically detects what you want based on your input — no mode switching, no dropdowns.

| Mode | How to trigger | Model |
|:----:|:--------------|:------|
| 💬 **Chat** | Type any question or message | Groq · `gpt-oss-120b` |
| ✨ **Image Generation** | *"Generate an image of..."* | HuggingFace FLUX.1-schnell → Gemini Imagen 3 |
| 🖼️ **Image Understanding** | Attach a `.png` / `.jpg` | OpenRouter · Nemotron-Omni-30B |
| 🎵 **Speech-to-Text** | Attach an `.mp3` | Groq · Whisper Large v3 |
| 🔊 **Text-to-Speech** | *"Say this..."* / *"Read aloud..."* | Groq + gTTS |
| 🎬 **Video Analysis** | Attach an `.mp4` | OpenRouter · Nemotron-Omni-30B |

---

## 🧠 Tech Stack

Prism AI is assembled from four best-in-class AI APIs — each chosen for a specific reason.

---

### ⚡ [Groq](https://groq.com) — Ultra-Fast LLM Inference

Used for **text chat**, **audio transcription**, and **TTS scripting**.

Groq's LPU (Language Processing Unit) delivers inference speeds that are 10–100× faster than traditional GPU-based providers. In Prism AI, this powers:

- `gpt-oss-120b` — main conversational model
- `whisper-large-v3` — audio transcription (Speech-to-Text)

```python
# Groq LLM via LangChain
from langchain_groq import ChatGroq
llm = ChatGroq(model="openai/gpt-oss-120b")
```

> **Required key:** `GROQ_API_KEY` → [Get one free at console.groq.com](https://console.groq.com)

---

### 🤗 [HuggingFace](https://huggingface.co) — FLUX Image Generation

Used as the **primary image generation engine**.

HuggingFace's Inference API, routed through the `fal-ai` provider, runs **FLUX.1-schnell** — one of the fastest and highest-quality open-source image generation models available. Prism AI first refines your prompt using a Qwen-2.5 model before sending it to FLUX.

```python
# HuggingFace Inference via fal-ai
from huggingface_hub import InferenceClient
img_client = InferenceClient(api_key=HF_KEY, provider="fal-ai")
image = img_client.text_to_image(prompt=refined_prompt, model="black-forest-labs/FLUX.1-schnell")
```

> **Required key:** `HUGGINGFACEHUB_API_TOKEN` → [Get one at huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

---

### 🔵 [Google Gemini](https://ai.google.dev) — Image Generation Fallback

Used as the **fallback image engine** when HuggingFace tokens are exhausted.

Prism AI automatically falls back to Gemini when HuggingFace fails. It uses a self-healing approach — calling `ListModels` on your API key first to discover which image-capable Gemini models are available, then trying each one. This makes the fallback resilient to Google's model lifecycle changes without any code edits.

```python
# Direct REST (no SDK) — bypasses v1beta routing issues
import requests
r = requests.post(
    f"{base_url}/models/{model}:generateContent?key={api_key}",
    json={"contents": [{"parts": [{"text": prompt}]}],
          "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}}
)
```

> **Required key:** `GOOGLE_API_KEY` → [Get one at aistudio.google.com](https://aistudio.google.com/app/apikey)

---

### 🟣 [OpenRouter](https://openrouter.ai) — Vision

Used for **image understanding**

OpenRouter provides a unified API gateway to hundreds of models. Prism AI uses **Nemotron-Omni-30B** — a multimodal reasoning model that handles image, video frame, and document inputs.

```python
# OpenRouter multimodal call
requests.post("https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {OR_KEY}"},
    json={"model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
          "messages": [{"role": "user", "content": [image_block, text_block]}]})
```

> **Required key:** `OPENROUTER_API_KEY` → [Get one at openrouter.ai/keys](https://openrouter.ai/keys)

---

## 📁 Project Structure

```
prism-ai/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── assets/
│   ├── banner.png          # Repo banner image
│   └── architecture.png    # Architecture diagram
└── README.md
```

---

## How to access the Application:

Click the link and Add your API Key: https://prism-ai-2w0x.onrender.com/

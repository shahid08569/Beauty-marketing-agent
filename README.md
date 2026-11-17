# Beauty Marketing Agent 🌟
### Autonomous AI Video Generation & Viral Marketing Engine for Beauty & Fashion E-Commerce

**Beauty Marketing Agent** is an end-to-end, full-stack AI content production pipeline designed specifically for Pakistani beauty, skincare, and fashion brands. It automates product research, script writing in conversational Roman Urdu, voiceover generation, 3D supermodel avatar selection, real AI motion video diffusion (Kling AI & Minimax), and final 1080x1920 cinematic reel production.

---

## 🚀 Key Capabilities

1. **⚡ AI Video Diffusion Engine (Kling AI & Minimax Video-01):**
   - Cloud GPU motion diffusion via **Replicate** and **Fal.ai**.
   - Integrates **Kling AI v1.6** (Standard & Pro) and **Minimax Video-01** (Hailuo).
   - Generates authentic physical motions: models lathering rich soap foam, touching glowing skin, and demonstrating real products.
   - Built-in **Studio Presets** mode for instant 1080x1920 reel generation with zero cloud costs.

2. **💃 3D AI Supermodels Catalog & Live Rehearsals:**
   - 6 curated high-fashion Pakistani avatars (Dr. Ayesha Khan, Zoya Malik, Fatima Noor, Hamza Grooming, Bibi Heritage, Aaliyah Runway).
   - Live 9:16 interactive rehearsal video preview in the wizard.
   - Dynamic customization of hairstyle (Low Bun, Waves, Headscarf) and wardrobe (Lab Coat, Silk Scrubs, Blazer).

3. **📝 Roman Urdu Script Generator & Review Wizard:**
   - Generates high-converting 4-part scripts: **Hook**, **Problem**, **Solution**, and **Call-To-Action (CTA)**.
   - Interactive step-by-step editor allows line-by-line review before rendering.
   - 1-click audio preview for individual lines or entire scripts.

4. **🎙️ Dual-Engine Neural Voiceover:**
   - Microsoft `edge-tts` and Google `gTTS` fallback for 100% reliable Pakistani accents (`ur-PK-UzmaNeural`, `ur-PK-AsadNeural`).
   - Integrated lofi and aesthetic background music with automatic audio ducking.

5. **🎨 Ink Wash Minimalist UI (Light & Dark Mode):**
   - Clean, modern dashboard built with Tailwind CSS.
   - Persistent theme toggle (Light / Dark mode).
   - Full-bleed 1080x1920 video player, content vault, and 1-click approval workflow.

---

## 📁 Repository Structure

```
beauty-marketing-agent/
├── backend/
│   ├── config/                     # Brand rules, hooks, and avatar definitions
│   ├── modules/
│   │   ├── ai_video_generator.py   # Replicate & Fal.ai video diffusion (Kling/Minimax)
│   │   ├── supermodel_engine.py    # 3D supermodels catalog & cinematic reel renderer
│   │   ├── roman_urdu_script.py    # Roman Urdu viral script generation
│   │   ├── tts_engine.py           # Neural voiceover engine (edge-tts + gTTS)
│   │   ├── media_fetcher.py        # Visual assets & scene cards
│   │   ├── compliance_checker.py   # Regulatory claim checker
│   │   └── publisher.py            # ZIP export pack generator
│   ├── pipeline.py                 # Master execution pipeline
│   └── server.py                   # FastAPI backend server
├── frontend/
│   └── index.html                  # Ink Wash Dashboard UI
├── frontend-angular/               # Optional Angular workspace
├── storage/
│   ├── audio/                      # Voiceovers & preview tracks
│   ├── music/                      # Background music tracks
│   ├── raw_assets/                 # Product photography & scene cards
│   ├── supermodel_rehearsals/      # 3D supermodel rehearsal video clips
│   ├── output_videos/              # Rendered 1080x1920 vertical reels
│   └── database.json               # Video generation catalog
├── .env.example                    # Environment variables template
├── run_dashboard.bat               # 1-Click launcher
└── README.md
```

---

## 🛠️ Quick Start Guide

### Prerequisites
- Python 3.10+
- FFmpeg installed and available on system PATH
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shahid08569/Beauty-marketing-agent.git
   cd Beauty-marketing-agent
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn pillow edge-tts gTTS pydantic requests
   ```

3. **Configure Environment Variables (Optional):**
   ```bash
   cp .env.example .env
   ```
   Add your `REPLICATE_API_TOKEN` if you want to use cloud GPU video diffusion (Kling AI / Minimax). Otherwise, the system defaults to high-quality Studio Presets.

4. **Launch the Dashboard:**
   ```bash
   # Windows launcher:
   run_dashboard.bat

   # Or manually via uvicorn:
   py -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
   ```
5. Open your browser and navigate to **`http://127.0.0.1:8000`**.

---

## 📄 License
MIT License. Free for commercial and personal marketing automation.

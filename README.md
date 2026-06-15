# GST Sahayak

GST & Tax Compliance Helper Chatbot — Academic Social Impact Project (June 2026)

- **Repo:** https://github.com/ahmedibu777/gst-sahayak
- **GitHub Pages:** https://ahmedibu777.github.io/gst-sahayak/

## Steps after downloading

1. Unzip `gst-sahayak-complete-codebase.zip`
2. `cd gst-sahayak`
3. `pip install -r requirements.txt`
4. Copy `.env.example` → `.env` and add **at least one** LLM API key:
   - Grok → [x.ai](https://x.ai)
   - OpenAI → [platform.openai.com](https://platform.openai.com)
   - Gemini → [aistudio.google.com](https://aistudio.google.com)
   - Claude → [console.anthropic.com](https://console.anthropic.com)
   - Hugging Face → [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
5. Set `LLM_PROVIDER=auto` (default) or pick a specific provider
6. `streamlit run main.py`

App opens at http://localhost:8501

## Tests

```bash
pytest tests/ -v
```

All 8 tests pass (verified):

- Due dates, late fees, TDS, ITC eligibility, GSTIN/HSN validators — all green.

## Key Highlights

**Hybrid Architecture:**

- High-confidence queries → Rule Engine + FAISS semantic search (fast, zero hallucination)
- Low-confidence / complex queries → LLM fallback (Grok, OpenAI, Gemini, Claude, or Hugging Face — `utils/llm_providers.py`)
- Every response ends with the full academic disclaimer

**Features:**

- Sidebar user profile (filing type, state, turnover, QRMP group)
- Dynamic due date calculator (Monthly + QRMP as of June 2026)
- Late fee, TDS (Sec 194J), ITC eligibility tools
- E-way bill & Composition scheme guidance
- Quick-reply buttons + natural chat
- Mobile-friendly Streamlit UI

## Deployment

### Streamlit Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select repo, set main file to `main.py`
4. Add at least one API key in Secrets (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.) and optional `LLM_PROVIDER`
5. Deploy

### Docker

```bash
docker build -t gst-sahayak .
docker run -p 8501:8501 --env-file .env gst-sahayak
```

## GitHub Pages

Landing page is in `docs/` — enable Pages in repo Settings → Pages → Source: `main` branch, `/docs` folder.

## Next Steps (Academic Submission)

1. Unzip → run locally (~5 minutes)
2. Add your preferred LLM API key in `.env`
3. Take screenshots of the chat for your report

## Disclaimer

Educational project only. Verify on gst.gov.in. Consult a qualified CA for professional advice.
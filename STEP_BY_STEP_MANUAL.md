# AISIH Multi-Agent Gateway v5.0 — OpenRouter Free

## OpenRouter setup (FREE models)

1. Go to https://openrouter.ai → Sign up
2. Keys → Create API key (starts with `sk-or-v1-...`)
3. Streamlit app → Manage app → Settings → Secrets:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
```

4. Save → restart app
5. Sidebar → Provider = **auto** or **openrouter**

Free models used automatically (Gemma, Llama, Phi, etc.). Rate limits apply on free tier.

## Optional other keys
```toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
XAI_API_KEY = "xai-..."
```

## Features
- Home AI Chat (Hinglish + real LLM via OpenRouter)
- Image Studio (edit + prompt; real DALL·E needs OpenAI credits)
- Video Studio, Learning Agent, Web Research
- Multi-Agent System

## Local run
```bash
pip install -r requirements.txt
streamlit run app.py
```

Admin: ceo / AI Software Innovation Infotech And Hardware Enterprises@CEO2026

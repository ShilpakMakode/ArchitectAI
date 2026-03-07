# ArchitectAI

ArchitectAI is an AI-powered cloud architecture generator.

## Current Run Options

### 1) Existing CLI prototype

```bash
python3 -m architect_ai.cli --input "Build a scalable AI chatbot backend with 1M users"
```

### 2) Streamlit UI (new MVP baseline)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

If your diagram is not rendered, install Graphviz system package:

```bash
brew install graphviz
```

## Using Groq

ArchitectAI supports Groq via OpenAI-compatible API settings:

```env
OPENAI_API_KEY=your_groq_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
```

## Streamlit MVP Modules

- `modules/requirement_parser.py`
- `modules/architecture_generator.py`
- `modules/diagram_generator.py`
- `modules/explanation_engine.py`
- `utils/aws_service_mapper.py`
- `prompts/parser_prompt.txt`
- `prompts/architecture_prompt.txt`

## Output Artifacts

The Streamlit app writes JSON artifacts to `outputs/` and diagrams to `outputs/diagrams/`.

# LifeDocs AI — Local AI Version

Ask questions about uploaded PDF and TXT documents using local AI models. This version does not use an OpenAI API key or API credits.

## Requirements
- Python 3.13 recommended
- Ollama for Windows: https://ollama.com/download/windows

## Setup in VS Code PowerShell terminal
Run these commands from this project folder:

```powershell
py -3.13 -m venv .venv313
.\.venv313\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ollama pull llama3.2:3b
ollama pull nomic-embed-text
python -m streamlit run app.py
```

Then open http://localhost:8501, upload a PDF or TXT file, click **Process Documents**, and ask a question.

If `py -3.13` is unavailable, check installed versions with `py -0p`.

## Notes
- Keep the Ollama application/service running while using the app.
- Scanned PDFs that contain only images may need OCR before text can be retrieved.
- Answers depend on the uploaded document content; verify important legal, insurance, and warranty details against the original document.

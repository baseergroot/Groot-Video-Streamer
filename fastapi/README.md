# FastAPI Backend (Dev Only)

This backend is for local development.

## Requirements

- Python 3.9+
- `pip`

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Default URL: `http://localhost:8000`

## Endpoints

- `GET /stream?url=...` — Stream video
- `GET /info?url=...` — Video info

## Notes

- Requires `yt-dlp` (included in `requirements.txt`).
- For production, add auth/rate limits and proper deployment config.

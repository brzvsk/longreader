# LongReader Backend

A FastAPI-based backend service for the LongReader application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

2. Access the API:
- Main endpoint: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   └── main.py
├── requirements.txt
└── README.md
```
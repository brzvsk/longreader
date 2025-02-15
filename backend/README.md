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

## Seeding Sample Data

> **Note**: For safety reasons, seeding is disabled by default. To enable it, you need to set `TELEGRAM_BOT_ENVIRONMENT=test` in your `.env` file or when running the command.

1. First, make sure you have a user in the database by logging in through the web application.

2. To seed the database with sample articles:
```bash
cd app/data

# Either add TELEGRAM_BOT_ENVIRONMENT=test to your .env file
python seed.py

# Or run directly with the environment variable
TELEGRAM_BOT_ENVIRONMENT=test python seed.py
```

This will:
- Keep existing users intact
- Clear existing articles and user-article links
- Create 6 sample articles
- Link the articles to your user account with random reading progress

To clear all data (including users):
```bash
TELEGRAM_BOT_ENVIRONMENT=test python seed.py --clear
```

## Project Structure

```
backend/
├── app/
│   └── main.py
├── requirements.txt
└── README.md
```
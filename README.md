# 📚 Longreader — save articles to read them later

<img width="200" alt="documents_file_20130_023032fbf8" src="https://github.com/user-attachments/assets/6219f69e-516e-4b9c-ac7b-64be39c6bd56" />
<img width="200" alt="documents_file_20129_1ffbc42f42" src="https://github.com/user-attachments/assets/a3637daa-db8b-4115-bc0d-324d68974b0f" />
<img width="200" alt="documents_file_20128_8cc9e52395" src="https://github.com/user-attachments/assets/cd0162a5-f902-4750-8462-32c25b848d66" />
<img width="200" alt="documents_file_20131_b3a5b8ca16" src="https://github.com/user-attachments/assets/8c0c24e9-bfce-4862-be66-33b7e67dcaef" />

## Overview

Longreader is a Telegram mini app designed to help users save and read long articles conveniently. It addresses the common pain points of reading lengthy content by offering features such as progress tracking and sharing capabilities.

**You can use this app as publicly deployed by [@brzvsk](https://github.com/brzvsk) here: https://t.me/ReadWatchLaterBot**

## Project Structure

- **frontend/**: Next.js application for the web interface
- **backend/**: FastAPI backend service
- **telegram-bot/**: Kotlin-based Telegram bot service
- **nginx.conf**: Nginx configuration for reverse proxy
- **docker-compose.yml**: Docker composition for all services

## Tech Stack

- **Frontend**: Next.js
- **Backend**: FastAPI (Python)
- **Telegram Bot**: Kotlin, Telegram Bot API
- **Database**: MongoDB
- **Proxy**: Nginx
- **Container**: Docker

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.8+ (for local development)
- JDK 8+ (for telegram bot development)
- Maven (for telegram bot development)

## Setup

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/brzvsk/longreader.git
   cd longreader
   ```

2. Set up environment variables:
   - Copy `.env.example` to `.env` in both `frontend/` and `backend/` directories
   - Update the environment variables as needed

3. Start the application:
   ```bash
   docker-compose up -d
   ```

   This will start all services:
   - Frontend on port 3000
   - Backend on port 8000
   - MongoDB on port 27017
   - Nginx on ports 80 and 443

### Local Development

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Start the development server:
   ```bash
   yarn dev
   ```

#### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Telegram Bot

1. Navigate to the telegram-bot directory:
   ```bash
   cd telegram-bot
   ```

2. Set up environment variables:
   - Create a `.env` file with the following variables:
     ```
     BOT_TOKEN=your_telegram_bot_token
     BOT_USERNAME=your_bot_username
     MONGODB_URI=mongodb://localhost:27017/database_name
     ```

3. Build the project:
   ```bash
   mvn clean install
   ```

4. Run the bot:
   ```bash
   mvn exec:java
   ```

## Credits

Project was started by [@brzvsk](https://github.com/brzvsk), [@goldenluk](https://github.com/goldenluk), and [@dreamwa1ker](https://github.com/dreamwa1ker) as an experiment. After that it was decided by the party to open source it.

## License

This project is released under the MIT License. See the `LICENSE` file for details.

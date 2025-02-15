# Longreader

## Overview

Longreader is a Telegram mini app designed to help users save and read long articles conveniently. It addresses the common pain points of reading lengthy content by offering features such as progress tracking and sharing capabilities.

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
   git clone https://github.com/MutimTemki/longreader.git
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
     MONGODB_URI=mongodb://localhost:27017/longreader
     ```

3. Build the project:
   ```bash
   mvn clean install
   ```

4. Run the bot:
   ```bash
   mvn exec:java
   ```

## Deployment and Updates

### Deploying Changes

The project uses GitHub Actions for CI/CD. Here's how to deploy updates:

1. Push changes to the `main` branch
2. Manually trigger the GitHub Actions workflow for the service you updated (frontend/backend/telegram-bot)
3. Wait for the new Docker image to be built successfully
4. SSH into the server:
   ```bash
   ssh -i ~/digitalocean root@104.248.33.158
   ```
5. Navigate to the project directory:
   ```bash
   cd /root/longreader
   ```
6. Pull and restart the specific service:
   ```bash
   # For frontend updates:
   docker compose pull frontend
   docker compose up -d frontend

   # For backend updates:
   docker compose pull backend
   docker compose up -d backend

   # For telegram bot updates:
   docker compose pull telegram-bot
   docker compose up -d telegram-bot
   ```

### Important Notes
- Always check the service logs after deployment:
  ```bash
  docker compose logs -f [service_name]  # e.g., frontend, backend, telegram-bot
  ```
- The production environment is in `/root/longreader` (not `/opt/longreader`)
- If multiple services need updating, you can update all at once:
  ```bash
  docker compose pull
  docker compose up -d
  ```
- GitHub Actions workflows must be triggered manually - they don't run automatically on push
- Monitor the GitHub Actions workflow to ensure the build succeeds before deploying
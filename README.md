# Longreader

## Overview

Longreader is a Telegram mini app designed to help users save and read long articles conveniently. It addresses the common pain points of reading lengthy content by offering features such as progress tracking, sharing capabilities.


## Project Structure

- **frontend/**: Contains the frontend application built with Next.js.
- **telegram-bot/**: Contains the backend application for the Telegram bot.

## Prerequisites

List any prerequisites needed to run the project, such as:

- Node.js
- npm or Yarn
- Java (for the Telegram bot)
- Maven (for building the Telegram bot)

## Setup // TODO: update with docker compose

### Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

### Telegram Bot

1. Navigate to the `telegram-bot` directory:
   ```bash
   cd telegram-bot
   ```

2. Build the project using Maven:
   ```bash
   mvn clean install
   ```

3. Run the application:
   ```bash
   java -jar target/telegram-bot.jar
   ```
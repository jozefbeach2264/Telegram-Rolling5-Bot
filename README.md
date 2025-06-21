# Rolling5 Telegram Bot

## Overview

Rolling5 is the primary user-facing interface for a multi-part trading bot ecosystem. It operates as a Telegram bot, accepting commands from authorized users to check system status and interact with the backend trading services.

This application is built using FastAPI and communicates with two other core services:
* **NeuroSync:** Handles network-level heartbeat and synchronization tasks.
* **TradingCore:** Contains the primary trading logic, analysis, and execution engine.

## Architecture

The bot is built on a clean, modular architecture:
* **`main.py`**: A FastAPI server that acts as the main entry point.
* **`telegram_bot.py`**: Manages all interactions with the `python-telegram-bot` library, including command registration and message polling.
* **`command_handler.py`**: Contains the core logic for each user command (e.g., `/status`), processing requests and formatting responses.
* **`core_api_client.py`**: A dedicated client for making asynchronous HTTP requests to the `NeuroSync` and `TradingCore` services.
* **`config.py`**: Loads and manages all necessary configuration from environment variables (Replit Secrets).

## Setup and Installation

1.  **Environment Variables:** This project relies on environment variables for configuration. In Replit, these should be set in the **Secrets** tool.
    * `TELEGRAM_BOT_TOKEN`: The API token for your Telegram bot from @BotFather.
    * `TELEGRAM_ADMIN_CHAT_ID`: Your personal Telegram user ID for admin access.
    * `NEUROSYNC_STATUS_URL`: The full URL for the `/status` endpoint of your `NeuroSync` service.
    * `CORE_STATUS_URL`: The full URL for the `/status` endpoint of your `TradingCore` service.

2.  **Install Dependencies:** All required Python packages are listed in `requirements.txt`. Install them using pip:
    ```shell
    pip install -r requirements.txt
    ```

## Running the Application

This application is run as an ASGI server using Uvicorn. From the shell, run the following command:

```shell
uvicorn main:app --host 0.0.0.0 --port 8000

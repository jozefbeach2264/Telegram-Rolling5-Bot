# Rolling5 - Telegram Bot Interface


## Overview

Rolling5 is the primary user interface for the DAN autonomous trading system. It operates as a Telegram bot, allowing users to monitor system health, receive trade alerts, and issue commands to the backend services (`NeuroSync` and `TradingCore`) from any device.

This application acts as a secure and convenient remote control for the entire trading operation.


## Features

- **Real-Time System Monitoring:** Get an instant health check of all connected backend services.
  
- **Trigger Trading Strategies:** Initiate the AI analysis pipeline for a specific strategy directly from the chat.
  
- **System Control:** Halt or resume all trading activity with a single command.
  
- **Performance Analysis:** Request detailed performance reports and accuracy checks.
  
- **Secure Communication:** Interacts with the backend services via a dedicated API client.


## Setup and Configuration

To run the Rolling5 bot, you must configure the necessary environment variables (secrets). Create a `.env` file in the `Rolling5` directory or set these secrets in your deployment environment.

```env
# --- ROLLING5 CONFIGURATION SECRETS ---

# Your unique token provided by Telegram's BotFather:

TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE

# The full URL for NeuroSync's status endpoint:

NEUROSYNC_STATUS_URL=[http://127.0.0.1:8001/status](http://127.0.0.1:8001/status)

# The full URL for TradingCore's status endpoint:

CORE_STATUS_URL=[http://127.0.0.1:8000/status](http://127.0.0.1:8000/status)

# The full URL for TradingCore's main command endpoint:

CORE_VALIDATE_URL=[http://127.0.0.1:8000/command/trigger-strategy](http://127.0.0.1:8000/command/trigger-strategy)


PROGRAM LAUNCH COMMAND:

-How to Run

This service is a FastAPI application that runs the Telegram bot as a background task. To launch the service, use an ASGI server like 
Uvicorn:

uvicorn Rolling5.main:app --host 0.0.0.0 --port 8002



COMMAND REFERENCE:

The following commands are available through the Telegram bot interface.


⚙️ SYSTEM CONTROL:

| Telegram Alias | Description |
|---|---|

| /start | Initializes the bot and welcomes the user. |

| /help | Displays a list of available commands. |

| /status | Provides a real-time heartbeat summary of all systems. |

| /sim | Switches the system to dry run mode. |

| /live | Returns the system to live trading mode. |

| /halt | Manually stops all trading activity. |

| /allclear | Resumes trading activity after a halt. |

| /sync | Performs a manual sync verification. |


📊 PERFORMANCE & BACKTESTING:

| Telegram Alias | Description |
|---|---|

| /evaluate | Runs a full performance analysis. |

| /accuracy | Requests a detailed accuracy trace check. |

| /optimize | Triggers a 24h data refinement pass. |

| /backtest [file] | Runs a custom backtest on a specified dataset. |


🧰 MAINTENANCE & DEBUG:

| Telegram Alias | Description |
|---|---|

| /cleanup | Deletes old log files. |

| /report | Generates a full report on systems and trades. |


💰 CAPITAL & TRADE MANAGEMENT:

| Telegram Alias | Description |
|---|---|

| /trade [strategy] | Triggers the AI analysis pipeline for a given strategy. |

| /withdraw [amount] | Withdraws capital at a specified threshold. |

| /vol_on | Enables the volume skew filter. |

| /vol_off | Disables the volume skew filter. |

END OF DOCUMENT 
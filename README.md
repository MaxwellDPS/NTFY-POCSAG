# NTFY POCSAG Bridge

This project is a proof-of-concept (POC) for a NTFY-to-POCSAG bridge. It listens for events on a specified [ntfy.sh](https://ntfy.sh) topic and relays them as POCSAG messages using `rpitx`.

## Prerequisites

- Docker and Docker Compose installed on your system.
- A Raspberry Pi with GPIO access for using `rpitx` (the software leverages the Raspberry Pi's hardware).

## Installation and Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/ntfy-pocsag-bridge.git
   cd ntfy-pocsag-bridge
   ```

2. Create and edit the .env file:

Create a .env file in the project directory based on the template below. This file will be used to configure the project parameters.

```bash
cp .env.sample .env
```

Create a .env file with the following variables:

```ini
# NTFY Configuration
NTFY_TOPIC=T0PIc                 # The NTFY topic to listen to for events
NTFY_URL=https://ntfy.sh         # Base URL for NTFY, typically https://ntfy.sh

# POCSAG Configuration
POCSAG_FREQ=915000000            # Frequency for POCSAG transmission (in Hz) 
POCSAG_TRIES=1                   # Number of transmission attempts per message
DEFAULT_CAPCODE=0000420          # Default pager capcode to send messages to

# Bridge Options
USE_TITLE_CAPCODE=true           # Use the title of the NTFY event as the CAPCODE
SILENCE_OVERRIDE_THRESHOLD=4     # Override and trigger the tone-only message at high priority
LOG_LEVEL=info                   # Logging level (error, warning, info, debug)
```


3. Build and run the Docker container using Docker Compose:

```bash
docker-compose up --build
```
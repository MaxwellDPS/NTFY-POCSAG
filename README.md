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

#! /usr/bin/env python3
"""NTFY POCSAG BRIDGE
"""
import os
import json
import logging
from subprocess import Popen, PIPE

import sseclient

IS_YES = ['true', 't', 'yes', 'yeet', 'duh', '1'] # if you use 1 you should feel dumb

class POCSAGMessageException(Exception):
    """Bad POCSAG RELAY MESSAGE
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SSEBridge:
    """
    SSE to POCSAG Bridge
    """
    def __init__(
        self,
        ntfy_topic: str | None,
        ntfy_url: str | None = "https://ntfy.sh",
        pocsag_freq: int = 915000000,
        pocsag_tries: int = 1,
        use_title_capcode: bool = True,
        silence_override_threshold: int = 4,    # NTFY Priority (high: 4)
        default_capcode: int | str | None = None,
        log_level: int = logging.INFO,
        **kwargs
    ) -> None:
        self.logger = logging.getLogger("POCSAG BRIDGE")
        self.logger.setLevel(log_level)

        if not ntfy_topic:
            raise ValueError("YOU MUST SET AN NTFY TOPIC")

        self.ntfy_url = ntfy_url if ntfy_url else "https://ntfy.sh"

        self.url = f"{self.ntfy_url}/{ntfy_topic}/sse"
        self.default_capcode = default_capcode
        self.use_title_capcode = use_title_capcode

        self.pocsag_freq = pocsag_freq
        self.pocsag_tries = pocsag_tries
        self.silence_override_threshold = silence_override_threshold

        self.sse_client = sseclient.SSEClient(self.url, **kwargs)


    def get_func_code(self, event_data: dict) -> int:
        """Gets the priority of the message and sets the function code

        Assumes the pager is set as follows

        Func Code:   1   2  3  4
        POSCAG MODE: A   T  A  T
        ALERT OVRD:  🔕 🔕 🔔 🔔

        Args:
            event_data (dict): The SSE event JSON

        This then will 

        Returns:
            int: POSCAG Func code
        """
        priority_level = event_data.get("priority", 3)
        message = event_data.get("message", None)


        if message in ("triggered", "tone")  or not message:
            if priority_level >= self.silence_override_threshold:
                return 3    # FUNC CODE 3   - OVERRIDE AND TONE ONLY 🔔
            return 1        # FUNC CODE 1   - TONE ONLY 🔕
        else:
            if priority_level >= self.silence_override_threshold:
                return 2    # FUNC CODE 2   - OVERRIDE AND ALPHANUMERIC 🔔
            return 0        # FUNC CODE 0   - ALPHANUMERIC ONLY 🔕

    def get_recpt_capcode(self, event_data: dict) -> int:
        """_summary_

        Args:
            event_data (dict): The SSE event JSON

        Returns:
            int: CAPCODE recpt
        """

        if self.use_title_capcode:
            try:
                return int(event_data.get("title",""))
            except ValueError: pass

        try:    # Get code in message like <CODE>:<MSG> 1234:ABCFG
            return int(event_data.get("message","").split(":")[0])
        except (IndexError, ValueError): pass


        if not self.default_capcode:
            self.logger.critical("[!!] NO CAPCODE")
            raise POCSAGMessageException("NO CAPCODE")
        else:
            return int(self.default_capcode)

    def generate_message(self, event_data: dict, func_code: int) -> str:
        """Generates the message to send to the pager

        Args:
            event_data (dict): The SSE event JSON
            func_code (int): The POCSAG Func code

        Assumes the pager is set as follows

        Func Code:   1   2  3  4    (Code is from an index 0 ie 0 1 2 3)
        POSCAG MODE: A   T  A  T
        ALERT OVRD:  🔕 🔕 🔔 🔔


        Returns:
            str: message to send to the pager
        """

        # Gets Message and title
        message = event_data.get("message", None)
        title = event_data.get("title", None)

        if func_code % 2 != 0:  # Odd Func codes are tone only
            message = "[TONE ONLY]"

        # If there is a title add it to the message
        if (title and message) and not self.use_title_capcode:
            message = f"{title} - {message}"

        return message

    def do_the_thing(self, event_data: dict) -> None:
        """Process and relay the message

        Args:
            event_data (dict): The SSE event JSON
        """
        # Determine func_code value
        func_code = self.get_func_code(event_data)

        # Gets the Dest Capcode
        recipient_capcode = self.get_recpt_capcode(event_data)

        # Generate the message
        message = self.generate_message(event_data, func_code=func_code)

        # Make the RPITX message
        pocsag_message = f" {recipient_capcode}:{message}"

        # Format and run the command
        self.logger.warning(f"NEW MESSAGE RELAY: [{recipient_capcode}]: {func_code} {message}")

        # Execute the command
        p = Popen(
            ['pocsag', '-f', str(self.pocsag_freq), '-t', '1', '-b', str(func_code)],
            stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True
        )
        p.communicate(input=pocsag_message)


    def start(self) -> None:
        """Listen for events from SSE stream
        """
        self.logger.info(f"LISTENING ON {self.url}")

        # Iterate over the events
        for event in self.sse_client:
            self.logger.debug(event)

            # Parse the event data, expecting JSON format
            try:
                if event.event != "message":    # Ignore non message events
                    continue

                event_data = json.loads(event.data)

                self.do_the_thing(event_data)

            except json.JSONDecodeError:
                self.logger.error("Received non-JSON event. Skipping...")
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    match log_level:
        case "error":
            log_level = logging.ERROR
        case "warning":
            log_level = logging.ERROR
        case "info":
            log_level = logging.ERROR
        case "debug":
            log_level = logging.ERROR

    bridge = SSEBridge(
        ntfy_topic = os.getenv('NTFY_TOPIC'),
        ntfy_url = os.getenv('NTFY_URL'),
        pocsag_freq = int(os.getenv("POCSAG_FREQ", '915000000')),
        pocsag_tries = int(os.getenv("POCSAG_TRIES", '1')),
        default_capcode = os.getenv("DEFAULT_CAPCODE"),
        use_title_capcode = os.getenv("USE_TITLE_CAPCODE", "false").lower() in IS_YES,
        silence_override_threshold = int(os.getenv("SILENCE_OVERRIDE_THRESHOLD", '4')),
    )

    bridge.start()

#!/usr/bin/python3

# Note that running python with the `-u` flag is required on Windows,
# in order to ensure that stdin and stdout are opened in binary, rather
# than text, mode.

import json
import sys
import struct
import os
from pathlib import Path
from tempfile import gettempdir

def get_communication_dir_path():
    """Returns directory that is used by command-server for communication

    Returns:
        Path: The path to the communication dir
    """
    suffix = ""

    # NB: We don't suffix on Windows, because the temp dir is user-specific
    # anyways
    if hasattr(os, "getuid"):
        suffix = f"-{os.getuid()}"

    return Path(gettempdir()) / f"browser-command-server{suffix}"

communication_dir_path = get_communication_dir_path()
if not communication_dir_path.exists():
  communication_dir_path.mkdir(parents=True, exist_ok=True)
request_path = communication_dir_path / "request.json"
response_path = communication_dir_path / "response.json"

# Read a message from stdin and decode it.
def get_message():
    raw_length = sys.stdin.buffer.read(4)

    if not raw_length:
        sys.exit(0)
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)

# Encode a message for transmission, given its content.
def encode_message(message_content):
    encoded_content = json.dumps(message_content).encode("utf-8")
    encoded_length = struct.pack('=I', len(encoded_content))
    #  use struct.pack("10s", bytes), to pack a string of the length of 10 characters
    return {'length': encoded_length, 'content': struct.pack(str(len(encoded_content))+"s",encoded_content)}

# Send an encoded message to stdout.
def send_message(encoded_message):
    sys.stdout.buffer.write(encoded_message['length'])
    sys.stdout.buffer.write(encoded_message['content'])
    sys.stdout.buffer.flush()

while True:
    message = get_message()
    if message == "ping":
        file = open(response_path)
        data = json.loads(file.read())
        os.remove(response_path)
        send_message(encode_message(data))

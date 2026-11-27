# SSH Honeypot

A small, low-interaction Python project for learning about SSH honeypots in a controlled environment.

The project is intended to record limited connection metadata, such as the source address and attempted username. It must not store passwords or other submitted secrets.

> **Status:** Under development. Keep it bound to your own machine while building and testing.

## Project structure

```text
.
├── config/
│   └── honeypot.ini
├── keys/
├── logs/
├── src/
│   └── ssh_honeypot/
│       ├── __init__.py
│       └── server.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

- Python 3
- Packages listed in `requirements.txt`

## Setup

From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

To leave the virtual environment, run:

```bash
deactivate
```

## Configuration

Edit `config/honeypot.ini` to set the listener address, port, and log-file path.

For local development, use:

```ini
[server]
bind_address = 127.0.0.1
port = 2222

[logging]
log_file = logs/attempts.log
```

Keep the listener on `127.0.0.1` while developing. Do not put passwords, API keys, or other secrets in the config file.

## Running

Run the server from the project root:

```bash
python src/ssh_honeypot/server.py
```

The server implementation is still under development, so this command will work once `server.py` has been implemented.

## Testing

Test only against the local listener with dummy credentials. For example, if the server is listening on port `2222`:

```bash
ssh -p 2222 testuser@127.0.0.1
```

Check that the log records only the intended metadata and contains no password.

## Data handling

- Do not store, print, or otherwise retain passwords submitted by clients.
- Treat connection logs as sensitive because they may contain IP addresses and usernames.
- Keep logs out of public repositories.
- Keep generated host keys private and out of version control.

## Safety

Use this project only on systems and networks you own or are authorized to test. Keep it isolated during development. Do not expose it to the internet without first reviewing the security, privacy, and authorization implications.


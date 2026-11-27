# Low-Interaction SSH Honeypot

A small Python SSH honeypot for controlled network security research. It uses Paramiko to handle SSH protocol details, records connection and authentication-attempt metadata, and rejects authentication attempts. It does not provide a shell or real system access.

## Features

- Configurable bind address, port, log path, and SSH host-key path
- Logs timestamps, source IPs, attempted usernames, and authentication methods
- Does not log or retain submitted passwords
- Rejects authentication attempts and does not execute commands

## Requirements

- Python 3.10 or later
- A virtual environment
- Dependencies listed in `pyproject.toml` and/or `requirements.txt`

## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

If you are installing from `requirements.txt` instead:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Edit `config/honeypot.ini`:

```ini
[server]
bind_address = 127.0.0.1
port = 2222

[logging]
log_file = logs/attempts.log

[key]
key_path = keys/host_ed25519
```

The application validates the configured bind address. If you change it from `127.0.0.1`, make sure the new address is assigned to the VM and is explicitly permitted by the allowlist in `src/ssh_honeypot/server.py`.

## Run

With the virtual environment active:

```bash
ssh-honeypot
```

Alternatively:

```bash
python src/ssh_honeypot/server.py
```

Stop the server with `Ctrl-C`.

## Local test

In a second terminal, connect to the local listener:

```bash
ssh -p 2222 testuser@127.0.0.1
```

Authentication should fail. Review the configured log file for connection and authentication-attempt events. Do not use a real password for testing.

## Logs and host keys

The application creates the log and key directories as needed. The SSH host key is generated on first run and reused on later runs. Keep the `keys/` directory private.

Logs may contain source IP addresses and usernames, which can be sensitive. Restrict access to the log files and rotate or delete them according to your research needs.

## Safety

- Run only in an isolated virtual machine or similarly controlled environment.
- Restrict inbound connections to authorized test sources.
- Restrict outbound network traffic from the VM.
- Do not run the honeypot on a production host or a machine containing sensitive data.
- Do not add shell access, command execution, or password/key logging.
- Keep the bind address and firewall configuration limited to the intended test network.
- Test only on networks and systems you are authorized to monitor.

## Project layout

```text
config/
  honeypot.ini
src/
  ssh_honeypot/
    __init__.py
    server.py
logs/
keys/
requirements.txt
pyproject.toml
```

## Development

Activate the virtual environment before running or editing the project:

```bash
source .venv/bin/activate
```

Install the package in editable mode after changing project metadata or dependencies:

```bash
python -m pip install -e .
```

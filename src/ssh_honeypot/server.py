from __future__ import annotations

import json
import logging
import socket
import threading
import time
from configparser import ConfigParser
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import paramiko
from paramiko.common import AUTH_FAILED


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "honeypot.ini"


def load_settings() -> tuple[str, int, Path, Path]:
    config = ConfigParser()

    if not config.read(CONFIG_PATH):
        raise FileNotFoundError(f"Could not read {CONFIG_PATH}")

    host = config.get("server", "bind_address", fallback="127.0.0.1")
    port = config.getint("server", "port", fallback=2222)
    log_path = ROOT / config.get(
        "logging", "log_file", fallback="logs/attempts.log"
    )
    key_path = ROOT / config.get(
        "key", "key_path", fallback="keys/host_ed25519"
    )

    allowed_hosts = {"127.0.0.1"}  # Add private IP of server
    if host not in allowed_hosts:
        raise ValueError(f"Host must be one of: {', '.join(sorted(allowed_hosts))}")

    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")

    return host, port, log_path, key_path

def setup_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ssh_honeypot")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger

def log_event(logger: logging.Logger, event: str, **fields: object) -> None:
    record = {
            "timestamp":datetime.now(ZoneInfo("Europe/Warsaw")).isoformat(),
            "event":event,
            **fields,
            }
    logger.info(json.dumps(record, ensure_ascii=True))

class HoneypotAuth(paramiko.ServerInterface):
    def __init__(self, logger: logging.Logger, source_ip: str) -> None:
        self.logger = logger
        self.source_ip = source_ip

    def _record_username(self, username: str, method: str) -> None:
        log_event(
                self.logger,
                "auth_attempt",
                source_ip=self.source_ip,
                username=username[:256],
                method=method,
                )

    def get_allowed_auths(self, username: str) -> str:
        return "password,publickey"

    def check_auth_none(self, username: str) -> int:
        self._record_username(username, "password")
        return AUTH_FAILED

    def check_auth_password(self, username: str, password: str) -> int:
        self._record_username(username, "password")
        return AUTH_FAILED

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        self._record_username(username, "publickey")
        return AUTH_FAILED

def handle_client(client: socket.socket, address: tuple[str, int], host_key: paramiko.PKey, logger: logging.Logger) -> None:
    source_ip = address[0]
    log_event(logger, "connection", source_ip=source_ip)

    transport = None
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)
        transport.start_server(server=HoneypotAuth(logger, source_ip))

        deadline = time.monotonic() + 20
        while transport.is_active() and time.monotonic() < deadline:
            time.sleep(0.2)
    except (paramiko.SSHException, OSError, EOFError):
        pass
    finally:
        if transport is not None:
            transport.close()
        else:
            client.close()

def main() -> None:
    host, port, log_path, key_path = load_settings()
    logger = setup_logger(log_path)

    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        host_key = paramiko.RSAKey.from_private_key_file(str(key_path))
    else:
        host_key = paramiko.RSAKey.generate(2048)
        host_key.write_private_key_file(str(key_path))
        key_path.chmod(0o600)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(20)
        log_event(logger, "listener_started", host=host, port=port)
        print(f"Listening on {host}:{port}; press Ctrl-C to stop.")

        try:
            while True:
                client, address = listener.accept()
                threading.Thread(
                    target=handle_client,
                    args=(client, address, host_key, logger),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            print("\nStopping honeypot.")


if __name__ == "__main__":
    main()

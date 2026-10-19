"""
Safety Guardrails for Black-Box Attack Simulator.

CRITICAL SAFETY CONSTRAINT:
This simulator must ONLY target local sandboxes (localhost, loopback IP 127.0.0.1,
or designated internal Docker service 'training_target').
Under NO circumstances can the engine scan, probe, or interact with external internet
hosts, internal corporate LANs, cloud metadata services, or public IP addresses.
"""

from urllib.parse import urlparse
import ipaddress
from typing import Set

ALLOWED_HOSTNAMES: Set[str] = {
    "localhost",
    "127.0.0.1",
    "::1",
    "[::1]",
    "training_target",
    "testserver",  # Used by starlette/fastapi TestClient
    "host.docker.internal",
}

class SecurityViolationError(ValueError):
    """Raised when an unsafe, non-local, or external target is specified."""
    pass


def validate_target_url(url: str) -> str:
    """
    Validates that a URL targets exclusively an authorized local sandbox.
    
    Raises SecurityViolationError if the URL targets:
    - Any external domain (e.g., google.com, example.com)
    - Any public IP address (e.g., 8.8.8.8)
    - Any non-loopback private LAN IP (e.g., 192.168.1.1, 10.0.0.1)
    - Any cloud metadata service (e.g., 169.254.169.254)
    - Any non-HTTP(S) protocol (e.g., file://, ftp://, gopher://)
    - Any sneaky domain name trick (e.g., localhost.attacker.com)
    
    Returns the sanitized URL string on success.
    """
    if not url or not isinstance(url, str):
        raise SecurityViolationError("Target URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise SecurityViolationError(
            f"Prohibited protocol '{parsed.scheme}'. Only local 'http' and 'https' are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SecurityViolationError(f"Target URL '{url}' has no valid hostname.")

    hostname_lower = hostname.lower()

    # Check against allowed exact names
    if hostname_lower in ALLOWED_HOSTNAMES:
        return url

    # Check if hostname is an IP address
    try:
        ip = ipaddress.ip_address(hostname_lower.strip("[]"))
        if ip.is_loopback:
            return url
        else:
            raise SecurityViolationError(
                f"SAFETY VIOLATION: Target IP '{hostname}' is not a loopback address. "
                f"Simulations are strictly restricted to local sandboxes."
            )
    except ValueError:
        # Not an IP address, check domain name
        pass

    # Any domain name not in ALLOWED_HOSTNAMES is rejected
    raise SecurityViolationError(
        f"SAFETY VIOLATION: Target host '{hostname}' is not an authorized local training target. "
        f"External domains and network scanning are strictly prohibited."
    )


def is_safe_target(url: str) -> bool:
    """Returns True if the target URL complies with safety guardrails, False otherwise."""
    try:
        validate_target_url(url)
        return True
    except SecurityViolationError:
        return False

import pytest
import sys
import os

# Add backend to path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.safety import validate_target_url, is_safe_target, SecurityViolationError


def test_safety_allows_valid_local_targets():
    """Verify that localhost, loopback IPs, and authorized docker containers are permitted."""
    valid_targets = [
        "http://localhost:8001",
        "http://localhost:8000/api/health",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8001/api/vulnerable/user/settings",
        "http://[::1]:8001",
        "http://training_target:8001",
        "http://testserver/api/test",
        "http://host.docker.internal:8001",
    ]
    for target in valid_targets:
        assert validate_target_url(target) == target
        assert is_safe_target(target) is True


def test_safety_blocks_public_ips():
    """Verify that public internet IP addresses are strictly rejected."""
    public_ips = [
        "http://8.8.8.8:8080",
        "http://1.1.1.1",
        "http://142.250.190.46",
        "https://93.184.216.34/api",
    ]
    for target in public_ips:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError, match="SAFETY VIOLATION"):
            validate_target_url(target)


def test_safety_blocks_cloud_metadata_service():
    """Verify that cloud metadata IP (169.254.169.254) is strictly blocked."""
    metadata_targets = [
        "http://169.254.169.254",
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/computeMetadata/v1/",
    ]
    for target in metadata_targets:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError, match="SAFETY VIOLATION"):
            validate_target_url(target)


def test_safety_blocks_private_lan_ips():
    """Verify that internal corporate/home LAN non-loopback IPs are blocked."""
    lan_ips = [
        "http://192.168.1.1",
        "http://192.168.1.50:8080",
        "http://10.0.0.1",
        "http://10.200.0.5",
        "http://172.16.0.1",
    ]
    for target in lan_ips:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError, match="SAFETY VIOLATION"):
            validate_target_url(target)


def test_safety_blocks_external_domains():
    """Verify that arbitrary internet domains are strictly rejected."""
    external_domains = [
        "http://example.com",
        "https://google.com/api",
        "http://target.org:8000",
        "http://evil.corp/payload",
        "http://scanme.nmap.org",
    ]
    for target in external_domains:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError, match="SAFETY VIOLATION"):
            validate_target_url(target)


def test_safety_blocks_domain_tricks_and_spoofing():
    """Verify that subdomain spoofing attempts (e.g. localhost.evil.com) are rejected."""
    spoofed = [
        "http://localhost.attacker.com",
        "http://training_target.co",
        "http://127.0.0.1.nip.io",
        "http://sub.localhost.com",
    ]
    for target in spoofed:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError, match="SAFETY VIOLATION"):
            validate_target_url(target)


def test_safety_blocks_non_http_protocols():
    """Verify that non-HTTP schemes are rejected."""
    unsafe_schemes = [
        "file:///etc/passwd",
        "ftp://localhost:21",
        "gopher://localhost:70",
        "ws://localhost:8001",
    ]
    for target in unsafe_schemes:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError, match="Prohibited protocol"):
            validate_target_url(target)


def test_safety_blocks_empty_and_malformed():
    """Verify that empty, None, or broken inputs are rejected."""
    invalid_inputs = ["", "   ", None, "not_a_url"]
    for target in invalid_inputs:
        assert is_safe_target(target) is False
        with pytest.raises(SecurityViolationError):
            validate_target_url(target)

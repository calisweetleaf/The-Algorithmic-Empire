#!/usr/bin/env python3
"""
ARCS Network Telemetry - Comprehensive Pytest Suite
=====================================================
Tests for PacketAnalysisEngine, DeviceDiscoveryEngine, and NetworkTelemetryEngine.
"""

import sys
import os
import asyncio
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from collections import Counter, defaultdict
from unittest.mock import patch, MagicMock
from types import ModuleType

import pytest
import numpy as np

# ---------------------------------------------------------------------------
# Ensure project root is importable
# ---------------------------------------------------------------------------
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Mock heavy third-party modules that may not be installed in test venv
# ---------------------------------------------------------------------------
_MOCK_MODULES = [
    "netifaces", "pcapy", "dpkt",
    "scapy", "scapy.all",
    "scapy.layers", "scapy.layers.inet", "scapy.layers.inet6",
    "scapy.layers.l2", "scapy.layers.dhcp", "scapy.layers.dns",
    "scapy.layers.http", "scapy.layers.tls", "scapy.layers.smb",
    "scapy.layers.netbios",
    "pyshark", "netaddr", "maxminddb",
    "onnxruntime",
    "aiohttp",
]

for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        mock_mod = MagicMock()
        # Give sub-module mocks proper __path__ for package traversal
        mock_mod.__path__ = []
        sys.modules[mod_name] = mock_mod

from ARCS.network_telemetry import (
    NetworkIntelligenceType,
    TelemetryAggression,
    ProtocolType,
    DeviceCategory,
    ThreatIndicatorType,
    NetworkDevice,
    NetworkFlow,
    ThreatIndicator,
    BehavioralBaseline,
    PacketAnalysisEngine,
    DeviceDiscoveryEngine,
    NetworkTelemetryEngine,
)

from ARCS.tests.conftest import MockIntelligenceDB


# ======================================================================
# Enum Tests
# ======================================================================

class TestNetworkIntelligenceTypeEnum:
    def test_all_members(self):
        expected = {
            "DEVICE_DISCOVERY", "PROTOCOL_ANALYSIS", "TRAFFIC_PATTERN",
            "BEHAVIORAL_BASELINE", "ANOMALY_DETECTION", "THREAT_INDICATOR",
            "VULNERABILITY_EXPOSURE", "COMMUNICATION_METADATA",
            "GEOLOCATION_INTELLIGENCE", "INFRASTRUCTURE_MAPPING",
        }
        assert {m.name for m in NetworkIntelligenceType} == expected

    def test_values_are_lowercase(self):
        for m in NetworkIntelligenceType:
            assert m.value == m.name.lower()


class TestTelemetryAggressionEnum:
    EXPECTED = {
        "PASSIVE_MONITORING": 1,
        "ACTIVE_FINGERPRINTING": 2,
        "DEEP_INSPECTION": 3,
        "BEHAVIORAL_PROFILING": 4,
        "AGGRESSIVE_CORRELATION": 5,
    }

    def test_all_levels(self):
        assert {m.name for m in TelemetryAggression} == set(self.EXPECTED.keys())

    def test_integer_values(self):
        for name, value in self.EXPECTED.items():
            assert TelemetryAggression[name].value == value


class TestProtocolTypeEnum:
    def test_all_protocols(self):
        expected = {
            "HTTP_HTTPS", "DNS", "DHCP", "ARP", "ICMP", "SSH", "FTP",
            "SMTP", "SMB_CIFS", "SNMP", "LDAP", "RDP", "VNC", "TELNET", "CUSTOM",
        }
        assert {m.name for m in ProtocolType} == expected


class TestDeviceCategoryEnum:
    def test_all_categories(self):
        expected = {
            "WORKSTATION", "SERVER", "NETWORK_DEVICE", "IOT_DEVICE",
            "MOBILE_DEVICE", "PRINTER", "SECURITY_CAMERA",
            "INDUSTRIAL_CONTROL", "UNKNOWN", "SUSPICIOUS",
        }
        assert {m.name for m in DeviceCategory} == expected


class TestThreatIndicatorTypeEnum:
    def test_all_types(self):
        expected = {
            "SUSPICIOUS_TRAFFIC", "ANOMALOUS_BEHAVIOR", "KNOWN_BAD_IP",
            "MALICIOUS_DOMAIN", "COMMAND_CONTROL", "DATA_EXFILTRATION",
            "LATERAL_MOVEMENT", "RECONNAISSANCE", "EXPLOIT_ATTEMPT",
            "MALWARE_COMMUNICATION",
        }
        assert {m.name for m in ThreatIndicatorType} == expected


# ======================================================================
# Dataclass Construction Tests
# ======================================================================

class TestNetworkDeviceDataclass:
    def test_construct(self):
        now = datetime.now(timezone.utc)
        dev = NetworkDevice(
            device_id="dev_001",
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_addresses=["192.168.1.10"],
            device_category=DeviceCategory.WORKSTATION,
            vendor="Dell",
            hostname="workstation-01",
            operating_system="Windows",
            open_ports=[22, 80, 443],
            services={22: "ssh", 80: "http", 443: "https"},
            first_seen=now,
            last_seen=now,
        )
        assert dev.total_bytes_sent == 0
        assert dev.trust_score == 0.5
        assert dev.anomaly_score == 0.0
        assert dev.protocol_usage == {}
        assert dev.communication_partners == set()


class TestNetworkFlowDataclass:
    def test_construct(self):
        now = datetime.now(timezone.utc)
        flow = NetworkFlow(
            flow_id="flow_001",
            source_ip="192.168.1.10",
            destination_ip="10.0.0.1",
            source_port=54321,
            destination_port=443,
            protocol="tcp",
            start_timestamp=now,
            end_timestamp=None,
            bytes_sent=1024,
            bytes_received=2048,
            packet_count=50,
            flags=["SYN", "ACK"],
            flow_state="established",
        )
        assert flow.application_protocol is None
        assert flow.threat_indicators == []


class TestThreatIndicatorDataclass:
    def test_construct(self):
        ind = ThreatIndicator(
            indicator_id="ind_001",
            indicator_type=ThreatIndicatorType.SUSPICIOUS_TRAFFIC,
            indicator_value="192.168.1.100",
            confidence_score=0.7,
            severity_level=5,
            detection_timestamp=datetime.now(timezone.utc),
            source_device="dev_001",
            destination_device="dev_002",
            protocol="tcp",
            evidence_data={"port": 4444, "payload": "suspicious"},
        )
        assert ind.false_positive_probability == 0.0
        assert ind.mitigation_recommendations == []
        assert ind.correlation_ids == []


class TestBehavioralBaselineDataclass:
    def test_construct(self):
        bl = BehavioralBaseline(
            device_id="dev_001",
            baseline_id="bl_001",
            observation_period=timedelta(days=7),
            traffic_patterns={"average_volume": 10000},
            communication_patterns={"unique_peers": 25},
            protocol_distribution={"tcp": 0.7, "udp": 0.2, "icmp": 0.1},
            temporal_patterns={"peak_hour": 14},
            bandwidth_profile={"avg_bps": 50000},
            connection_behavior={"average_connections": 100},
            anomaly_thresholds={"volume_ratio": 3.0},
            last_updated=datetime.now(timezone.utc),
            confidence_level=0.85,
        )
        assert bl.confidence_level == 0.85
        assert bl.protocol_distribution["tcp"] == 0.7


# ======================================================================
# PacketAnalysisEngine Tests
# ======================================================================

class TestPacketAnalysisEngine:
    """Test PacketAnalysisEngine helper methods."""

    @patch("ARCS.network_telemetry.netifaces")
    def _make_engine(self, mock_netifaces):
        """Helper to create engine without touching real network interfaces."""
        mock_netifaces.interfaces.return_value = ["eth0"]
        mock_netifaces.AF_INET = 2
        mock_netifaces.ifaddresses.return_value = {
            2: [{"addr": "192.168.1.50", "netmask": "255.255.255.0"}]
        }
        engine = PacketAnalysisEngine(interface="test0", promiscuous=False)
        return engine

    def test_calculate_entropy_empty(self):
        engine = self._make_engine()
        assert engine._calculate_entropy(b"") == 0.0

    def test_calculate_entropy_uniform(self):
        """All-identical bytes → entropy = 0."""
        engine = self._make_engine()
        data = b"\x41" * 100  # all 'A'
        assert engine._calculate_entropy(data) == pytest.approx(0.0)

    def test_calculate_entropy_mixed(self):
        """Mixed data → positive entropy."""
        engine = self._make_engine()
        data = bytes(range(256)) * 4  # every byte 4 times
        entropy = engine._calculate_entropy(data)
        # max entropy for 256 symbols is 8.0
        assert entropy == pytest.approx(8.0, abs=0.01)

    def test_calculate_entropy_two_symbols(self):
        """Equal mix of two symbols → entropy = 1.0."""
        engine = self._make_engine()
        data = b"\x00\x01" * 50
        assert engine._calculate_entropy(data) == pytest.approx(1.0, abs=0.01)

    def test_rule_based_classification_http(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 80, "protocols": []}) == "http"

    def test_rule_based_classification_https(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 443, "protocols": []}) == "https"

    def test_rule_based_classification_dns(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 53, "protocols": []}) == "dns"

    def test_rule_based_classification_ssh(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 22, "protocols": []}) == "ssh"

    def test_rule_based_classification_ftp(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 21, "protocols": []}) == "ftp"

    def test_rule_based_classification_smtp(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 25, "protocols": []}) == "smtp"

    def test_rule_based_classification_smb(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 445, "protocols": []}) == "smb"

    def test_rule_based_classification_icmp(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 0, "protocols": ["icmp"]}) == "icmp"

    def test_rule_based_classification_other(self):
        engine = self._make_engine()
        assert engine._rule_based_classification({"destination_port": 9999, "protocols": []}) == "other"

    def test_prepare_feature_vector_shape(self):
        engine = self._make_engine()
        features = {
            "size": 100, "protocols": ["tcp"], "source_port": 54321,
            "destination_port": 443, "payload_size": 50, "payload_entropy": 3.0,
            "flags": ["SYN"], "ttl": 64, "window_size": 65535, "ip_version": 4,
        }
        vec = engine._prepare_feature_vector(features)
        assert vec.shape == (1, 32)
        assert vec.dtype == np.float32


# ======================================================================
# DeviceDiscoveryEngine Tests
# ======================================================================

class TestDeviceDiscoveryEngine:
    """Test DeviceDiscoveryEngine helper methods."""

    def _make_device(self, **overrides):
        now = datetime.now(timezone.utc)
        defaults = dict(
            device_id="dev_test",
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_addresses=["192.168.1.10"],
            device_category=DeviceCategory.UNKNOWN,
            vendor=None,
            hostname=None,
            operating_system=None,
            open_ports=[],
            services={},
            first_seen=now,
            last_seen=now,
        )
        defaults.update(overrides)
        return NetworkDevice(**defaults)

    @patch("ARCS.network_telemetry.netifaces")
    @patch("ARCS.network_telemetry.maxminddb")
    def _make_engine(self, mock_maxminddb, mock_netifaces):
        mock_netifaces.interfaces.return_value = ["eth0"]
        mock_netifaces.AF_INET = 2
        mock_netifaces.ifaddresses.return_value = {
            2: [{"addr": "192.168.1.50", "netmask": "255.255.255.0"}]
        }
        mock_maxminddb.open_database.side_effect = Exception("no db")
        db = MockIntelligenceDB()
        engine = DeviceDiscoveryEngine(db, subnets=["192.168.1.0/24"])
        return engine

    def test_guess_os_linux(self):
        engine = self._make_engine()
        assert engine._guess_os_from_ttl(64) == "Linux/Unix"
        assert engine._guess_os_from_ttl(50) == "Linux/Unix"

    def test_guess_os_windows(self):
        engine = self._make_engine()
        assert engine._guess_os_from_ttl(128) == "Windows"
        assert engine._guess_os_from_ttl(100) == "Windows"

    def test_guess_os_network_device(self):
        engine = self._make_engine()
        assert engine._guess_os_from_ttl(255) == "Network Device"
        assert engine._guess_os_from_ttl(200) == "Network Device"

    def test_categorize_server(self):
        engine = self._make_engine()
        dev = self._make_device(
            open_ports=[22, 80, 443, 3306, 5432],
            services={22: "ssh", 80: "http"},
        )
        assert engine._categorize_device(dev) == DeviceCategory.SERVER

    def test_categorize_network_device(self):
        engine = self._make_engine()
        dev = self._make_device(vendor="Cisco")
        assert engine._categorize_device(dev) == DeviceCategory.NETWORK_DEVICE

    def test_categorize_iot(self):
        engine = self._make_engine()
        dev = self._make_device(hostname="smart-thermostat-01")
        assert engine._categorize_device(dev) == DeviceCategory.IOT_DEVICE

    def test_categorize_printer(self):
        engine = self._make_engine()
        dev = self._make_device(open_ports=[631])
        assert engine._categorize_device(dev) == DeviceCategory.PRINTER

    def test_categorize_workstation_default(self):
        engine = self._make_engine()
        dev = self._make_device(
            open_ports=[22],
            vendor="Unknown",
            hostname="desktop-01",
        )
        assert engine._categorize_device(dev) == DeviceCategory.WORKSTATION

    def test_categorize_industrial_control(self):
        engine = self._make_engine()
        dev = self._make_device(open_ports=[502, 102])
        assert engine._categorize_device(dev) == DeviceCategory.INDUSTRIAL_CONTROL

    def test_categorize_mobile(self):
        engine = self._make_engine()
        dev = self._make_device(vendor="Apple")
        assert engine._categorize_device(dev) == DeviceCategory.MOBILE_DEVICE

    def test_calculate_trust_score_trusted_vendor(self):
        engine = self._make_engine()
        dev = self._make_device(vendor="Cisco", hostname="router1", open_ports=[22])
        score = engine._calculate_trust_score(dev)
        assert 0 <= score <= 1
        # Cisco is trusted, few ports, proper hostname → relatively high trust
        assert score > 0.6

    def test_calculate_trust_score_risky_services(self):
        engine = self._make_engine()
        dev = self._make_device(
            vendor="Unknown",
            services={23: "telnet", 21: "ftp"},
            open_ports=[21, 23],
        )
        score = engine._calculate_trust_score(dev)
        assert 0 <= score <= 1
        # Risky services + unknown vendor → lower trust
        assert score < 0.65

    def test_calculate_trust_score_many_open_ports(self):
        engine = self._make_engine()
        dev = self._make_device(
            vendor="Unknown",
            open_ports=list(range(20, 35)),  # 15 open ports
        )
        score = engine._calculate_trust_score(dev)
        assert 0 <= score <= 1
        assert score < 0.65


# ======================================================================
# NetworkTelemetryEngine Tests
# ======================================================================

class TestNetworkTelemetryEngine:
    """Test top-level NetworkTelemetryEngine init and status."""

    @patch("ARCS.network_telemetry.netifaces")
    def test_init(self, mock_netifaces, tmp_path):
        mock_netifaces.interfaces.return_value = []
        mock_netifaces.AF_INET = 2
        db = MockIntelligenceDB()
        config = tmp_path / "nt.yaml"
        engine = NetworkTelemetryEngine(db, config_path=str(config))
        assert engine.aggression_level == TelemetryAggression.DEEP_INSPECTION
        assert engine.packet_analyzer is None  # Not yet initialized
        assert engine.device_discovery is None
        assert not engine.shutdown_event.is_set()

    @patch("ARCS.network_telemetry.netifaces")
    @pytest.mark.asyncio
    async def test_shutdown(self, mock_netifaces, tmp_path):
        mock_netifaces.interfaces.return_value = []
        mock_netifaces.AF_INET = 2
        db = MockIntelligenceDB()
        engine = NetworkTelemetryEngine(db, config_path=str(tmp_path / "nt.yaml"))
        await engine.shutdown()
        assert engine.shutdown_event.is_set()


# ======================================================================
# NetworkTelemetryEngine._detect_behavioral_anomalies Tests
# ======================================================================

class TestDetectBehavioralAnomalies:
    """Test the _detect_behavioral_anomalies method on NetworkTelemetryEngine."""

    @patch("ARCS.network_telemetry.netifaces")
    def _make_engine(self, mock_netifaces, tmp_path=None):
        mock_netifaces.interfaces.return_value = []
        mock_netifaces.AF_INET = 2
        db = MockIntelligenceDB()
        engine = NetworkTelemetryEngine(db, config_path=str(tmp_path / "nt.yaml") if tmp_path else "config/nt.yaml")
        return engine

    def test_traffic_volume_spike(self, tmp_path):
        engine = self._make_engine(tmp_path=tmp_path)
        baseline = BehavioralBaseline(
            device_id="dev1", baseline_id="bl1",
            observation_period=timedelta(days=7),
            traffic_patterns={"average_volume": 1000},
            communication_patterns={},
            protocol_distribution={"tcp": 0.8},
            temporal_patterns={},
            bandwidth_profile={},
            connection_behavior={"average_connections": 50},
            anomaly_thresholds={},
            last_updated=datetime.now(timezone.utc),
            confidence_level=0.9,
        )
        current = {"traffic_volume": 5000, "connection_frequency": 50}
        anomalies = engine._detect_behavioral_anomalies(current, baseline)
        assert any("traffic_volume_anomaly" in a for a in anomalies)

    def test_connection_spike(self, tmp_path):
        engine = self._make_engine(tmp_path=tmp_path)
        baseline = BehavioralBaseline(
            device_id="dev1", baseline_id="bl1",
            observation_period=timedelta(days=7),
            traffic_patterns={"average_volume": 1000},
            communication_patterns={},
            protocol_distribution={"tcp": 0.8},
            temporal_patterns={},
            bandwidth_profile={},
            connection_behavior={"average_connections": 50},
            anomaly_thresholds={},
            last_updated=datetime.now(timezone.utc),
            confidence_level=0.9,
        )
        current = {"traffic_volume": 1000, "connection_frequency": 200}
        anomalies = engine._detect_behavioral_anomalies(current, baseline)
        assert any("connection_spike" in a for a in anomalies)

    def test_new_protocols(self, tmp_path):
        engine = self._make_engine(tmp_path=tmp_path)
        baseline = BehavioralBaseline(
            device_id="dev1", baseline_id="bl1",
            observation_period=timedelta(days=7),
            traffic_patterns={"average_volume": 1000},
            communication_patterns={},
            protocol_distribution={"tcp": 0.8, "udp": 0.2},
            temporal_patterns={},
            bandwidth_profile={},
            connection_behavior={"average_connections": 50},
            anomaly_thresholds={},
            last_updated=datetime.now(timezone.utc),
            confidence_level=0.9,
        )
        current = {
            "traffic_volume": 1000,
            "connection_frequency": 50,
            "protocol_usage": {"tcp": 100, "udp": 20, "icmp": 5},
        }
        anomalies = engine._detect_behavioral_anomalies(current, baseline)
        assert any("new_protocols" in a for a in anomalies)

    def test_no_anomalies(self, tmp_path):
        engine = self._make_engine(tmp_path=tmp_path)
        baseline = BehavioralBaseline(
            device_id="dev1", baseline_id="bl1",
            observation_period=timedelta(days=7),
            traffic_patterns={"average_volume": 1000},
            communication_patterns={},
            protocol_distribution={"tcp": 0.8, "udp": 0.2},
            temporal_patterns={},
            bandwidth_profile={},
            connection_behavior={"average_connections": 50},
            anomaly_thresholds={},
            last_updated=datetime.now(timezone.utc),
            confidence_level=0.9,
        )
        current = {
            "traffic_volume": 1000,
            "connection_frequency": 50,
            "protocol_usage": {"tcp": 100},
        }
        anomalies = engine._detect_behavioral_anomalies(current, baseline)
        assert anomalies == []

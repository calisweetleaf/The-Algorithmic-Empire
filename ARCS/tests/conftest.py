#!/usr/bin/env python3
"""
ARCS Test Suite - Shared Fixtures and Mocks
============================================
Provides mock dependencies (intelligence DB, aggregation engine) and
factory helpers used across all three ARCS module test files.
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pytest
import numpy as np

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so ARCS modules are importable
# ---------------------------------------------------------------------------
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Mock intelligence database
# ---------------------------------------------------------------------------

@dataclass
class MockIntelRecord:
    """Minimal record returned by MockIntelligenceDB.advanced_query."""
    record_id: str
    intelligence_type: str
    collection_timestamp: datetime
    source_system: str = "test"
    source_reliability: float = 0.8
    confidence_score: float = 0.7
    threat_level: int = 5
    priority_score: float = 0.5
    raw_data: Dict[str, Any] = field(default_factory=dict)
    processed_indicators: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MockIntelligenceDB:
    """Async-compatible mock that stands in for the real intelligence database."""

    def __init__(self, records: Optional[List[MockIntelRecord]] = None):
        self._records = records or []
        self._stored: List[Any] = []

    async def advanced_query(self, params: Dict[str, Any]) -> list:
        return self._records

    async def store_intelligence(self, record) -> bool:
        self._stored.append(record)
        return True

    async def search_intelligence(self, query: str) -> list:
        return self._records


class MockThreatAggregation:
    """Minimal stand-in for the threat aggregation engine dependency."""
    pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    """Return a MockIntelligenceDB with no pre-loaded records."""
    return MockIntelligenceDB()


@pytest.fixture
def mock_db_with_records():
    """Return a MockIntelligenceDB pre-loaded with sample records."""
    now = datetime.now(timezone.utc)
    records = [
        MockIntelRecord(
            record_id=str(uuid4()),
            intelligence_type="network_telemetry",
            collection_timestamp=now - timedelta(hours=i),
            confidence_score=0.5 + i * 0.1,
            threat_level=5 + i,
            processed_indicators=[
                f"scan_indicator_{i}",
                f"exploit_attempt_{i}",
                f"malware_beacon_{i}",
            ],
            tags=["test"],
            raw_data={"source_ip": f"192.168.1.{100+i}", "port": 443},
        )
        for i in range(5)
    ]
    return MockIntelligenceDB(records=records)


@pytest.fixture
def mock_threat_aggregation():
    return MockThreatAggregation()


@pytest.fixture
def tmp_config_dir(tmp_path):
    """Provide a temporary directory for config / data files so tests never
    touch the real filesystem outside of tmp."""
    return tmp_path


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_threat_input(**overrides):
    """Build a ``ThreatIntelligenceInput`` with sensible defaults.

    Keyword arguments override any default field.
    """
    from ARCS.threat_aggregation import ThreatIntelligenceInput, IntelligenceSource

    defaults = dict(
        input_id=str(uuid4()),
        source=IntelligenceSource.NETWORK_TELEMETRY,
        intelligence_type="suspicious_traffic",
        raw_data={
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "port": 443,
            "protocol": "tcp",
            "payload_size": 1024,
            "anomaly_score": 0.8,
        },
        indicators=["suspicious_traffic", "anomalous_behavior", "high_entropy"],
        confidence_score=0.75,
        collection_timestamp=datetime.now(timezone.utc),
        source_reliability=0.9,
        correlation_keys=["192.168.1.100", "suspicious_traffic"],
    )
    defaults.update(overrides)
    return ThreatIntelligenceInput(**defaults)

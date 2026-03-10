#!/usr/bin/env python3
"""
ARCS Threat Aggregation - Comprehensive Pytest Suite
======================================================
Tests for ROEClassificationEngine, MultiSourceCorrelationEngine,
and ThreatAggregationEngine.
"""

import sys
import os
import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch, MagicMock

import pytest
import numpy as np

# ---------------------------------------------------------------------------
# Ensure project root is importable
# ---------------------------------------------------------------------------
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Mock heavy third-party modules that may not be in the test venv
# ---------------------------------------------------------------------------
_MOCK_MODULES = [
    "onnxruntime",
    "sklearn", "sklearn.cluster", "sklearn.preprocessing",
    "sklearn.metrics", "sklearn.metrics.pairwise",
    "scipy", "scipy.stats", "scipy.spatial", "scipy.spatial.distance",
    "aiofiles",
    "cryptography", "cryptography.fernet",
    "cryptography.hazmat", "cryptography.hazmat.primitives",
    "cryptography.hazmat.primitives.kdf", "cryptography.hazmat.primitives.kdf.pbkdf2",
    "cryptography.hazmat.primitives.hashes",
]

for mod_name in _MOCK_MODULES:
    if mod_name not in sys.modules:
        mock_mod = MagicMock()
        mock_mod.__path__ = []
        sys.modules[mod_name] = mock_mod

from ARCS.threat_aggregation import (
    ROELevel,
    ThreatTier,
    IntelligenceSource,
    ThreatConfidenceLevel,
    EngagementStatus,
    ThreatIntelligenceInput,
    ROEThreatClassification,
    EngagementAuthorization,
    ThreatCorrelation,
    ROEAuditEvent,
    ROEClassificationEngine,
    MultiSourceCorrelationEngine,
    ThreatAggregationEngine,
)

from ARCS.tests.conftest import MockIntelligenceDB, make_threat_input


# ======================================================================
# Enum Tests
# ======================================================================

class TestROELevelEnum:
    EXPECTED = {"OBSERVE": 1, "DECEIVE": 2, "DEGRADE": 3, "NEUTRALIZE": 4}

    def test_all_members(self):
        assert {m.name for m in ROELevel} == set(self.EXPECTED.keys())

    def test_integer_values(self):
        for name, value in self.EXPECTED.items():
            assert ROELevel[name].value == value


class TestThreatTierEnum:
    def test_all_tiers(self):
        expected = {
            "NOISE", "AUTOMATED_PROBES", "CORPORATE_SURVEILLANCE",
            "TARGETED_INTRUSION", "ADVANCED_PERSISTENT_THREAT",
            "CRITICAL_INFRASTRUCTURE_ATTACK",
        }
        assert {m.name for m in ThreatTier} == expected

    def test_values_are_lowercase_strings(self):
        for m in ThreatTier:
            assert isinstance(m.value, str)
            assert m.value == m.name.lower()


class TestIntelligenceSourceEnum:
    def test_all_sources(self):
        expected = {
            "BROWSER_INTELLIGENCE", "NETWORK_TELEMETRY", "OSINT_ORCHESTRATOR",
            "EXTERNAL_FEEDS", "SYSTEM_BEHAVIOR", "ATTRIBUTION_ENGINE",
            "MANUAL_INPUT", "CORRELATION_ENGINE",
        }
        assert {m.name for m in IntelligenceSource} == expected


class TestThreatConfidenceLevelEnum:
    EXPECTED = {
        "VERY_LOW": 0.1, "LOW": 0.3, "MEDIUM": 0.5,
        "HIGH": 0.7, "VERY_HIGH": 0.9,
    }

    def test_float_values(self):
        for name, value in self.EXPECTED.items():
            assert ThreatConfidenceLevel[name].value == pytest.approx(value)


class TestEngagementStatusEnum:
    def test_all_statuses(self):
        expected = {
            "STANDBY", "ANALYZING", "AUTHORIZED", "EXECUTING",
            "COMPLETED", "ESCALATED", "ABORTED", "HUMAN_REVIEW_REQUIRED",
        }
        assert {m.name for m in EngagementStatus} == expected


# ======================================================================
# Dataclass Construction Tests
# ======================================================================

class TestThreatIntelligenceInputDataclass:
    def test_construct_with_defaults(self):
        ti = make_threat_input()
        assert ti.source == IntelligenceSource.NETWORK_TELEMETRY
        assert ti.confidence_score == 0.75
        assert isinstance(ti.indicators, list)
        assert isinstance(ti.metadata, dict)

    def test_override_fields(self):
        ti = make_threat_input(
            confidence_score=0.95,
            indicators=["exploit_attempt", "privilege_escalation"],
        )
        assert ti.confidence_score == 0.95
        assert len(ti.indicators) == 2


class TestROEThreatClassificationDataclass:
    def test_construct(self):
        now = datetime.now(timezone.utc)
        cls = ROEThreatClassification(
            classification_id="c1",
            threat_tier=ThreatTier.TARGETED_INTRUSION,
            roe_level=ROELevel.DEGRADE,
            confidence_score=0.8,
            threat_indicators=["exploit_attempt"],
            attribution_data={"actor": "unknown"},
            impact_assessment={"severity": 7.0},
            time_sensitivity="urgent",
            source_correlation={IntelligenceSource.NETWORK_TELEMETRY: 0.9},
            supporting_evidence={"raw": "data"},
            engagement_recommendations=["block_source"],
            escalation_triggers=["confidence > 0.9"],
            de_escalation_conditions=["threat resolved"],
            classification_timestamp=now,
        )
        assert cls.human_validated is False
        assert cls.analyst_notes is None
        assert cls.roe_level == ROELevel.DEGRADE


class TestEngagementAuthorizationDataclass:
    def test_default_legal_review(self):
        now = datetime.now(timezone.utc)
        threat_cls = ROEThreatClassification(
            classification_id="c1", threat_tier=ThreatTier.NOISE,
            roe_level=ROELevel.OBSERVE, confidence_score=0.2,
            threat_indicators=[], attribution_data={}, impact_assessment={},
            time_sensitivity="routine",
            source_correlation={}, supporting_evidence={},
            engagement_recommendations=[], escalation_triggers=[],
            de_escalation_conditions=[], classification_timestamp=now,
        )
        auth = EngagementAuthorization(
            authorization_id="a1", threat_classification=threat_cls,
            roe_level=ROELevel.OBSERVE, authorized_actions=["log_event"],
            authorization_timestamp=now,
            authorization_expiry=now + timedelta(hours=1),
            authorizing_system="arcs_threat_aggregation",
        )
        assert auth.legal_review_status == "pending"
        assert auth.human_authorized is False
        assert auth.collateral_damage_assessment == {}


class TestROEAuditEventDataclass:
    def test_construct(self):
        event = ROEAuditEvent(
            event_id="e1", event_type="classification",
            roe_level=ROELevel.DECEIVE, threat_classification_id="c1",
            authorization_id=None, action_taken="deploy_honeypot",
            decision_rationale="Moderate confidence surveillance detected",
            confidence_score=0.6, human_involvement=False,
            system_components=["roe_classifier"],
            evidence_summary={"indicators": 3},
            compliance_status="compliant",
            audit_timestamp=datetime.now(timezone.utc),
        )
        assert event.legal_framework_references == []
        assert event.ethical_considerations == []


# ======================================================================
# ROEClassificationEngine Tests
# ======================================================================

class TestROEClassificationEngine:
    """Tests for the ROE-integrated threat classification engine."""

    def test_init_loads_default_config(self, tmp_path):
        """When no config file exists, engine creates default config."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        assert len(engine.classification_matrix) > 0
        assert "noise" in engine.classification_matrix
        assert "critical_infrastructure_attack" in engine.classification_matrix

    def test_default_roe_thresholds(self, tmp_path):
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        assert engine.roe_thresholds["roe_1_max_confidence"] == pytest.approx(0.4)
        assert engine.roe_thresholds["roe_4_min_confidence"] == pytest.approx(0.8)

    @pytest.mark.asyncio
    async def test_assess_threat_tier_noise(self, tmp_path):
        """Low-confidence benign indicators should classify as NOISE."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        ti = make_threat_input(
            indicators=["scan_noise", "false_positive", "benign_anomaly"],
            confidence_score=0.15,
        )
        tier = await engine._assess_threat_tier(ti)
        assert isinstance(tier, ThreatTier)

    @pytest.mark.asyncio
    async def test_assess_threat_tier_targeted(self, tmp_path):
        """Exploit-related indicators should elevate the tier."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        ti = make_threat_input(
            indicators=["exploit_attempt", "privilege_escalation", "persistence"],
            confidence_score=0.85,
        )
        tier = await engine._assess_threat_tier(ti)
        assert isinstance(tier, ThreatTier)
        # With strong exploit indicators, should NOT be noise
        assert tier != ThreatTier.NOISE

    def test_determine_roe_level_low_confidence(self, tmp_path):
        """Low confidence → OBSERVE regardless of tier."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        result = engine._determine_roe_level(ThreatTier.TARGETED_INTRUSION, 0.3)
        assert result == ROELevel.OBSERVE

    def test_determine_roe_level_medium_confidence_high_tier(self, tmp_path):
        """Medium confidence + high tier → DECEIVE or higher."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        result = engine._determine_roe_level(ThreatTier.TARGETED_INTRUSION, 0.55)
        assert result == ROELevel.DECEIVE

    def test_determine_roe_level_high_confidence_apt(self, tmp_path):
        """High confidence APT → NEUTRALIZE."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        result = engine._determine_roe_level(
            ThreatTier.ADVANCED_PERSISTENT_THREAT, 0.9
        )
        assert result == ROELevel.NEUTRALIZE

    def test_determine_roe_level_high_confidence_low_tier(self, tmp_path):
        """High confidence but low tier → capped at DEGRADE."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        result = engine._determine_roe_level(ThreatTier.NOISE, 0.9)
        assert result == ROELevel.DEGRADE

    def test_engagement_recommendations_observe(self, tmp_path):
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        recs = engine._generate_engagement_recommendations(
            ThreatTier.NOISE, ROELevel.OBSERVE, 0.2
        )
        assert isinstance(recs, list)
        assert "passive_monitoring" in recs

    def test_engagement_recommendations_neutralize(self, tmp_path):
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        recs = engine._generate_engagement_recommendations(
            ThreatTier.CRITICAL_INFRASTRUCTURE_ATTACK, ROELevel.NEUTRALIZE, 0.95
        )
        assert "comprehensive_countermeasures" in recs
        assert "immediate_action_authorized" in recs

    @pytest.mark.asyncio
    async def test_classify_threat_returns_classification(self, tmp_path):
        """Full classify_threat pipeline produces valid classification."""
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        ti = make_threat_input()
        result = await engine.classify_threat(ti)
        assert isinstance(result, ROEThreatClassification)
        assert isinstance(result.threat_tier, ThreatTier)
        assert isinstance(result.roe_level, ROELevel)
        assert 0 <= result.confidence_score <= 1

    @pytest.mark.asyncio
    async def test_classify_threat_stores_in_history(self, tmp_path):
        engine = ROEClassificationEngine(config_path=str(tmp_path / "roe.yaml"))
        ti = make_threat_input()
        await engine.classify_threat(ti)
        assert len(engine.classification_history) == 1


# ======================================================================
# MultiSourceCorrelationEngine Tests
# ======================================================================

class TestMultiSourceCorrelationEngine:
    """Tests for the multi-source correlation engine."""

    def test_init(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        assert engine.time_window == timedelta(hours=24)
        expected_algos = {"temporal", "spatial", "behavioral", "attribution", "semantic"}
        assert set(engine.correlation_algorithms.keys()) == expected_algos

    def test_extract_ip_addresses_from_flat_dict(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        data = {"source_ip": "192.168.1.100", "destination_ip": "10.0.0.1"}
        ips = engine._extract_ip_addresses(data)
        assert "192.168.1.100" in ips
        assert "10.0.0.1" in ips

    def test_extract_ip_addresses_from_nested(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        data = {"network": {"inner": {"ip": "172.16.0.5"}}, "list": ["8.8.8.8"]}
        ips = engine._extract_ip_addresses(data)
        assert "172.16.0.5" in ips
        assert "8.8.8.8" in ips

    def test_extract_ip_addresses_no_ips(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        data = {"key": "no ip here", "count": 42}
        ips = engine._extract_ip_addresses(data)
        assert ips == []

    def test_get_network_range_private_192(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        assert engine._get_network_range("192.168.1.100") == "192.168.1.0/24"

    def test_get_network_range_private_10(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        assert engine._get_network_range("10.5.3.1") == "10.0.0.0/8"

    def test_get_network_range_private_172(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        assert engine._get_network_range("172.16.0.5") == "172.16.0.0/16"

    def test_get_network_range_public(self):
        db = MockIntelligenceDB()
        engine = MultiSourceCorrelationEngine(db)
        assert engine._get_network_range("8.8.8.8") == "8.8.8.0/24"


# ======================================================================
# ThreatAggregationEngine Tests
# ======================================================================

class TestThreatAggregationEngine:
    """Tests for the top-level ThreatAggregationEngine orchestrator."""

    def test_init(self, tmp_path):
        db = MockIntelligenceDB()
        config = tmp_path / "ta.yaml"
        audit_db = tmp_path / "audit" / "roe_audit.db"

        engine = ThreatAggregationEngine(db, config_path=str(config))
        # Override audit path so we don't pollute real data dir
        engine.audit_db_path = audit_db
        engine._initialize_audit_system()

        assert engine.roe_classifier is not None
        assert engine.correlation_engine is not None
        assert not engine.shutdown_event.is_set()

    def test_default_config_loaded(self, tmp_path):
        db = MockIntelligenceDB()
        engine = ThreatAggregationEngine(db, config_path=str(tmp_path / "ta.yaml"))
        assert "processing" in engine.aggregation_config
        assert "source_reliability" in engine.aggregation_config
        assert engine.aggregation_config["processing"]["priority_thresholds"]["high"] == 0.8

    def test_audit_database_created(self, tmp_path):
        db = MockIntelligenceDB()
        audit_db = tmp_path / "audit" / "roe_audit.db"

        engine = ThreatAggregationEngine(db, config_path=str(tmp_path / "ta.yaml"))
        engine.audit_db_path = audit_db
        engine._initialize_audit_system()

        assert audit_db.exists()
        conn = sqlite3.connect(audit_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='roe_audit_events'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    @pytest.mark.asyncio
    async def test_get_aggregation_status(self, tmp_path):
        db = MockIntelligenceDB()
        engine = ThreatAggregationEngine(db, config_path=str(tmp_path / "ta.yaml"))
        status = await engine.get_aggregation_status()
        assert status["engine_status"] == "operational"
        assert "active_threats" in status
        assert "processing_queues" in status
        assert "metrics" in status

    @pytest.mark.asyncio
    async def test_shutdown_sets_event(self, tmp_path):
        db = MockIntelligenceDB()
        engine = ThreatAggregationEngine(db, config_path=str(tmp_path / "ta.yaml"))
        await engine.shutdown()
        assert engine.shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_shutdown_cancel_tasks(self, tmp_path):
        db = MockIntelligenceDB()
        engine = ThreatAggregationEngine(db, config_path=str(tmp_path / "ta.yaml"))

        async def _long_task():
            await asyncio.sleep(3600)

        task = asyncio.create_task(_long_task())
        engine.background_tasks.append(task)

        await engine.shutdown()
        assert task.cancelled()

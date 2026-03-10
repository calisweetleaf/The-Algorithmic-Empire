#!/usr/bin/env python3
"""
ARCS Data Fusion - Comprehensive Pytest Suite
===============================================
Tests for RecursiveLearningEngine, IntelligenceSynthesisEngine, and DataFusionEngine.
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
import numpy as np
import torch

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
    "transformers",
    "networkx",
    "sklearn", "sklearn.cluster", "sklearn.preprocessing",
    "sklearn.decomposition", "sklearn.ensemble", "sklearn.metrics",
    "sklearn.metrics.pairwise",
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

from ARCS.data_fusion import (
    SynthesisType,
    HypothesisConfidence,
    LearningPhase,
    IntelligenceHypothesis,
    SynthesisProduct,
    ModelTrainingData,
    SessionAnalytics,
    RecursiveLearningEngine,
    IntelligenceSynthesisEngine,
    DataFusionEngine,
)

# Import shared fixtures / mocks
from ARCS.tests.conftest import MockIntelligenceDB, MockThreatAggregation


# ======================================================================
# Enum Tests
# ======================================================================

class TestSynthesisTypeEnum:
    """Validate SynthesisType enum members."""

    def test_all_members_present(self):
        expected = {
            "THREAT_ASSESSMENT", "CAMPAIGN_ANALYSIS", "ATTRIBUTION_HYPOTHESIS",
            "PREDICTIVE_INTELLIGENCE", "BEHAVIORAL_PROFILE",
            "INFRASTRUCTURE_MAPPING", "VULNERABILITY_SYNTHESIS",
            "TACTICAL_RECOMMENDATION",
        }
        actual = {m.name for m in SynthesisType}
        assert actual == expected

    def test_values_are_strings(self):
        for member in SynthesisType:
            assert isinstance(member.value, str)
            assert member.value == member.name.lower()


class TestHypothesisConfidenceEnum:
    """Validate numeric confidence tiers."""

    EXPECTED = {
        "SPECULATIVE": 0.2,
        "POSSIBLE": 0.4,
        "PROBABLE": 0.6,
        "HIGHLY_LIKELY": 0.8,
        "CONFIRMED": 0.95,
    }

    def test_all_levels_present(self):
        assert {m.name for m in HypothesisConfidence} == set(self.EXPECTED.keys())

    def test_numeric_values(self):
        for name, value in self.EXPECTED.items():
            assert HypothesisConfidence[name].value == pytest.approx(value)


class TestLearningPhaseEnum:
    def test_all_phases_present(self):
        expected = {
            "INITIALIZATION", "ACTIVE_LEARNING", "SYNTHESIS_OPTIMIZATION",
            "FEEDBACK_INTEGRATION", "MODEL_EVOLUTION",
        }
        assert {m.name for m in LearningPhase} == expected


# ======================================================================
# Dataclass Construction Tests
# ======================================================================

class TestIntelligenceHypothesisDataclass:
    """Ensure IntelligenceHypothesis can be constructed with all fields."""

    def test_construct_with_required_fields(self):
        now = datetime.now(timezone.utc)
        h = IntelligenceHypothesis(
            hypothesis_id=str(uuid4()),
            hypothesis_type=SynthesisType.THREAT_ASSESSMENT,
            hypothesis_statement="Possible APT campaign targeting critical infra",
            confidence_level=HypothesisConfidence.PROBABLE,
            supporting_evidence=[{"source": "network", "data": "scan detected"}],
            contradicting_evidence=[],
            reasoning_chain=["Step 1: Identified scan", "Step 2: Correlated IPs"],
            data_sources=["network_telemetry", "osint"],
            correlation_strength=0.75,
            temporal_relevance=0.9,
            predictive_indicators=["lateral_movement", "c2_beacon"],
            validation_criteria=["confirm source IP reputation"],
            alternative_hypotheses=["random scanner"],
            uncertainty_factors=["limited data"],
            creation_timestamp=now,
            last_updated=now,
        )
        assert h.hypothesis_type == SynthesisType.THREAT_ASSESSMENT
        assert h.confidence_level == HypothesisConfidence.PROBABLE
        assert h.correlation_strength == 0.75
        assert h.validation_status is None
        assert h.outcome_validation is None


class TestSynthesisProductDataclass:
    def test_default_review_and_dissemination(self):
        now = datetime.now(timezone.utc)
        hyp = IntelligenceHypothesis(
            hypothesis_id="h1", hypothesis_type=SynthesisType.CAMPAIGN_ANALYSIS,
            hypothesis_statement="test", confidence_level=HypothesisConfidence.SPECULATIVE,
            supporting_evidence=[], contradicting_evidence=[], reasoning_chain=[],
            data_sources=[], correlation_strength=0.1, temporal_relevance=0.1,
            predictive_indicators=[], validation_criteria=[], alternative_hypotheses=[],
            uncertainty_factors=[], creation_timestamp=now, last_updated=now,
        )
        sp = SynthesisProduct(
            product_id="sp1", synthesis_type=SynthesisType.CAMPAIGN_ANALYSIS,
            title="Test Product", executive_summary="Summary here",
            key_findings=["finding1"], primary_hypothesis=hyp,
            supporting_hypotheses=[], analytical_confidence=0.5,
            source_reliability_assessment={"net": 0.9},
            data_quality_metrics={"completeness": 0.8},
            synthesis_methodology=["clustering"], validation_requirements=["review"],
            intelligence_gaps=["attribution"], recommendations=["monitor"],
            follow_up_requirements=["deep_analysis"], synthesis_timestamp=now,
        )
        assert sp.review_status == "pending"
        assert sp.dissemination_level == "restricted"


class TestModelTrainingDataDataclass:
    def test_construct(self):
        td = ModelTrainingData(
            training_id="td1", data_source="synthesis_output",
            feature_vector=np.zeros(32), target_labels={"class": 1},
            confidence_scores=np.array([0.8, 0.9]),
            reasoning_patterns=["pattern_A"], outcome_validation=True,
            training_timestamp=datetime.now(timezone.utc), data_quality_score=0.85,
        )
        assert td.data_quality_score == 0.85
        assert td.outcome_validation is True


# ======================================================================
# RecursiveLearningEngine Tests
# ======================================================================

class TestRecursiveLearningEngine:
    """Test the RecursiveLearningEngine initialization and data caching."""

    def test_init_creates_models_dir(self, tmp_path):
        models_dir = tmp_path / "test_models"
        engine = RecursiveLearningEngine(models_path=str(models_dir))
        assert models_dir.exists()
        assert len(engine.active_models) == 4  # 4 PyTorch models created fresh
        for name in ["synthesis_optimizer", "hypothesis_generator",
                      "confidence_estimator", "pattern_recognizer"]:
            assert name in engine.active_models
            assert isinstance(engine.active_models[name], torch.nn.Module)

    def test_model_versions_initialized(self, tmp_path):
        engine = RecursiveLearningEngine(models_path=str(tmp_path / "m"))
        for name in engine.model_versions:
            assert engine.model_versions[name]["version"] == 1.0
            assert engine.model_versions[name]["training_samples"] == 0

    @pytest.mark.asyncio
    async def test_add_training_data_stores_in_cache(self, tmp_path):
        engine = RecursiveLearningEngine(models_path=str(tmp_path / "m"))
        td = ModelTrainingData(
            training_id="td1", data_source="synthesis_output",
            feature_vector=np.zeros(128), target_labels={"class": 0},
            confidence_scores=np.array([0.5]),
            reasoning_patterns=[], outcome_validation=None,
            training_timestamp=datetime.now(timezone.utc), data_quality_score=0.7,
        )
        await engine.add_training_data(td)
        assert len(engine.training_data_cache) == 1

    def test_learning_config_defaults(self, tmp_path):
        engine = RecursiveLearningEngine(models_path=str(tmp_path / "m"))
        assert engine.learning_config["batch_size"] == 32
        assert engine.learning_config["retrain_threshold"] == 100


# ======================================================================
# IntelligenceSynthesisEngine Tests
# ======================================================================

class TestIntelligenceSynthesisEngine:
    """Test IntelligenceSynthesisEngine init and config."""

    def test_init_sets_analysis_techniques(self):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        engine = IntelligenceSynthesisEngine(db, ta)
        expected_techniques = {
            "clustering_analysis", "temporal_analysis", "network_analysis",
            "anomaly_detection", "correlation_analysis", "predictive_modeling",
        }
        assert set(engine.analysis_techniques.keys()) == expected_techniques

    def test_synthesis_config_defaults(self):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        engine = IntelligenceSynthesisEngine(db, ta)
        assert engine.synthesis_config["min_confidence_threshold"] == 0.3
        assert engine.synthesis_config["max_hypotheses_per_synthesis"] == 5
        assert engine.synthesis_config["temporal_window_hours"] == 168


# ======================================================================
# DataFusionEngine Tests
# ======================================================================

class TestDataFusionEngine:
    """Test the top-level DataFusionEngine orchestrator."""

    def test_init_creates_synthesis_engine(self, tmp_path):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        config_file = tmp_path / "fusion.yaml"
        engine = DataFusionEngine(db, ta, config_path=str(config_file))
        assert engine.synthesis_engine is not None
        assert isinstance(engine.synthesis_engine, IntelligenceSynthesisEngine)

    def test_init_default_state(self, tmp_path):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        engine = DataFusionEngine(db, ta, config_path=str(tmp_path / "f.yaml"))
        assert engine.active_sessions == {}
        assert not engine.shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_get_fusion_status_returns_expected_keys(self, tmp_path):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        engine = DataFusionEngine(db, ta, config_path=str(tmp_path / "f.yaml"))
        status = await engine.get_fusion_status()
        assert status["engine_status"] == "operational"
        assert "active_sessions" in status
        assert "total_syntheses_created" in status
        assert "model_versions" in status
        assert "last_updated" in status

    @pytest.mark.asyncio
    async def test_shutdown_sets_event(self, tmp_path):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        engine = DataFusionEngine(db, ta, config_path=str(tmp_path / "f.yaml"))
        await engine.shutdown()
        assert engine.shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_shutdown_cancels_background_tasks(self, tmp_path):
        db = MockIntelligenceDB()
        ta = MockThreatAggregation()
        engine = DataFusionEngine(db, ta, config_path=str(tmp_path / "f.yaml"))

        # Simulate a long-running background task
        async def _long_task():
            await asyncio.sleep(3600)

        task = asyncio.create_task(_long_task())
        engine.background_tasks.append(task)

        await engine.shutdown()
        assert task.cancelled()

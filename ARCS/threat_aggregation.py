#!/usr/bin/env python3
"""
ARCS Threat Aggregation - ROE-Integrated Multi-Source Intelligence Fusion
=========================================================================
Autonomous Reactive Cyber Systems - Threat Intelligence Fusion Domain

Mission: Aggregate intelligence from all sources, apply ROE-based threat classification,
and provide autonomous engagement recommendations with comprehensive audit trails
for sovereign defensive operations.

Classification: INTELLIGENCE FUSION - SOVEREIGN INFRASTRUCTURE
ROE Authority: Multi-source correlation with autonomous engagement recommendation
Deployment: Field-ready production system with military operational standards
"""

import asyncio
import logging
import json
import time
import hashlib
import hmac
import threading
import sqlite3
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Callable, Tuple, Iterator
from uuid import UUID, uuid4
from collections import defaultdict, deque, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import re

import numpy as np
import pandas as pd
import aiofiles
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# ML and correlation analysis
import onnxruntime as ort
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
from scipy.stats import pearsonr

logger = logging.getLogger(__name__)


class ROELevel(Enum):
    """Rules of Engagement escalation levels"""
    OBSERVE = 1      # Passive monitoring and intelligence gathering
    DECEIVE = 2      # Active counter-intelligence and deception
    DEGRADE = 3      # Active defense and system degradation
    NEUTRALIZE = 4   # Offensive countermeasures (requires human authorization)


class ThreatTier(Enum):
    """Threat classification tiers for ROE engagement decisions"""
    NOISE = "noise"                                 # Background noise, false positives
    AUTOMATED_PROBES = "automated_probes"          # Automated scanning, bots
    CORPORATE_SURVEILLANCE = "corporate_surveillance"  # Data mining, tracking
    TARGETED_INTRUSION = "targeted_intrusion"      # Directed attacks, specific targeting
    ADVANCED_PERSISTENT_THREAT = "advanced_persistent_threat"  # Nation-state, APT groups
    CRITICAL_INFRASTRUCTURE_ATTACK = "critical_infrastructure_attack"  # Infrastructure targeting


class IntelligenceSource(Enum):
    """Intelligence source categorization"""
    BROWSER_INTELLIGENCE = "browser_intelligence"
    NETWORK_TELEMETRY = "network_telemetry"
    OSINT_ORCHESTRATOR = "osint_orchestrator"
    EXTERNAL_FEEDS = "external_feeds"
    SYSTEM_BEHAVIOR = "system_behavior"
    ATTRIBUTION_ENGINE = "attribution_engine"
    MANUAL_INPUT = "manual_input"
    CORRELATION_ENGINE = "correlation_engine"


class ThreatConfidenceLevel(Enum):
    """Threat confidence assessment levels"""
    VERY_LOW = 0.1      # 0-20% confidence
    LOW = 0.3           # 20-40% confidence  
    MEDIUM = 0.5        # 40-60% confidence
    HIGH = 0.7          # 60-80% confidence
    VERY_HIGH = 0.9     # 80-100% confidence


class EngagementStatus(Enum):
    """Current engagement operation status"""
    STANDBY = "standby"
    ANALYZING = "analyzing"
    AUTHORIZED = "authorized"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    ABORTED = "aborted"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


@dataclass
class ThreatIntelligenceInput:
    """Standardized threat intelligence input from any source"""
    input_id: str
    source: IntelligenceSource
    intelligence_type: str
    raw_data: Dict[str, Any]
    indicators: List[str]
    confidence_score: float
    collection_timestamp: datetime
    source_reliability: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_keys: List[str] = field(default_factory=list)


@dataclass
class ROEThreatClassification:
    """ROE-integrated threat classification"""
    classification_id: str
    threat_tier: ThreatTier
    roe_level: ROELevel
    confidence_score: float
    threat_indicators: List[str]
    attribution_data: Dict[str, Any]
    impact_assessment: Dict[str, float]
    time_sensitivity: str  # immediate, urgent, routine
    source_correlation: Dict[IntelligenceSource, float]
    supporting_evidence: Dict[str, Any]
    engagement_recommendations: List[str]
    escalation_triggers: List[str]
    de_escalation_conditions: List[str]
    classification_timestamp: datetime
    analyst_notes: Optional[str] = None
    human_validated: bool = False


@dataclass
class EngagementAuthorization:
    """Formal ROE-compliant engagement authorization"""
    authorization_id: str
    threat_classification: ROEThreatClassification
    roe_level: ROELevel
    authorized_actions: List[str]
    authorization_timestamp: datetime
    authorization_expiry: datetime
    authorizing_system: str
    human_authorized: bool = False
    authorization_conditions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    abort_conditions: List[str] = field(default_factory=list)
    collateral_damage_assessment: Dict[str, float] = field(default_factory=dict)
    legal_review_status: str = "pending"


@dataclass
class ThreatCorrelation:
    """Multi-source threat intelligence correlation"""
    correlation_id: str
    primary_threat_id: str
    correlated_threats: List[str]
    correlation_strength: float
    correlation_type: str  # temporal, spatial, behavioral, attribution
    evidence_sources: List[IntelligenceSource]
    correlation_metrics: Dict[str, float]
    confidence_boost: float  # How much correlation increases confidence
    discovered_timestamp: datetime
    correlation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ROEAuditEvent:
    """Comprehensive ROE audit event for compliance tracking"""
    event_id: str
    event_type: str
    roe_level: ROELevel
    threat_classification_id: str
    authorization_id: Optional[str]
    action_taken: str
    decision_rationale: str
    confidence_score: float
    human_involvement: bool
    system_components: List[str]
    evidence_summary: Dict[str, Any]
    compliance_status: str
    audit_timestamp: datetime
    legal_framework_references: List[str] = field(default_factory=list)
    ethical_considerations: List[str] = field(default_factory=list)


class ROEClassificationEngine:
    """
    ROE-integrated threat classification engine
    
    Maps threat intelligence to appropriate ROE levels and generates
    engagement recommendations with compliance boundaries.
    """
    
    def __init__(self, config_path: str = "config/roe_threat_mapping.yaml"):
        self.config_path = Path(config_path)
        self.classification_matrix = {}
        self.roe_thresholds = {}
        self.engagement_policies = {}
        
        # ML models for classification enhancement
        self.threat_classifier = None
        self.confidence_estimator = None
        
        # ROE compliance tracking
        self.classification_history = deque(maxlen=10000)
        self.escalation_patterns = defaultdict(list)
        
        self._load_roe_configuration()
        self._initialize_ml_models()
    
    def _load_roe_configuration(self):
        """Load ROE classification configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = self._create_default_roe_config()
                self._save_roe_configuration(config)
            
            # Extract configuration components
            self.classification_matrix = config.get('classification_matrix', {})
            self.roe_thresholds = config.get('roe_thresholds', {})
            self.engagement_policies = config.get('engagement_policies', {})
            
            logger.info("ROE classification configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load ROE configuration: {e}")
            self.classification_matrix = self._create_default_classification_matrix()
    
    def _create_default_roe_config(self) -> Dict[str, Any]:
        """Create default ROE classification configuration"""
        return {
            'classification_matrix': {
                'noise': {
                    'confidence_threshold': 0.1,
                    'default_roe_level': 1,
                    'indicators': ['scan_noise', 'false_positive', 'benign_anomaly'],
                    'engagement_policy': 'ignore'
                },
                'automated_probes': {
                    'confidence_threshold': 0.3,
                    'default_roe_level': 1,
                    'indicators': ['port_scan', 'vulnerability_scan', 'automated_enumeration'],
                    'engagement_policy': 'monitor_and_log'
                },
                'corporate_surveillance': {
                    'confidence_threshold': 0.5,
                    'default_roe_level': 2,
                    'indicators': ['tracking_pixel', 'fingerprinting', 'data_collection'],
                    'engagement_policy': 'active_deception'
                },
                'targeted_intrusion': {
                    'confidence_threshold': 0.7,
                    'default_roe_level': 3,
                    'indicators': ['exploit_attempt', 'privilege_escalation', 'persistence'],
                    'engagement_policy': 'active_defense'
                },
                'advanced_persistent_threat': {
                    'confidence_threshold': 0.8,
                    'default_roe_level': 3,
                    'indicators': ['lateral_movement', 'data_exfiltration', 'command_control'],
                    'engagement_policy': 'comprehensive_defense'
                },
                'critical_infrastructure_attack': {
                    'confidence_threshold': 0.9,
                    'default_roe_level': 4,
                    'indicators': ['infrastructure_targeting', 'scada_attack', 'supply_chain'],
                    'engagement_policy': 'maximum_response'
                }
            },
            'roe_thresholds': {
                'roe_1_max_confidence': 0.4,
                'roe_2_min_confidence': 0.3,
                'roe_2_max_confidence': 0.6,
                'roe_3_min_confidence': 0.6,
                'roe_3_max_confidence': 0.8,
                'roe_4_min_confidence': 0.8,
                'human_authorization_threshold': 0.85
            },
            'engagement_policies': {
                'ignore': {'actions': [], 'monitoring': 'basic'},
                'monitor_and_log': {'actions': ['log_event', 'update_baseline'], 'monitoring': 'enhanced'},
                'active_deception': {'actions': ['deploy_honeypot', 'false_data_injection'], 'monitoring': 'comprehensive'},
                'active_defense': {'actions': ['block_source', 'isolate_target'], 'monitoring': 'real_time'},
                'comprehensive_defense': {'actions': ['multi_layer_blocking', 'threat_hunting'], 'monitoring': 'continuous'},
                'maximum_response': {'actions': ['all_available_countermeasures'], 'monitoring': 'maximum', 'human_required': True}
            }
        }
    
    def _save_roe_configuration(self, config: Dict[str, Any]) -> None:
        """Save ROE configuration to file.

        Serializes the given configuration dictionary to the YAML config
        file on disk.  Parent directories are created automatically.

        Args:
            config: ROE configuration dictionary to persist.
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save ROE configuration: {e}")
    
    def _initialize_ml_models(self):
        """Initialize ML models for enhanced classification"""
        try:
            models_path = Path("models/threat_classification/")
            models_path.mkdir(parents=True, exist_ok=True)
            
            # Load threat classification model
            threat_model_path = models_path / "roe_threat_classifier.onnx"
            if threat_model_path.exists():
                self.threat_classifier = ort.InferenceSession(str(threat_model_path))
            
            # Load confidence estimation model
            confidence_model_path = models_path / "confidence_estimator.onnx"
            if confidence_model_path.exists():
                self.confidence_estimator = ort.InferenceSession(str(confidence_model_path))
            
            logger.info("ROE classification ML models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def classify_threat(self, threat_input: ThreatIntelligenceInput,
                            correlation_data: Optional[Dict[str, Any]] = None) -> ROEThreatClassification:
        """Classify threat with ROE integration"""
        try:
            classification_id = str(uuid4())
            
            # Initial threat tier assessment
            threat_tier = await self._assess_threat_tier(threat_input)
            
            # Confidence score calculation
            confidence_score = await self._calculate_confidence_score(threat_input, correlation_data)
            
            # ROE level determination
            roe_level = self._determine_roe_level(threat_tier, confidence_score)
            
            # Attribution analysis
            attribution_data = await self._analyze_attribution(threat_input)
            
            # Impact assessment
            impact_assessment = await self._assess_potential_impact(threat_input, threat_tier)
            
            # Time sensitivity evaluation
            time_sensitivity = self._evaluate_time_sensitivity(threat_input, threat_tier)
            
            # Source correlation analysis
            source_correlation = self._analyze_source_correlation(threat_input, correlation_data)
            
            # Generate engagement recommendations
            engagement_recommendations = self._generate_engagement_recommendations(
                threat_tier, roe_level, confidence_score
            )
            
            # Define escalation triggers
            escalation_triggers = self._define_escalation_triggers(threat_tier, roe_level)
            
            # Define de-escalation conditions
            de_escalation_conditions = self._define_de_escalation_conditions(threat_tier, roe_level)
            
            # Create classification
            classification = ROEThreatClassification(
                classification_id=classification_id,
                threat_tier=threat_tier,
                roe_level=roe_level,
                confidence_score=confidence_score,
                threat_indicators=threat_input.indicators,
                attribution_data=attribution_data,
                impact_assessment=impact_assessment,
                time_sensitivity=time_sensitivity,
                source_correlation=source_correlation,
                supporting_evidence={
                    'raw_data_summary': self._summarize_raw_data(threat_input.raw_data),
                    'correlation_evidence': correlation_data or {},
                    'historical_patterns': self._analyze_historical_patterns(threat_input)
                },
                engagement_recommendations=engagement_recommendations,
                escalation_triggers=escalation_triggers,
                de_escalation_conditions=de_escalation_conditions,
                classification_timestamp=datetime.now(timezone.utc)
            )
            
            # Store in classification history
            self.classification_history.append(classification)
            
            # Log classification event
            await self._log_classification_event(classification, threat_input)
            
            return classification
            
        except Exception as e:
            logger.error(f"Threat classification failed: {e}")
            # Return minimal safe classification
            return self._create_safe_fallback_classification(threat_input)
    
    async def _assess_threat_tier(self, threat_input: ThreatIntelligenceInput) -> ThreatTier:
        """Assess threat tier based on indicators and data"""
        try:
            # Analyze indicators against classification matrix
            indicator_scores = {}
            for tier_name, tier_config in self.classification_matrix.items():
                tier_indicators = tier_config.get('indicators', [])
                matches = sum(1 for indicator in threat_input.indicators 
                            if any(tier_ind in indicator.lower() for tier_ind in tier_indicators))
                indicator_scores[tier_name] = matches / len(tier_indicators) if tier_indicators else 0
            
            # Use ML model if available
            if self.threat_classifier:
                ml_prediction = await self._ml_threat_classification(threat_input)
                # Combine rule-based and ML scores
                for tier_name in indicator_scores:
                    if tier_name in ml_prediction:
                        indicator_scores[tier_name] = (indicator_scores[tier_name] + ml_prediction[tier_name]) / 2
            
            # Select highest scoring tier
            best_tier = max(indicator_scores.items(), key=lambda x: x[1])
            
            # Apply confidence threshold
            tier_config = self.classification_matrix.get(best_tier[0], {})
            confidence_threshold = tier_config.get('confidence_threshold', 0.5)
            
            if best_tier[1] >= confidence_threshold:
                return ThreatTier(best_tier[0])
            else:
                return ThreatTier.NOISE  # Default for low confidence
            
        except Exception as e:
            logger.error(f"Threat tier assessment failed: {e}")
            return ThreatTier.AUTOMATED_PROBES  # Safe default
    
    async def _ml_threat_classification(self, threat_input: ThreatIntelligenceInput) -> Dict[str, float]:
        """Use ML model for threat classification"""
        try:
            # Prepare feature vector
            features = self._extract_classification_features(threat_input)
            
            # Run inference
            input_data = {self.threat_classifier.get_inputs()[0].name: features}
            output = self.threat_classifier.run(None, input_data)
            
            # Map output to threat tiers
            tier_names = list(self.classification_matrix.keys())
            scores = output[0][0] if output and len(output[0]) > 0 else [0] * len(tier_names)
            
            return dict(zip(tier_names, scores))
            
        except Exception as e:
            logger.error(f"ML threat classification failed: {e}")
            return {}
    
    def _extract_classification_features(self, threat_input: ThreatIntelligenceInput) -> np.ndarray:
        """Extract features for ML classification"""
        features = [
            threat_input.confidence_score,
            threat_input.source_reliability,
            len(threat_input.indicators),
            len(threat_input.raw_data),
            len(threat_input.correlation_keys),
            int(threat_input.source.value == 'network_telemetry'),
            int(threat_input.source.value == 'browser_intelligence'),
            int(threat_input.source.value == 'osint_orchestrator'),
            int('malware' in str(threat_input.indicators).lower()),
            int('exploit' in str(threat_input.indicators).lower()),
            int('scanning' in str(threat_input.indicators).lower()),
            int('anomaly' in str(threat_input.indicators).lower())
        ]
        
        # Pad or truncate to expected input size
        while len(features) < 32:
            features.append(0.0)
        
        return np.array([features[:32]], dtype=np.float32)
    
    async def _calculate_confidence_score(self, threat_input: ThreatIntelligenceInput,
                                        correlation_data: Optional[Dict[str, Any]]) -> float:
        """Calculate comprehensive confidence score"""
        try:
            base_confidence = threat_input.confidence_score
            source_reliability = threat_input.source_reliability
            
            # Correlation boost
            correlation_boost = 0.0
            if correlation_data:
                correlation_count = len(correlation_data.get('correlations', []))
                correlation_boost = min(0.3, correlation_count * 0.1)  # Max 30% boost
            
            # Multi-source validation boost
            source_diversity = len(set(threat_input.metadata.get('sources', [threat_input.source.value])))
            diversity_boost = min(0.2, (source_diversity - 1) * 0.1)  # Max 20% boost
            
            # Historical pattern boost
            historical_boost = self._calculate_historical_confidence_boost(threat_input)
            
            # Combine confidence factors
            combined_confidence = min(1.0, 
                base_confidence * source_reliability + 
                correlation_boost + 
                diversity_boost + 
                historical_boost
            )
            
            # Apply ML confidence estimation if available
            if self.confidence_estimator:
                ml_confidence = await self._ml_confidence_estimation(threat_input, combined_confidence)
                combined_confidence = (combined_confidence + ml_confidence) / 2
            
            return combined_confidence
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return threat_input.confidence_score  # Fallback to base confidence
    
    def _determine_roe_level(self, threat_tier: ThreatTier, confidence_score: float) -> ROELevel:
        """Determine appropriate ROE level based on threat tier and confidence"""
        try:
            # Get tier configuration
            tier_config = self.classification_matrix.get(threat_tier.value, {})
            base_roe_level = tier_config.get('default_roe_level', 1)
            
            # Apply confidence thresholds
            thresholds = self.roe_thresholds
            
            if confidence_score <= thresholds.get('roe_1_max_confidence', 0.4):
                return ROELevel.OBSERVE
            elif confidence_score <= thresholds.get('roe_2_max_confidence', 0.6):
                return ROELevel.DECEIVE if base_roe_level >= 2 else ROELevel.OBSERVE
            elif confidence_score <= thresholds.get('roe_3_max_confidence', 0.8):
                return ROELevel.DEGRADE if base_roe_level >= 3 else ROELevel.DECEIVE
            else:
                # High confidence - check if tier warrants ROE 4
                if threat_tier in [ThreatTier.ADVANCED_PERSISTENT_THREAT, 
                                 ThreatTier.CRITICAL_INFRASTRUCTURE_ATTACK]:
                    return ROELevel.NEUTRALIZE
                else:
                    return ROELevel.DEGRADE
            
        except Exception as e:
            logger.error(f"ROE level determination failed: {e}")
            return ROELevel.OBSERVE  # Safe default
    
    def _generate_engagement_recommendations(self, threat_tier: ThreatTier, 
                                           roe_level: ROELevel, confidence_score: float) -> List[str]:
        """Generate ROE-compliant engagement recommendations"""
        try:
            recommendations = []
            
            # Get tier-specific engagement policy
            tier_config = self.classification_matrix.get(threat_tier.value, {})
            engagement_policy = tier_config.get('engagement_policy', 'monitor_and_log')
            
            # Get policy actions
            policy_config = self.engagement_policies.get(engagement_policy, {})
            base_actions = policy_config.get('actions', [])
            
            # ROE level specific actions
            if roe_level == ROELevel.OBSERVE:
                recommendations.extend(['passive_monitoring', 'intelligence_gathering', 'baseline_establishment'])
            elif roe_level == ROELevel.DECEIVE:
                recommendations.extend(['active_deception', 'false_data_injection', 'honeypot_deployment'])
            elif roe_level == ROELevel.DEGRADE:
                recommendations.extend(['active_blocking', 'service_disruption', 'network_isolation'])
            elif roe_level == ROELevel.NEUTRALIZE:
                recommendations.extend(['comprehensive_countermeasures', 'threat_neutralization'])
                if confidence_score >= self.roe_thresholds.get('human_authorization_threshold', 0.85):
                    recommendations.append('human_authorization_required')
            
            # Add base actions from policy
            recommendations.extend(base_actions)
            
            # Add confidence-specific recommendations
            if confidence_score < 0.5:
                recommendations.append('additional_validation_required')
            elif confidence_score > 0.9:
                recommendations.append('immediate_action_authorized')
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Engagement recommendation generation failed: {e}")
            return ['passive_monitoring', 'log_event']


class MultiSourceCorrelationEngine:
    """
    Advanced multi-source intelligence correlation engine
    
    Correlates threat intelligence across multiple sources using temporal,
    spatial, behavioral, and attribution analysis techniques.
    """
    
    def __init__(self, intelligence_db, time_window_hours: int = 24):
        self.intelligence_db = intelligence_db
        self.time_window = timedelta(hours=time_window_hours)
        
        # Correlation algorithms
        self.correlation_algorithms = {
            'temporal': self._temporal_correlation,
            'spatial': self._spatial_correlation,
            'behavioral': self._behavioral_correlation,
            'attribution': self._attribution_correlation,
            'semantic': self._semantic_correlation
        }
        
        # Correlation cache
        self.correlation_cache = {}
        self.correlation_patterns = defaultdict(list)
        
        # Performance tracking
        self.correlation_metrics = defaultdict(int)
        
    async def correlate_intelligence(self, primary_input: ThreatIntelligenceInput,
                                   correlation_scope: List[IntelligenceSource] = None) -> Dict[str, Any]:
        """Perform comprehensive multi-source correlation"""
        try:
            correlation_start = time.time()
            
            # Define correlation scope
            if correlation_scope is None:
                correlation_scope = list(IntelligenceSource)
            
            # Retrieve related intelligence within time window
            related_intelligence = await self._retrieve_related_intelligence(
                primary_input, correlation_scope
            )
            
            # Perform correlation analysis
            correlations = {}
            for algorithm_name, algorithm_func in self.correlation_algorithms.items():
                try:
                    correlation_result = await algorithm_func(primary_input, related_intelligence)
                    if correlation_result:
                        correlations[algorithm_name] = correlation_result
                except Exception as e:
                    logger.error(f"Correlation algorithm {algorithm_name} failed: {e}")
            
            # Calculate composite correlation score
            composite_score = self._calculate_composite_correlation_score(correlations)
            
            # Generate correlation summary
            correlation_summary = {
                'correlation_id': str(uuid4()),
                'primary_input_id': primary_input.input_id,
                'related_intelligence_count': len(related_intelligence),
                'correlations': correlations,
                'composite_score': composite_score,
                'correlation_timestamp': datetime.now(timezone.utc),
                'processing_time_ms': (time.time() - correlation_start) * 1000
            }
            
            # Cache correlation results
            self._cache_correlation_results(correlation_summary)
            
            # Update metrics
            self.correlation_metrics['correlations_performed'] += 1
            self.correlation_metrics['total_processing_time_ms'] += correlation_summary['processing_time_ms']
            
            return correlation_summary
            
        except Exception as e:
            logger.error(f"Intelligence correlation failed: {e}")
            return {
                'correlation_id': str(uuid4()),
                'error': str(e),
                'correlations': {},
                'composite_score': 0.0
            }
    
    async def _retrieve_related_intelligence(self, primary_input: ThreatIntelligenceInput,
                                           correlation_scope: List[IntelligenceSource]) -> List[Dict[str, Any]]:
        """Retrieve related intelligence for correlation analysis"""
        try:
            # Define time window
            start_time = primary_input.collection_timestamp - self.time_window
            end_time = primary_input.collection_timestamp + self.time_window
            
            # Query intelligence database
            query_params = {
                'time_range': (start_time, end_time),
                'intelligence_types': [source.value for source in correlation_scope],
                'limit': 1000
            }
            
            # Add correlation key filters
            if primary_input.correlation_keys:
                query_params['search_text'] = ' OR '.join(primary_input.correlation_keys)
            
            related_records = await self.intelligence_db.advanced_query(query_params)
            
            # Convert to correlation format
            related_intelligence = []
            for record in related_records:
                if record.record_id != primary_input.input_id:  # Exclude self
                    related_intelligence.append({
                        'record_id': record.record_id,
                        'intelligence_type': record.intelligence_type,
                        'collection_timestamp': record.collection_timestamp,
                        'raw_data': record.raw_data,
                        'processed_indicators': record.processed_indicators,
                        'confidence_score': record.confidence_score,
                        'threat_level': record.threat_level,
                        'tags': record.tags,
                        'metadata': record.metadata
                    })
            
            return related_intelligence
            
        except Exception as e:
            logger.error(f"Related intelligence retrieval failed: {e}")
            return []
    
    async def _temporal_correlation(self, primary_input: ThreatIntelligenceInput,
                                  related_intelligence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform temporal correlation analysis"""
        try:
            temporal_correlations = []
            primary_timestamp = primary_input.collection_timestamp
            
            for related_intel in related_intelligence:
                related_timestamp = related_intel['collection_timestamp']
                time_diff = abs((primary_timestamp - related_timestamp).total_seconds())
                
                # Calculate temporal proximity score
                max_time_diff = self.time_window.total_seconds()
                proximity_score = max(0, 1 - (time_diff / max_time_diff))
                
                if proximity_score > 0.1:  # Minimum threshold
                    temporal_correlations.append({
                        'related_record_id': related_intel['record_id'],
                        'time_difference_seconds': time_diff,
                        'proximity_score': proximity_score,
                        'correlation_type': 'temporal_proximity'
                    })
            
            # Sort by proximity score
            temporal_correlations.sort(key=lambda x: x['proximity_score'], reverse=True)
            
            return {
                'correlations': temporal_correlations[:10],  # Top 10
                'total_temporal_matches': len(temporal_correlations),
                'average_proximity_score': np.mean([c['proximity_score'] for c in temporal_correlations]) if temporal_correlations else 0
            }
            
        except Exception as e:
            logger.error(f"Temporal correlation failed: {e}")
            return {}
    
    async def _spatial_correlation(self, primary_input: ThreatIntelligenceInput,
                                 related_intelligence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform spatial/network correlation analysis"""
        try:
            spatial_correlations = []
            
            # Extract IP addresses and network information from primary input
            primary_ips = self._extract_ip_addresses(primary_input.raw_data)
            primary_networks = [self._get_network_range(ip) for ip in primary_ips]
            
            for related_intel in related_intelligence:
                related_ips = self._extract_ip_addresses(related_intel['raw_data'])
                
                # Calculate IP overlap
                ip_overlap = len(set(primary_ips) & set(related_ips))
                
                # Calculate network overlap
                related_networks = [self._get_network_range(ip) for ip in related_ips]
                network_overlap = len(set(primary_networks) & set(related_networks))
                
                # Calculate spatial correlation score
                ip_score = ip_overlap / max(len(primary_ips), 1)
                network_score = network_overlap / max(len(primary_networks), 1)
                spatial_score = (ip_score + network_score) / 2
                
                if spatial_score > 0.1:
                    spatial_correlations.append({
                        'related_record_id': related_intel['record_id'],
                        'ip_overlap': ip_overlap,
                        'network_overlap': network_overlap,
                        'spatial_score': spatial_score,
                        'correlation_type': 'spatial_network'
                    })
            
            # Sort by spatial score
            spatial_correlations.sort(key=lambda x: x['spatial_score'], reverse=True)
            
            return {
                'correlations': spatial_correlations[:10],
                'total_spatial_matches': len(spatial_correlations),
                'average_spatial_score': np.mean([c['spatial_score'] for c in spatial_correlations]) if spatial_correlations else 0
            }
            
        except Exception as e:
            logger.error(f"Spatial correlation failed: {e}")
            return {}
    
    def _extract_ip_addresses(self, data: Dict[str, Any]) -> List[str]:
        """Extract IP addresses from data"""
        ip_addresses = []
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        
        def extract_from_value(value: Any) -> None:
            """Recursively extract IP addresses from nested data structures.

            Appends all IPv4 matches found in *value* (str, dict, or list)
            to the enclosing ``ip_addresses`` accumulator.

            Args:
                value: A string, dict, or list to scan for IP patterns.
            """
            if isinstance(value, str):
                matches = ip_pattern.findall(value)
                ip_addresses.extend(matches)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
        
        extract_from_value(data)
        return list(set(ip_addresses))  # Remove duplicates
    
    def _get_network_range(self, ip: str) -> str:
        """Get network range for IP address"""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            if ip_obj.is_private:
                # Private networks
                if ip.startswith('192.168.'):
                    return f"{'.'.join(ip.split('.')[:3])}.0/24"
                elif ip.startswith('10.'):
                    return f"{ip.split('.')[0]}.0.0.0/8"
                elif ip.startswith('172.'):
                    return f"{'.'.join(ip.split('.')[:2])}.0.0/16"
            else:
                # Public networks - use /24
                return f"{'.'.join(ip.split('.')[:3])}.0/24"
            
            return ip  # Fallback
            
        except Exception:
            return ip


class ThreatAggregationEngine:
    """
    Master ARCS Threat Aggregation Engine
    
    Orchestrates multi-source intelligence aggregation, ROE-based classification,
    and autonomous engagement authorization with comprehensive audit trails.
    """
    
    def __init__(self, intelligence_db, config_path: str = "config/threat_aggregation.yaml"):
        self.intelligence_db = intelligence_db
        self.config_path = Path(config_path)
        
        # Core engines
        self.roe_classifier = ROEClassificationEngine()
        self.correlation_engine = MultiSourceCorrelationEngine(intelligence_db)
        
        # Intelligence sources
        self.intelligence_sources = {}
        self.source_reliability_scores = {}
        
        # Threat tracking
        self.active_threats = {}
        self.threat_classifications = {}
        self.engagement_authorizations = {}
        
        # ROE audit system
        self.audit_events = deque(maxlen=10000)
        self.audit_db_path = Path("data/audit/roe_audit.db")
        
        # Configuration
        self.aggregation_config = {}
        self.processing_queues = {
            'high_priority': asyncio.Queue(),
            'normal_priority': asyncio.Queue(),
            'low_priority': asyncio.Queue()
        }
        
        # Background services
        self.background_tasks = []
        self.shutdown_event = asyncio.Event()
        
        # Performance metrics
        self.aggregation_metrics = defaultdict(int)
        
        self._load_configuration()
        self._initialize_audit_system()
    
    def _load_configuration(self):
        """Load threat aggregation configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.aggregation_config = yaml.safe_load(f)
            else:
                self.aggregation_config = self._create_default_config()
                self._save_configuration()
            
            logger.info("Threat aggregation configuration loaded")
            
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            self.aggregation_config = self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default aggregation configuration"""
        return {
            'processing': {
                'correlation_window_hours': 24,
                'max_concurrent_analyses': 10,
                'priority_thresholds': {
                    'high': 0.8,
                    'normal': 0.5,
                    'low': 0.2
                }
            },
            'source_reliability': {
                'browser_intelligence': 0.8,
                'network_telemetry': 0.9,
                'osint_orchestrator': 0.7,
                'external_feeds': 0.6,
                'system_behavior': 0.8,
                'attribution_engine': 0.7,
                'manual_input': 0.95
            },
            'aggregation_rules': {
                'min_correlation_score': 0.3,
                'max_correlation_age_hours': 72,
                'confidence_boost_per_source': 0.1,
                'max_confidence_boost': 0.4
            },
            'roe_integration': {
                'auto_classify_threshold': 0.5,
                'human_review_threshold': 0.8,
                'escalation_cooldown_minutes': 30,
                'audit_all_decisions': True
            }
        }
    
    def _save_configuration(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.aggregation_config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Configuration saving failed: {e}")
    
    def _initialize_audit_system(self):
        """Initialize ROE audit database"""
        try:
            self.audit_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create audit database schema
            conn = sqlite3.connect(self.audit_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roe_audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    roe_level INTEGER NOT NULL,
                    threat_classification_id TEXT,
                    authorization_id TEXT,
                    action_taken TEXT NOT NULL,
                    decision_rationale TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    human_involvement BOOLEAN NOT NULL,
                    system_components TEXT,
                    evidence_summary TEXT,
                    compliance_status TEXT NOT NULL,
                    audit_timestamp TEXT NOT NULL,
                    legal_framework_references TEXT,
                    ethical_considerations TEXT
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON roe_audit_events(audit_timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_roe_level 
                ON roe_audit_events(roe_level)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("ROE audit system initialized")
            
        except Exception as e:
            logger.error(f"Audit system initialization failed: {e}")
    
    async def initialize(self):
        """Initialize threat aggregation engine"""
        try:
            logger.info("Initializing ARCS Threat Aggregation Engine...")
            
            # Start background services
            await self._start_background_services()
            
            logger.info("Threat aggregation engine fully operational")
            
        except Exception as e:
            logger.error(f"Threat aggregation initialization failed: {e}")
            raise
    
    async def _start_background_services(self):
        """Start background aggregation services"""
        try:
            self.background_tasks.extend([
                asyncio.create_task(self._process_high_priority_queue()),
                asyncio.create_task(self._process_normal_priority_queue()),
                asyncio.create_task(self._process_low_priority_queue()),
                asyncio.create_task(self._correlation_maintenance_service()),
                asyncio.create_task(self._audit_maintenance_service()),
                asyncio.create_task(self._metrics_collection_service())
            ])
            
            logger.info("Background aggregation services started")
            
        except Exception as e:
            logger.error(f"Background service startup failed: {e}")
    
    async def process_threat_intelligence(self, threat_input: ThreatIntelligenceInput) -> Dict[str, Any]:
        """Process incoming threat intelligence with ROE integration"""
        try:
            processing_start = time.time()
            
            # Determine processing priority
            priority = self._determine_processing_priority(threat_input)
            
            # Add to appropriate processing queue
            processing_task = {
                'task_id': str(uuid4()),
                'threat_input': threat_input,
                'priority': priority,
                'submitted_timestamp': datetime.now(timezone.utc)
            }
            
            await self.processing_queues[f'{priority}_priority'].put(processing_task)
            
            # If high priority, process immediately
            if priority == 'high':
                result = await self._execute_threat_analysis(processing_task)
                return result
            else:
                return {
                    'task_id': processing_task['task_id'],
                    'status': 'queued',
                    'priority': priority,
                    'estimated_processing_time': self._estimate_processing_time(priority)
                }
            
        except Exception as e:
            logger.error(f"Threat intelligence processing failed: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def _determine_processing_priority(self, threat_input: ThreatIntelligenceInput) -> str:
        """Determine processing priority based on threat characteristics"""
        try:
            priority_thresholds = self.aggregation_config['processing']['priority_thresholds']
            
            # Base priority on confidence score
            if threat_input.confidence_score >= priority_thresholds['high']:
                return 'high'
            elif threat_input.confidence_score >= priority_thresholds['normal']:
                return 'normal'
            else:
                return 'low'
            
        except Exception as e:
            logger.error(f"Priority determination failed: {e}")
            return 'normal'  # Safe default
    
    async def _execute_threat_analysis(self, processing_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive threat analysis with ROE integration"""
        try:
            threat_input = processing_task['threat_input']
            analysis_start = time.time()
            
            # Step 1: Multi-source correlation
            correlation_data = await self.correlation_engine.correlate_intelligence(threat_input)
            
            # Step 2: ROE-based threat classification
            threat_classification = await self.roe_classifier.classify_threat(
                threat_input, correlation_data
            )
            
            # Step 3: Generate engagement authorization
            engagement_authorization = await self._generate_engagement_authorization(
                threat_classification
            )
            
            # Step 4: Create comprehensive audit event
            audit_event = await self._create_audit_event(
                threat_classification, engagement_authorization, threat_input
            )
            
            # Step 5: Store results
            await self._store_analysis_results(
                threat_input, threat_classification, engagement_authorization, correlation_data
            )
            
            # Step 6: Execute authorized actions (if any)
            action_results = await self._execute_authorized_actions(
                engagement_authorization, threat_classification
            )
            
            analysis_time = (time.time() - analysis_start) * 1000
            
            # Create comprehensive result
            result = {
                'task_id': processing_task['task_id'],
                'threat_input_id': threat_input.input_id,
                'threat_classification': asdict(threat_classification),
                'engagement_authorization': asdict(engagement_authorization),
                'correlation_summary': correlation_data,
                'audit_event_id': audit_event.event_id,
                'action_results': action_results,
                'analysis_time_ms': analysis_time,
                'status': 'completed',
                'completion_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Update metrics
            self.aggregation_metrics['analyses_completed'] += 1
            self.aggregation_metrics['total_analysis_time_ms'] += analysis_time
            
            return result
            
        except Exception as e:
            logger.error(f"Threat analysis execution failed: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def _generate_engagement_authorization(self, 
                                               threat_classification: ROEThreatClassification) -> EngagementAuthorization:
        """Generate ROE-compliant engagement authorization"""
        try:
            authorization_id = str(uuid4())
            current_time = datetime.now(timezone.utc)
            
            # Determine if human authorization is required
            human_required = (
                threat_classification.roe_level == ROELevel.NEUTRALIZE or
                threat_classification.confidence_score >= 
                self.aggregation_config['roe_integration']['human_review_threshold']
            )
            
            # Calculate authorization expiry
            if threat_classification.time_sensitivity == 'immediate':
                expiry_hours = 1
            elif threat_classification.time_sensitivity == 'urgent':
                expiry_hours = 4
            else:
                expiry_hours = 24
            
            authorization_expiry = current_time + timedelta(hours=expiry_hours)
            
            # Generate authorized actions based on ROE level and engagement recommendations
            authorized_actions = self._generate_authorized_actions(threat_classification)
            
            # Assess collateral damage potential
            collateral_assessment = self._assess_collateral_damage(threat_classification)
            
            # Create authorization
            authorization = EngagementAuthorization(
                authorization_id=authorization_id,
                threat_classification=threat_classification,
                roe_level=threat_classification.roe_level,
                authorized_actions=authorized_actions,
                authorization_timestamp=current_time,
                authorization_expiry=authorization_expiry,
                authorizing_system="arcs_threat_aggregation",
                human_authorized=False,  # Will be updated if human review occurs
                authorization_conditions=[
                    f"roe_level_{threat_classification.roe_level.value}_authorized",
                    f"confidence_threshold_{threat_classification.confidence_score:.2f}_met",
                    "compliance_verified"
                ],
                success_criteria=[
                    "threat_neutralized",
                    "no_collateral_damage",
                    "roe_compliance_maintained"
                ],
                abort_conditions=[
                    "confidence_score_drops_below_0.3",
                    "collateral_damage_detected",
                    "roe_violation_risk"
                ],
                collateral_damage_assessment=collateral_assessment,
                legal_review_status="automated_compliance_check_passed"
            )
            
            # Store authorization
            self.engagement_authorizations[authorization_id] = authorization
            
            return authorization
            
        except Exception as e:
            logger.error(f"Engagement authorization generation failed: {e}")
            # Return minimal safe authorization
            return self._create_safe_fallback_authorization(threat_classification)
    
    def _generate_authorized_actions(self, threat_classification: ROEThreatClassification) -> List[str]:
        """Generate specific authorized actions based on classification"""
        authorized_actions = []
        
        # Base actions from engagement recommendations
        authorized_actions.extend(threat_classification.engagement_recommendations)
        
        # ROE level specific actions
        if threat_classification.roe_level == ROELevel.OBSERVE:
            authorized_actions.extend([
                'log_threat_event',
                'update_threat_intelligence',
                'monitor_threat_development'
            ])
        elif threat_classification.roe_level == ROELevel.DECEIVE:
            authorized_actions.extend([
                'deploy_deception_measures',
                'false_data_injection',
                'redirect_malicious_traffic'
            ])
        elif threat_classification.roe_level == ROELevel.DEGRADE:
            authorized_actions.extend([
                'implement_traffic_shaping',
                'deploy_network_blocks',
                'activate_defense_countermeasures'
            ])
        elif threat_classification.roe_level == ROELevel.NEUTRALIZE:
            authorized_actions.extend([
                'comprehensive_threat_response',
                'activate_all_countermeasures',
                'coordinate_with_external_systems'
            ])
        
        return list(set(authorized_actions))  # Remove duplicates
    
    async def _create_audit_event(self, threat_classification: ROEThreatClassification,
                                 engagement_authorization: EngagementAuthorization,
                                 threat_input: ThreatIntelligenceInput) -> ROEAuditEvent:
        """Create comprehensive ROE audit event"""
        try:
            audit_event = ROEAuditEvent(
                event_id=str(uuid4()),
                event_type="threat_analysis_and_authorization",
                roe_level=threat_classification.roe_level,
                threat_classification_id=threat_classification.classification_id,
                authorization_id=engagement_authorization.authorization_id,
                action_taken=f"threat_classified_as_{threat_classification.threat_tier.value}",
                decision_rationale=f"Confidence: {threat_classification.confidence_score:.2f}, "
                                 f"Tier: {threat_classification.threat_tier.value}, "
                                 f"ROE: {threat_classification.roe_level.value}",
                confidence_score=threat_classification.confidence_score,
                human_involvement=engagement_authorization.human_authorized,
                system_components=[
                    "threat_aggregation_engine",
                    "roe_classification_engine",
                    "correlation_engine"
                ],
                evidence_summary={
                    'threat_indicators': threat_classification.threat_indicators,
                    'source_correlation': threat_classification.source_correlation,
                    'attribution_data': threat_classification.attribution_data,
                    'original_source': threat_input.source.value
                },
                compliance_status="compliant",
                audit_timestamp=datetime.now(timezone.utc),
                legal_framework_references=[
                    "defensive_cybersecurity_operations",
                    "autonomous_system_authority",
                    "roe_framework_v3"
                ],
                ethical_considerations=[
                    "proportional_response",
                    "minimal_collateral_impact",
                    "human_oversight_when_required"
                ]
            )
            
            # Store audit event
            await self._store_audit_event(audit_event)
            
            return audit_event
            
        except Exception as e:
            logger.error(f"Audit event creation failed: {e}")
            # Return minimal audit event
            return self._create_minimal_audit_event(threat_classification, threat_input)
    
    async def _store_audit_event(self, audit_event: ROEAuditEvent) -> None:
        """Store audit event in the SQLite audit database.

        Inserts a complete ``ROEAuditEvent`` row into the
        ``roe_audit_events`` table.  The caller is responsible for
        ensuring the event has been fully populated.

        Args:
            audit_event: The fully-populated audit event to persist.
        """
        try:
            conn = sqlite3.connect(self.audit_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO roe_audit_events
                (event_id, event_type, roe_level, threat_classification_id,
                 authorization_id, action_taken, decision_rationale, confidence_score,
                 human_involvement, system_components, evidence_summary,
                 compliance_status, audit_timestamp, legal_framework_references,
                 ethical_considerations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_event.event_id,
                audit_event.event_type,
                audit_event.roe_level.value,
                audit_event.threat_classification_id,
                audit_event.authorization_id,
                audit_event.action_taken,
                audit_event.decision_rationale,
                audit_event.confidence_score,
                audit_event.human_involvement,
                json.dumps(audit_event.system_components),
                json.dumps(audit_event.evidence_summary),
                audit_event.compliance_status,
                audit_event.audit_timestamp.isoformat(),
                json.dumps(audit_event.legal_framework_references),
                json.dumps(audit_event.ethical_considerations)
            ))
            
            conn.commit()
            conn.close()
            
            # Also store in memory
            self.audit_events.append(audit_event)
            
        except Exception as e:
            logger.error(f"Audit event storage failed: {e}")
    
    async def get_aggregation_status(self) -> Dict[str, Any]:
        """Get comprehensive threat aggregation status"""
        try:
            status = {
                'engine_status': 'operational',
                'active_threats': len(self.active_threats),
                'total_classifications': len(self.threat_classifications),
                'active_authorizations': len(self.engagement_authorizations),
                'recent_audit_events': len([e for e in self.audit_events 
                                          if (datetime.now(timezone.utc) - e.audit_timestamp).total_seconds() < 3600]),
                'processing_queues': {
                    'high_priority': self.processing_queues['high_priority'].qsize(),
                    'normal_priority': self.processing_queues['normal_priority'].qsize(),
                    'low_priority': self.processing_queues['low_priority'].qsize()
                },
                'metrics': dict(self.aggregation_metrics),
                'roe_distribution': self._get_roe_level_distribution(),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {'engine_status': 'error', 'error': str(e)}
    
    def _get_roe_level_distribution(self) -> Dict[str, int]:
        """Get distribution of ROE levels in recent classifications"""
        distribution = defaultdict(int)
        
        recent_events = [e for e in self.audit_events 
                        if (datetime.now(timezone.utc) - e.audit_timestamp).hours < 24]
        
        for event in recent_events:
            distribution[f"roe_{event.roe_level.value}"] += 1
        
        return dict(distribution)
    
    async def shutdown(self):
        """Gracefully shutdown threat aggregation engine"""
        logger.info("Shutting down threat aggregation engine...")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Threat aggregation engine shutdown complete")


# Export primary interfaces
__all__ = [
    'ThreatAggregationEngine',
    'ROEThreatClassification',
    'EngagementAuthorization',
    'ThreatIntelligenceInput',
    'ROELevel',
    'ThreatTier',
    'ROEAuditEvent'
]


if __name__ == "__main__":
    # Development testing and validation
    async def test_threat_aggregation():
        """Comprehensive testing of threat aggregation functionality"""
        
        # Mock intelligence database
        class MockIntelligenceDB:
            """Minimal mock intelligence database for threat aggregation smoke tests.

            Maintains an in-memory record store so that ``store_intelligence``
            calls can be verified after the test run.  ``advanced_query``
            supports basic filtering by ``intelligence_type`` and
            ``min_confidence``.
            """

            def __init__(self):
                self._records: list = []

            async def advanced_query(self, params: Dict[str, Any]) -> list:
                """Return stored records matching the supplied filters.

                Supported filter keys:
                    - ``intelligence_type``: exact string match.
                    - ``min_confidence``: minimum ``confidence_score``.
                    - ``limit``: maximum number of records returned.

                Args:
                    params: Query filter dictionary.

                Returns:
                    List of matching records (may be empty).
                """
                results = list(self._records)
                itype = params.get('intelligence_type')
                if itype:
                    results = [r for r in results if getattr(r, 'intelligence_type', None) == itype]
                min_conf = params.get('min_confidence')
                if min_conf is not None:
                    results = [r for r in results if getattr(r, 'confidence_score', 0) >= min_conf]
                limit = params.get('limit')
                if limit is not None:
                    results = results[:int(limit)]
                return results

            async def store_intelligence(self, record: Any) -> bool:
                """Persist an intelligence record in the in-memory store.

                Args:
                    record: The intelligence record to store.

                Returns:
                    ``True`` after the record has been appended.
                """
                self._records.append(record)
                print(f"Stored intelligence: {record.record_id}")
                return True
        
        # Initialize aggregation engine
        mock_db = MockIntelligenceDB()
        aggregation_engine = ThreatAggregationEngine(mock_db)
        
        try:
            # Initialize engine
            await aggregation_engine.initialize()
            
            # Create test threat input
            test_input = ThreatIntelligenceInput(
                input_id=str(uuid4()),
                source=IntelligenceSource.NETWORK_TELEMETRY,
                intelligence_type="suspicious_traffic",
                raw_data={
                    'source_ip': '192.168.1.100',
                    'destination_ip': '10.0.0.1',
                    'port': 443,
                    'protocol': 'tcp',
                    'payload_size': 1024,
                    'anomaly_score': 0.8
                },
                indicators=['suspicious_traffic', 'anomalous_behavior', 'high_entropy'],
                confidence_score=0.75,
                collection_timestamp=datetime.now(timezone.utc),
                source_reliability=0.9,
                correlation_keys=['192.168.1.100', 'suspicious_traffic']
            )
            
            # Process threat intelligence
            result = await aggregation_engine.process_threat_intelligence(test_input)
            print(f"Processing result: {json.dumps(result, indent=2, default=str)}")
            
            # Get engine status
            status = await aggregation_engine.get_aggregation_status()
            print(f"Engine status: {json.dumps(status, indent=2, default=str)}")
            
        finally:
            # Shutdown
            await aggregation_engine.shutdown()
            print("Test completed successfully")
    
    # Run test
    asyncio.run(test_threat_aggregation())
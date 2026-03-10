#!/usr/bin/env python3
"""
ARCS Attribution Engine - Recursive Threat Actor Intelligence
============================================================
Autonomous Reactive Cyber Systems - Attribution Intelligence Domain

Mission: Advanced threat actor attribution through behavioral profiling, campaign correlation,
infrastructure analysis, and recursive machine learning with continuous model evolution
through operational feedback and attribution hypothesis validation.

Classification: ATTRIBUTION INTELLIGENCE - SOVEREIGN INFRASTRUCTURE
ROE Authority: Autonomous threat actor profiling with recursive learning evolution
Deployment: Field-ready production system with attribution cognitive improvement
"""

import asyncio
import logging
import json
import time
import hashlib
import pickle
import threading
import sqlite3
import tempfile
import shutil
import re
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Callable, Tuple, Iterator
from uuid import UUID, uuid4
from collections import defaultdict, deque, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

import numpy as np
import pandas as pd
import aiofiles
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# ML and attribution analysis
import onnxruntime as ort
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from scipy.stats import entropy, pearsonr
from scipy.spatial.distance import cosine, euclidean
import networkx as nx

# Advanced attribution techniques
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class AttributionConfidence(Enum):
    """Attribution confidence assessment levels"""
    UNATTRIBUTED = 0.1     # No clear attribution
    POSSIBLE = 0.3         # Weak attribution signals
    PROBABLE = 0.6         # Moderate attribution confidence
    HIGHLY_LIKELY = 0.8    # Strong attribution evidence
    CONFIRMED = 0.95       # Definitive attribution


class ActorCategory(Enum):
    """Threat actor categorization taxonomy"""
    NATION_STATE = "nation_state"
    CYBERCRIMINAL_GROUP = "cybercriminal_group"
    HACKTIVIST = "hacktivist"
    INSIDER_THREAT = "insider_threat"
    SCRIPT_KIDDIE = "script_kiddie"
    CORPORATE_ESPIONAGE = "corporate_espionage"
    UNKNOWN_ACTOR = "unknown_actor"
    AUTOMATED_SYSTEM = "automated_system"


class AttributionMethod(Enum):
    """Attribution analysis methodology"""
    BEHAVIORAL_PROFILING = "behavioral_profiling"
    INFRASTRUCTURE_ANALYSIS = "infrastructure_analysis"
    MALWARE_GENEALOGY = "malware_genealogy"
    CAMPAIGN_CORRELATION = "campaign_correlation"
    LINGUISTIC_ANALYSIS = "linguistic_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    TECHNICAL_FINGERPRINTING = "technical_fingerprinting"
    GEOLOCATION_ANALYSIS = "geolocation_analysis"


class ThreatCampaignPhase(Enum):
    """Campaign lifecycle phase identification"""
    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_CONTROL = "command_control"
    ACTIONS_OBJECTIVES = "actions_objectives"
    PERSISTENCE = "persistence"
    LATERAL_MOVEMENT = "lateral_movement"
    EXFILTRATION = "exfiltration"


@dataclass
class ThreatActor:
    """Comprehensive threat actor profile"""
    actor_id: str
    actor_names: List[str]
    actor_category: ActorCategory
    attribution_confidence: AttributionConfidence
    first_observed: datetime
    last_observed: datetime
    active_campaigns: List[str]
    historical_campaigns: List[str]
    behavioral_signature: Dict[str, Any]
    infrastructure_fingerprint: Dict[str, Any]
    malware_families: List[str]
    target_sectors: List[str]
    target_geographies: List[str]
    tactics_techniques: List[str]  # MITRE ATT&CK TTPs
    capabilities_assessment: Dict[str, float]
    motivation_profile: Dict[str, float]
    operational_patterns: Dict[str, Any]
    linguistic_markers: List[str]
    technical_proficiency: float
    resource_availability: float
    attribution_evidence: List[Dict[str, Any]]
    confidence_factors: Dict[str, float]
    related_actors: List[str]
    deception_indicators: List[str]
    false_flag_probability: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatCampaign:
    """Threat campaign analysis structure"""
    campaign_id: str
    campaign_names: List[str]
    attributed_actor: Optional[str]
    attribution_confidence: AttributionConfidence
    campaign_start: datetime
    campaign_end: Optional[datetime]
    campaign_phases: List[ThreatCampaignPhase]
    target_analysis: Dict[str, Any]
    infrastructure_used: List[str]
    malware_deployed: List[str]
    attack_vectors: List[str]
    techniques_observed: List[str]
    indicators_of_compromise: List[str]
    victim_impact_assessment: Dict[str, Any]
    campaign_evolution: List[Dict[str, Any]]
    deception_techniques: List[str]
    countermeasures_encountered: List[str]
    success_metrics: Dict[str, float]
    intelligence_sources: List[str]
    correlation_strength: float
    validation_status: str = "pending"


@dataclass
class AttributionHypothesis:
    """Attribution hypothesis with evidence chain"""
    hypothesis_id: str
    primary_actor: str
    alternative_actors: List[str]
    confidence_score: float
    evidence_chain: List[Dict[str, Any]]
    supporting_indicators: List[str]
    contradicting_indicators: List[str]
    hypothesis_reasoning: List[str]
    validation_criteria: List[str]
    uncertainty_factors: List[str]
    deception_assessment: Dict[str, Any]
    hypothesis_timestamp: datetime
    last_updated: datetime
    validation_status: Optional[bool] = None
    peer_review_status: str = "pending"


@dataclass
class AttributionSession:
    """Session-level attribution analytics for model training"""
    session_id: str
    session_start: datetime
    session_end: Optional[datetime]
    intelligence_inputs: List[str]
    actors_analyzed: int
    campaigns_correlated: int
    hypotheses_generated: int
    attribution_methods_used: List[str]
    confidence_distribution: Dict[str, int]
    decision_points: List[Dict[str, Any]]
    reasoning_patterns: List[str]
    model_predictions: List[Dict[str, Any]]
    validation_outcomes: List[Dict[str, Any]]
    learning_insights: List[str]
    performance_metrics: Dict[str, float]
    model_updates_applied: List[str]
    error_patterns: List[str]
    session_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttributionTrainingData:
    """Training data for attribution model evolution"""
    training_id: str
    data_source: str  # behavioral_analysis, infrastructure_correlation, campaign_analysis
    feature_vector: np.ndarray
    actor_labels: Dict[str, Any]
    confidence_targets: np.ndarray
    attribution_patterns: List[str]
    validation_feedback: Optional[bool]
    training_timestamp: datetime
    data_quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecursiveAttributionEngine:
    """
    Recursive learning engine for threat actor attribution
    
    Implements autonomous model improvement through attribution validation,
    campaign correlation feedback, and recursive training on actor patterns.
    """
    
    def __init__(self, models_path: str = "models/attribution/"):
        self.models_path = Path(models_path)
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Model management
        self.active_models = {}
        self.model_versions = {}
        self.training_data_cache = deque(maxlen=8000)
        
        # Learning configuration
        self.learning_config = {
            'batch_size': 48,
            'learning_rate': 0.0015,
            'training_epochs': 12,
            'validation_split': 0.25,
            'retrain_threshold': 120,  # New samples before retraining
            'model_evolution_interval': 2700  # 45 minutes
        }
        
        # Training metrics
        self.training_metrics = defaultdict(list)
        self.learning_history = deque(maxlen=1500)
        
        # Model architectures for attribution capabilities
        self.model_architectures = {
            'actor_profiler': self._create_actor_profiling_model,
            'campaign_correlator': self._create_campaign_correlation_model,
            'attribution_classifier': self._create_attribution_classification_model,
            'confidence_estimator': self._create_confidence_estimation_model,
            'deception_detector': self._create_deception_detection_model
        }
        
        self._initialize_attribution_models()
    
    def _initialize_attribution_models(self):
        """Initialize or load existing attribution models"""
        try:
            for model_name, architecture_func in self.model_architectures.items():
                model_path = self.models_path / f"{model_name}.onnx"
                
                if model_path.exists():
                    # Load existing model
                    self.active_models[model_name] = ort.InferenceSession(str(model_path))
                    logger.info(f"Loaded existing attribution model: {model_name}")
                else:
                    # Create new model
                    model = architecture_func()
                    self.active_models[model_name] = model
                    logger.info(f"Created new attribution model: {model_name}")
                
                # Initialize version tracking
                self.model_versions[model_name] = {
                    'version': 1.0,
                    'last_updated': datetime.now(timezone.utc),
                    'training_samples': 0,
                    'attribution_accuracy': 0.0,
                    'false_positive_rate': 0.0
                }
            
            logger.info("Recursive attribution engine initialized")
            
        except Exception as e:
            logger.error(f"Attribution model initialization failed: {e}")
            raise
    
    def _create_actor_profiling_model(self):
        """Create neural network for threat actor profiling"""
        class ActorProfiler(nn.Module):
            def __init__(self, input_size=256, hidden_size=512, output_size=128):
                super(ActorProfiler, self).__init__()
                self.behavioral_encoder = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.25),
                    nn.Linear(hidden_size, hidden_size),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size),
                    nn.Dropout(0.2)
                )
                self.profile_generator = nn.Sequential(
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Tanh()
                )
            
            def forward(self, x):
                encoded = self.behavioral_encoder(x)
                return self.profile_generator(encoded)
        
        return ActorProfiler()
    
    def _create_campaign_correlation_model(self):
        """Create model for campaign correlation analysis"""
        class CampaignCorrelator(nn.Module):
            def __init__(self, input_size=256, hidden_size=384, output_size=64):
                super(CampaignCorrelator, self).__init__()
                self.campaign_analyzer = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(hidden_size, hidden_size),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size)
                )
                self.correlation_predictor = nn.Sequential(
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                analyzed = self.campaign_analyzer(x)
                return self.correlation_predictor(analyzed)
        
        return CampaignCorrelator()
    
    def _create_attribution_classification_model(self):
        """Create model for attribution classification"""
        class AttributionClassifier(nn.Module):
            def __init__(self, input_size=256, hidden_size=512, num_actor_categories=8):
                super(AttributionClassifier, self).__init__()
                self.classifier_network = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size // 2),
                    nn.Linear(hidden_size // 2, num_actor_categories),
                    nn.Softmax(dim=1)
                )
            
            def forward(self, x):
                return self.classifier_network(x)
        
        return AttributionClassifier()
    
    def _create_confidence_estimation_model(self):
        """Create confidence estimation model for attributions"""
        class ConfidenceEstimator(nn.Module):
            def __init__(self, input_size=256, hidden_size=256):
                super(ConfidenceEstimator, self).__init__()
                self.confidence_network = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.25),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                return self.confidence_network(x)
        
        return ConfidenceEstimator()
    
    def _create_deception_detection_model(self):
        """Create model for detecting deception and false flags"""
        class DeceptionDetector(nn.Module):
            def __init__(self, input_size=256, hidden_size=384, output_size=32):
                super(DeceptionDetector, self).__init__()
                self.deception_analyzer = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size // 2),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Tanh()
                )
            
            def forward(self, x):
                return self.deception_analyzer(x)
        
        return DeceptionDetector()
    
    async def add_attribution_training_data(self, training_data: AttributionTrainingData):
        """Add new training data for attribution model evolution"""
        try:
            # Add to cache
            self.training_data_cache.append(training_data)
            
            # Update training metrics
            self.training_metrics['attribution_samples_added'].append(len(self.training_data_cache))
            self.training_metrics['data_quality'].append(training_data.data_quality_score)
            
            # Check if retraining is needed
            if len(self.training_data_cache) >= self.learning_config['retrain_threshold']:
                await self._trigger_attribution_retraining()
            
        except Exception as e:
            logger.error(f"Attribution training data addition failed: {e}")
    
    async def _trigger_attribution_retraining(self):
        """Trigger attribution model retraining with accumulated data"""
        try:
            logger.info("Starting recursive attribution model retraining...")
            
            # Prepare attribution training datasets
            training_datasets = await self._prepare_attribution_training_datasets()
            
            # Retrain each attribution model
            for model_name, model in self.active_models.items():
                if isinstance(model, nn.Module):  # PyTorch models
                    await self._retrain_attribution_pytorch_model(model_name, model, training_datasets)
                else:  # ONNX models
                    await self._update_attribution_onnx_model(model_name, training_datasets)
            
            # Clear training cache
            self.training_data_cache.clear()
            
            # Update model versions
            await self._update_attribution_model_versions()
            
            logger.info("Recursive attribution model retraining completed")
            
        except Exception as e:
            logger.error(f"Attribution model retraining failed: {e}")
    
    async def _prepare_attribution_training_datasets(self) -> Dict[str, Any]:
        """Prepare attribution training datasets from cached data"""
        try:
            datasets = {
                'input_features': [],
                'actor_profiling_targets': [],
                'campaign_correlation_targets': [],
                'attribution_classification_targets': [],
                'confidence_estimation_targets': [],
                'deception_detection_targets': []
            }
            
            for training_data in self.training_data_cache:
                # Extract features
                features = training_data.feature_vector
                datasets['input_features'].append(features)
                
                # Extract targets based on data source
                if training_data.data_source == 'behavioral_analysis':
                    datasets['actor_profiling_targets'].append(training_data.actor_labels)
                elif training_data.data_source == 'campaign_correlation':
                    datasets['campaign_correlation_targets'].append(training_data.actor_labels)
                elif training_data.data_source == 'attribution_classification':
                    datasets['attribution_classification_targets'].append(training_data.actor_labels)
                elif training_data.data_source == 'confidence_estimation':
                    datasets['confidence_estimation_targets'].append(training_data.confidence_targets)
                elif training_data.data_source == 'deception_detection':
                    datasets['deception_detection_targets'].append(training_data.actor_labels)
            
            # Convert to tensors
            for key in datasets:
                if datasets[key]:
                    datasets[key] = torch.tensor(np.array(datasets[key]), dtype=torch.float32)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Attribution training dataset preparation failed: {e}")
            return {}


class ThreatActorProfiler:
    """
    Advanced threat actor profiling engine
    
    Creates comprehensive behavioral and technical profiles of threat actors
    through multi-dimensional analysis and recursive pattern recognition.
    """
    
    def __init__(self, intelligence_db, attribution_learning_engine):
        self.intelligence_db = intelligence_db
        self.learning_engine = attribution_learning_engine
        
        # Profiling components
        self.actor_profiles = {}
        self.behavioral_patterns = {}
        self.infrastructure_clusters = {}
        
        # Analysis techniques
        self.profiling_techniques = {
            'behavioral_clustering': self._perform_behavioral_clustering,
            'infrastructure_analysis': self._analyze_infrastructure_patterns,
            'malware_genealogy': self._analyze_malware_genealogy,
            'temporal_profiling': self._perform_temporal_profiling,
            'linguistic_analysis': self._analyze_linguistic_patterns,
            'technical_profiling': self._analyze_technical_capabilities
        }
        
        # Profiling configuration
        self.profiling_config = {
            'min_confidence_threshold': 0.4,
            'clustering_epsilon': 0.3,
            'min_samples_per_cluster': 3,
            'temporal_window_days': 90,
            'behavioral_similarity_threshold': 0.75
        }
        
        # Performance metrics
        self.profiling_metrics = defaultdict(int)
    
    async def create_actor_profile(self, intelligence_data: List[Dict[str, Any]]) -> ThreatActor:
        """Create comprehensive threat actor profile from intelligence data"""
        try:
            profiling_start = time.time()
            
            # Extract actor indicators
            actor_indicators = await self._extract_actor_indicators(intelligence_data)
            
            # Perform behavioral analysis
            behavioral_profile = await self._analyze_behavioral_patterns(intelligence_data)
            
            # Analyze infrastructure fingerprints
            infrastructure_profile = await self._analyze_infrastructure_fingerprints(intelligence_data)
            
            # Correlate with known actors
            correlation_results = await self._correlate_with_known_actors(
                actor_indicators, behavioral_profile, infrastructure_profile
            )
            
            # Generate actor profile
            actor_profile = await self._synthesize_actor_profile(
                actor_indicators, behavioral_profile, infrastructure_profile, correlation_results
            )
            
            # Calculate attribution confidence
            attribution_confidence = await self._calculate_attribution_confidence(actor_profile)
            actor_profile.attribution_confidence = attribution_confidence
            
            # Generate training data
            training_data = await self._generate_profiling_training_data(
                intelligence_data, actor_profile
            )
            
            # Add to learning engine
            await self.learning_engine.add_attribution_training_data(training_data)
            
            # Store actor profile
            self.actor_profiles[actor_profile.actor_id] = actor_profile
            
            # Update metrics
            profiling_time = (time.time() - profiling_start) * 1000
            self.profiling_metrics['profiles_created'] += 1
            self.profiling_metrics['total_profiling_time_ms'] += profiling_time
            
            logger.info(f"Created actor profile {actor_profile.actor_id} in {profiling_time:.2f}ms")
            
            return actor_profile
            
        except Exception as e:
            logger.error(f"Actor profiling failed: {e}")
            raise
    
    async def _extract_actor_indicators(self, intelligence_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract threat actor indicators from intelligence data"""
        try:
            indicators = {
                'ip_addresses': set(),
                'domain_names': set(),
                'file_hashes': set(),
                'email_addresses': set(),
                'infrastructure_patterns': [],
                'attack_techniques': [],
                'malware_families': set(),
                'campaign_identifiers': [],
                'linguistic_markers': [],
                'temporal_patterns': [],
                'geolocation_data': []
            }
            
            # Extract indicators from each intelligence record
            for intel_record in intelligence_data:
                processed_indicators = intel_record.get('processed_indicators', [])
                raw_data = intel_record.get('raw_data', {})
                
                # Extract network indicators
                for indicator in processed_indicators:
                    if self._is_ip_address(indicator):
                        indicators['ip_addresses'].add(indicator)
                    elif self._is_domain_name(indicator):
                        indicators['domain_names'].add(indicator)
                    elif self._is_file_hash(indicator):
                        indicators['file_hashes'].add(indicator)
                    elif self._is_email_address(indicator):
                        indicators['email_addresses'].add(indicator)
                
                # Extract structured data
                if 'attack_techniques' in raw_data:
                    indicators['attack_techniques'].extend(raw_data['attack_techniques'])
                
                if 'malware_family' in raw_data:
                    indicators['malware_families'].add(raw_data['malware_family'])
                
                if 'campaign_id' in raw_data:
                    indicators['campaign_identifiers'].append(raw_data['campaign_id'])
                
                # Extract temporal patterns
                if 'collection_timestamp' in intel_record:
                    indicators['temporal_patterns'].append(intel_record['collection_timestamp'])
                
                # Extract geolocation data
                if 'geolocation' in raw_data:
                    indicators['geolocation_data'].append(raw_data['geolocation'])
            
            # Convert sets to lists for JSON serialization
            for key, value in indicators.items():
                if isinstance(value, set):
                    indicators[key] = list(value)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Actor indicator extraction failed: {e}")
            return {}
    
    async def _analyze_behavioral_patterns(self, intelligence_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavioral patterns of threat actor"""
        try:
            behavioral_analysis = {
                'attack_timing_patterns': {},
                'target_selection_patterns': {},
                'technique_preferences': {},
                'infrastructure_usage_patterns': {},
                'persistence_methods': [],
                'evasion_techniques': [],
                'operational_security_level': 0.0,
                'technical_sophistication': 0.0
            }
            
            # Analyze timing patterns
            timestamps = []
            for intel_record in intelligence_data:
                if 'collection_timestamp' in intel_record:
                    timestamps.append(datetime.fromisoformat(intel_record['collection_timestamp']))
            
            if timestamps:
                behavioral_analysis['attack_timing_patterns'] = self._analyze_temporal_patterns(timestamps)
            
            # Analyze technique preferences
            all_techniques = []
            for intel_record in intelligence_data:
                raw_data = intel_record.get('raw_data', {})
                if 'attack_techniques' in raw_data:
                    all_techniques.extend(raw_data['attack_techniques'])
            
            if all_techniques:
                technique_counts = Counter(all_techniques)
                behavioral_analysis['technique_preferences'] = dict(technique_counts.most_common(10))
            
            # Analyze target selection
            target_info = []
            for intel_record in intelligence_data:
                raw_data = intel_record.get('raw_data', {})
                if 'target_sector' in raw_data:
                    target_info.append(raw_data['target_sector'])
                if 'target_geography' in raw_data:
                    target_info.append(raw_data['target_geography'])
            
            if target_info:
                target_counts = Counter(target_info)
                behavioral_analysis['target_selection_patterns'] = dict(target_counts.most_common(5))
            
            # Calculate sophistication scores
            behavioral_analysis['technical_sophistication'] = self._calculate_technical_sophistication(intelligence_data)
            behavioral_analysis['operational_security_level'] = self._calculate_opsec_level(intelligence_data)
            
            return behavioral_analysis
            
        except Exception as e:
            logger.error(f"Behavioral pattern analysis failed: {e}")
            return {}
    
    def _analyze_temporal_patterns(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze temporal patterns in threat actor activity"""
        try:
            if not timestamps:
                return {}
            
            # Sort timestamps
            timestamps.sort()
            
            # Calculate intervals between activities
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
                intervals.append(interval)
            
            # Analyze patterns
            patterns = {
                'total_activity_span_days': (timestamps[-1] - timestamps[0]).days,
                'activity_frequency_hours': statistics.mean(intervals) if intervals else 0,
                'activity_regularity': 1.0 / (statistics.stdev(intervals) + 1) if len(intervals) > 1 else 0,
                'most_active_hours': self._find_most_active_hours(timestamps),
                'most_active_days': self._find_most_active_days(timestamps),
                'burst_activity_detected': len([i for i in intervals if i < 1]) > len(intervals) * 0.3
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Temporal pattern analysis failed: {e}")
            return {}
    
    def _find_most_active_hours(self, timestamps: List[datetime]) -> List[int]:
        """Find most active hours for threat actor"""
        hour_counts = Counter(ts.hour for ts in timestamps)
        return [hour for hour, count in hour_counts.most_common(3)]
    
    def _find_most_active_days(self, timestamps: List[datetime]) -> List[int]:
        """Find most active days of week for threat actor"""
        day_counts = Counter(ts.weekday() for ts in timestamps)
        return [day for day, count in day_counts.most_common(3)]
    
    def _calculate_technical_sophistication(self, intelligence_data: List[Dict[str, Any]]) -> float:
        """Calculate technical sophistication score"""
        try:
            sophistication_indicators = [
                'custom_malware', 'zero_day_exploits', 'advanced_evasion',
                'multi_stage_attacks', 'living_off_land', 'supply_chain_attacks'
            ]
            
            sophistication_score = 0.0
            total_indicators = 0
            
            for intel_record in intelligence_data:
                raw_data = intel_record.get('raw_data', {})
                for indicator in sophistication_indicators:
                    if indicator in raw_data and raw_data[indicator]:
                        sophistication_score += 1.0
                    total_indicators += 1
            
            return sophistication_score / max(total_indicators, 1)
            
        except Exception as e:
            logger.error(f"Technical sophistication calculation failed: {e}")
            return 0.5
    
    def _calculate_opsec_level(self, intelligence_data: List[Dict[str, Any]]) -> float:
        """Calculate operational security level"""
        try:
            opsec_indicators = [
                'infrastructure_compartmentalization', 'anti_forensics',
                'traffic_obfuscation', 'identity_protection', 'attribution_avoidance'
            ]
            
            opsec_score = 0.0
            total_indicators = 0
            
            for intel_record in intelligence_data:
                raw_data = intel_record.get('raw_data', {})
                for indicator in opsec_indicators:
                    if indicator in raw_data and raw_data[indicator]:
                        opsec_score += 1.0
                    total_indicators += 1
            
            return opsec_score / max(total_indicators, 1)
            
        except Exception as e:
            logger.error(f"OPSEC level calculation failed: {e}")
            return 0.5
    
    def _is_ip_address(self, value: str) -> bool:
        """Check if value is an IP address"""
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(ip_pattern, value))
    
    def _is_domain_name(self, value: str) -> bool:
        """Check if value is a domain name"""
        import re
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, value))
    
    def _is_file_hash(self, value: str) -> bool:
        """Check if value is a file hash"""
        return len(value) in [32, 40, 64] and all(c in '0123456789abcdefABCDEF' for c in value)
    
    def _is_email_address(self, value: str) -> bool:
        """Check if value is an email address"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))

    # ------------------------------------------------------------------
    # ThreatActorProfiler — missing analysis methods
    # ------------------------------------------------------------------

    async def _analyze_infrastructure_fingerprints(
        self, intelligence_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build an infrastructure fingerprint from observed network indicators."""
        try:
            ip_addresses: List[str] = []
            domains: List[str] = []
            asn_info: List[str] = []
            hosting_providers: List[str] = []

            for record in intelligence_data:
                for indicator in record.get('processed_indicators', []):
                    if self._is_ip_address(indicator):
                        ip_addresses.append(indicator)
                    elif self._is_domain_name(indicator):
                        domains.append(indicator)
                raw = record.get('raw_data', {})
                if 'asn' in raw:
                    asn_info.append(str(raw['asn']))
                if 'hosting_provider' in raw:
                    hosting_providers.append(str(raw['hosting_provider']))

            # Subnet diversity — count unique /24 prefixes
            unique_24s: Set[str] = set()
            for ip in ip_addresses:
                parts = ip.rsplit('.', 1)
                if len(parts) == 2:
                    unique_24s.add(parts[0])

            # Domain registration pattern analysis
            domain_tlds = Counter(d.rsplit('.', 1)[-1] for d in domains if '.' in d)

            fingerprint: Dict[str, Any] = {
                'ip_count': len(ip_addresses),
                'unique_ips': list(set(ip_addresses)),
                'domain_count': len(domains),
                'unique_domains': list(set(domains)),
                'subnet_diversity': len(unique_24s),
                'asn_distribution': dict(Counter(asn_info).most_common(10)),
                'hosting_providers': dict(Counter(hosting_providers).most_common(5)),
                'tld_distribution': dict(domain_tlds.most_common(10)),
                'infrastructure_complexity': min(1.0, (len(set(ip_addresses)) + len(set(domains))) / 100)
            }

            # Run DBSCAN on IP numeric representations if enough data
            if len(ip_addresses) >= 3:
                try:
                    numeric_ips = []
                    for ip in ip_addresses:
                        parts = ip.split('.')
                        if len(parts) == 4:
                            numeric_ips.append([int(p) for p in parts])
                    if len(numeric_ips) >= 3:
                        X = StandardScaler().fit_transform(np.array(numeric_ips, dtype=float))
                        labels = DBSCAN(eps=0.5, min_samples=2).fit_predict(X)
                        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                        fingerprint['ip_clusters'] = int(n_clusters)
                except Exception:
                    fingerprint['ip_clusters'] = 0
            else:
                fingerprint['ip_clusters'] = 0

            return fingerprint

        except Exception as e:
            logger.error(f"_analyze_infrastructure_fingerprints failed: {e}")
            return {}

    async def _correlate_with_known_actors(
        self,
        actor_indicators: Dict[str, Any],
        behavioral_profile: Dict[str, Any],
        infrastructure_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare extracted indicators against known actor profiles."""
        try:
            correlation_results: Dict[str, Any] = {
                'matched_actors': [],
                'best_match_actor': None,
                'best_match_score': 0.0,
                'correlation_method': 'multi_factor'
            }

            observed_techniques = set(behavioral_profile.get('technique_preferences', {}).keys())
            observed_ips = set(actor_indicators.get('ip_addresses', []))
            observed_domains = set(actor_indicators.get('domain_names', []))
            observed_malware = set(actor_indicators.get('malware_families', []))

            for known_actor_id, known_profile in self.actor_profiles.items():
                score_components: List[float] = []

                # TTP overlap
                known_ttps = set(getattr(known_profile, 'tactics_techniques', []))
                if observed_techniques and known_ttps:
                    ttp_score = len(observed_techniques & known_ttps) / max(
                        len(observed_techniques | known_ttps), 1
                    )
                    score_components.append(ttp_score)

                # Malware family overlap
                known_malware = set(getattr(known_profile, 'malware_families', []))
                if observed_malware and known_malware:
                    malware_score = len(observed_malware & known_malware) / max(
                        len(observed_malware | known_malware), 1
                    )
                    score_components.append(malware_score * 1.5)  # weighted

                # Infrastructure overlap
                known_infra = known_profile.infrastructure_fingerprint or {}
                known_ips = set(known_infra.get('unique_ips', []))
                known_domains = set(known_infra.get('unique_domains', []))
                if observed_ips and known_ips:
                    ip_score = len(observed_ips & known_ips) / max(len(observed_ips | known_ips), 1)
                    score_components.append(ip_score * 2.0)  # highest weight
                if observed_domains and known_domains:
                    domain_score = len(observed_domains & known_domains) / max(
                        len(observed_domains | known_domains), 1
                    )
                    score_components.append(domain_score * 2.0)

                if not score_components:
                    continue

                composite = float(np.mean(score_components))
                if composite > 0.1:
                    correlation_results['matched_actors'].append({
                        'actor_id': known_actor_id,
                        'correlation_score': composite,
                        'actor_category': known_profile.actor_category.value
                    })

            # Sort by score and pick best
            correlation_results['matched_actors'].sort(
                key=lambda x: x['correlation_score'], reverse=True
            )
            if correlation_results['matched_actors']:
                best = correlation_results['matched_actors'][0]
                correlation_results['best_match_actor'] = best['actor_id']
                correlation_results['best_match_score'] = best['correlation_score']

            return correlation_results

        except Exception as e:
            logger.error(f"_correlate_with_known_actors failed: {e}")
            return {'matched_actors': [], 'best_match_actor': None, 'best_match_score': 0.0}

    async def _synthesize_actor_profile(
        self,
        actor_indicators: Dict[str, Any],
        behavioral_profile: Dict[str, Any],
        infrastructure_profile: Dict[str, Any],
        correlation_results: Dict[str, Any]
    ) -> ThreatActor:
        """Synthesize a ThreatActor dataclass from all analysis results."""
        try:
            actor_id = str(uuid4())
            now = datetime.now(timezone.utc)

            # Determine actor category from correlation or default to unknown
            actor_category = ActorCategory.UNKNOWN_ACTOR
            best_match_id = correlation_results.get('best_match_actor')
            if best_match_id and correlation_results.get('best_match_score', 0) > 0.7:
                known = self.actor_profiles.get(best_match_id)
                if known:
                    actor_id = best_match_id
                    actor_category = known.actor_category

            # Determine timestamps from temporal patterns
            temporal = behavioral_profile.get('attack_timing_patterns', {})
            span_days = temporal.get('total_activity_span_days', 0)
            first_obs = now - timedelta(days=span_days) if span_days > 0 else now

            techniques = list(behavioral_profile.get('technique_preferences', {}).keys())
            target_patterns = behavioral_profile.get('target_selection_patterns', {})
            target_sectors = [k for k in target_patterns.keys() if not k.startswith('geo_')]
            target_geos = actor_indicators.get('geolocation_data', [])

            actor = ThreatActor(
                actor_id=actor_id,
                actor_names=[f"ACTOR-{actor_id[:8].upper()}"],
                actor_category=actor_category,
                attribution_confidence=AttributionConfidence.POSSIBLE,  # updated later
                first_observed=first_obs,
                last_observed=now,
                active_campaigns=list(set(actor_indicators.get('campaign_identifiers', []))),
                historical_campaigns=[],
                behavioral_signature=behavioral_profile,
                infrastructure_fingerprint=infrastructure_profile,
                malware_families=list(actor_indicators.get('malware_families', [])),
                target_sectors=target_sectors[:10],
                target_geographies=[str(g) for g in target_geos[:10]],
                tactics_techniques=techniques,
                capabilities_assessment={
                    'technical_sophistication': behavioral_profile.get('technical_sophistication', 0.5),
                    'operational_security': behavioral_profile.get('operational_security_level', 0.5),
                    'infrastructure_complexity': infrastructure_profile.get('infrastructure_complexity', 0.5)
                },
                motivation_profile={},
                operational_patterns=temporal,
                linguistic_markers=actor_indicators.get('linguistic_markers', []),
                technical_proficiency=behavioral_profile.get('technical_sophistication', 0.5),
                resource_availability=infrastructure_profile.get('infrastructure_complexity', 0.5),
                attribution_evidence=[
                    {'type': 'correlation', 'results': correlation_results}
                ],
                confidence_factors={
                    'ttp_match': correlation_results.get('best_match_score', 0.0),
                    'indicator_volume': min(1.0, (
                        len(actor_indicators.get('ip_addresses', [])) +
                        len(actor_indicators.get('domain_names', []))
                    ) / 50)
                },
                related_actors=[m['actor_id'] for m in correlation_results.get('matched_actors', [])[:5]],
                deception_indicators=[],
                false_flag_probability=0.1,
                metadata={'synthesized_at': now.isoformat()}
            )

            return actor

        except Exception as e:
            logger.error(f"_synthesize_actor_profile failed: {e}")
            raise

    async def _calculate_attribution_confidence(
        self, actor_profile: ThreatActor
    ) -> AttributionConfidence:
        """Calculate attribution confidence level from actor profile evidence."""
        try:
            factors: List[float] = []

            # Indicator volume score
            infra = actor_profile.infrastructure_fingerprint or {}
            n_ips = infra.get('ip_count', 0)
            n_domains = infra.get('domain_count', 0)
            indicator_score = min(1.0, (n_ips + n_domains) / 20)
            factors.append(indicator_score)

            # TTP coverage
            n_ttps = len(actor_profile.tactics_techniques)
            ttp_score = min(1.0, n_ttps / 10)
            factors.append(ttp_score)

            # Correlation match score
            conf_factors = actor_profile.confidence_factors or {}
            ttp_match = conf_factors.get('ttp_match', 0.0)
            factors.append(float(ttp_match))

            # Campaign evidence
            campaign_score = min(1.0, len(actor_profile.active_campaigns) / 3)
            factors.append(campaign_score)

            composite = float(np.mean(factors)) if factors else 0.1

            if composite >= 0.9:
                return AttributionConfidence.CONFIRMED
            elif composite >= 0.7:
                return AttributionConfidence.HIGHLY_LIKELY
            elif composite >= 0.5:
                return AttributionConfidence.PROBABLE
            elif composite >= 0.3:
                return AttributionConfidence.POSSIBLE
            else:
                return AttributionConfidence.UNATTRIBUTED

        except Exception as e:
            logger.error(f"_calculate_attribution_confidence failed: {e}")
            return AttributionConfidence.UNATTRIBUTED

    async def _generate_profiling_training_data(
        self,
        intelligence_data: List[Dict[str, Any]],
        actor_profile: ThreatActor
    ) -> AttributionTrainingData:
        """Generate training data from the profiling process."""
        try:
            features: List[float] = [
                actor_profile.attribution_confidence.value,
                actor_profile.technical_proficiency,
                actor_profile.resource_availability,
                actor_profile.false_flag_probability,
                len(actor_profile.tactics_techniques),
                len(actor_profile.malware_families),
                len(actor_profile.active_campaigns),
                len(actor_profile.related_actors),
                len(actor_profile.target_sectors),
                len(intelligence_data)
            ]
            # Pad to 256
            while len(features) < 256:
                features.append(0.0)

            confidence_targets = np.array(
                [actor_profile.attribution_confidence.value], dtype=np.float32
            )

            actor_labels: Dict[str, Any] = {
                'actor_id': actor_profile.actor_id,
                'actor_category': actor_profile.actor_category.value,
                'confidence': actor_profile.attribution_confidence.value
            }

            return AttributionTrainingData(
                training_id=str(uuid4()),
                data_source='behavioral_analysis',
                feature_vector=np.array(features[:256], dtype=np.float32),
                actor_labels=actor_labels,
                confidence_targets=confidence_targets,
                attribution_patterns=actor_profile.tactics_techniques[:20],
                validation_feedback=None,
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=actor_profile.attribution_confidence.value,
                metadata={'actor_id': actor_profile.actor_id}
            )

        except Exception as e:
            logger.error(f"_generate_profiling_training_data failed: {e}")
            return AttributionTrainingData(
                training_id=str(uuid4()),
                data_source='behavioral_analysis',
                feature_vector=np.zeros(256, dtype=np.float32),
                actor_labels={'actor_id': 'unknown'},
                confidence_targets=np.array([0.1], dtype=np.float32),
                attribution_patterns=[],
                validation_feedback=None,
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=0.1
            )

    def _perform_behavioral_clustering(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cluster behavioral indicators using DBSCAN."""
        try:
            if len(data) < 3:
                return {'clusters': 0, 'noise_points': len(data), 'cluster_labels': []}

            feature_rows: List[List[float]] = []
            for record in data:
                row = [
                    float(record.get('confidence_score', 0.5)),
                    float(record.get('threat_level', 0)),
                    len(record.get('processed_indicators', [])),
                ]
                feature_rows.append(row)

            X = StandardScaler().fit_transform(np.array(feature_rows, dtype=float))
            db = DBSCAN(
                eps=self.profiling_config['clustering_epsilon'],
                min_samples=self.profiling_config['min_samples_per_cluster']
            ).fit(X)
            labels = db.labels_
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

            return {
                'clusters': int(n_clusters),
                'noise_points': int(np.sum(labels == -1)),
                'cluster_labels': labels.tolist(),
                'cluster_sizes': dict(Counter(labels.tolist()))
            }
        except Exception as e:
            logger.error(f"_perform_behavioral_clustering failed: {e}")
            return {'clusters': 0, 'error': str(e)}

    def _analyze_infrastructure_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify recurring infrastructure deployment patterns."""
        try:
            all_ips: List[str] = []
            all_domains: List[str] = []
            for record in data:
                for ind in record.get('processed_indicators', []):
                    if self._is_ip_address(ind):
                        all_ips.append(ind)
                    elif self._is_domain_name(ind):
                        all_domains.append(ind)

            ip_counter = Counter(all_ips)
            domain_counter = Counter(all_domains)

            # Detect reuse patterns (same infra across multiple records)
            reused_ips = {ip: cnt for ip, cnt in ip_counter.items() if cnt > 1}
            reused_domains = {d: cnt for d, cnt in domain_counter.items() if cnt > 1}

            return {
                'total_ips': len(all_ips),
                'unique_ips': len(set(all_ips)),
                'total_domains': len(all_domains),
                'unique_domains': len(set(all_domains)),
                'reused_ips': reused_ips,
                'reused_domains': reused_domains,
                'infrastructure_reuse_ratio': (
                    len(reused_ips) + len(reused_domains)
                ) / max(len(set(all_ips)) + len(set(all_domains)), 1)
            }
        except Exception as e:
            logger.error(f"_analyze_infrastructure_patterns failed: {e}")
            return {}

    def _analyze_malware_genealogy(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trace malware family relationships across intelligence records."""
        try:
            family_timeline: Dict[str, List[str]] = defaultdict(list)
            for record in data:
                raw = record.get('raw_data', {})
                family = raw.get('malware_family', '')
                ts = str(record.get('collection_timestamp', ''))
                if family:
                    family_timeline[family].append(ts)

            family_frequency = {fam: len(ts_list) for fam, ts_list in family_timeline.items()}
            family_frequency_sorted = dict(
                sorted(family_frequency.items(), key=lambda x: x[1], reverse=True)
            )

            # Detect co-occurring families (in same record)
            co_occurrences: List[Tuple[str, str]] = []
            for record in data:
                raw = record.get('raw_data', {})
                families_in_record = raw.get('malware_families', [])
                if isinstance(families_in_record, list) and len(families_in_record) > 1:
                    for i in range(len(families_in_record)):
                        for j in range(i + 1, len(families_in_record)):
                            co_occurrences.append((families_in_record[i], families_in_record[j]))

            co_occurrence_counts = dict(Counter(co_occurrences).most_common(10))

            return {
                'observed_families': list(family_frequency_sorted.keys()),
                'family_frequency': family_frequency_sorted,
                'primary_family': next(iter(family_frequency_sorted), None),
                'co_occurring_families': {str(k): v for k, v in co_occurrence_counts.items()},
                'genealogy_depth': len(family_frequency_sorted)
            }
        except Exception as e:
            logger.error(f"_analyze_malware_genealogy failed: {e}")
            return {}

    def _perform_temporal_profiling(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Profile temporal activity patterns across intelligence records."""
        try:
            timestamps: List[datetime] = []
            for record in data:
                ts_raw = record.get('collection_timestamp')
                if ts_raw:
                    if isinstance(ts_raw, datetime):
                        timestamps.append(ts_raw)
                    else:
                        try:
                            parsed = datetime.fromisoformat(str(ts_raw))
                            timestamps.append(parsed)
                        except ValueError:
                            pass

            if not timestamps:
                return {'temporal_data_available': False}

            return self._analyze_temporal_patterns(timestamps)
        except Exception as e:
            logger.error(f"_perform_temporal_profiling failed: {e}")
            return {}

    def _analyze_linguistic_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract linguistic patterns from text fields in intelligence records."""
        try:
            all_text_tokens: List[str] = []
            language_indicators: List[str] = []

            for record in data:
                raw = record.get('raw_data', {})
                # Extract text from various fields
                for field_name in ['description', 'notes', 'analyst_notes', 'raw_content']:
                    text = raw.get(field_name, '')
                    if text and isinstance(text, str):
                        tokens = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
                        all_text_tokens.extend(tokens)

                if 'language' in raw:
                    language_indicators.append(str(raw['language']))

            token_freq = Counter(all_text_tokens)
            # Remove common English stop words
            stopwords = {
                'this', 'that', 'with', 'from', 'have', 'been', 'will', 'they',
                'their', 'also', 'when', 'were', 'what', 'which', 'into', 'used'
            }
            filtered_tokens = {
                tok: cnt for tok, cnt in token_freq.items() if tok not in stopwords
            }
            top_tokens = dict(
                sorted(filtered_tokens.items(), key=lambda x: x[1], reverse=True)[:20]
            )

            return {
                'vocabulary_size': len(set(all_text_tokens)),
                'top_terms': top_tokens,
                'detected_languages': dict(Counter(language_indicators).most_common(5)),
                'text_record_coverage': sum(
                    1 for r in data if any(
                        r.get('raw_data', {}).get(f) for f in ['description', 'notes', 'raw_content']
                    )
                ) / max(len(data), 1)
            }
        except Exception as e:
            logger.error(f"_analyze_linguistic_patterns failed: {e}")
            return {}

    def _analyze_technical_capabilities(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess technical capabilities from observed attack techniques."""
        try:
            all_techniques: List[str] = []
            capability_indicators: Dict[str, int] = defaultdict(int)

            capability_keywords: Dict[str, List[str]] = {
                'exploit_development': ['zero_day', '0day', 'exploit', 'overflow', 'injection'],
                'malware_development': ['custom_malware', 'backdoor', 'implant', 'loader'],
                'evasion': ['evasion', 'obfuscation', 'anti_analysis', 'sandbox', 'polymorphic'],
                'persistence': ['persistence', 'bootkit', 'rootkit', 'scheduled_task', 'registry'],
                'privilege_escalation': ['privilege', 'escalation', 'uac', 'elevation'],
                'lateral_movement': ['lateral', 'pass_the_hash', 'kerberoasting', 'wmi'],
                'exfiltration': ['exfiltration', 'dns_tunnel', 'steganography', 'covert_channel'],
                'cryptography': ['encryption', 'crypto', 'certificate', 'tls', 'ssl']
            }

            for record in data:
                raw = record.get('raw_data', {})
                techniques = raw.get('attack_techniques', [])
                all_techniques.extend(techniques)
                for technique in techniques:
                    tech_lower = technique.lower()
                    for capability, keywords in capability_keywords.items():
                        if any(kw in tech_lower for kw in keywords):
                            capability_indicators[capability] += 1

            technique_counter = Counter(all_techniques)
            sophistication = min(
                1.0,
                len(capability_indicators) / len(capability_keywords)
            )

            return {
                'observed_techniques': dict(technique_counter.most_common(20)),
                'capability_indicators': dict(capability_indicators),
                'capability_breadth': len(capability_indicators),
                'technical_sophistication_score': sophistication,
                'unique_techniques': len(set(all_techniques))
            }
        except Exception as e:
            logger.error(f"_analyze_technical_capabilities failed: {e}")
            return {}


class AttributionEngine:
    """
    Master ARCS Attribution Engine
    
    Orchestrates comprehensive threat actor attribution through multi-modal analysis,
    recursive learning, and continuous hypothesis validation and refinement.
    """
    
    def __init__(self, intelligence_db, threat_aggregation, data_fusion,
                 config_path: str = "config/attribution.yaml"):
        self.intelligence_db = intelligence_db
        self.threat_aggregation = threat_aggregation
        self.data_fusion = data_fusion
        self.config_path = Path(config_path)

        # Core engines
        self.learning_engine = RecursiveAttributionEngine()
        self.actor_profiler = ThreatActorProfiler(intelligence_db, self.learning_engine)

        # Attribution state
        self.active_attributions = {}
        self.attribution_hypotheses = {}
        self.campaign_correlations = {}

        # Configuration
        self.attribution_config = {}

        # Background services
        self.background_tasks = []
        self.shutdown_event = asyncio.Event()
        self._running = True

        # Performance metrics
        self.attribution_metrics = defaultdict(int)

        self._load_configuration()
    
    def _load_configuration(self):
        """Load attribution engine configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.attribution_config = yaml.safe_load(f)
            else:
                self.attribution_config = self._create_default_config()
                self._save_configuration()
            
            logger.info("Attribution engine configuration loaded")
            
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            self.attribution_config = self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default attribution configuration"""
        return {
            'attribution': {
                'continuous_attribution_enabled': True,
                'attribution_interval_hours': 6,
                'min_attribution_confidence': 0.6,
                'max_concurrent_attributions': 5
            },
            'actor_profiling': {
                'behavioral_analysis_enabled': True,
                'infrastructure_analysis_enabled': True,
                'malware_genealogy_enabled': True,
                'temporal_analysis_enabled': True
            },
            'learning': {
                'recursive_learning_enabled': True,
                'model_update_interval_hours': 0.75,
                'training_batch_size': 48,
                'learning_rate': 0.0015
            },
            'validation': {
                'hypothesis_validation_enabled': True,
                'peer_review_required': False,
                'confidence_threshold_validation': 0.8
            }
        }
    
    def _save_configuration(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.attribution_config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Configuration saving failed: {e}")
    
    async def initialize(self):
        """Initialize attribution engine"""
        try:
            logger.info("Initializing ARCS Attribution Engine...")
            
            # Start background services
            await self._start_attribution_services()
            
            logger.info("Attribution engine fully operational")
            
        except Exception as e:
            logger.error(f"Attribution engine initialization failed: {e}")
            raise
    
    async def _start_attribution_services(self):
        """Start background attribution services"""
        try:
            self.background_tasks.extend([
                asyncio.create_task(self._continuous_attribution_service()),
                asyncio.create_task(self._actor_profiling_service()),
                asyncio.create_task(self._campaign_correlation_service()),
                asyncio.create_task(self._hypothesis_validation_service())
            ])
            
            logger.info("Background attribution services started")
            
        except Exception as e:
            logger.error(f"Background service startup failed: {e}")
    
    async def perform_attribution_analysis(self, intelligence_ids: List[str]) -> Dict[str, Any]:
        """Perform comprehensive attribution analysis on intelligence data"""
        try:
            analysis_start = time.time()
            
            # Retrieve intelligence data
            intelligence_data = []
            for intel_id in intelligence_ids:
                record = await self.intelligence_db.retrieve_intelligence(intel_id)
                if record:
                    intelligence_data.append({
                        'record_id': record.record_id,
                        'intelligence_type': record.intelligence_type.value,
                        'collection_timestamp': record.collection_timestamp.isoformat(),
                        'processed_indicators': record.processed_indicators,
                        'raw_data': record.raw_data,
                        'confidence_score': record.confidence_score,
                        'threat_level': record.threat_level,
                        'metadata': record.metadata
                    })
            
            # Create actor profile
            actor_profile = await self.actor_profiler.create_actor_profile(intelligence_data)
            
            # Generate attribution hypotheses
            hypotheses = await self._generate_attribution_hypotheses(intelligence_data, actor_profile)
            
            # Correlate with campaigns
            campaign_correlations = await self._correlate_with_campaigns(intelligence_data, actor_profile)
            
            # Validate hypotheses
            validated_hypotheses = await self._validate_attribution_hypotheses(hypotheses)
            
            # Create attribution analysis result
            attribution_result = {
                'analysis_id': str(uuid4()),
                'actor_profile': asdict(actor_profile),
                'attribution_hypotheses': [asdict(h) for h in validated_hypotheses],
                'campaign_correlations': campaign_correlations,
                'confidence_assessment': self._calculate_overall_confidence(validated_hypotheses),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'intelligence_sources': intelligence_ids,
                'analysis_metadata': {
                    'analysis_duration_ms': (time.time() - analysis_start) * 1000,
                    'hypotheses_generated': len(hypotheses),
                    'correlations_found': len(campaign_correlations)
                }
            }
            
            # Store attribution analysis
            self.active_attributions[attribution_result['analysis_id']] = attribution_result
            
            # Update metrics
            self.attribution_metrics['analyses_completed'] += 1
            
            logger.info(f"Completed attribution analysis {attribution_result['analysis_id']}")
            
            return attribution_result
            
        except Exception as e:
            logger.error(f"Attribution analysis failed: {e}")
            raise
    
    # ------------------------------------------------------------------
    # Background service coroutines
    # ------------------------------------------------------------------

    async def _continuous_attribution_service(self) -> None:
        """Poll for unprocessed intel records and run attribution on each."""
        logger.info("Continuous attribution service started")
        while self._running:
            try:
                recent_records = await self._get_unprocessed_records(limit=50)
                for record in recent_records:
                    try:
                        profile = await self.actor_profiler.create_actor_profile(
                            [record] if isinstance(record, dict) else record
                        )
                        if profile:
                            await self._store_attribution_result(profile)
                    except Exception as e:
                        record_id = record.get('record_id', '?') if isinstance(record, dict) else '?'
                        logger.warning(f"Attribution failed for record {record_id}: {e}")
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Continuous attribution service error: {e}")
                await asyncio.sleep(10)
        logger.info("Continuous attribution service stopped")

    async def _actor_profiling_service(self) -> None:
        """Monitor for actors whose profiles are stale and refresh them."""
        logger.info("Actor profiling service started")
        while self._running:
            try:
                stale_actor_ids = await self._get_stale_actor_profiles(max_age_hours=24)
                for actor_id in stale_actor_ids:
                    try:
                        await self._refresh_actor_profile(actor_id)
                    except Exception as e:
                        logger.warning(f"Profile refresh failed for {actor_id}: {e}")
                await asyncio.sleep(120)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Actor profiling service error: {e}")
                await asyncio.sleep(15)
        logger.info("Actor profiling service stopped")

    async def _campaign_correlation_service(self) -> None:
        """Cluster actors by shared TTPs and infrastructure overlaps."""
        logger.info("Campaign correlation service started")
        while self._running:
            try:
                profiles = await self._get_recent_actor_profiles(limit=100)
                if len(profiles) >= 2:
                    correlations: List[Dict[str, Any]] = []
                    for i, p1 in enumerate(profiles):
                        for p2 in profiles[i + 1:]:
                            try:
                                score = self._calculate_ttp_overlap(p1, p2)
                                if score > 0.6:
                                    correlations.append({
                                        'actor_a': p1.actor_id if isinstance(p1, ThreatActor) else str(p1),
                                        'actor_b': p2.actor_id if isinstance(p2, ThreatActor) else str(p2),
                                        'correlation_score': score,
                                        'timestamp': time.time()
                                    })
                            except Exception:
                                continue
                    if correlations:
                        await self._store_campaign_correlations(correlations)
                        logger.info(f"Stored {len(correlations)} campaign correlations")
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Campaign correlation service error: {e}")
                await asyncio.sleep(30)
        logger.info("Campaign correlation service stopped")

    async def _hypothesis_validation_service(self) -> None:
        """Cross-validate pending attribution hypotheses against known actor DB."""
        logger.info("Hypothesis validation service started")
        while self._running:
            try:
                pending = await self._get_pending_hypotheses(limit=20)
                for hypothesis in pending:
                    try:
                        validation_result = await self._validate_hypothesis(hypothesis)
                        hyp_id = hypothesis.hypothesis_id if isinstance(hypothesis, AttributionHypothesis) else str(hypothesis)
                        await self._update_hypothesis_confidence(hyp_id, validation_result)
                    except Exception as e:
                        logger.warning(f"Hypothesis validation error: {e}")
                await asyncio.sleep(180)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Hypothesis validation service error: {e}")
                await asyncio.sleep(20)
        logger.info("Hypothesis validation service stopped")

    # ------------------------------------------------------------------
    # Background service helper methods
    # ------------------------------------------------------------------

    async def _get_unprocessed_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve unprocessed intel records from the intelligence database."""
        try:
            if hasattr(self.intelligence_db, 'get_unprocessed_records'):
                return await self.intelligence_db.get_unprocessed_records(limit=limit)
            if hasattr(self.intelligence_db, 'advanced_query'):
                records = await self.intelligence_db.advanced_query({
                    'processed': False,
                    'limit': limit
                })
                return [
                    {
                        'record_id': getattr(r, 'record_id', str(uuid4())),
                        'intelligence_type': getattr(r, 'intelligence_type', 'unknown'),
                        'collection_timestamp': getattr(r, 'collection_timestamp', datetime.now(timezone.utc)).isoformat()
                        if hasattr(getattr(r, 'collection_timestamp', None), 'isoformat')
                        else str(getattr(r, 'collection_timestamp', '')),
                        'processed_indicators': getattr(r, 'processed_indicators', []),
                        'raw_data': getattr(r, 'raw_data', {}),
                        'confidence_score': getattr(r, 'confidence_score', 0.5),
                        'threat_level': getattr(r, 'threat_level', 0),
                        'metadata': getattr(r, 'metadata', {})
                    }
                    for r in records
                ]
            logger.debug("Intelligence DB has no suitable query method; returning empty record list")
            return []
        except Exception as e:
            logger.error(f"_get_unprocessed_records failed: {e}")
            return []

    async def _store_attribution_result(self, profile: 'ThreatActor') -> None:
        """Persist an attribution result to storage."""
        try:
            self.active_attributions[profile.actor_id] = asdict(profile)
            if hasattr(self.intelligence_db, 'store_attribution'):
                await self.intelligence_db.store_attribution(asdict(profile))
            logger.debug(f"Stored attribution result for actor {profile.actor_id}")
        except Exception as e:
            logger.error(f"_store_attribution_result failed: {e}")

    async def _get_stale_actor_profiles(self, max_age_hours: int = 24) -> List[str]:
        """Return actor IDs whose profiles have not been updated within max_age_hours."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            stale_ids = []
            for actor_id, profile in self.actor_profiler.actor_profiles.items():
                last_seen = getattr(profile, 'last_observed', None)
                if last_seen is None:
                    stale_ids.append(actor_id)
                elif isinstance(last_seen, datetime):
                    last_seen_aware = last_seen if last_seen.tzinfo else last_seen.replace(tzinfo=timezone.utc)
                    if last_seen_aware < cutoff:
                        stale_ids.append(actor_id)
            return stale_ids
        except Exception as e:
            logger.error(f"_get_stale_actor_profiles failed: {e}")
            return []

    async def _refresh_actor_profile(self, actor_id: str) -> None:
        """Refresh a single actor profile by re-pulling its associated intel."""
        try:
            if hasattr(self.intelligence_db, 'get_records_for_actor'):
                records = await self.intelligence_db.get_records_for_actor(actor_id)
            else:
                logger.debug(f"No get_records_for_actor method; skipping refresh for {actor_id}")
                return
            if records:
                intel_data = [
                    {
                        'record_id': getattr(r, 'record_id', str(uuid4())),
                        'processed_indicators': getattr(r, 'processed_indicators', []),
                        'raw_data': getattr(r, 'raw_data', {}),
                        'confidence_score': getattr(r, 'confidence_score', 0.5),
                        'threat_level': getattr(r, 'threat_level', 0),
                        'collection_timestamp': str(getattr(r, 'collection_timestamp', '')),
                        'intelligence_type': str(getattr(r, 'intelligence_type', 'unknown')),
                        'metadata': getattr(r, 'metadata', {})
                    }
                    for r in records
                ]
                updated_profile = await self.actor_profiler.create_actor_profile(intel_data)
                updated_profile.actor_id = actor_id
                self.actor_profiler.actor_profiles[actor_id] = updated_profile
                logger.debug(f"Refreshed profile for actor {actor_id}")
        except Exception as e:
            logger.error(f"_refresh_actor_profile failed for {actor_id}: {e}")

    async def _get_recent_actor_profiles(self, limit: int = 100) -> List['ThreatActor']:
        """Return the most recently observed actor profiles up to limit."""
        try:
            profiles = list(self.actor_profiler.actor_profiles.values())
            profiles.sort(
                key=lambda p: p.last_observed if isinstance(p.last_observed, datetime)
                else datetime.min.replace(tzinfo=timezone.utc),
                reverse=True
            )
            return profiles[:limit]
        except Exception as e:
            logger.error(f"_get_recent_actor_profiles failed: {e}")
            return []

    def _calculate_ttp_overlap(self, p1: 'ThreatActor', p2: 'ThreatActor') -> float:
        """Calculate Jaccard similarity of TTP sets between two actor profiles."""
        try:
            ttps1 = set(getattr(p1, 'tactics_techniques', []))
            ttps2 = set(getattr(p2, 'tactics_techniques', []))
            if not ttps1 and not ttps2:
                return 0.0
            intersection = len(ttps1 & ttps2)
            union = len(ttps1 | ttps2)
            jaccard = intersection / union if union > 0 else 0.0

            # Boost score if infrastructure overlaps
            infra1 = set(getattr(p1, 'infrastructure_fingerprint', {}).keys())
            infra2 = set(getattr(p2, 'infrastructure_fingerprint', {}).keys())
            if infra1 and infra2:
                infra_overlap = len(infra1 & infra2) / len(infra1 | infra2)
                jaccard = (jaccard * 0.7) + (infra_overlap * 0.3)

            return round(jaccard, 4)
        except Exception as e:
            logger.error(f"_calculate_ttp_overlap failed: {e}")
            return 0.0

    async def _store_campaign_correlations(self, correlations: List[Dict[str, Any]]) -> None:
        """Persist campaign correlation records."""
        try:
            for correlation in correlations:
                corr_id = f"{correlation['actor_a']}_{correlation['actor_b']}"
                self.campaign_correlations[corr_id] = correlation
            if hasattr(self.intelligence_db, 'store_campaign_correlations'):
                await self.intelligence_db.store_campaign_correlations(correlations)
        except Exception as e:
            logger.error(f"_store_campaign_correlations failed: {e}")

    async def _get_pending_hypotheses(self, limit: int = 20) -> List[AttributionHypothesis]:
        """Return hypotheses whose validation_status is still None (pending)."""
        try:
            pending = [
                h for h in self.attribution_hypotheses.values()
                if isinstance(h, AttributionHypothesis) and h.validation_status is None
            ]
            return pending[:limit]
        except Exception as e:
            logger.error(f"_get_pending_hypotheses failed: {e}")
            return []

    async def _validate_hypothesis(self, hypothesis: AttributionHypothesis) -> Dict[str, Any]:
        """Cross-validate a hypothesis against the known actor store."""
        try:
            result: Dict[str, Any] = {
                'validated': False,
                'confidence_adjustment': 0.0,
                'validation_notes': []
            }

            # Check primary actor exists in known profiles
            known_actor = self.actor_profiler.actor_profiles.get(hypothesis.primary_actor)
            if known_actor:
                # Count how many supporting indicators match known actor TTPs
                known_ttps = set(getattr(known_actor, 'tactics_techniques', []))
                supporting = set(hypothesis.supporting_indicators)
                match_ratio = len(known_ttps & supporting) / max(len(supporting), 1)
                result['confidence_adjustment'] = match_ratio * 0.1
                result['validation_notes'].append(
                    f"TTP match ratio with known actor profile: {match_ratio:.2f}"
                )
                result['validated'] = match_ratio > 0.3
            else:
                result['validation_notes'].append("Primary actor not found in known profile store")

            # Check contradicting indicators against known actor behaviour
            if hypothesis.contradicting_indicators:
                result['confidence_adjustment'] -= 0.05
                result['validation_notes'].append(
                    f"{len(hypothesis.contradicting_indicators)} contradicting indicators reduce confidence"
                )

            return result
        except Exception as e:
            logger.error(f"_validate_hypothesis failed: {e}")
            return {'validated': False, 'confidence_adjustment': 0.0, 'validation_notes': [str(e)]}

    async def _update_hypothesis_confidence(
        self, hypothesis_id: str, validation_result: Dict[str, Any]
    ) -> None:
        """Apply validation result to update hypothesis confidence score."""
        try:
            hypothesis = self.attribution_hypotheses.get(hypothesis_id)
            if hypothesis is None:
                logger.debug(f"Hypothesis {hypothesis_id} not found for confidence update")
                return
            adjustment = float(validation_result.get('confidence_adjustment', 0.0))
            hypothesis.confidence_score = max(0.0, min(1.0, hypothesis.confidence_score + adjustment))
            hypothesis.validation_status = validation_result.get('validated', False)
            hypothesis.last_updated = datetime.now(timezone.utc)
            notes = validation_result.get('validation_notes', [])
            if notes:
                hypothesis.hypothesis_reasoning.extend(notes)
            logger.debug(
                f"Updated hypothesis {hypothesis_id} confidence to {hypothesis.confidence_score:.3f}"
            )
        except Exception as e:
            logger.error(f"_update_hypothesis_confidence failed: {e}")

    # ------------------------------------------------------------------
    # Core attribution analysis methods
    # ------------------------------------------------------------------

    async def _generate_attribution_hypotheses(
        self,
        intelligence_data: List[Dict[str, Any]],
        actor_profile: 'ThreatActor'
    ) -> List[AttributionHypothesis]:
        """Generate attribution hypotheses from intelligence data and actor profile."""
        try:
            hypotheses: List[AttributionHypothesis] = []

            # Gather all unique TTPs from intelligence
            observed_ttps: List[str] = []
            for record in intelligence_data:
                raw = record.get('raw_data', {})
                observed_ttps.extend(raw.get('attack_techniques', []))

            # For each known actor profile, measure similarity
            candidate_actors = list(self.actor_profiler.actor_profiles.values())
            if not candidate_actors:
                # No known actors — generate a single speculative hypothesis
                hypothesis = AttributionHypothesis(
                    hypothesis_id=str(uuid4()),
                    primary_actor=actor_profile.actor_id,
                    alternative_actors=[],
                    confidence_score=actor_profile.attribution_confidence.value,
                    evidence_chain=[
                        {'type': 'profiling', 'actor_id': actor_profile.actor_id,
                         'confidence': actor_profile.attribution_confidence.value}
                    ],
                    supporting_indicators=list(observed_ttps),
                    contradicting_indicators=[],
                    hypothesis_reasoning=[
                        f"No known actor baseline; speculative attribution to new profile {actor_profile.actor_id}"
                    ],
                    validation_criteria=['collect_additional_intel', 'compare_against_threat_feeds'],
                    uncertainty_factors=['no_known_actor_baseline', 'limited_evidence_chain'],
                    deception_assessment={'false_flag_probability': actor_profile.false_flag_probability},
                    hypothesis_timestamp=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc)
                )
                hypotheses.append(hypothesis)
                self.attribution_hypotheses[hypothesis.hypothesis_id] = hypothesis
                return hypotheses

            # Score each known actor against observed TTPs
            scored_actors: List[Tuple[float, ThreatActor]] = []
            observed_set = set(observed_ttps)
            for candidate in candidate_actors:
                known_set = set(getattr(candidate, 'tactics_techniques', []))
                if not known_set:
                    continue
                overlap = len(observed_set & known_set) / max(len(observed_set | known_set), 1)
                scored_actors.append((overlap, candidate))

            scored_actors.sort(key=lambda x: x[0], reverse=True)
            top_actors = scored_actors[:3]

            if not top_actors:
                return hypotheses

            primary_score, primary_candidate = top_actors[0]
            alternative_ids = [c.actor_id for _, c in top_actors[1:]]

            # Build evidence chain
            evidence_chain = [
                {'type': 'ttp_overlap', 'actor_id': primary_candidate.actor_id,
                 'overlap_score': primary_score, 'observed_ttps': list(observed_ttps)}
            ]
            supporting = list(observed_set & set(getattr(primary_candidate, 'tactics_techniques', [])))
            contradicting = list(observed_set - set(getattr(primary_candidate, 'tactics_techniques', [])))[:5]

            confidence = min(0.95, primary_score + actor_profile.attribution_confidence.value * 0.3)

            hypothesis = AttributionHypothesis(
                hypothesis_id=str(uuid4()),
                primary_actor=primary_candidate.actor_id,
                alternative_actors=alternative_ids,
                confidence_score=confidence,
                evidence_chain=evidence_chain,
                supporting_indicators=supporting,
                contradicting_indicators=contradicting,
                hypothesis_reasoning=[
                    f"TTP overlap score with {primary_candidate.actor_id}: {primary_score:.3f}",
                    f"Actor confidence level: {actor_profile.attribution_confidence.name}",
                    f"Observed {len(observed_ttps)} techniques, {len(supporting)} matched known profile"
                ],
                validation_criteria=[
                    'independent_source_corroboration',
                    'infrastructure_overlap_verification',
                    'temporal_activity_confirmation'
                ],
                uncertainty_factors=[
                    'potential_false_flag' if actor_profile.false_flag_probability > 0.3 else 'low_false_flag_risk',
                    'limited_corroborating_sources' if len(intelligence_data) < 5 else 'adequate_source_depth'
                ],
                deception_assessment={'false_flag_probability': actor_profile.false_flag_probability},
                hypothesis_timestamp=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc)
            )
            hypotheses.append(hypothesis)
            self.attribution_hypotheses[hypothesis.hypothesis_id] = hypothesis

            return hypotheses

        except Exception as e:
            logger.error(f"_generate_attribution_hypotheses failed: {e}")
            return []

    async def _correlate_with_campaigns(
        self,
        intelligence_data: List[Dict[str, Any]],
        actor_profile: 'ThreatActor'
    ) -> List[Dict[str, Any]]:
        """Correlate intelligence with known threat campaigns."""
        try:
            correlations: List[Dict[str, Any]] = []

            # Extract campaign identifiers from intelligence
            observed_campaign_ids: Set[str] = set()
            for record in intelligence_data:
                raw = record.get('raw_data', {})
                if 'campaign_id' in raw:
                    observed_campaign_ids.add(str(raw['campaign_id']))

            # Match against active campaign correlations already stored
            for corr_id, corr in self.campaign_correlations.items():
                actor_a = corr.get('actor_a', '')
                actor_b = corr.get('actor_b', '')
                if actor_profile.actor_id in (actor_a, actor_b):
                    correlations.append({
                        'correlation_id': corr_id,
                        'correlation_type': 'known_actor_correlation',
                        'correlation_score': corr.get('correlation_score', 0.0),
                        'correlated_actor': actor_b if actor_a == actor_profile.actor_id else actor_a,
                        'timestamp': corr.get('timestamp', time.time())
                    })

            # Match observed campaign IDs against actor's active campaigns
            actor_campaign_set = set(actor_profile.active_campaigns)
            for observed_id in observed_campaign_ids:
                if observed_id in actor_campaign_set:
                    correlations.append({
                        'correlation_id': str(uuid4()),
                        'correlation_type': 'campaign_id_match',
                        'correlation_score': 0.9,
                        'campaign_id': observed_id,
                        'timestamp': time.time()
                    })

            logger.debug(f"Found {len(correlations)} campaign correlations for actor {actor_profile.actor_id}")
            return correlations

        except Exception as e:
            logger.error(f"_correlate_with_campaigns failed: {e}")
            return []

    async def _validate_attribution_hypotheses(
        self, hypotheses: List[AttributionHypothesis]
    ) -> List[AttributionHypothesis]:
        """Validate a batch of hypotheses and return those meeting confidence threshold."""
        try:
            min_confidence = self.attribution_config.get('validation', {}).get(
                'confidence_threshold_validation', 0.3
            )
            validated: List[AttributionHypothesis] = []
            for hypothesis in hypotheses:
                validation_result = await self._validate_hypothesis(hypothesis)
                await self._update_hypothesis_confidence(
                    hypothesis.hypothesis_id, validation_result
                )
                if hypothesis.confidence_score >= min_confidence:
                    validated.append(hypothesis)
            return validated
        except Exception as e:
            logger.error(f"_validate_attribution_hypotheses failed: {e}")
            return hypotheses

    def _calculate_overall_confidence(
        self, validated_hypotheses: List[AttributionHypothesis]
    ) -> Dict[str, Any]:
        """Compute aggregate confidence metrics across all validated hypotheses."""
        try:
            if not validated_hypotheses:
                return {
                    'overall_confidence': 0.0,
                    'confidence_level': AttributionConfidence.UNATTRIBUTED.name,
                    'hypothesis_count': 0,
                    'mean_confidence': 0.0,
                    'max_confidence': 0.0,
                    'min_confidence': 0.0
                }

            scores = [h.confidence_score for h in validated_hypotheses]
            mean_conf = float(np.mean(scores))
            max_conf = float(np.max(scores))
            min_conf = float(np.min(scores))

            # Determine overall confidence tier
            if max_conf >= AttributionConfidence.CONFIRMED.value:
                level = AttributionConfidence.CONFIRMED.name
            elif max_conf >= AttributionConfidence.HIGHLY_LIKELY.value:
                level = AttributionConfidence.HIGHLY_LIKELY.name
            elif max_conf >= AttributionConfidence.PROBABLE.value:
                level = AttributionConfidence.PROBABLE.name
            elif max_conf >= AttributionConfidence.POSSIBLE.value:
                level = AttributionConfidence.POSSIBLE.name
            else:
                level = AttributionConfidence.UNATTRIBUTED.name

            return {
                'overall_confidence': mean_conf,
                'confidence_level': level,
                'hypothesis_count': len(validated_hypotheses),
                'mean_confidence': mean_conf,
                'max_confidence': max_conf,
                'min_confidence': min_conf,
                'primary_actor': validated_hypotheses[0].primary_actor if validated_hypotheses else None
            }
        except Exception as e:
            logger.error(f"_calculate_overall_confidence failed: {e}")
            return {'overall_confidence': 0.0, 'confidence_level': 'ERROR', 'error': str(e)}

    async def get_attribution_status(self) -> Dict[str, Any]:
        """Get comprehensive attribution engine status"""
        try:
            status = {
                'engine_status': 'operational',
                'active_attributions': len(self.active_attributions),
                'actor_profiles_created': len(self.actor_profiler.actor_profiles),
                'attribution_hypotheses': len(self.attribution_hypotheses),
                'campaign_correlations': len(self.campaign_correlations),
                'metrics': dict(self.attribution_metrics),
                'model_versions': self.learning_engine.model_versions,
                'background_tasks_active': len([t for t in self.background_tasks if not t.done()]),
                'configuration': self.attribution_config,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {'engine_status': 'error', 'error': str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown attribution engine"""
        logger.info("Shutting down attribution engine...")

        # Signal all services to stop
        self._running = False
        self.shutdown_event.set()

        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)

        logger.info("Attribution engine shutdown complete")


# Export primary interfaces
__all__ = [
    'AttributionEngine',
    'ThreatActorProfiler',
    'RecursiveAttributionEngine',
    'ThreatActor',
    'ThreatCampaign',
    'AttributionHypothesis',
    'AttributionConfidence',
    'ActorCategory'
]


if __name__ == "__main__":
    # Development testing and validation
    async def test_attribution_engine():
        """Comprehensive testing of attribution engine functionality"""
        
        # Mock dependencies
        class MockIntelligenceDB:
            async def retrieve_intelligence(self, record_id):
                return None
        
        class MockThreatAggregation:
            pass
        
        class MockDataFusion:
            pass
        
        # Initialize attribution engine
        mock_db = MockIntelligenceDB()
        mock_aggregation = MockThreatAggregation()
        mock_fusion = MockDataFusion()
        
        engine = AttributionEngine(mock_db, mock_aggregation, mock_fusion)
        
        try:
            # Initialize engine
            await engine.initialize()
            
            # Get engine status
            status = await engine.get_attribution_status()
            print(f"Attribution engine status: {json.dumps(status, indent=2, default=str)}")
            
            print("Attribution engine test completed successfully")
            
        finally:
            # Shutdown
            await engine.shutdown()
    
    # Run test
    asyncio.run(test_attribution_engine())

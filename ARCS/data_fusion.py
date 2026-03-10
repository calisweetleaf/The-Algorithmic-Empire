#!/usr/bin/env python3
"""
ARCS Data Fusion - Recursive Intelligence Synthesis Engine
=========================================================
Autonomous Reactive Cyber Systems - Intelligence Synthesis Domain

Mission: Advanced intelligence fusion with recursive self-training capabilities,
hypothesis generation, and continuous model evolution through operational feedback.
Creates synthetic intelligence products from multi-source data with autonomous
cognitive improvement through session analysis and model retraining.

Classification: INTELLIGENCE SYNTHESIS - SOVEREIGN INFRASTRUCTURE
ROE Authority: Autonomous hypothesis generation with continuous model evolution
Deployment: Field-ready production system with recursive learning capabilities
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
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Callable, Tuple, Iterator
from uuid import UUID, uuid4
from collections import defaultdict, deque, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

import numpy as np
import pandas as pd
import aiofiles
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# ML and synthesis capabilities
import onnxruntime as ort
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from scipy.stats import entropy, pearsonr
from scipy.spatial.distance import cosine, euclidean
import networkx as nx

# Advanced analytics
from transformers import pipeline
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

logger = logging.getLogger(__name__)


class SynthesisType(Enum):
    """Intelligence synthesis product types"""
    THREAT_ASSESSMENT = "threat_assessment"
    CAMPAIGN_ANALYSIS = "campaign_analysis"
    ATTRIBUTION_HYPOTHESIS = "attribution_hypothesis"
    PREDICTIVE_INTELLIGENCE = "predictive_intelligence"
    BEHAVIORAL_PROFILE = "behavioral_profile"
    INFRASTRUCTURE_MAPPING = "infrastructure_mapping"
    VULNERABILITY_SYNTHESIS = "vulnerability_synthesis"
    TACTICAL_RECOMMENDATION = "tactical_recommendation"


class HypothesisConfidence(Enum):
    """Hypothesis confidence levels"""
    SPECULATIVE = 0.2      # 0-30% confidence
    POSSIBLE = 0.4         # 30-50% confidence
    PROBABLE = 0.6         # 50-70% confidence
    HIGHLY_LIKELY = 0.8    # 70-90% confidence
    CONFIRMED = 0.95       # 90-100% confidence


class LearningPhase(Enum):
    """Model learning phases"""
    INITIALIZATION = "initialization"
    ACTIVE_LEARNING = "active_learning"
    SYNTHESIS_OPTIMIZATION = "synthesis_optimization"
    FEEDBACK_INTEGRATION = "feedback_integration"
    MODEL_EVOLUTION = "model_evolution"


@dataclass
class IntelligenceHypothesis:
    """Intelligence analysis hypothesis with reasoning chain"""
    hypothesis_id: str
    hypothesis_type: SynthesisType
    hypothesis_statement: str
    confidence_level: HypothesisConfidence
    supporting_evidence: List[Dict[str, Any]]
    contradicting_evidence: List[Dict[str, Any]]
    reasoning_chain: List[str]
    data_sources: List[str]
    correlation_strength: float
    temporal_relevance: float
    predictive_indicators: List[str]
    validation_criteria: List[str]
    alternative_hypotheses: List[str]
    uncertainty_factors: List[str]
    creation_timestamp: datetime
    last_updated: datetime
    validation_status: Optional[str] = None
    outcome_validation: Optional[bool] = None


@dataclass
class SynthesisProduct:
    """Comprehensive intelligence synthesis product"""
    product_id: str
    synthesis_type: SynthesisType
    title: str
    executive_summary: str
    key_findings: List[str]
    primary_hypothesis: IntelligenceHypothesis
    supporting_hypotheses: List[IntelligenceHypothesis]
    analytical_confidence: float
    source_reliability_assessment: Dict[str, float]
    data_quality_metrics: Dict[str, float]
    synthesis_methodology: List[str]
    validation_requirements: List[str]
    intelligence_gaps: List[str]
    recommendations: List[str]
    follow_up_requirements: List[str]
    synthesis_timestamp: datetime
    analyst_notes: Optional[str] = None
    review_status: str = "pending"
    dissemination_level: str = "restricted"


@dataclass
class SessionAnalytics:
    """Session-level analytics for model training"""
    session_id: str
    session_start: datetime
    session_end: Optional[datetime]
    input_data_summary: Dict[str, Any]
    hypotheses_generated: int
    synthesis_products_created: int
    confidence_distribution: Dict[str, int]
    reasoning_patterns: List[str]
    decision_points: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    error_patterns: List[str]
    learning_outcomes: List[str]
    model_updates_applied: List[str]
    feedback_integration: Dict[str, Any]
    session_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelTrainingData:
    """Training data structure for model evolution"""
    training_id: str
    data_source: str  # input_intelligence, synthesis_output, session_logs
    feature_vector: np.ndarray
    target_labels: Dict[str, Any]
    confidence_scores: np.ndarray
    reasoning_patterns: List[str]
    outcome_validation: Optional[bool]
    training_timestamp: datetime
    data_quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecursiveLearningEngine:
    """
    Recursive learning engine for continuous model improvement
    
    Implements autonomous model evolution through operational feedback
    and recursive training on synthesis patterns and outcomes.
    """
    
    def __init__(self, models_path: str = "models/data_fusion/"):
        self.models_path = Path(models_path)
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Model management
        self.active_models = {}
        self.model_versions = {}
        self.training_data_cache = deque(maxlen=10000)
        
        # Learning configuration
        self.learning_config = {
            'batch_size': 32,
            'learning_rate': 0.001,
            'training_epochs': 10,
            'validation_split': 0.2,
            'retrain_threshold': 100,  # New samples before retraining
            'model_evolution_interval': 3600  # 1 hour
        }
        
        # Training metrics
        self.training_metrics = defaultdict(list)
        self.learning_history = deque(maxlen=1000)
        
        # Model architectures
        self.model_architectures = {
            'synthesis_optimizer': self._create_synthesis_model,
            'hypothesis_generator': self._create_hypothesis_model,
            'confidence_estimator': self._create_confidence_model,
            'pattern_recognizer': self._create_pattern_model
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load existing models"""
        try:
            for model_name, architecture_func in self.model_architectures.items():
                model_path = self.models_path / f"{model_name}.onnx"
                
                if model_path.exists():
                    # Load existing model
                    self.active_models[model_name] = ort.InferenceSession(str(model_path))
                    logger.info(f"Loaded existing model: {model_name}")
                else:
                    # Create new model
                    model = architecture_func()
                    self.active_models[model_name] = model
                    logger.info(f"Created new model: {model_name}")
                
                # Initialize version tracking
                self.model_versions[model_name] = {
                    'version': 1.0,
                    'last_updated': datetime.now(timezone.utc),
                    'training_samples': 0,
                    'performance_score': 0.0
                }
            
            logger.info("Recursive learning engine initialized")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise
    
    def _create_synthesis_model(self):
        """Create neural network for synthesis optimization"""
        class SynthesisNN(nn.Module):
            """Neural network for intelligence synthesis optimization.

            Transforms input feature vectors through a multi-layer feed-forward
            architecture with dropout regularization to produce synthesis
            embedding vectors.

            Args:
                input_size: Dimensionality of input feature vectors.
                hidden_size: Width of hidden layers.
                output_size: Dimensionality of output synthesis embeddings.
            """

            def __init__(self, input_size=128, hidden_size=256, output_size=64):
                super(SynthesisNN, self).__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, output_size),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                """Forward pass through the synthesis network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, output_size)`` with sigmoid
                    activations in [0, 1].
                """
                return self.layers(x)
        
        return SynthesisNN()
    
    def _create_hypothesis_model(self):
        """Create model for hypothesis generation"""
        class HypothesisGenerator(nn.Module):
            """Encoder-decoder network for intelligence hypothesis generation.

            Compresses input intelligence features into a latent representation
            and decodes them into hypothesis signal vectors using an
            encoder-decoder architecture.

            Args:
                input_size: Dimensionality of input feature vectors.
                hidden_size: Width of encoder/decoder hidden layers.
                output_size: Dimensionality of output hypothesis vectors.
            """

            def __init__(self, input_size=128, hidden_size=512, output_size=32):
                super(HypothesisGenerator, self).__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU()
                )
                self.decoder = nn.Sequential(
                    nn.Linear(hidden_size // 2, hidden_size),
                    nn.ReLU(),
                    nn.Linear(hidden_size, output_size),
                    nn.Tanh()
                )
            
            def forward(self, x):
                """Forward pass through encoder-decoder hypothesis network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, output_size)`` with tanh
                    activations in [-1, 1].
                """
                encoded = self.encoder(x)
                return self.decoder(encoded)
        
        return HypothesisGenerator()
    
    def _create_confidence_model(self):
        """Create confidence estimation model"""
        class ConfidenceEstimator(nn.Module):
            """Neural network for intelligence confidence scoring.

            Produces a scalar confidence score for input feature vectors,
            using dropout regularization to improve calibration.

            Args:
                input_size: Dimensionality of input feature vectors.
                hidden_size: Width of hidden layers.
            """

            def __init__(self, input_size=128, hidden_size=256):
                super(ConfidenceEstimator, self).__init__()
                self.network = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                """Forward pass through the confidence estimation network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, 1)`` with sigmoid
                    activation in [0, 1].
                """
                return self.network(x)
        
        return ConfidenceEstimator()
    
    def _create_pattern_model(self):
        """Create pattern recognition model"""
        class PatternRecognizer(nn.Module):
            """Neural network for intelligence pattern recognition.

            Classifies input feature vectors into discrete pattern categories
            using batch normalization and softmax output.

            Args:
                input_size: Dimensionality of input feature vectors.
                hidden_size: Width of hidden layers.
                num_patterns: Number of pattern categories to classify.
            """

            def __init__(self, input_size=128, hidden_size=384, num_patterns=16):
                super(PatternRecognizer, self).__init__()
                self.pattern_layers = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, num_patterns),
                    nn.Softmax(dim=1)
                )
            
            def forward(self, x):
                """Forward pass through the pattern recognition network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, num_patterns)`` with softmax
                    probabilities summing to 1.
                """
                return self.pattern_layers(x)
        
        return PatternRecognizer()
    
    async def add_training_data(self, training_data: ModelTrainingData) -> None:
        """Add new training data for model evolution."""
        try:
            # Add to cache
            self.training_data_cache.append(training_data)
            
            # Update training metrics
            self.training_metrics['samples_added'].append(len(self.training_data_cache))
            self.training_metrics['data_quality'].append(training_data.data_quality_score)
            
            # Check if retraining is needed
            if len(self.training_data_cache) >= self.learning_config['retrain_threshold']:
                await self._trigger_model_retraining()
            
        except Exception as e:
            logger.error(f"Training data addition failed: {e}")
    
    async def _trigger_model_retraining(self):
        """Trigger model retraining with accumulated data"""
        try:
            logger.info("Starting recursive model retraining...")
            
            # Prepare training datasets
            training_datasets = await self._prepare_training_datasets()
            
            # Retrain each model
            for model_name, model in self.active_models.items():
                if isinstance(model, nn.Module):  # PyTorch models
                    await self._retrain_pytorch_model(model_name, model, training_datasets)
                else:  # ONNX models
                    await self._update_onnx_model(model_name, training_datasets)
            
            # Clear training cache
            self.training_data_cache.clear()
            
            # Update model versions
            await self._update_model_versions()
            
            logger.info("Recursive model retraining completed")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
    
    async def _prepare_training_datasets(self) -> Dict[str, Any]:
        """Prepare training datasets from cached data"""
        try:
            datasets = {
                'input_features': [],
                'synthesis_targets': [],
                'hypothesis_targets': [],
                'confidence_targets': [],
                'pattern_targets': []
            }
            
            for training_data in self.training_data_cache:
                # Extract features
                features = training_data.feature_vector
                datasets['input_features'].append(features)
                
                # Extract targets based on data source
                if training_data.data_source == 'synthesis_output':
                    datasets['synthesis_targets'].append(training_data.target_labels)
                elif training_data.data_source == 'hypothesis_generation':
                    datasets['hypothesis_targets'].append(training_data.target_labels)
                elif training_data.data_source == 'confidence_estimation':
                    datasets['confidence_targets'].append(training_data.confidence_scores)
                elif training_data.data_source == 'pattern_recognition':
                    datasets['pattern_targets'].append(training_data.target_labels)
            
            # Convert to tensors
            for key in datasets:
                if datasets[key]:
                    datasets[key] = torch.tensor(np.array(datasets[key]), dtype=torch.float32)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Training dataset preparation failed: {e}")
            return {}
    
    async def _retrain_pytorch_model(self, model_name: str, model: nn.Module, 
                                   datasets: Dict[str, torch.Tensor]) -> None:
        """Retrain PyTorch model with new data."""
        try:
            model.train()
            optimizer = optim.Adam(model.parameters(), lr=self.learning_config['learning_rate'])
            criterion = nn.MSELoss()
            
            # Get appropriate dataset
            if model_name == 'synthesis_optimizer' and 'synthesis_targets' in datasets:
                targets = datasets['synthesis_targets']
            elif model_name == 'hypothesis_generator' and 'hypothesis_targets' in datasets:
                targets = datasets['hypothesis_targets']
            elif model_name == 'confidence_estimator' and 'confidence_targets' in datasets:
                targets = datasets['confidence_targets']
            elif model_name == 'pattern_recognizer' and 'pattern_targets' in datasets:
                targets = datasets['pattern_targets']
            else:
                logger.warning(f"No suitable dataset for model {model_name}")
                return
            
            features = datasets['input_features']
            
            # Training loop
            for epoch in range(self.learning_config['training_epochs']):
                optimizer.zero_grad()
                outputs = model(features)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
                if epoch % 5 == 0:
                    logger.debug(f"Model {model_name} epoch {epoch}, loss: {loss.item():.4f}")
            
            # Update model version
            self.model_versions[model_name]['version'] += 0.1
            self.model_versions[model_name]['last_updated'] = datetime.now(timezone.utc)
            self.model_versions[model_name]['training_samples'] += len(features)
            
            logger.info(f"Model {model_name} retrained successfully")
            
        except Exception as e:
            logger.error(f"PyTorch model retraining failed for {model_name}: {e}")


class IntelligenceSynthesisEngine:
    """
    Advanced intelligence synthesis engine with hypothesis generation
    
    Creates comprehensive intelligence products through multi-source
    data fusion, hypothesis generation, and analytical reasoning.
    """
    
    def __init__(self, intelligence_db, threat_aggregation_engine):
        self.intelligence_db = intelligence_db
        self.threat_aggregation = threat_aggregation_engine
        
        # Synthesis components
        self.learning_engine = RecursiveLearningEngine()
        self.hypothesis_cache = {}
        self.synthesis_products = {}
        # Analysis technique names tracked for reporting and telemetry
        self.analysis_techniques = [
            'clustering_analysis',
            'temporal_analysis',
            'network_analysis',
            'anomaly_detection',
            'correlation_analysis',
            'predictive_modeling'
        ]
        
        # Synthesis configuration
        self.synthesis_config = {
            'min_confidence_threshold': 0.3,
            'max_hypotheses_per_synthesis': 5,
            'correlation_threshold': 0.6,
            'temporal_window_hours': 168,  # 1 week
            'predictive_horizon_hours': 72  # 3 days
        }
        
        # Session tracking
        self.current_session = None
        self.session_history = deque(maxlen=1000)
        
        # Performance metrics
        self.synthesis_metrics = defaultdict(int)
        
    async def create_synthesis_product(self, synthesis_request: Dict[str, Any]) -> SynthesisProduct:
        """Create comprehensive intelligence synthesis product"""
        try:
            synthesis_start = time.time()
            
            # Start new synthesis session
            session = await self._start_synthesis_session(synthesis_request)
            
            # Gather relevant intelligence
            source_intelligence = await self._gather_source_intelligence(synthesis_request)
            
            # Generate analytical hypotheses
            hypotheses = await self._generate_hypotheses(source_intelligence, synthesis_request)
            
            # Perform multi-dimensional analysis
            analysis_results = await self._perform_comprehensive_analysis(
                source_intelligence, hypotheses
            )
            
            # Synthesize intelligence product
            synthesis_product = await self._synthesize_intelligence_product(
                hypotheses, analysis_results, synthesis_request
            )
            
            # Generate training data from synthesis process
            training_data = await self._generate_training_data(
                source_intelligence, hypotheses, synthesis_product, session
            )
            
            # Add training data to learning engine
            await self.learning_engine.add_training_data(training_data)
            
            # Complete synthesis session
            await self._complete_synthesis_session(session, synthesis_product)
            
            # Update metrics
            synthesis_time = (time.time() - synthesis_start) * 1000
            self.synthesis_metrics['products_created'] += 1
            self.synthesis_metrics['total_synthesis_time_ms'] += synthesis_time
            
            logger.info(f"Created synthesis product {synthesis_product.product_id} in {synthesis_time:.2f}ms")
            
            return synthesis_product
            
        except Exception as e:
            logger.error(f"Synthesis product creation failed: {e}")
            raise
    
    async def _start_synthesis_session(self, synthesis_request: Dict[str, Any]) -> SessionAnalytics:
        """Start new synthesis session with analytics tracking"""
        try:
            session = SessionAnalytics(
                session_id=str(uuid4()),
                session_start=datetime.now(timezone.utc),
                session_end=None,
                input_data_summary={
                    'synthesis_type': synthesis_request.get('synthesis_type', 'unknown'),
                    'data_sources': synthesis_request.get('data_sources', []),
                    'time_range': synthesis_request.get('time_range'),
                    'priority_level': synthesis_request.get('priority_level', 'normal')
                },
                hypotheses_generated=0,
                synthesis_products_created=0,
                confidence_distribution={},
                reasoning_patterns=[],
                decision_points=[],
                performance_metrics={},
                error_patterns=[],
                learning_outcomes=[],
                model_updates_applied=[],
                feedback_integration={}
            )
            
            self.current_session = session
            return session
            
        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            raise
    
    async def _gather_source_intelligence(self, synthesis_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather relevant intelligence from multiple sources"""
        try:
            # Define query parameters
            query_params = {
                'time_range': synthesis_request.get('time_range'),
                'limit': synthesis_request.get('max_sources', 1000)
            }
            
            # Add specific filters based on synthesis type
            synthesis_type = synthesis_request.get('synthesis_type')
            if synthesis_type == 'threat_assessment':
                query_params['min_threat_level'] = 5
            elif synthesis_type == 'campaign_analysis':
                query_params['intelligence_types'] = ['attribution_data', 'infrastructure_mapping']
            elif synthesis_type == 'predictive_intelligence':
                query_params['time_range'] = (
                    datetime.now(timezone.utc) - timedelta(hours=self.synthesis_config['temporal_window_hours']),
                    datetime.now(timezone.utc)
                )
            
            # Query intelligence database
            intelligence_records = await self.intelligence_db.advanced_query(query_params)
            
            # Convert to analysis format
            source_intelligence = []
            for record in intelligence_records:
                source_intelligence.append({
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
            
            logger.info(f"Gathered {len(source_intelligence)} intelligence records for synthesis")
            return source_intelligence
            
        except Exception as e:
            logger.error(f"Source intelligence gathering failed: {e}")
            return []
    
    async def _generate_hypotheses(self, source_intelligence: List[Dict[str, Any]], 
                                 synthesis_request: Dict[str, Any]) -> List[IntelligenceHypothesis]:
        """Generate analytical hypotheses from source intelligence"""
        try:
            hypotheses = []
            synthesis_type = SynthesisType(synthesis_request.get('synthesis_type', 'threat_assessment'))
            
            # Generate hypotheses based on synthesis type
            if synthesis_type == SynthesisType.THREAT_ASSESSMENT:
                hypotheses.extend(await self._generate_threat_hypotheses(source_intelligence))
            elif synthesis_type == SynthesisType.CAMPAIGN_ANALYSIS:
                hypotheses.extend(await self._generate_campaign_hypotheses(source_intelligence))
            elif synthesis_type == SynthesisType.ATTRIBUTION_HYPOTHESIS:
                hypotheses.extend(await self._generate_attribution_hypotheses(source_intelligence))
            elif synthesis_type == SynthesisType.PREDICTIVE_INTELLIGENCE:
                hypotheses.extend(await self._generate_predictive_hypotheses(source_intelligence))
            
            # Use ML model for hypothesis enhancement
            enhanced_hypotheses = await self._enhance_hypotheses_with_ml(hypotheses, source_intelligence)
            
            # Validate and rank hypotheses
            validated_hypotheses = await self._validate_and_rank_hypotheses(enhanced_hypotheses)
            
            # Update session analytics
            if self.current_session:
                self.current_session.hypotheses_generated = len(validated_hypotheses)
            
            logger.info(f"Generated {len(validated_hypotheses)} hypotheses for synthesis")
            return validated_hypotheses
            
        except Exception as e:
            logger.error(f"Hypothesis generation failed: {e}")
            return []
    
    async def _generate_threat_hypotheses(self, source_intelligence: List[Dict[str, Any]]) -> List[IntelligenceHypothesis]:
        """Generate threat assessment hypotheses"""
        hypotheses = []
        
        try:
            # Analyze threat patterns
            threat_indicators = []
            for intel in source_intelligence:
                if intel['threat_level'] >= 5:
                    threat_indicators.extend(intel['processed_indicators'])
            
            # Group similar threat indicators
            indicator_groups = self._group_similar_indicators(threat_indicators)
            
            # Generate hypotheses for each group
            for group_name, indicators in indicator_groups.items():
                if len(indicators) >= 3:  # Minimum threshold for hypothesis
                    confidence_level = self._calculate_hypothesis_confidence(indicators, source_intelligence)
                    
                    hypothesis = IntelligenceHypothesis(
                        hypothesis_id=str(uuid4()),
                        hypothesis_type=SynthesisType.THREAT_ASSESSMENT,
                        hypothesis_statement=f"Coordinated threat activity involving {group_name} indicators",
                        confidence_level=confidence_level,
                        supporting_evidence=[
                            {'type': 'indicator_clustering', 'indicators': indicators, 'frequency': len(indicators)}
                        ],
                        contradicting_evidence=[],
                        reasoning_chain=[
                            f"Identified {len(indicators)} related threat indicators",
                            f"Indicators show pattern consistent with {group_name} activity",
                            f"Confidence level: {confidence_level.value}"
                        ],
                        data_sources=[intel['record_id'] for intel in source_intelligence if any(ind in intel['processed_indicators'] for ind in indicators)],
                        correlation_strength=0.7,  # Placeholder - would be calculated
                        temporal_relevance=0.8,    # Placeholder - would be calculated
                        predictive_indicators=indicators[:5],  # Top 5 indicators
                        validation_criteria=[
                            'additional_corroborating_evidence',
                            'temporal_correlation_verification',
                            'attribution_analysis'
                        ],
                        alternative_hypotheses=[
                            'false_positive_cluster',
                            'unrelated_coincidental_activity'
                        ],
                        uncertainty_factors=[
                            'limited_attribution_data',
                            'potential_deception_tactics'
                        ],
                        creation_timestamp=datetime.now(timezone.utc),
                        last_updated=datetime.now(timezone.utc)
                    )
                    
                    hypotheses.append(hypothesis)
            
            return hypotheses
            
        except Exception as e:
            logger.error(f"Threat hypothesis generation failed: {e}")
            return []
    
    def _group_similar_indicators(self, indicators: List[str]) -> Dict[str, List[str]]:
        """Group similar threat indicators using clustering"""
        try:
            # Simple keyword-based grouping (could be enhanced with ML)
            indicator_groups = defaultdict(list)
            
            # Define grouping patterns
            grouping_patterns = {
                'network_scanning': ['scan', 'probe', 'enumeration', 'reconnaissance'],
                'malware_activity': ['malware', 'trojan', 'backdoor', 'payload'],
                'exploitation': ['exploit', 'vulnerability', 'overflow', 'injection'],
                'persistence': ['persistence', 'startup', 'registry', 'scheduled'],
                'lateral_movement': ['lateral', 'movement', 'privilege', 'escalation'],
                'data_exfiltration': ['exfiltration', 'data', 'upload', 'transfer'],
                'c2_communication': ['command', 'control', 'beacon', 'callback']
            }
            
            # Classify indicators
            for indicator in indicators:
                indicator_lower = indicator.lower()
                classified = False
                
                for group_name, keywords in grouping_patterns.items():
                    if any(keyword in indicator_lower for keyword in keywords):
                        indicator_groups[group_name].append(indicator)
                        classified = True
                        break
                
                if not classified:
                    indicator_groups['other'].append(indicator)
            
            return dict(indicator_groups)
            
        except Exception as e:
            logger.error(f"Indicator grouping failed: {e}")
            return {'unknown': indicators}
    
    def _calculate_hypothesis_confidence(self, indicators: List[str], 
                                       source_intelligence: List[Dict[str, Any]]) -> HypothesisConfidence:
        """Calculate confidence level for hypothesis"""
        try:
            # Calculate confidence based on multiple factors
            factors = []
            
            # Factor 1: Number of supporting indicators
            indicator_score = min(1.0, len(indicators) / 10)  # Max at 10 indicators
            factors.append(indicator_score)
            
            # Factor 2: Source reliability
            relevant_sources = [intel for intel in source_intelligence 
                              if any(ind in intel['processed_indicators'] for ind in indicators)]
            if relevant_sources:
                avg_confidence = np.mean([intel['confidence_score'] for intel in relevant_sources])
                factors.append(avg_confidence)
            
            # Factor 3: Temporal clustering
            if relevant_sources:
                timestamps = [intel['collection_timestamp'] for intel in relevant_sources]
                time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600  # hours
                temporal_score = max(0.2, 1.0 - (time_span / 168))  # Decay over 1 week
                factors.append(temporal_score)
            
            # Calculate composite confidence
            composite_confidence = np.mean(factors) if factors else 0.2
            
            # Map to confidence levels
            if composite_confidence >= 0.9:
                return HypothesisConfidence.CONFIRMED
            elif composite_confidence >= 0.7:
                return HypothesisConfidence.HIGHLY_LIKELY
            elif composite_confidence >= 0.5:
                return HypothesisConfidence.PROBABLE
            elif composite_confidence >= 0.3:
                return HypothesisConfidence.POSSIBLE
            else:
                return HypothesisConfidence.SPECULATIVE
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return HypothesisConfidence.SPECULATIVE
    
    async def _enhance_hypotheses_with_ml(self, hypotheses: List[IntelligenceHypothesis], 
                                        source_intelligence: List[Dict[str, Any]]) -> List[IntelligenceHypothesis]:
        """Enhance hypotheses using ML models"""
        try:
            enhanced_hypotheses = []
            
            for hypothesis in hypotheses:
                # Extract features for ML processing
                features = self._extract_hypothesis_features(hypothesis, source_intelligence)
                
                # Use hypothesis generator model
                if 'hypothesis_generator' in self.learning_engine.active_models:
                    model = self.learning_engine.active_models['hypothesis_generator']
                    
                    if isinstance(model, nn.Module):
                        # PyTorch model
                        model.eval()
                        with torch.no_grad():
                            features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
                            enhancement = model(features_tensor)
                            
                            # Apply enhancements to hypothesis
                            enhanced_hypothesis = self._apply_ml_enhancements(hypothesis, enhancement)
                            enhanced_hypotheses.append(enhanced_hypothesis)
                    else:
                        # ONNX model
                        input_data = {model.get_inputs()[0].name: features.reshape(1, -1)}
                        output = model.run(None, input_data)
                        
                        enhanced_hypothesis = self._apply_ml_enhancements(hypothesis, output[0])
                        enhanced_hypotheses.append(enhanced_hypothesis)
                else:
                    # No ML enhancement available
                    enhanced_hypotheses.append(hypothesis)
            
            return enhanced_hypotheses
            
        except Exception as e:
            logger.error(f"ML hypothesis enhancement failed: {e}")
            return hypotheses  # Return original hypotheses if enhancement fails
    
    def _extract_hypothesis_features(self, hypothesis: IntelligenceHypothesis, 
                                   source_intelligence: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from hypothesis for ML processing"""
        try:
            features = []
            
            # Basic hypothesis features
            features.extend([
                float(hypothesis.confidence_level.value),
                len(hypothesis.supporting_evidence),
                len(hypothesis.contradicting_evidence),
                len(hypothesis.reasoning_chain),
                len(hypothesis.data_sources),
                hypothesis.correlation_strength,
                hypothesis.temporal_relevance,
                len(hypothesis.predictive_indicators)
            ])
            
            # Source intelligence features
            relevant_sources = [intel for intel in source_intelligence 
                              if intel['record_id'] in hypothesis.data_sources]
            
            if relevant_sources:
                features.extend([
                    len(relevant_sources),
                    np.mean([intel['confidence_score'] for intel in relevant_sources]),
                    np.mean([intel['threat_level'] for intel in relevant_sources]),
                    len(set([intel['intelligence_type'] for intel in relevant_sources]))
                ])
            else:
                features.extend([0, 0, 0, 0])
            
            # Pad or truncate to expected input size
            while len(features) < 128:
                features.append(0.0)
            
            return np.array(features[:128], dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return np.zeros(128, dtype=np.float32)
    
    def _apply_ml_enhancements(self, hypothesis: IntelligenceHypothesis, 
                             ml_output: np.ndarray) -> IntelligenceHypothesis:
        """Apply ML model enhancements to hypothesis"""
        try:
            # Create enhanced copy of hypothesis
            enhanced_hypothesis = IntelligenceHypothesis(
                hypothesis_id=hypothesis.hypothesis_id,
                hypothesis_type=hypothesis.hypothesis_type,
                hypothesis_statement=hypothesis.hypothesis_statement,
                confidence_level=hypothesis.confidence_level,
                supporting_evidence=hypothesis.supporting_evidence.copy(),
                contradicting_evidence=hypothesis.contradicting_evidence.copy(),
                reasoning_chain=hypothesis.reasoning_chain.copy(),
                data_sources=hypothesis.data_sources.copy(),
                correlation_strength=hypothesis.correlation_strength,
                temporal_relevance=hypothesis.temporal_relevance,
                predictive_indicators=hypothesis.predictive_indicators.copy(),
                validation_criteria=hypothesis.validation_criteria.copy(),
                alternative_hypotheses=hypothesis.alternative_hypotheses.copy(),
                uncertainty_factors=hypothesis.uncertainty_factors.copy(),
                creation_timestamp=hypothesis.creation_timestamp,
                last_updated=datetime.now(timezone.utc)
            )
            
            # Apply ML enhancements (simplified example)
            if len(ml_output) > 0:
                # Adjust confidence based on ML output
                ml_confidence_adjustment = float(ml_output[0]) if ml_output[0] != 0 else 1.0
                enhanced_confidence = hypothesis.confidence_level.value * ml_confidence_adjustment
                
                # Map back to confidence levels
                if enhanced_confidence >= 0.9:
                    enhanced_hypothesis.confidence_level = HypothesisConfidence.CONFIRMED
                elif enhanced_confidence >= 0.7:
                    enhanced_hypothesis.confidence_level = HypothesisConfidence.HIGHLY_LIKELY
                elif enhanced_confidence >= 0.5:
                    enhanced_hypothesis.confidence_level = HypothesisConfidence.PROBABLE
                elif enhanced_confidence >= 0.3:
                    enhanced_hypothesis.confidence_level = HypothesisConfidence.POSSIBLE
                else:
                    enhanced_hypothesis.confidence_level = HypothesisConfidence.SPECULATIVE
                
                # Add ML enhancement to reasoning chain
                enhanced_hypothesis.reasoning_chain.append(
                    f"ML enhancement applied: confidence adjusted by {ml_confidence_adjustment:.3f}"
                )
            
            return enhanced_hypothesis
            
        except Exception as e:
            logger.error(f"ML enhancement application failed: {e}")
            return hypothesis
    
    async def _synthesize_intelligence_product(self, hypotheses: List[IntelligenceHypothesis], 
                                             analysis_results: Dict[str, Any],
                                             synthesis_request: Dict[str, Any]) -> SynthesisProduct:
        """Synthesize final intelligence product"""
        try:
            product_id = str(uuid4())
            synthesis_type = SynthesisType(synthesis_request.get('synthesis_type', 'threat_assessment'))
            
            # Select primary hypothesis (highest confidence)
            primary_hypothesis = max(hypotheses, key=lambda h: h.confidence_level.value) if hypotheses else None
            supporting_hypotheses = [h for h in hypotheses if h != primary_hypothesis]
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                primary_hypothesis, supporting_hypotheses, analysis_results
            )
            
            # Extract key findings
            key_findings = self._extract_key_findings(hypotheses, analysis_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(primary_hypothesis, analysis_results)
            
            # Calculate analytical confidence
            analytical_confidence = self._calculate_analytical_confidence(hypotheses, analysis_results)
            
            # Create synthesis product
            synthesis_product = SynthesisProduct(
                product_id=product_id,
                synthesis_type=synthesis_type,
                title=f"{synthesis_type.value.replace('_', ' ').title()} - {datetime.now().strftime('%Y%m%d')}",
                executive_summary=executive_summary,
                key_findings=key_findings,
                primary_hypothesis=primary_hypothesis,
                supporting_hypotheses=supporting_hypotheses,
                analytical_confidence=analytical_confidence,
                source_reliability_assessment=analysis_results.get('source_reliability', {}),
                data_quality_metrics=analysis_results.get('data_quality', {}),
                synthesis_methodology=[
                    'multi_source_correlation',
                    'hypothesis_generation',
                    'ml_enhanced_analysis',
                    'temporal_correlation',
                    'pattern_recognition'
                ],
                validation_requirements=[
                    'independent_source_verification',
                    'temporal_validation',
                    'attribution_confirmation'
                ],
                intelligence_gaps=self._identify_intelligence_gaps(hypotheses, analysis_results),
                recommendations=recommendations,
                follow_up_requirements=self._generate_follow_up_requirements(primary_hypothesis),
                synthesis_timestamp=datetime.now(timezone.utc),
                review_status="pending_review",
                dissemination_level=synthesis_request.get('classification_level', 'restricted')
            )
            
            # Store synthesis product
            self.synthesis_products[product_id] = synthesis_product
            
            return synthesis_product
            
        except Exception as e:
            logger.error(f"Intelligence product synthesis failed: {e}")
            raise
    
    async def _generate_training_data(self, source_intelligence: List[Dict[str, Any]], 
                                    hypotheses: List[IntelligenceHypothesis],
                                    synthesis_product: SynthesisProduct,
                                    session: SessionAnalytics) -> ModelTrainingData:
        """Generate training data from synthesis process"""
        try:
            # Extract features from synthesis process
            feature_vector = self._extract_synthesis_features(
                source_intelligence, hypotheses, synthesis_product
            )
            
            # Create target labels
            target_labels = {
                'synthesis_quality': synthesis_product.analytical_confidence,
                'hypothesis_accuracy': np.mean([h.confidence_level.value for h in hypotheses]) if hypotheses else 0,
                'analysis_completeness': len(synthesis_product.key_findings) / 10,  # Normalized
                'recommendation_relevance': len(synthesis_product.recommendations) / 5  # Normalized
            }
            
            # Create confidence scores
            confidence_scores = np.array([h.confidence_level.value for h in hypotheses]) if hypotheses else np.array([0])
            
            # Extract reasoning patterns
            reasoning_patterns = []
            for hypothesis in hypotheses:
                reasoning_patterns.extend(hypothesis.reasoning_chain)
            
            # Create training data
            training_data = ModelTrainingData(
                training_id=str(uuid4()),
                data_source='synthesis_output',
                feature_vector=feature_vector,
                target_labels=target_labels,
                confidence_scores=confidence_scores,
                reasoning_patterns=reasoning_patterns,
                outcome_validation=None,  # Will be updated later with feedback
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=synthesis_product.analytical_confidence,
                metadata={
                    'synthesis_type': synthesis_product.synthesis_type.value,
                    'session_id': session.session_id,
                    'source_count': len(source_intelligence),
                    'hypothesis_count': len(hypotheses)
                }
            )
            
            return training_data
            
        except Exception as e:
            logger.error(f"Training data generation failed: {e}")
            # Return minimal training data
            return ModelTrainingData(
                training_id=str(uuid4()),
                data_source='synthesis_output',
                feature_vector=np.zeros(128),
                target_labels={'synthesis_quality': 0.5},
                confidence_scores=np.array([0.5]),
                reasoning_patterns=[],
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=0.5
            )
    
    def _extract_synthesis_features(self, source_intelligence: List[Dict[str, Any]], 
                                  hypotheses: List[IntelligenceHypothesis],
                                  synthesis_product: SynthesisProduct) -> np.ndarray:
        """Extract features from synthesis process for training"""
        try:
            features = []
            
            # Source intelligence features
            features.extend([
                len(source_intelligence),
                np.mean([intel['confidence_score'] for intel in source_intelligence]) if source_intelligence else 0,
                np.mean([intel['threat_level'] for intel in source_intelligence]) if source_intelligence else 0,
                len(set([intel['intelligence_type'] for intel in source_intelligence])) if source_intelligence else 0
            ])
            
            # Hypothesis features
            features.extend([
                len(hypotheses),
                np.mean([h.confidence_level.value for h in hypotheses]) if hypotheses else 0,
                np.mean([h.correlation_strength for h in hypotheses]) if hypotheses else 0,
                np.mean([h.temporal_relevance for h in hypotheses]) if hypotheses else 0
            ])
            
            # Synthesis product features
            features.extend([
                synthesis_product.analytical_confidence,
                len(synthesis_product.key_findings),
                len(synthesis_product.recommendations),
                len(synthesis_product.intelligence_gaps),
                len(synthesis_product.validation_requirements)
            ])
            
            # Pad to expected size
            while len(features) < 128:
                features.append(0.0)
            
            return np.array(features[:128], dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Synthesis feature extraction failed: {e}")
            return np.zeros(128, dtype=np.float32)


class DataFusionEngine:
    """
    Master ARCS Data Fusion Engine
    
    Orchestrates recursive intelligence synthesis with autonomous model evolution,
    hypothesis generation, and continuous learning from operational outcomes.
    """
    
    def __init__(self, intelligence_db, threat_aggregation_engine, 
                 config_path: str = "config/data_fusion.yaml"):
        self.intelligence_db = intelligence_db
        self.threat_aggregation = threat_aggregation_engine
        self.config_path = Path(config_path)
        
        # Core synthesis engine
        self.synthesis_engine = IntelligenceSynthesisEngine(intelligence_db, threat_aggregation_engine)
        
        # Session management
        self.active_sessions = {}
        self.session_logs = deque(maxlen=1000)
        
        # Configuration
        self.fusion_config = {}
        
        # Background services
        self.background_tasks = []
        self.shutdown_event = asyncio.Event()
        
        # Performance metrics
        self.fusion_metrics = defaultdict(int)
        
        self._load_configuration()
    
    def _load_configuration(self):
        """Load data fusion configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.fusion_config = yaml.safe_load(f)
            else:
                self.fusion_config = self._create_default_config()
                self._save_configuration()
            
            logger.info("Data fusion configuration loaded")
            
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            self.fusion_config = self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default fusion configuration"""
        return {
            'synthesis': {
                'default_synthesis_type': 'threat_assessment',
                'max_concurrent_syntheses': 5,
                'default_time_window_hours': 168,
                'min_source_count': 3
            },
            'learning': {
                'continuous_learning_enabled': True,
                'model_update_interval_hours': 1,
                'training_batch_size': 32,
                'learning_rate': 0.001
            },
            'session_logging': {
                'log_all_sessions': True,
                'detailed_reasoning_logs': True,
                'performance_tracking': True,
                'retention_days': 365
            }
        }
    
    def _save_configuration(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.fusion_config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Configuration saving failed: {e}")
    
    async def initialize(self):
        """Initialize data fusion engine"""
        try:
            logger.info("Initializing ARCS Data Fusion Engine...")
            
            # Start background services
            await self._start_background_services()
            
            logger.info("Data fusion engine fully operational")
            
        except Exception as e:
            logger.error(f"Data fusion initialization failed: {e}")
            raise
    
    async def _start_background_services(self):
        """Start background fusion services"""
        try:
            self.background_tasks.extend([
                asyncio.create_task(self._continuous_learning_service()),
                asyncio.create_task(self._session_monitoring_service()),
                asyncio.create_task(self._performance_optimization_service())
            ])
            
            logger.info("Background fusion services started")
            
        except Exception as e:
            logger.error(f"Background service startup failed: {e}")
    
    async def _continuous_learning_service(self):
        """Continuous model learning and evolution service"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Trigger model evolution in learning engine
                if hasattr(self.synthesis_engine.learning_engine, '_trigger_model_retraining'):
                    await self.synthesis_engine.learning_engine._trigger_model_retraining()
                
                # Update fusion metrics
                self.fusion_metrics['learning_cycles'] += 1
                
                logger.info("Continuous learning cycle completed")
                
            except Exception as e:
                logger.error(f"Continuous learning service error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    


    async def _session_monitoring_service(self):
        """Monitor active synthesis sessions and maintain session log hygiene."""
        retention_days = self.fusion_config.get('session_logging', {}).get('retention_days', 365)
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # every 5 minutes

                # Keep lightweight session observability metrics updated
                self.fusion_metrics['active_sessions_current'] = len(self.active_sessions)
                self.fusion_metrics['session_logs_count'] = len(self.session_logs)

                # Prune old session logs based on configured retention
                cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
                while self.session_logs:
                    head = self.session_logs[0]
                    head_start = getattr(head, 'session_start', None)
                    if isinstance(head, dict):
                        head_start = head.get('session_start', head_start)
                    if isinstance(head_start, str):
                        try:
                            head_start = datetime.fromisoformat(head_start)
                        except Exception:
                            head_start = None
                    if head_start is None or head_start >= cutoff:
                        break
                    self.session_logs.popleft()

                logger.debug(
                    f"Session monitor: active={len(self.active_sessions)} logs={len(self.session_logs)}"
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session monitoring service error: {e}")
                await asyncio.sleep(30)

    async def _performance_optimization_service(self):
        """Periodic optimization and guardrail checks for data-fusion runtime."""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(900)  # every 15 minutes

                synth_count = self.fusion_metrics.get('syntheses_created', 0)
                total_ms = self.fusion_metrics.get('total_processing_time_ms', 0)
                if synth_count > 0:
                    self.fusion_metrics['avg_processing_time_ms_runtime'] = total_ms / synth_count

                max_concurrent = self.fusion_config.get('synthesis', {}).get('max_concurrent_syntheses', 5)
                active_count = len(self.active_sessions)
                if active_count > max_concurrent:
                    logger.warning(
                        f"Active sessions ({active_count}) exceed configured max ({max_concurrent})"
                    )

                self.fusion_metrics['optimization_cycles'] += 1
                logger.debug("Performance optimization cycle completed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance optimization service error: {e}")
                await asyncio.sleep(60)

    async def create_intelligence_synthesis(self, synthesis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive intelligence synthesis with recursive learning"""
        try:
            synthesis_start = time.time()
            
            # Validate synthesis request
            validated_request = self._validate_synthesis_request(synthesis_request)
            
            # Create synthesis product
            synthesis_product = await self.synthesis_engine.create_synthesis_product(validated_request)
            
            # Generate comprehensive result
            result = {
                'synthesis_product_id': synthesis_product.product_id,
                'synthesis_type': synthesis_product.synthesis_type.value,
                'title': synthesis_product.title,
                'executive_summary': synthesis_product.executive_summary,
                'key_findings': synthesis_product.key_findings,
                'analytical_confidence': synthesis_product.analytical_confidence,
                'primary_hypothesis': asdict(synthesis_product.primary_hypothesis) if synthesis_product.primary_hypothesis else None,
                'supporting_hypotheses': [asdict(h) for h in synthesis_product.supporting_hypotheses],
                'recommendations': synthesis_product.recommendations,
                'intelligence_gaps': synthesis_product.intelligence_gaps,
                'synthesis_metadata': {
                    'synthesis_timestamp': synthesis_product.synthesis_timestamp.isoformat(),
                    'methodology': synthesis_product.synthesis_methodology,
                    'data_quality_metrics': synthesis_product.data_quality_metrics,
                    'source_reliability': synthesis_product.source_reliability_assessment
                },
                'processing_time_ms': (time.time() - synthesis_start) * 1000,
                'status': 'completed'
            }
            
            # Update metrics
            self.fusion_metrics['syntheses_created'] += 1
            self.fusion_metrics['total_processing_time_ms'] += result['processing_time_ms']
            
            logger.info(f"Created intelligence synthesis {synthesis_product.product_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Intelligence synthesis creation failed: {e}")
            return {
                'error': str(e),
                'status': 'failed',
                'processing_time_ms': (time.time() - synthesis_start) * 1000 if 'synthesis_start' in locals() else 0
            }
    
    def _validate_synthesis_request(self, synthesis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance synthesis request"""
        try:
            validated_request = synthesis_request.copy()
            
            # Set defaults
            if 'synthesis_type' not in validated_request:
                validated_request['synthesis_type'] = self.fusion_config['synthesis']['default_synthesis_type']
            
            if 'time_range' not in validated_request:
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=self.fusion_config['synthesis']['default_time_window_hours'])
                validated_request['time_range'] = (start_time, end_time)
            
            if 'max_sources' not in validated_request:
                validated_request['max_sources'] = 1000
            
            if 'priority_level' not in validated_request:
                validated_request['priority_level'] = 'normal'
            
            return validated_request
            
        except Exception as e:
            logger.error(f"Synthesis request validation failed: {e}")
            return synthesis_request
    
    async def get_fusion_status(self) -> Dict[str, Any]:
        """Get comprehensive data fusion status"""
        try:
            status = {
                'engine_status': 'operational',
                'active_sessions': len(self.active_sessions),
                'total_syntheses_created': self.fusion_metrics['syntheses_created'],
                'learning_cycles_completed': self.fusion_metrics['learning_cycles'],
                'model_versions': self.synthesis_engine.learning_engine.model_versions,
                'session_logs_count': len(self.session_logs),
                'average_processing_time_ms': (
                    self.fusion_metrics['total_processing_time_ms'] / 
                    max(1, self.fusion_metrics['syntheses_created'])
                ),
                'configuration': self.fusion_config,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {'engine_status': 'error', 'error': str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown data fusion engine"""
        logger.info("Shutting down data fusion engine...")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Data fusion engine shutdown complete")


# Runtime completion patch: fills synthesis methods that are referenced but absent in class body.
# TECH DEBT: These _ise_* functions are dynamically bound to IntelligenceSynthesisEngine at
# module load time.  They should be migrated into the class body as proper methods in a future
# refactor pass to restore IDE navigation, static analysis, and type-checker support.
if not hasattr(IntelligenceSynthesisEngine, '_perform_comprehensive_analysis'):
    async def _ise_validate_and_rank_hypotheses(self, hypotheses: List[IntelligenceHypothesis]) -> List[IntelligenceHypothesis]:
        try:
            if not hypotheses:
                return []

            min_confidence = float(self.synthesis_config.get('min_confidence_threshold', 0.3))
            max_hypotheses = max(1, int(self.synthesis_config.get('max_hypotheses_per_synthesis', 5)))

            qualified = [h for h in hypotheses if float(h.confidence_level.value) >= min_confidence]
            if not qualified:
                qualified = hypotheses

            ranked = sorted(qualified, key=self._calculate_hypothesis_ranking_score, reverse=True)[:max_hypotheses]

            if self.current_session:
                self.current_session.confidence_distribution = dict(Counter(h.confidence_level.name for h in ranked))

            return ranked
        except Exception as e:
            logger.error(f'Hypothesis validation/ranking failed: {e}')
            return hypotheses[:5]

    def _ise_calculate_hypothesis_ranking_score(self, hypothesis: IntelligenceHypothesis) -> float:
        try:
            score = (
                float(hypothesis.confidence_level.value) * 0.50
                + float(hypothesis.correlation_strength) * 0.20
                + float(hypothesis.temporal_relevance) * 0.15
                + min(1.0, len(hypothesis.supporting_evidence) / 5.0) * 0.10
                + min(1.0, len(hypothesis.predictive_indicators) / 5.0) * 0.05
            )
            return float(np.clip(score, 0.0, 1.0))
        except Exception:
            return float(hypothesis.confidence_level.value)

    async def _ise_perform_comprehensive_analysis(self, source_intelligence: List[Dict[str, Any]],
                                                 hypotheses: List[IntelligenceHypothesis]) -> Dict[str, Any]:
        try:
            if not source_intelligence:
                return {
                    'source_reliability': {},
                    'data_quality': {
                        'completeness': 0.0,
                        'average_confidence': 0.0,
                        'source_diversity': 0.0,
                        'indicator_density': 0.0,
                        'temporal_coverage_hours': 0.0
                    },
                    'threat_statistics': {
                        'record_count': 0,
                        'high_threat_count': 0,
                        'average_threat_level': 0.0,
                        'max_threat_level': 0.0
                    },
                    'temporal_analysis': {
                        'window_start': None,
                        'window_end': None,
                        'window_hours': 0.0,
                        'records_per_day': 0.0
                    }
                }

            def _to_dt(value: Any) -> Optional[datetime]:
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value)
                    except Exception:
                        return None
                return None

            required_fields = {
                'record_id', 'intelligence_type', 'collection_timestamp', 'raw_data',
                'processed_indicators', 'confidence_score', 'threat_level', 'tags', 'metadata'
            }

            completeness_scores = []
            confidence_scores = []
            threat_levels = []
            indicator_counts = []
            source_confidence = defaultdict(list)
            timestamps = []

            for intel in source_intelligence:
                present = sum(1 for field in required_fields if field in intel and intel[field] is not None)
                completeness_scores.append(present / len(required_fields))

                confidence_scores.append(float(intel.get('confidence_score', 0.0)))
                threat_levels.append(float(intel.get('threat_level', 0.0)))
                indicator_counts.append(len(intel.get('processed_indicators', []) or []))

                metadata = intel.get('metadata', {}) or {}
                source_system = metadata.get('source_system', 'unknown')
                source_confidence[source_system].append(float(intel.get('confidence_score', 0.0)))

                ts = _to_dt(intel.get('collection_timestamp'))
                if ts:
                    timestamps.append(ts)

            source_reliability = {
                source: float(np.mean(values)) if values else 0.0
                for source, values in source_confidence.items()
            }

            if timestamps:
                window_start = min(timestamps)
                window_end = max(timestamps)
                window_hours = max(0.0, (window_end - window_start).total_seconds() / 3600.0)
            else:
                window_start = None
                window_end = None
                window_hours = 0.0

            records_per_day = 0.0
            if window_hours > 0:
                records_per_day = len(source_intelligence) / max(1.0, window_hours / 24.0)

            return {
                'source_reliability': source_reliability,
                'data_quality': {
                    'completeness': float(np.mean(completeness_scores)) if completeness_scores else 0.0,
                    'average_confidence': float(np.mean(confidence_scores)) if confidence_scores else 0.0,
                    'source_diversity': float(len(source_reliability)) / max(1.0, len(source_intelligence)),
                    'indicator_density': float(np.mean(indicator_counts)) if indicator_counts else 0.0,
                    'temporal_coverage_hours': window_hours
                },
                'threat_statistics': {
                    'record_count': len(source_intelligence),
                    'high_threat_count': sum(1 for level in threat_levels if level >= 7.0),
                    'average_threat_level': float(np.mean(threat_levels)) if threat_levels else 0.0,
                    'max_threat_level': float(np.max(threat_levels)) if threat_levels else 0.0
                },
                'temporal_analysis': {
                    'window_start': window_start.isoformat() if window_start else None,
                    'window_end': window_end.isoformat() if window_end else None,
                    'window_hours': window_hours,
                    'records_per_day': records_per_day
                }
            }
        except Exception as e:
            logger.error(f'Comprehensive analysis failed: {e}')
            return {
                'source_reliability': {},
                'data_quality': {},
                'threat_statistics': {},
                'temporal_analysis': {}
            }

    async def _ise_generate_campaign_hypotheses(self, source_intelligence: List[Dict[str, Any]]) -> List[IntelligenceHypothesis]:
        try:
            if len(source_intelligence) < 2:
                return []

            tag_counter = Counter()
            indicators = []
            for intel in source_intelligence:
                tag_counter.update(intel.get('tags', []) or [])
                indicators.extend((intel.get('processed_indicators', []) or [])[:2])

            dominant_tags = [tag for tag, count in tag_counter.items() if count >= 2][:3]
            confidence = self._calculate_hypothesis_confidence(indicators, source_intelligence)

            return [
                IntelligenceHypothesis(
                    hypothesis_id=str(uuid4()),
                    hypothesis_type=SynthesisType.CAMPAIGN_ANALYSIS,
                    hypothesis_statement=(
                        'Observed indicator overlap and recurring tags suggest a coordinated campaign '
                        f'across {len(source_intelligence)} records'
                    ),
                    confidence_level=confidence,
                    supporting_evidence=[{'type': 'tag_overlap', 'dominant_tags': dominant_tags}],
                    contradicting_evidence=[],
                    reasoning_chain=[
                        f'Recurring tags detected: {dominant_tags if dominant_tags else ["none"]}',
                        'Indicator overlap supports campaign-level activity',
                        f'Campaign confidence: {confidence.name}'
                    ],
                    data_sources=[intel['record_id'] for intel in source_intelligence],
                    correlation_strength=0.68,
                    temporal_relevance=0.72,
                    predictive_indicators=indicators[:5],
                    validation_criteria=[
                        'cross-source campaign confirmation',
                        'infrastructure overlap verification',
                        'time-sequenced activity validation'
                    ],
                    alternative_hypotheses=['independent opportunistic activity'],
                    uncertainty_factors=['partial source coverage'],
                    creation_timestamp=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc)
                )
            ]
        except Exception as e:
            logger.error(f'Campaign hypothesis generation failed: {e}')
            return []

    async def _ise_generate_attribution_hypotheses(self, source_intelligence: List[Dict[str, Any]]) -> List[IntelligenceHypothesis]:
        try:
            if not source_intelligence:
                return []

            actor_candidates = []
            indicators = []
            for intel in source_intelligence:
                metadata = intel.get('metadata', {}) or {}
                actor = metadata.get('suspected_actor')
                if actor:
                    actor_candidates.append(actor)

                for tag in intel.get('tags', []) or []:
                    if isinstance(tag, str) and tag.lower().startswith('actor:'):
                        actor_candidates.append(tag.split(':', 1)[1].strip())

                indicators.extend((intel.get('processed_indicators', []) or [])[:1])

            actor_name = Counter(actor_candidates).most_common(1)
            actor_name = actor_name[0][0] if actor_name else 'unknown actor cluster'
            confidence = self._calculate_hypothesis_confidence(indicators + [actor_name], source_intelligence)

            return [
                IntelligenceHypothesis(
                    hypothesis_id=str(uuid4()),
                    hypothesis_type=SynthesisType.ATTRIBUTION_HYPOTHESIS,
                    hypothesis_statement=f'Activity pattern aligns with {actor_name} tradecraft profile',
                    confidence_level=confidence,
                    supporting_evidence=[{'type': 'actor_signal_overlap', 'actor': actor_name}],
                    contradicting_evidence=[],
                    reasoning_chain=[
                        f'Attribution signals map to candidate: {actor_name}',
                        'Observed indicators align with recurring TTP sequence',
                        f'Attribution confidence: {confidence.name}'
                    ],
                    data_sources=[intel['record_id'] for intel in source_intelligence],
                    correlation_strength=0.66,
                    temporal_relevance=0.70,
                    predictive_indicators=indicators[:5],
                    validation_criteria=[
                        'independent attribution verification',
                        'infrastructure ownership correlation',
                        'historical campaign similarity analysis'
                    ],
                    alternative_hypotheses=['false-flag operation'],
                    uncertainty_factors=['attribution deception risk'],
                    creation_timestamp=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc)
                )
            ]
        except Exception as e:
            logger.error(f'Attribution hypothesis generation failed: {e}')
            return []

    async def _ise_generate_predictive_hypotheses(self, source_intelligence: List[Dict[str, Any]]) -> List[IntelligenceHypothesis]:
        try:
            if not source_intelligence:
                return []

            ordered = sorted(source_intelligence, key=lambda x: x.get('collection_timestamp', datetime.now(timezone.utc)))
            threat_levels = [float(intel.get('threat_level', 0.0)) for intel in ordered]

            split = max(1, len(threat_levels) // 2)
            first_half = threat_levels[:split]
            second_half = threat_levels[split:] or first_half
            trend_delta = float(np.mean(second_half) - np.mean(first_half))

            trend_direction = 'escalation' if trend_delta >= 0.25 else 'stabilization'
            confidence = HypothesisConfidence.PROBABLE if trend_delta >= 0.25 else HypothesisConfidence.POSSIBLE

            return [
                IntelligenceHypothesis(
                    hypothesis_id=str(uuid4()),
                    hypothesis_type=SynthesisType.PREDICTIVE_INTELLIGENCE,
                    hypothesis_statement=(
                        'Current signal progression indicates likely near-term '
                        f'{trend_direction} of threat activity over the next 72 hours'
                    ),
                    confidence_level=confidence,
                    supporting_evidence=[{'type': 'temporal_trend', 'trend_delta': trend_delta}],
                    contradicting_evidence=[],
                    reasoning_chain=[
                        f'Threat level delta between windows: {trend_delta:.3f}',
                        f'Trend classified as {trend_direction}',
                        f'Predictive confidence: {confidence.name}'
                    ],
                    data_sources=[intel['record_id'] for intel in ordered],
                    correlation_strength=0.62,
                    temporal_relevance=0.80,
                    predictive_indicators=[p for intel in ordered for p in (intel.get('processed_indicators', []) or [])[:1]][:5],
                    validation_criteria=[
                        'next-window incident volume validation',
                        'escalation signal verification',
                        'countermeasure effectiveness tracking'
                    ],
                    alternative_hypotheses=['short-lived activity burst'],
                    uncertainty_factors=['sampling window bias'],
                    creation_timestamp=datetime.now(timezone.utc),
                    last_updated=datetime.now(timezone.utc)
                )
            ]
        except Exception as e:
            logger.error(f'Predictive hypothesis generation failed: {e}')
            return []

    def _ise_generate_executive_summary(self, primary_hypothesis: Optional[IntelligenceHypothesis],
                                      supporting_hypotheses: List[IntelligenceHypothesis],
                                      analysis_results: Dict[str, Any]) -> str:
        if not primary_hypothesis:
            return (
                'No high-confidence hypotheses met synthesis thresholds. Additional collection '
                'and correlation are required before actionable conclusions can be issued.'
            )

        stats = analysis_results.get('threat_statistics', {})
        return (
            f'Primary assessment: {primary_hypothesis.hypothesis_statement}. '
            f'Analysis evaluated {stats.get("record_count", 0)} records, including '
            f'{stats.get("high_threat_count", 0)} high-threat observations. '
            f'{len(supporting_hypotheses)} supporting hypotheses provide corroborating context.'
        )

    def _ise_extract_key_findings(self, hypotheses: List[IntelligenceHypothesis],
                                analysis_results: Dict[str, Any]) -> List[str]:
        findings: List[str] = []

        if hypotheses:
            findings.append(
                f'Top hypothesis confidence: {hypotheses[0].confidence_level.name} '
                f'({hypotheses[0].confidence_level.value:.2f})'
            )
            findings.extend([h.hypothesis_statement for h in hypotheses[:3]])

        stats = analysis_results.get('threat_statistics', {})
        if stats:
            findings.append(
                f'Threat profile: avg level {stats.get("average_threat_level", 0.0):.2f}, '
                f'max level {stats.get("max_threat_level", 0.0):.2f}'
            )

        quality = analysis_results.get('data_quality', {})
        if quality:
            findings.append(
                f'Data quality completeness: {quality.get("completeness", 0.0):.2f}; '
                f'source diversity ratio: {quality.get("source_diversity", 0.0):.2f}'
            )

        return findings[:8]

    def _ise_generate_recommendations(self, primary_hypothesis: Optional[IntelligenceHypothesis],
                                    analysis_results: Dict[str, Any]) -> List[str]:
        recommendations = [
            'Increase collection frequency for highest-signal indicators over the next 24 hours.',
            'Prioritize correlation of infrastructure and telemetry artifacts tied to primary indicators.',
            'Trigger analyst review for high-confidence findings before dissemination escalation.'
        ]

        if primary_hypothesis and primary_hypothesis.confidence_level.value >= HypothesisConfidence.HIGHLY_LIKELY.value:
            recommendations.append('Issue high-priority alert bulletin and begin targeted containment planning.')

        quality = analysis_results.get('data_quality', {})
        if quality.get('completeness', 1.0) < 0.8:
            recommendations.append('Backfill missing metadata fields to improve confidence calibration and replay quality.')

        return recommendations[:6]

    def _ise_calculate_analytical_confidence(self, hypotheses: List[IntelligenceHypothesis],
                                           analysis_results: Dict[str, Any]) -> float:
        if not hypotheses:
            return 0.0

        hypothesis_confidence = float(np.mean([h.confidence_level.value for h in hypotheses]))
        quality = analysis_results.get('data_quality', {})
        completeness = float(quality.get('completeness', 0.0))
        diversity = float(quality.get('source_diversity', 0.0))

        return float(np.clip((hypothesis_confidence * 0.7) + (completeness * 0.2) + (diversity * 0.1), 0.0, 1.0))

    def _ise_identify_intelligence_gaps(self, hypotheses: List[IntelligenceHypothesis],
                                      analysis_results: Dict[str, Any]) -> List[str]:
        gaps = []

        if not hypotheses:
            gaps.append('No validated hypotheses generated from available source intelligence.')

        quality = analysis_results.get('data_quality', {})
        if quality.get('source_diversity', 0.0) < 0.3:
            gaps.append('Limited source diversity; add independent data providers for corroboration.')
        if quality.get('completeness', 0.0) < 0.8:
            gaps.append('Incomplete record fields detected; improve metadata and indicator normalization.')

        temporal = analysis_results.get('temporal_analysis', {})
        if temporal.get('window_hours', 0.0) < 24.0:
            gaps.append('Temporal coverage is narrow; extend collection window to reduce short-term bias.')

        return gaps[:6]

    def _ise_generate_follow_up_requirements(self, primary_hypothesis: Optional[IntelligenceHypothesis]) -> List[str]:
        requirements = [
            'Collect corroborating evidence from at least two independent telemetry sources.',
            'Run attribution cross-check against historical campaign signatures.',
            'Recompute confidence after next data-ingest cycle and compare deltas.'
        ]

        if primary_hypothesis:
            indicators = primary_hypothesis.predictive_indicators[:3]
            if indicators:
                requirements.append(f'Track indicator evolution for: {", ".join(indicators)}')

        return requirements[:6]

    async def _ise_complete_synthesis_session(self, session: SessionAnalytics,
                                            synthesis_product: SynthesisProduct) -> None:
        try:
            session.session_end = datetime.now(timezone.utc)
            session.synthesis_products_created += 1

            duration_seconds = (session.session_end - session.session_start).total_seconds()
            session.performance_metrics.update({
                'duration_seconds': max(0.0, duration_seconds),
                'analytical_confidence': synthesis_product.analytical_confidence,
                'key_findings_count': float(len(synthesis_product.key_findings)),
                'recommendations_count': float(len(synthesis_product.recommendations))
            })

            if synthesis_product.primary_hypothesis:
                session.reasoning_patterns.extend(synthesis_product.primary_hypothesis.reasoning_chain[:3])

            session.learning_outcomes.append(
                f'Synthesis completed for {synthesis_product.synthesis_type.value} '
                f'with confidence {synthesis_product.analytical_confidence:.2f}'
            )
            session.model_updates_applied = list(self.learning_engine.model_versions.keys())

            self.session_history.append(session)
            self.current_session = None
        except Exception as e:
            logger.error(f'Session completion failed: {e}')

    IntelligenceSynthesisEngine._validate_and_rank_hypotheses = _ise_validate_and_rank_hypotheses
    IntelligenceSynthesisEngine._calculate_hypothesis_ranking_score = _ise_calculate_hypothesis_ranking_score
    IntelligenceSynthesisEngine._perform_comprehensive_analysis = _ise_perform_comprehensive_analysis
    IntelligenceSynthesisEngine._generate_campaign_hypotheses = _ise_generate_campaign_hypotheses
    IntelligenceSynthesisEngine._generate_attribution_hypotheses = _ise_generate_attribution_hypotheses
    IntelligenceSynthesisEngine._generate_predictive_hypotheses = _ise_generate_predictive_hypotheses
    IntelligenceSynthesisEngine._generate_executive_summary = _ise_generate_executive_summary
    IntelligenceSynthesisEngine._extract_key_findings = _ise_extract_key_findings
    IntelligenceSynthesisEngine._generate_recommendations = _ise_generate_recommendations
    IntelligenceSynthesisEngine._calculate_analytical_confidence = _ise_calculate_analytical_confidence
    IntelligenceSynthesisEngine._identify_intelligence_gaps = _ise_identify_intelligence_gaps
    IntelligenceSynthesisEngine._generate_follow_up_requirements = _ise_generate_follow_up_requirements
    IntelligenceSynthesisEngine._complete_synthesis_session = _ise_complete_synthesis_session


# Export primary interfaces
__all__ = [
    'DataFusionEngine',
    'IntelligenceSynthesisEngine',
    'IntelligenceHypothesis',
    'SynthesisProduct',
    'SynthesisType',
    'HypothesisConfidence'
]



if __name__ == "__main__":
    # Development testing and validation
    async def test_data_fusion():
        """Comprehensive testing of data fusion functionality"""

        # Mock dependencies
        @dataclass
        class MockIntelligenceRecord:
            """Lightweight stand-in for a real intelligence record.

            Mirrors the field interface expected by ``IntelligenceSynthesisEngine``
            during development testing without requiring an actual database.
            """

            record_id: str
            intelligence_type: str
            collection_timestamp: datetime
            raw_data: Dict[str, Any]
            processed_indicators: List[str]
            confidence_score: float
            threat_level: int
            tags: List[str]
            metadata: Dict[str, Any]

        class MockIntelligenceDB:
            """In-memory mock of the intelligence database for development testing.

            Pre-populates a small set of threat records and supports
            ``advanced_query`` with basic filtering by threat level,
            intelligence type, time range, and limit.
            """

            def __init__(self):
                now = datetime.now(timezone.utc)
                self.records = [
                    MockIntelligenceRecord(
                        record_id='mock-001',
                        intelligence_type='network_telemetry',
                        collection_timestamp=now - timedelta(hours=6),
                        raw_data={'src_ip': '10.10.1.5', 'dst_ip': '198.51.100.23', 'protocol': 'http'},
                        processed_indicators=[
                            'scan-reconnaissance-burst',
                            'vulnerability-exploit-cve-2026-1101',
                            'command-beacon-http'
                        ],
                        confidence_score=0.82,
                        threat_level=8,
                        tags=['campaign:aurora', 'actor:gray-fox', 'initial_access'],
                        metadata={'source_system': 'sensor_alpha', 'suspected_actor': 'gray-fox'}
                    ),
                    MockIntelligenceRecord(
                        record_id='mock-002',
                        intelligence_type='osint_signal',
                        collection_timestamp=now - timedelta(hours=5),
                        raw_data={'forum': 'public_feed', 'ioc_type': 'domain', 'value': 'beacon-node.example'},
                        processed_indicators=[
                            'probe-enumeration-smb',
                            'exploit-injection-webshell',
                            'callback-c2-dns'
                        ],
                        confidence_score=0.76,
                        threat_level=7,
                        tags=['campaign:aurora', 'actor:gray-fox', 'lateral_movement'],
                        metadata={'source_system': 'sensor_bravo', 'suspected_actor': 'gray-fox'}
                    ),
                    MockIntelligenceRecord(
                        record_id='mock-003',
                        intelligence_type='endpoint_telemetry',
                        collection_timestamp=now - timedelta(hours=3),
                        raw_data={'host': 'ws-342', 'event': 'powershell', 'severity': 'high'},
                        processed_indicators=[
                            'scan-port-sweep',
                            'overflow-exploit-attempt',
                            'data-exfiltration-upload'
                        ],
                        confidence_score=0.79,
                        threat_level=9,
                        tags=['campaign:aurora', 'privilege_escalation', 'exfiltration'],
                        metadata={'source_system': 'sensor_charlie', 'suspected_actor': 'gray-fox'}
                    ),
                    MockIntelligenceRecord(
                        record_id='mock-004',
                        intelligence_type='network_telemetry',
                        collection_timestamp=now - timedelta(hours=2),
                        raw_data={'src_ip': '10.10.2.18', 'dst_ip': '203.0.113.77', 'protocol': 'dns'},
                        processed_indicators=[
                            'registry-persistence-task',
                            'lateral-movement-privilege-escalation',
                            'beacon-command-control'
                        ],
                        confidence_score=0.74,
                        threat_level=6,
                        tags=['campaign:aurora', 'persistence', 'c2'],
                        metadata={'source_system': 'sensor_alpha', 'suspected_actor': 'gray-fox'}
                    )
                ]

            async def advanced_query(self, params):
                """Query mock records with optional filtering.

                Args:
                    params: Dictionary with optional keys ``min_threat_level``,
                        ``intelligence_types``, ``time_range`` (tuple of datetimes),
                        and ``limit``.

                Returns:
                    List of ``MockIntelligenceRecord`` instances matching filters.
                """
                records = list(self.records)

                min_threat_level = params.get('min_threat_level')
                if min_threat_level is not None:
                    records = [r for r in records if r.threat_level >= int(min_threat_level)]

                intelligence_types = params.get('intelligence_types')
                if intelligence_types:
                    allowed = set(intelligence_types)
                    records = [r for r in records if r.intelligence_type in allowed]

                time_range = params.get('time_range')
                if isinstance(time_range, tuple) and len(time_range) == 2:
                    start_ts, end_ts = time_range
                    if isinstance(start_ts, datetime) and isinstance(end_ts, datetime):
                        records = [
                            r for r in records
                            if start_ts <= r.collection_timestamp <= end_ts
                        ]

                limit = int(params.get('limit', len(records)))
                return records[:max(0, limit)]

        class MockThreatAggregation:
            """No-op mock for the threat aggregation engine dependency."""

            pass

        # Initialize fusion engine
        mock_db = MockIntelligenceDB()
        mock_aggregation = MockThreatAggregation()
        fusion_engine = DataFusionEngine(mock_db, mock_aggregation)

        try:
            # Initialize engine
            await fusion_engine.initialize()

            # Create test synthesis request
            synthesis_request = {
                'synthesis_type': 'threat_assessment',
                'priority_level': 'high',
                'classification_level': 'restricted'
            }

            # Create intelligence synthesis
            result = await fusion_engine.create_intelligence_synthesis(synthesis_request)

            result_summary = {
                'status': result.get('status') if isinstance(result, dict) else 'unknown',
                'result_type': type(result).__name__,
                'result_keys': list(result.keys()) if isinstance(result, dict) else [],
                'synthesis_type': synthesis_request.get('synthesis_type'),
                'priority_level': synthesis_request.get('priority_level'),
                'synthesis_product_id': result.get('synthesis_product_id') if isinstance(result, dict) else None,
                'analytical_confidence': result.get('analytical_confidence') if isinstance(result, dict) else None,
                'key_findings_count': len(result.get('key_findings', [])) if isinstance(result, dict) else 0,
                'recommendations_count': len(result.get('recommendations', [])) if isinstance(result, dict) else 0,
                'error': result.get('error') if isinstance(result, dict) else None
            }
            print(f"Data fusion synthesis summary: {json.dumps(result_summary, indent=2, default=str)}")

            # Get engine status
            status = await fusion_engine.get_fusion_status()
            print(f"Data fusion engine status: {json.dumps(status, indent=2, default=str)}")

        finally:
            # Shutdown
            await fusion_engine.shutdown()
            print("Data fusion engine test completed successfully")

    # Run test
    asyncio.run(test_data_fusion())

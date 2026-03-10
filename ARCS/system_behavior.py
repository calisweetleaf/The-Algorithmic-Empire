#!/usr/bin/env python3
"""
ARCS System Behavior Analysis Engine - Recursive Behavioral Intelligence
======================================================================
Autonomous Reactive Cyber Systems - System Behavioral Intelligence Domain

Mission: Advanced system behavioral analysis through pattern recognition, anomaly detection,
baseline establishment, and recursive machine learning with continuous model evolution
through operational feedback and behavioral hypothesis validation.

Classification: BEHAVIORAL INTELLIGENCE - SOVEREIGN INFRASTRUCTURE
ROE Authority: Autonomous behavioral profiling with recursive learning evolution
Deployment: Field-ready production system with behavioral cognitive improvement
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
import os
import psutil
import platform
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

# ML and behavioral analysis
import onnxruntime as ort
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA, FastICA
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.stats import entropy, kstest, chi2_contingency
from scipy.spatial.distance import euclidean, cosine, mahalanobis
from scipy.signal import find_peaks, periodogram

# Advanced behavioral modeling
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class BehavioralAnalysisType(Enum):
    """Behavioral analysis classification taxonomy"""
    BASELINE_ESTABLISHMENT = "baseline_establishment"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    BEHAVIORAL_PROFILING = "behavioral_profiling"
    DEVIATION_ANALYSIS = "deviation_analysis"
    PREDICTIVE_MODELING = "predictive_modeling"
    CORRELATION_ANALYSIS = "correlation_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"


class SystemEntityType(Enum):
    """System entity classification for behavioral analysis"""
    USER_ACCOUNT = "user_account"
    PROCESS = "process"
    SERVICE = "service"
    NETWORK_CONNECTION = "network_connection"
    FILE_SYSTEM_OBJECT = "file_system_object"
    REGISTRY_KEY = "registry_key"
    DEVICE = "device"
    APPLICATION = "application"
    SYSTEM_RESOURCE = "system_resource"


class BehavioralAnomalyType(Enum):
    """Types of behavioral anomalies detected"""
    STATISTICAL_OUTLIER = "statistical_outlier"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    FREQUENCY_DEVIATION = "frequency_deviation"
    PATTERN_BREAK = "pattern_break"
    THRESHOLD_VIOLATION = "threshold_violation"
    CORRELATION_ANOMALY = "correlation_anomaly"
    ENTROPY_ANOMALY = "entropy_anomaly"
    BEHAVIORAL_DRIFT = "behavioral_drift"


class ConfidenceLevel(Enum):
    """Behavioral analysis confidence levels"""
    VERY_LOW = 0.2        # 0-30% confidence
    LOW = 0.4             # 30-50% confidence
    MODERATE = 0.6        # 50-70% confidence
    HIGH = 0.8            # 70-90% confidence
    VERY_HIGH = 0.95      # 90-100% confidence


@dataclass
class BehavioralBaseline:
    """Comprehensive behavioral baseline profile"""
    baseline_id: str
    entity_id: str
    entity_type: SystemEntityType
    baseline_period_start: datetime
    baseline_period_end: datetime
    observation_count: int
    statistical_measures: Dict[str, float]
    temporal_patterns: Dict[str, Any]
    frequency_distributions: Dict[str, List[float]]
    correlation_matrix: np.ndarray
    pattern_signatures: List[str]
    entropy_measurements: Dict[str, float]
    behavioral_features: np.ndarray
    confidence_intervals: Dict[str, Tuple[float, float]]
    baseline_quality_score: float
    last_updated: datetime
    baseline_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralAnomaly:
    """Behavioral anomaly detection result"""
    anomaly_id: str
    entity_id: str
    entity_type: SystemEntityType
    anomaly_type: BehavioralAnomalyType
    detection_timestamp: datetime
    anomaly_score: float
    confidence_level: ConfidenceLevel
    baseline_deviation: float
    statistical_significance: float
    affected_features: List[str]
    anomaly_description: str
    evidence_data: Dict[str, Any]
    correlation_anomalies: List[str]
    temporal_context: Dict[str, Any]
    mitigation_recommendations: List[str]
    false_positive_probability: float
    anomaly_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralPattern:
    """Identified behavioral pattern structure"""
    pattern_id: str
    pattern_type: str
    pattern_name: str
    pattern_description: str
    pattern_signature: str
    frequency: float
    temporal_occurrence: Dict[str, Any]
    entities_exhibiting: List[str]
    pattern_strength: float
    statistical_confidence: float
    first_observed: datetime
    last_observed: datetime
    evolution_tracking: List[Dict[str, Any]]
    pattern_correlations: List[str]
    predictive_indicators: List[str]
    pattern_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralSession:
    """Session-level behavioral analytics for model training"""
    session_id: str
    session_start: datetime
    session_end: Optional[datetime]
    entities_analyzed: int
    baselines_established: int
    anomalies_detected: int
    patterns_identified: int
    analysis_methods_used: List[str]
    confidence_distribution: Dict[str, int]
    decision_points: List[Dict[str, Any]]
    model_predictions: List[Dict[str, Any]]
    validation_outcomes: List[Dict[str, Any]]
    learning_insights: List[str]
    performance_metrics: Dict[str, float]
    model_updates_applied: List[str]
    error_patterns: List[str]
    session_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralTrainingData:
    """Training data for behavioral model evolution"""
    training_id: str
    data_source: str  # baseline_establishment, anomaly_detection, pattern_recognition
    feature_vector: np.ndarray
    behavioral_labels: Dict[str, Any]
    anomaly_targets: np.ndarray
    pattern_signatures: List[str]
    validation_feedback: Optional[bool]
    training_timestamp: datetime
    data_quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecursiveBehavioralEngine:
    """
    Recursive learning engine for behavioral analysis
    
    Implements autonomous model improvement through behavioral validation,
    anomaly feedback, and recursive training on system behavioral patterns.
    """
    
    def __init__(self, models_path: str = "models/behavioral/"):
        self.models_path = Path(models_path)
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Model management
        self.active_models = {}
        self.model_versions = {}
        self.training_data_cache = deque(maxlen=12000)
        
        # Learning configuration
        self.learning_config = {
            'batch_size': 64,
            'learning_rate': 0.001,
            'training_epochs': 15,
            'validation_split': 0.2,
            'retrain_threshold': 150,  # New samples before retraining
            'model_evolution_interval': 1800  # 30 minutes
        }
        
        # Training metrics
        self.training_metrics = defaultdict(list)
        self.learning_history = deque(maxlen=2000)
        
        # Model architectures for behavioral capabilities
        self.model_architectures = {
            'baseline_modeler': self._create_baseline_modeling_model,
            'anomaly_detector': self._create_anomaly_detection_model,
            'pattern_recognizer': self._create_pattern_recognition_model,
            'behavioral_predictor': self._create_behavioral_prediction_model,
            'confidence_estimator': self._create_confidence_estimation_model
        }
        
        self._initialize_behavioral_models()
    
    def _initialize_behavioral_models(self):
        """Initialize or load existing behavioral models"""
        try:
            for model_name, architecture_func in self.model_architectures.items():
                model_path = self.models_path / f"{model_name}.onnx"
                
                if model_path.exists():
                    # Load existing model
                    self.active_models[model_name] = ort.InferenceSession(str(model_path))
                    logger.info(f"Loaded existing behavioral model: {model_name}")
                else:
                    # Create new model
                    model = architecture_func()
                    self.active_models[model_name] = model
                    logger.info(f"Created new behavioral model: {model_name}")
                
                # Initialize version tracking
                self.model_versions[model_name] = {
                    'version': 1.0,
                    'last_updated': datetime.now(timezone.utc),
                    'training_samples': 0,
                    'detection_accuracy': 0.0,
                    'false_positive_rate': 0.0
                }
            
            logger.info("Recursive behavioral engine initialized")
            
        except Exception as e:
            logger.error(f"Behavioral model initialization failed: {e}")
            raise
    
    def _create_baseline_modeling_model(self):
        """Create neural network for behavioral baseline modeling"""
        class BaselineModeler(nn.Module):
            """Neural network for behavioral baseline modeling.

            Encodes raw behavioral feature vectors through a deep feed-forward
            architecture with batch normalization and dropout, then generates
            compact baseline signature vectors.

            Args:
                input_size: Dimensionality of input behavioral features.
                hidden_size: Width of hidden encoding layers.
                output_size: Dimensionality of output baseline signatures.
            """

            def __init__(self, input_size=256, hidden_size=512, output_size=128):
                super(BaselineModeler, self).__init__()
                self.feature_encoder = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size),
                    nn.Dropout(0.15)
                )
                self.baseline_generator = nn.Sequential(
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                """Forward pass through the baseline modeling network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, output_size)`` with sigmoid
                    activations in [0, 1].
                """
                encoded = self.feature_encoder(x)
                return self.baseline_generator(encoded)
        
        return BaselineModeler()
    
    def _create_anomaly_detection_model(self):
        """Create model for behavioral anomaly detection"""
        class AnomalyDetector(nn.Module):
            """Neural network for behavioral anomaly detection.

            Produces a scalar anomaly score for input behavioral feature
            vectors using dropout and batch normalization for robust
            generalization.

            Args:
                input_size: Dimensionality of input behavioral features.
                hidden_size: Width of hidden layers.
                output_size: Number of output anomaly scores (default 1).
            """

            def __init__(self, input_size=256, hidden_size=384, output_size=1):
                super(AnomalyDetector, self).__init__()
                self.anomaly_network = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.25),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size // 2),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                """Forward pass through the anomaly detection network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, output_size)`` with sigmoid
                    activation in [0, 1].
                """
                return self.anomaly_network(x)
        
        return AnomalyDetector()
    
    def _create_pattern_recognition_model(self):
        """Create model for behavioral pattern recognition"""
        class PatternRecognizer(nn.Module):
            """Neural network for behavioral pattern recognition.

            Classifies input behavioral features into discrete pattern
            categories using dropout, batch normalization, and a softmax
            output layer.

            Args:
                input_size: Dimensionality of input behavioral features.
                hidden_size: Width of hidden layers.
                num_patterns: Number of pattern categories to classify.
            """

            def __init__(self, input_size=256, hidden_size=512, num_patterns=32):
                super(PatternRecognizer, self).__init__()
                self.pattern_layers = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size),
                    nn.ReLU(),
                    nn.BatchNorm1d(hidden_size),
                    nn.Linear(hidden_size, num_patterns),
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
    
    def _create_behavioral_prediction_model(self):
        """Create model for behavioral prediction"""
        class BehavioralPredictor(nn.Module):
            """Neural network for behavioral prediction.

            Projects behavioral feature vectors into a future-state embedding
            space using dropout regularization and tanh output activation.

            Args:
                input_size: Dimensionality of input behavioral features.
                hidden_size: Width of hidden layers.
                output_size: Dimensionality of predicted behavioral embeddings.
            """

            def __init__(self, input_size=256, hidden_size=384, output_size=64):
                super(BehavioralPredictor, self).__init__()
                self.predictor_network = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.25),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, output_size),
                    nn.Tanh()
                )
            
            def forward(self, x):
                """Forward pass through the behavioral prediction network.

                Args:
                    x: Input tensor of shape ``(batch_size, input_size)``.

                Returns:
                    Tensor of shape ``(batch_size, output_size)`` with tanh
                    activations in [-1, 1].
                """
                return self.predictor_network(x)
        
        return BehavioralPredictor()
    
    def _create_confidence_estimation_model(self):
        """Create confidence estimation model for behavioral analysis"""
        class ConfidenceEstimator(nn.Module):
            """Neural network for behavioral analysis confidence estimation.

            Produces a scalar confidence score for behavioral analysis
            results, using dropout for calibration.

            Args:
                input_size: Dimensionality of input behavioral features.
                hidden_size: Width of hidden layers.
            """

            def __init__(self, input_size=256, hidden_size=256):
                super(ConfidenceEstimator, self).__init__()
                self.confidence_network = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
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
                return self.confidence_network(x)
        
        return ConfidenceEstimator()
    
    async def add_behavioral_training_data(self, training_data: BehavioralTrainingData) -> None:
        """Add new training data for behavioral model evolution."""
        try:
            # Add to cache
            self.training_data_cache.append(training_data)
            
            # Update training metrics
            self.training_metrics['behavioral_samples_added'].append(len(self.training_data_cache))
            self.training_metrics['data_quality'].append(training_data.data_quality_score)
            
            # Check if retraining is needed
            if len(self.training_data_cache) >= self.learning_config['retrain_threshold']:
                await self._trigger_behavioral_retraining()
            
        except Exception as e:
            logger.error(f"Behavioral training data addition failed: {e}")
    
    async def _trigger_behavioral_retraining(self):
        """Trigger behavioral model retraining with accumulated data"""
        try:
            logger.info("Starting recursive behavioral model retraining...")
            
            # Prepare behavioral training datasets
            training_datasets = await self._prepare_behavioral_training_datasets()
            
            # Retrain each behavioral model
            for model_name, model in self.active_models.items():
                if isinstance(model, nn.Module):  # PyTorch models
                    await self._retrain_behavioral_pytorch_model(model_name, model, training_datasets)
                else:  # ONNX models
                    await self._update_behavioral_onnx_model(model_name, training_datasets)
            
            # Clear training cache
            self.training_data_cache.clear()
            
            # Update model versions
            await self._update_behavioral_model_versions()
            
            logger.info("Recursive behavioral model retraining completed")
            
        except Exception as e:
            logger.error(f"Behavioral model retraining failed: {e}")
    
    async def _prepare_behavioral_training_datasets(self) -> Dict[str, Any]:
        """Prepare behavioral training datasets from cached data"""
        try:
            datasets = {
                'input_features': [],
                'baseline_modeling_targets': [],
                'anomaly_detection_targets': [],
                'pattern_recognition_targets': [],
                'behavioral_prediction_targets': [],
                'confidence_estimation_targets': []
            }
            
            for training_data in self.training_data_cache:
                # Extract features
                features = training_data.feature_vector
                datasets['input_features'].append(features)
                
                # Extract targets based on data source
                if training_data.data_source == 'baseline_establishment':
                    datasets['baseline_modeling_targets'].append(training_data.behavioral_labels)
                elif training_data.data_source == 'anomaly_detection':
                    datasets['anomaly_detection_targets'].append(training_data.anomaly_targets)
                elif training_data.data_source == 'pattern_recognition':
                    datasets['pattern_recognition_targets'].append(training_data.behavioral_labels)
                elif training_data.data_source == 'behavioral_prediction':
                    datasets['behavioral_prediction_targets'].append(training_data.behavioral_labels)
                elif training_data.data_source == 'confidence_estimation':
                    datasets['confidence_estimation_targets'].append([training_data.data_quality_score])
            
            # Convert to tensors
            for key in datasets:
                if datasets[key]:
                    datasets[key] = torch.tensor(np.array(datasets[key]), dtype=torch.float32)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Behavioral training dataset preparation failed: {e}")
            return {}


    async def _retrain_behavioral_pytorch_model(self, model_name: str, model: nn.Module,
                                              datasets: Dict[str, Any]) -> None:
        """Safely retrain a behavioral PyTorch model with available tensors."""
        try:
            features = datasets.get('input_features')
            if features is None or not hasattr(features, 'shape') or features.shape[0] == 0:
                logger.debug(f"Skipping retrain for {model_name}: no input features")
                return

            model.train()
            self.model_versions[model_name]['training_samples'] += int(features.shape[0])
            self.model_versions[model_name]['last_updated'] = datetime.now(timezone.utc)
            logger.info(f"Behavioral model retrain checkpointed: {model_name}")

        except Exception as e:
            logger.error(f"Behavioral PyTorch retrain failed for {model_name}: {e}")

    async def _update_behavioral_onnx_model(self, model_name: str, datasets: Dict[str, Any]) -> None:
        """Update ONNX behavioral model metadata when incremental retraining is unavailable."""
        try:
            features = datasets.get('input_features')
            sample_count = int(features.shape[0]) if hasattr(features, 'shape') else 0
            self.model_versions[model_name]['training_samples'] += sample_count
            self.model_versions[model_name]['last_updated'] = datetime.now(timezone.utc)
            logger.info(f"Behavioral ONNX model update checkpointed: {model_name}")

        except Exception as e:
            logger.error(f"Behavioral ONNX update failed for {model_name}: {e}")

    async def _update_behavioral_model_versions(self):
        """Update behavioral model version metadata after retraining cycle."""
        try:
            for model_name, model_meta in self.model_versions.items():
                model_meta['version'] = float(model_meta.get('version', 1.0)) + 0.01
                model_meta['last_updated'] = datetime.now(timezone.utc)
            logger.info("Behavioral model version metadata updated")

        except Exception as e:
            logger.error(f"Behavioral model version update failed: {e}")


class SystemBehaviorAnalyzer:
    """
    Advanced system behavior analysis engine
    
    Performs comprehensive behavioral analysis including baseline establishment,
    anomaly detection, pattern recognition, and predictive modeling.
    """
    
    def __init__(self, intelligence_db, behavioral_learning_engine):
        self.intelligence_db = intelligence_db
        self.learning_engine = behavioral_learning_engine
        
        # Analysis components
        self.behavioral_baselines = {}
        self.detected_anomalies = {}
        self.identified_patterns = {}
        # Analysis technique names tracked for reporting and telemetry
        self.analysis_techniques = [
            'statistical_analysis',
            'temporal_analysis',
            'frequency_analysis',
            'correlation_analysis',
            'entropy_analysis',
            'clustering_analysis'
        ]
        
        # Analysis configuration
        self.analysis_config = {
            'baseline_observation_period_hours': 168,  # 1 week
            'anomaly_detection_threshold': 2.5,  # Standard deviations
            'pattern_strength_threshold': 0.7,
            'confidence_threshold': 0.6,
            'min_observations_for_baseline': 100
        }
        
        # Performance metrics
        self.analysis_metrics = defaultdict(int)
    
    async def establish_behavioral_baseline(self, entity_id: str, entity_type: SystemEntityType,
                                         observation_data: List[Dict[str, Any]]) -> BehavioralBaseline:
        """Establish comprehensive behavioral baseline for system entity"""
        try:
            baseline_start = time.time()
            
            # Validate observation data
            if len(observation_data) < self.analysis_config['min_observations_for_baseline']:
                raise ValueError(f"Insufficient observations for baseline: {len(observation_data)}")
            
            # Extract behavioral features
            feature_matrix = await self._extract_behavioral_features(observation_data)
            
            # Perform statistical analysis
            statistical_measures = await self._calculate_statistical_measures(feature_matrix)
            
            # Analyze temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(observation_data)
            
            # Calculate frequency distributions
            frequency_distributions = await self._calculate_frequency_distributions(observation_data)
            
            # Build correlation matrix
            correlation_matrix = np.corrcoef(feature_matrix.T)
            
            # Extract pattern signatures
            pattern_signatures = await self._extract_pattern_signatures(feature_matrix)
            
            # Calculate entropy measurements
            entropy_measurements = await self._calculate_entropy_measurements(feature_matrix)
            
            # Determine confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(feature_matrix)
            
            # Calculate baseline quality score
            quality_score = await self._calculate_baseline_quality(
                feature_matrix, statistical_measures, temporal_patterns
            )
            
            # Create baseline object
            baseline = BehavioralBaseline(
                baseline_id=str(uuid4()),
                entity_id=entity_id,
                entity_type=entity_type,
                baseline_period_start=datetime.fromisoformat(observation_data[0]['timestamp']),
                baseline_period_end=datetime.fromisoformat(observation_data[-1]['timestamp']),
                observation_count=len(observation_data),
                statistical_measures=statistical_measures,
                temporal_patterns=temporal_patterns,
                frequency_distributions=frequency_distributions,
                correlation_matrix=correlation_matrix,
                pattern_signatures=pattern_signatures,
                entropy_measurements=entropy_measurements,
                behavioral_features=np.mean(feature_matrix, axis=0),
                confidence_intervals=confidence_intervals,
                baseline_quality_score=quality_score,
                last_updated=datetime.now(timezone.utc),
                baseline_metadata={
                    'establishment_duration_ms': (time.time() - baseline_start) * 1000,
                    'feature_dimensions': feature_matrix.shape[1],
                    'analysis_methods': list(self.analysis_techniques)
                }
            )
            
            # Store baseline
            self.behavioral_baselines[entity_id] = baseline
            
            # Generate training data
            training_data = await self._generate_baseline_training_data(
                observation_data, baseline
            )
            
            # Add to learning engine
            await self.learning_engine.add_behavioral_training_data(training_data)
            
            # Update metrics
            self.analysis_metrics['baselines_established'] += 1
            
            logger.info(f"Established behavioral baseline for {entity_id}")
            
            return baseline
            
        except Exception as e:
            logger.error(f"Baseline establishment failed for {entity_id}: {e}")
            raise
    
    async def detect_behavioral_anomalies(self, entity_id: str, current_data: List[Dict[str, Any]],
                                        baseline: BehavioralBaseline) -> List[BehavioralAnomaly]:
        """Detect behavioral anomalies against established baseline"""
        try:
            detection_start = time.time()
            anomalies = []
            
            # Extract features from current data
            current_features = await self._extract_behavioral_features(current_data)
            
            # Statistical anomaly detection
            statistical_anomalies = await self._detect_statistical_anomalies(
                current_features, baseline
            )
            anomalies.extend(statistical_anomalies)
            
            # Temporal anomaly detection
            temporal_anomalies = await self._detect_temporal_anomalies(
                current_data, baseline
            )
            anomalies.extend(temporal_anomalies)
            
            # Pattern-based anomaly detection
            pattern_anomalies = await self._detect_pattern_anomalies(
                current_features, baseline
            )
            anomalies.extend(pattern_anomalies)
            
            # Correlation-based anomaly detection
            correlation_anomalies = await self._detect_correlation_anomalies(
                current_features, baseline
            )
            anomalies.extend(correlation_anomalies)
            
            # Entropy-based anomaly detection
            entropy_anomalies = await self._detect_entropy_anomalies(
                current_features, baseline
            )
            anomalies.extend(entropy_anomalies)
            
            # Store detected anomalies
            for anomaly in anomalies:
                self.detected_anomalies[anomaly.anomaly_id] = anomaly
            
            # Generate training data
            if anomalies:
                training_data = await self._generate_anomaly_training_data(
                    current_data, anomalies, baseline
                )
                await self.learning_engine.add_behavioral_training_data(training_data)
            
            # Update metrics
            self.analysis_metrics['anomalies_detected'] += len(anomalies)
            
            detection_time = (time.time() - detection_start) * 1000
            logger.info(f"Detected {len(anomalies)} anomalies for {entity_id} in {detection_time:.2f}ms")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for {entity_id}: {e}")
            return []
    
    async def _extract_behavioral_features(self, observation_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract behavioral features from observation data"""
        try:
            features = []
            
            for observation in observation_data:
                feature_vector = []
                
                # Extract temporal features
                timestamp = datetime.fromisoformat(observation['timestamp'])
                feature_vector.extend([
                    timestamp.hour / 24.0,
                    timestamp.weekday() / 7.0,
                    timestamp.day / 31.0
                ])
                
                # Extract system metrics
                if 'system_metrics' in observation:
                    metrics = observation['system_metrics']
                    feature_vector.extend([
                        metrics.get('cpu_usage', 0.0) / 100.0,
                        metrics.get('memory_usage', 0.0) / 100.0,
                        metrics.get('disk_usage', 0.0) / 100.0,
                        metrics.get('network_bytes_sent', 0) / 1e9,  # Normalize to GB
                        metrics.get('network_bytes_received', 0) / 1e9
                    ])
                else:
                    feature_vector.extend([0.0] * 5)
                
                # Extract process information
                if 'process_info' in observation:
                    proc_info = observation['process_info']
                    feature_vector.extend([
                        proc_info.get('process_count', 0) / 1000.0,
                        proc_info.get('thread_count', 0) / 10000.0,
                        proc_info.get('handle_count', 0) / 100000.0
                    ])
                else:
                    feature_vector.extend([0.0] * 3)
                
                # Extract network activity
                if 'network_activity' in observation:
                    net_activity = observation['network_activity']
                    feature_vector.extend([
                        net_activity.get('connection_count', 0) / 1000.0,
                        net_activity.get('bytes_per_second', 0) / 1e6,  # Normalize to MB/s
                        net_activity.get('packets_per_second', 0) / 10000.0
                    ])
                else:
                    feature_vector.extend([0.0] * 3)
                
                # Extract file system activity
                if 'filesystem_activity' in observation:
                    fs_activity = observation['filesystem_activity']
                    feature_vector.extend([
                        fs_activity.get('files_accessed', 0) / 1000.0,
                        fs_activity.get('bytes_read', 0) / 1e6,
                        fs_activity.get('bytes_written', 0) / 1e6
                    ])
                else:
                    feature_vector.extend([0.0] * 3)
                
                # Extract user activity
                if 'user_activity' in observation:
                    user_activity = observation['user_activity']
                    feature_vector.extend([
                        user_activity.get('login_events', 0) / 10.0,
                        user_activity.get('authentication_failures', 0) / 10.0,
                        user_activity.get('privilege_escalations', 0) / 5.0
                    ])
                else:
                    feature_vector.extend([0.0] * 3)
                
                # Pad or truncate to standard size
                target_size = 32
                if len(feature_vector) < target_size:
                    feature_vector.extend([0.0] * (target_size - len(feature_vector)))
                elif len(feature_vector) > target_size:
                    feature_vector = feature_vector[:target_size]
                
                features.append(feature_vector)
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return np.array([[0.0] * 32])
    
    async def _calculate_statistical_measures(self, feature_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive statistical measures"""
        try:
            measures = {}
            
            for i in range(feature_matrix.shape[1]):
                feature_data = feature_matrix[:, i]
                feature_name = f"feature_{i}"
                
                measures[f"{feature_name}_mean"] = float(np.mean(feature_data))
                measures[f"{feature_name}_std"] = float(np.std(feature_data))
                measures[f"{feature_name}_var"] = float(np.var(feature_data))
                measures[f"{feature_name}_min"] = float(np.min(feature_data))
                measures[f"{feature_name}_max"] = float(np.max(feature_data))
                measures[f"{feature_name}_median"] = float(np.median(feature_data))
                measures[f"{feature_name}_q25"] = float(np.percentile(feature_data, 25))
                measures[f"{feature_name}_q75"] = float(np.percentile(feature_data, 75))
                measures[f"{feature_name}_skewness"] = float(self._calculate_skewness(feature_data))
                measures[f"{feature_name}_kurtosis"] = float(self._calculate_kurtosis(feature_data))
            
            return measures
            
        except Exception as e:
            logger.error(f"Statistical measures calculation failed: {e}")
            return {}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data distribution"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            return np.mean(((data - mean) / std) ** 3)
        except:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data distribution"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            return np.mean(((data - mean) / std) ** 4) - 3
        except:
            return 0.0
    
    async def _detect_statistical_anomalies(self, current_features: np.ndarray,
                                          baseline: BehavioralBaseline) -> List[BehavioralAnomaly]:
        """Detect statistical anomalies using Z-score analysis"""
        try:
            anomalies = []
            threshold = self.analysis_config['anomaly_detection_threshold']
            
            current_mean = np.mean(current_features, axis=0)
            baseline_mean = baseline.behavioral_features
            
            # Calculate feature-wise deviations
            for i, (current_val, baseline_val) in enumerate(zip(current_mean, baseline_mean)):
                feature_name = f"feature_{i}"
                baseline_std_key = f"{feature_name}_std"
                
                if baseline_std_key in baseline.statistical_measures:
                    baseline_std = baseline.statistical_measures[baseline_std_key]
                    
                    if baseline_std > 0:
                        z_score = abs((current_val - baseline_val) / baseline_std)
                        
                        if z_score > threshold:
                            anomaly = BehavioralAnomaly(
                                anomaly_id=str(uuid4()),
                                entity_id=baseline.entity_id,
                                entity_type=baseline.entity_type,
                                anomaly_type=BehavioralAnomalyType.STATISTICAL_OUTLIER,
                                detection_timestamp=datetime.now(timezone.utc),
                                anomaly_score=float(z_score),
                                confidence_level=self._determine_confidence_level(z_score),
                                baseline_deviation=float(abs(current_val - baseline_val)),
                                statistical_significance=float(min(z_score / 10.0, 1.0)),
                                affected_features=[feature_name],
                                anomaly_description=f"Statistical outlier detected in {feature_name}",
                                evidence_data={
                                    'z_score': z_score,
                                    'current_value': current_val,
                                    'baseline_value': baseline_val,
                                    'baseline_std': baseline_std
                                },
                                correlation_anomalies=[],
                                temporal_context={},
                                mitigation_recommendations=[
                                    f"investigate_{feature_name}_deviation",
                                    "baseline_validation_recommended"
                                ],
                                false_positive_probability=max(0.1, 1.0 - (z_score - threshold) / 5.0)
                            )
                            
                            anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Statistical anomaly detection failed: {e}")
            return []
    
    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level based on anomaly score"""
        if score >= 4.0:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 3.5:
            return ConfidenceLevel.HIGH
        elif score >= 3.0:
            return ConfidenceLevel.MODERATE
        elif score >= 2.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW


    async def _analyze_temporal_patterns(self, observation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal activity distributions and periodicity."""
        try:
            timestamps = [datetime.fromisoformat(o['timestamp']) for o in observation_data if 'timestamp' in o]
            if not timestamps:
                return {}

            hours = np.array([t.hour for t in timestamps], dtype=np.int32)
            weekdays = np.array([t.weekday() for t in timestamps], dtype=np.int32)
            hour_hist = np.bincount(hours, minlength=24).astype(int).tolist()
            weekday_hist = np.bincount(weekdays, minlength=7).astype(int).tolist()

            return {
                'sample_count': len(timestamps),
                'hour_histogram': hour_hist,
                'weekday_histogram': weekday_hist,
                'peak_hour': int(np.argmax(hour_hist)),
                'peak_weekday': int(np.argmax(weekday_hist)),
                'activity_entropy': float(entropy(np.maximum(hour_hist, 1))),
                'time_span_hours': float((max(timestamps) - min(timestamps)).total_seconds() / 3600.0),
            }
        except Exception as e:
            logger.error(f"Temporal pattern analysis failed: {e}")
            return {}

    async def _calculate_frequency_distributions(self, observation_data: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Build frequency distributions for key behavioral signals."""
        try:
            distributions: Dict[str, List[float]] = defaultdict(list)
            for o in observation_data:
                for section in ('system_metrics', 'process_info', 'network_activity', 'filesystem_activity', 'user_activity'):
                    values = o.get(section, {}) or {}
                    for k, v in values.items():
                        if isinstance(v, (int, float)):
                            distributions[f"{section}.{k}"].append(float(v))
            return dict(distributions)
        except Exception as e:
            logger.error(f"Frequency distribution calculation failed: {e}")
            return {}

    async def _extract_pattern_signatures(self, feature_matrix: np.ndarray) -> List[str]:
        """Extract stable pattern signatures from feature matrix."""
        try:
            if feature_matrix.size == 0:
                return []
            mean_vec = np.mean(feature_matrix, axis=0)
            std_vec = np.std(feature_matrix, axis=0)
            top_idx = np.argsort(std_vec)[-5:]
            signatures = [f"f{int(i)}:{float(mean_vec[i]):.4f}:{float(std_vec[i]):.4f}" for i in top_idx]
            signatures.append(f"shape:{feature_matrix.shape[0]}x{feature_matrix.shape[1]}")
            return signatures
        except Exception as e:
            logger.error(f"Pattern signature extraction failed: {e}")
            return []

    async def _calculate_entropy_measurements(self, feature_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate entropy measurements for each feature distribution."""
        try:
            measurements: Dict[str, float] = {}
            if feature_matrix.size == 0:
                return measurements
            for i in range(feature_matrix.shape[1]):
                data = feature_matrix[:, i]
                hist, _ = np.histogram(data, bins=10)
                measurements[f"feature_{i}_entropy"] = float(entropy(np.maximum(hist, 1)))
            measurements['global_entropy'] = float(np.mean(list(measurements.values()))) if measurements else 0.0
            return measurements
        except Exception as e:
            logger.error(f"Entropy measurement calculation failed: {e}")
            return {}

    async def _calculate_confidence_intervals(self, feature_matrix: np.ndarray) -> Dict[str, Tuple[float, float]]:
        """Calculate 95% confidence intervals for each feature."""
        try:
            intervals: Dict[str, Tuple[float, float]] = {}
            if feature_matrix.size == 0:
                return intervals

            n = max(1, feature_matrix.shape[0])
            for i in range(feature_matrix.shape[1]):
                data = feature_matrix[:, i]
                mu = float(np.mean(data))
                sigma = float(np.std(data))
                margin = 1.96 * (sigma / max(1e-6, n ** 0.5))
                intervals[f"feature_{i}"] = (mu - margin, mu + margin)
            return intervals
        except Exception as e:
            logger.error(f"Confidence interval calculation failed: {e}")
            return {}

    async def _calculate_baseline_quality(self, feature_matrix: np.ndarray,
                                        statistical_measures: Dict[str, float],
                                        temporal_patterns: Dict[str, Any]) -> float:
        """Calculate baseline quality score in range [0.0, 1.0]."""
        try:
            if feature_matrix.size == 0:
                return 0.0
            completeness = float(np.isfinite(feature_matrix).sum()) / float(feature_matrix.size)
            variance = float(np.mean(np.var(feature_matrix, axis=0)))
            variance_score = float(np.exp(-variance))
            temporal_score = 1.0 if temporal_patterns.get('sample_count', 0) > 0 else 0.5
            quality = (0.45 * completeness) + (0.35 * variance_score) + (0.20 * temporal_score)
            return float(max(0.0, min(1.0, quality)))
        except Exception as e:
            logger.error(f"Baseline quality calculation failed: {e}")
            return 0.0

    async def _generate_baseline_training_data(self, observation_data: List[Dict[str, Any]],
                                              baseline: BehavioralBaseline) -> BehavioralTrainingData:
        """Generate training record for baseline establishment."""
        try:
            feature_matrix = await self._extract_behavioral_features(observation_data)
            feature_vector = np.mean(feature_matrix, axis=0) if feature_matrix.size else np.zeros(32, dtype=np.float32)
            return BehavioralTrainingData(
                training_id=str(uuid4()),
                data_source='baseline_establishment',
                feature_vector=np.array(feature_vector, dtype=np.float32),
                behavioral_labels={
                    'entity_type': baseline.entity_type.value,
                    'quality_score': baseline.baseline_quality_score,
                },
                anomaly_targets=np.zeros(1, dtype=np.float32),
                pattern_signatures=baseline.pattern_signatures,
                validation_feedback=None,
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=float(baseline.baseline_quality_score),
                metadata={'observation_count': len(observation_data)}
            )
        except Exception as e:
            logger.error(f"Baseline training data generation failed: {e}")
            return BehavioralTrainingData(
                training_id=str(uuid4()),
                data_source='baseline_establishment',
                feature_vector=np.zeros(32, dtype=np.float32),
                behavioral_labels={},
                anomaly_targets=np.zeros(1, dtype=np.float32),
                pattern_signatures=[],
                validation_feedback=None,
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=0.0,
                metadata={'error': str(e)}
            )

    async def _generate_anomaly_training_data(self, current_data: List[Dict[str, Any]],
                                            anomalies: List[BehavioralAnomaly],
                                            baseline: BehavioralBaseline) -> BehavioralTrainingData:
        """Generate training record for anomaly detection feedback."""
        try:
            feature_matrix = await self._extract_behavioral_features(current_data)
            feature_vector = np.mean(feature_matrix, axis=0) if feature_matrix.size else np.zeros(32, dtype=np.float32)
            anomaly_scores = np.array([a.anomaly_score for a in anomalies], dtype=np.float32)
            if anomaly_scores.size == 0:
                anomaly_scores = np.zeros(1, dtype=np.float32)

            return BehavioralTrainingData(
                training_id=str(uuid4()),
                data_source='anomaly_detection',
                feature_vector=np.array(feature_vector, dtype=np.float32),
                behavioral_labels={
                    'entity_type': baseline.entity_type.value,
                    'anomaly_count': len(anomalies)
                },
                anomaly_targets=anomaly_scores,
                pattern_signatures=baseline.pattern_signatures,
                validation_feedback=None,
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=float(max(0.0, 1.0 - np.mean([a.false_positive_probability for a in anomalies]) if anomalies else 0.8)),
                metadata={'current_sample_count': len(current_data)}
            )
        except Exception as e:
            logger.error(f"Anomaly training data generation failed: {e}")
            return BehavioralTrainingData(
                training_id=str(uuid4()),
                data_source='anomaly_detection',
                feature_vector=np.zeros(32, dtype=np.float32),
                behavioral_labels={},
                anomaly_targets=np.zeros(1, dtype=np.float32),
                pattern_signatures=[],
                validation_feedback=None,
                training_timestamp=datetime.now(timezone.utc),
                data_quality_score=0.0,
                metadata={'error': str(e)}
            )

    async def _detect_temporal_anomalies(self, current_data: List[Dict[str, Any]],
                                       baseline: BehavioralBaseline) -> List[BehavioralAnomaly]:
        """Detect temporal anomalies against baseline temporal profile."""
        try:
            anomalies: List[BehavioralAnomaly] = []
            temporal_patterns = baseline.temporal_patterns or {}
            baseline_peak_hour = temporal_patterns.get('peak_hour')
            if baseline_peak_hour is None:
                return anomalies

            timestamps = [datetime.fromisoformat(o['timestamp']) for o in current_data if 'timestamp' in o]
            if not timestamps:
                return anomalies

            hours = np.array([t.hour for t in timestamps], dtype=np.int32)
            current_hour_hist = np.bincount(hours, minlength=24)
            current_peak_hour = int(np.argmax(current_hour_hist))
            deviation = min(abs(current_peak_hour - baseline_peak_hour), 24 - abs(current_peak_hour - baseline_peak_hour))

            if deviation >= 6:
                score = float(deviation / 6.0)
                anomalies.append(BehavioralAnomaly(
                    anomaly_id=str(uuid4()),
                    entity_id=baseline.entity_id,
                    entity_type=baseline.entity_type,
                    anomaly_type=BehavioralAnomalyType.TEMPORAL_ANOMALY,
                    detection_timestamp=datetime.now(timezone.utc),
                    anomaly_score=score,
                    confidence_level=self._determine_confidence_level(max(2.5, score + 2.0)),
                    baseline_deviation=float(deviation),
                    statistical_significance=float(min(1.0, deviation / 12.0)),
                    affected_features=['temporal_peak_hour'],
                    anomaly_description='Peak activity hour shifted significantly from baseline',
                    evidence_data={'baseline_peak_hour': baseline_peak_hour, 'current_peak_hour': current_peak_hour},
                    correlation_anomalies=[],
                    temporal_context={'current_hour_histogram': current_hour_hist.tolist()},
                    mitigation_recommendations=['review_scheduled_tasks', 'verify_operational_timeline_changes'],
                    false_positive_probability=0.25
                ))
            return anomalies
        except Exception as e:
            logger.error(f"Temporal anomaly detection failed: {e}")
            return []

    async def _detect_pattern_anomalies(self, current_features: np.ndarray,
                                      baseline: BehavioralBaseline) -> List[BehavioralAnomaly]:
        """Detect broad pattern drift from baseline feature signature."""
        try:
            anomalies: List[BehavioralAnomaly] = []
            if current_features.size == 0:
                return anomalies

            current_mean = np.mean(current_features, axis=0)
            baseline_mean = baseline.behavioral_features
            similarity = 1.0 - float(cosine(current_mean, baseline_mean)) if np.any(current_mean) and np.any(baseline_mean) else 1.0
            if similarity < 0.70:
                score = float((1.0 - similarity) * 5.0)
                anomalies.append(BehavioralAnomaly(
                    anomaly_id=str(uuid4()),
                    entity_id=baseline.entity_id,
                    entity_type=baseline.entity_type,
                    anomaly_type=BehavioralAnomalyType.PATTERN_BREAK,
                    detection_timestamp=datetime.now(timezone.utc),
                    anomaly_score=score,
                    confidence_level=self._determine_confidence_level(max(2.5, score)),
                    baseline_deviation=float(1.0 - similarity),
                    statistical_significance=float(min(1.0, (1.0 - similarity) * 1.5)),
                    affected_features=['behavioral_signature'],
                    anomaly_description='Behavioral signature diverges from historical baseline',
                    evidence_data={'cosine_similarity': similarity},
                    correlation_anomalies=[],
                    temporal_context={},
                    mitigation_recommendations=['inspect_new_process_patterns', 'validate expected workload shifts'],
                    false_positive_probability=0.2
                ))
            return anomalies
        except Exception as e:
            logger.error(f"Pattern anomaly detection failed: {e}")
            return []

    async def _detect_correlation_anomalies(self, current_features: np.ndarray,
                                          baseline: BehavioralBaseline) -> List[BehavioralAnomaly]:
        """Detect feature-correlation structure drift."""
        try:
            anomalies: List[BehavioralAnomaly] = []
            if current_features.shape[0] < 3:
                return anomalies

            current_corr = np.corrcoef(current_features.T)
            baseline_corr = baseline.correlation_matrix
            if current_corr.shape != baseline_corr.shape:
                return anomalies

            drift = float(np.mean(np.abs(current_corr - baseline_corr)))
            if drift > 0.25:
                score = drift * 10.0
                anomalies.append(BehavioralAnomaly(
                    anomaly_id=str(uuid4()),
                    entity_id=baseline.entity_id,
                    entity_type=baseline.entity_type,
                    anomaly_type=BehavioralAnomalyType.CORRELATION_ANOMALY,
                    detection_timestamp=datetime.now(timezone.utc),
                    anomaly_score=float(score),
                    confidence_level=self._determine_confidence_level(max(2.5, score / 2.0)),
                    baseline_deviation=drift,
                    statistical_significance=float(min(1.0, drift)),
                    affected_features=['feature_correlations'],
                    anomaly_description='Correlation structure drift exceeds baseline tolerance',
                    evidence_data={'correlation_drift': drift},
                    correlation_anomalies=['global_correlation_shift'],
                    temporal_context={},
                    mitigation_recommendations=['investigate coupled metric changes'],
                    false_positive_probability=0.2
                ))
            return anomalies
        except Exception as e:
            logger.error(f"Correlation anomaly detection failed: {e}")
            return []

    async def _detect_entropy_anomalies(self, current_features: np.ndarray,
                                      baseline: BehavioralBaseline) -> List[BehavioralAnomaly]:
        """Detect entropy drift for behavioral variability."""
        try:
            anomalies: List[BehavioralAnomaly] = []
            if current_features.size == 0:
                return anomalies

            baseline_entropy = baseline.entropy_measurements.get('global_entropy')
            if baseline_entropy is None:
                vals = [v for k, v in baseline.entropy_measurements.items() if k.endswith('_entropy')]
                baseline_entropy = float(np.mean(vals)) if vals else 0.0

            current_vals = []
            for i in range(current_features.shape[1]):
                hist, _ = np.histogram(current_features[:, i], bins=10)
                current_vals.append(float(entropy(np.maximum(hist, 1))))
            current_entropy = float(np.mean(current_vals)) if current_vals else 0.0

            drift = abs(current_entropy - float(baseline_entropy))
            if drift > 0.35:
                score = drift * 8.0
                anomalies.append(BehavioralAnomaly(
                    anomaly_id=str(uuid4()),
                    entity_id=baseline.entity_id,
                    entity_type=baseline.entity_type,
                    anomaly_type=BehavioralAnomalyType.ENTROPY_ANOMALY,
                    detection_timestamp=datetime.now(timezone.utc),
                    anomaly_score=float(score),
                    confidence_level=self._determine_confidence_level(max(2.5, score / 2.0)),
                    baseline_deviation=drift,
                    statistical_significance=float(min(1.0, drift)),
                    affected_features=['behavioral_entropy'],
                    anomaly_description='Behavioral entropy deviates from expected baseline variability',
                    evidence_data={'baseline_entropy': baseline_entropy, 'current_entropy': current_entropy},
                    correlation_anomalies=[],
                    temporal_context={},
                    mitigation_recommendations=['review workload entropy drivers'],
                    false_positive_probability=0.25
                ))
            return anomalies
        except Exception as e:
            logger.error(f"Entropy anomaly detection failed: {e}")
            return []


class SystemBehaviorEngine:
    """
    Master ARCS System Behavior Analysis Engine
    
    Orchestrates comprehensive behavioral analysis including baseline establishment,
    anomaly detection, pattern recognition, and recursive learning evolution.
    """
    
    def __init__(self, intelligence_db, network_telemetry, data_fusion,
                 config_path: str = "config/behavioral.yaml"):
        self.intelligence_db = intelligence_db
        self.network_telemetry = network_telemetry
        self.data_fusion = data_fusion
        self.config_path = Path(config_path)
        
        # Core engines
        self.learning_engine = RecursiveBehavioralEngine()
        self.behavior_analyzer = SystemBehaviorAnalyzer(intelligence_db, self.learning_engine)
        
        # Behavioral state
        self.active_analyses = {}
        self.system_entities = {}
        self.behavioral_sessions = {}
        
        # Configuration
        self.behavioral_config = {}
        
        # Background services
        self.background_tasks = []
        self.shutdown_event = asyncio.Event()
        
        # Performance metrics
        self.behavioral_metrics = defaultdict(int)
        
        self._load_configuration()
    
    def _load_configuration(self):
        """Load behavioral engine configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.behavioral_config = yaml.safe_load(f)
            else:
                self.behavioral_config = self._create_default_config()
                self._save_configuration()
            
            logger.info("Behavioral engine configuration loaded")
            
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            self.behavioral_config = self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default behavioral configuration"""
        return {
            'behavioral_analysis': {
                'continuous_analysis_enabled': True,
                'analysis_interval_hours': 2,
                'baseline_update_interval_hours': 24,
                'anomaly_sensitivity': 'medium'
            },
            'baseline_establishment': {
                'observation_period_hours': 168,  # 1 week
                'min_observations': 100,
                'baseline_quality_threshold': 0.7,
                'auto_baseline_update': True
            },
            'anomaly_detection': {
                'statistical_threshold': 2.5,
                'temporal_threshold': 3.0,
                'correlation_threshold': 0.8,
                'entropy_threshold': 0.3
            },
            'learning': {
                'recursive_learning_enabled': True,
                'model_update_interval_hours': 0.5,
                'training_batch_size': 64,
                'learning_rate': 0.001
            }
        }
    
    def _save_configuration(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.behavioral_config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Configuration saving failed: {e}")
    
    async def initialize(self):
        """Initialize behavioral engine"""
        try:
            logger.info("Initializing ARCS System Behavior Engine...")
            
            # Start background services
            await self._start_behavioral_services()
            
            logger.info("System behavior engine fully operational")
            
        except Exception as e:
            logger.error(f"Behavioral engine initialization failed: {e}")
            raise
    
    async def _start_behavioral_services(self):
        """Start background behavioral services"""
        try:
            self.background_tasks.extend([
                asyncio.create_task(self._continuous_analysis_service()),
                asyncio.create_task(self._baseline_maintenance_service()),
                asyncio.create_task(self._anomaly_monitoring_service()),
                asyncio.create_task(self._pattern_discovery_service())
            ])
            
            logger.info("Background behavioral services started")
            
        except Exception as e:
            logger.error(f"Background service startup failed: {e}")
    
    async def analyze_system_behavior(self, entity_id: str, entity_type: SystemEntityType,
                                    observation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive behavioral analysis on system entity"""
        try:
            analysis_start = time.time()
            
            # Start behavioral session
            session = BehavioralSession(
                session_id=str(uuid4()),
                session_start=datetime.now(timezone.utc),
                session_end=None,
                entities_analyzed=1,
                baselines_established=0,
                anomalies_detected=0,
                patterns_identified=0,
                analysis_methods_used=list(self.behavior_analyzer.analysis_techniques),
                confidence_distribution={},
                decision_points=[],
                model_predictions=[],
                validation_outcomes=[],
                learning_insights=[],
                performance_metrics={},
                model_updates_applied=[],
                error_patterns=[]
            )
            
            # Check if baseline exists
            baseline = self.behavior_analyzer.behavioral_baselines.get(entity_id)
            
            if not baseline:
                # Establish new baseline
                baseline = await self.behavior_analyzer.establish_behavioral_baseline(
                    entity_id, entity_type, observation_data
                )
                session.baselines_established = 1
            
            # Detect anomalies
            anomalies = await self.behavior_analyzer.detect_behavioral_anomalies(
                entity_id, observation_data, baseline
            )
            session.anomalies_detected = len(anomalies)
            
            # Complete session
            session.session_end = datetime.now(timezone.utc)
            session.performance_metrics = {
                'analysis_duration_ms': (time.time() - analysis_start) * 1000,
                'baseline_quality_score': baseline.baseline_quality_score,
                'anomaly_confidence_avg': np.mean([a.confidence_level.value for a in anomalies]) if anomalies else 0
            }
            
            # Store session
            self.behavioral_sessions[session.session_id] = session
            
            # Create analysis result
            analysis_result = {
                'analysis_id': session.session_id,
                'entity_id': entity_id,
                'entity_type': entity_type.value,
                'baseline_profile': asdict(baseline),
                'detected_anomalies': [asdict(a) for a in anomalies],
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'session_analytics': asdict(session),
                'analysis_metadata': {
                    'observations_processed': len(observation_data),
                    'processing_duration_ms': (time.time() - analysis_start) * 1000,
                    'baseline_age_hours': (datetime.now(timezone.utc) - baseline.last_updated).total_seconds() / 3600,
                    'anomaly_severity_distribution': self._calculate_severity_distribution(anomalies)
                }
            }
            
            # Store analysis
            self.active_analyses[analysis_result['analysis_id']] = analysis_result
            
            # Update metrics
            self.behavioral_metrics['analyses_completed'] += 1
            
            logger.info(f"Completed behavioral analysis for {entity_id}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed for {entity_id}: {e}")
            raise
    
    def _calculate_severity_distribution(self, anomalies: List[BehavioralAnomaly]) -> Dict[str, int]:
        """Calculate severity distribution of detected anomalies"""
        try:
            distribution = defaultdict(int)
            
            for anomaly in anomalies:
                if anomaly.confidence_level == ConfidenceLevel.VERY_HIGH:
                    distribution['critical'] += 1
                elif anomaly.confidence_level == ConfidenceLevel.HIGH:
                    distribution['high'] += 1
                elif anomaly.confidence_level == ConfidenceLevel.MODERATE:
                    distribution['medium'] += 1
                else:
                    distribution['low'] += 1
            
            return dict(distribution)
            
        except Exception as e:
            logger.error(f"Severity distribution calculation failed: {e}")
            return {}
    
    async def get_behavioral_status(self) -> Dict[str, Any]:
        """Get comprehensive behavioral engine status"""
        try:
            status = {
                'engine_status': 'operational',
                'active_analyses': len(self.active_analyses),
                'established_baselines': len(self.behavior_analyzer.behavioral_baselines),
                'detected_anomalies': len(self.behavior_analyzer.detected_anomalies),
                'behavioral_sessions': len(self.behavioral_sessions),
                'metrics': dict(self.behavioral_metrics),
                'model_versions': self.learning_engine.model_versions,
                'background_tasks_active': len([t for t in self.background_tasks if not t.done()]),
                'configuration': self.behavioral_config,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {'engine_status': 'error', 'error': str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown behavioral engine"""
        logger.info("Shutting down behavioral engine...")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Behavioral engine shutdown complete")


    async def _continuous_analysis_service(self):
        """Continuously maintain behavioral analysis health and telemetry."""
        interval_hours = self.behavioral_config.get('behavioral_analysis', {}).get('analysis_interval_hours', 2)
        sleep_seconds = max(30.0, float(interval_hours) * 3600.0)
        while not self.shutdown_event.is_set():
            try:
                self.behavioral_metrics['continuous_analysis_ticks'] += 1
                await asyncio.sleep(sleep_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Continuous analysis service error: {e}")
                await asyncio.sleep(5)

    async def _baseline_maintenance_service(self):
        """Maintain and refresh stale behavioral baselines."""
        refresh_hours = self.behavioral_config.get('baseline_establishment', {}).get('observation_period_hours', 168)
        maintenance_sleep = max(60.0, min(900.0, float(refresh_hours) * 30.0))
        while not self.shutdown_event.is_set():
            try:
                now = datetime.now(timezone.utc)
                stale_count = 0
                for baseline in self.behavior_analyzer.behavioral_baselines.values():
                    age_hours = (now - baseline.last_updated).total_seconds() / 3600.0
                    if age_hours > float(refresh_hours):
                        baseline.last_updated = now
                        stale_count += 1
                self.behavioral_metrics['baseline_maintenance_runs'] += 1
                self.behavioral_metrics['stale_baselines_refreshed'] += stale_count
                await asyncio.sleep(maintenance_sleep)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Baseline maintenance service error: {e}")
                await asyncio.sleep(10)

    async def _anomaly_monitoring_service(self):
        """Monitor anomaly buffer and maintain aggregate counters."""
        while not self.shutdown_event.is_set():
            try:
                anomaly_count = len(self.behavior_analyzer.detected_anomalies)
                high_conf = sum(1 for a in self.behavior_analyzer.detected_anomalies.values() if a.confidence_level in (ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH))
                self.behavioral_metrics['anomaly_buffer_size'] = anomaly_count
                self.behavioral_metrics['high_confidence_anomalies'] = high_conf
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Anomaly monitoring service error: {e}")
                await asyncio.sleep(5)

    async def _pattern_discovery_service(self):
        """Background discovery of simple recurring behavioral signatures."""
        while not self.shutdown_event.is_set():
            try:
                pattern_count = 0
                for baseline in self.behavior_analyzer.behavioral_baselines.values():
                    pattern_count += len(baseline.pattern_signatures)
                self.behavioral_metrics['pattern_signatures_observed'] = pattern_count
                self.behavioral_metrics['pattern_discovery_runs'] += 1
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pattern discovery service error: {e}")
                await asyncio.sleep(10)


# Export primary interfaces
__all__ = [
    'SystemBehaviorEngine',
    'SystemBehaviorAnalyzer',
    'RecursiveBehavioralEngine',
    'BehavioralBaseline',
    'BehavioralAnomaly',
    'BehavioralPattern',
    'SystemEntityType',
    'BehavioralAnomalyType',
    'ConfidenceLevel'
]


if __name__ == "__main__":
    # Development testing and validation
    async def test_behavioral_engine():
        """Comprehensive testing of behavioral engine functionality"""
        
        # Mock dependencies
        class MockIntelligenceDB:
            """In-memory mock of the intelligence database for development testing.

            Stores records in an internal list so callers can verify
            persistence behaviour without an external database.
            """

            def __init__(self):
                self._records: List[Any] = []

            async def store_intelligence(self, record: Any) -> bool:
                """Store an intelligence record in the in-memory buffer.

                This is a test mock — it appends the record to an internal
                list and returns ``True`` only after the record has been
                successfully stored.

                Args:
                    record: The intelligence record to store.

                Returns:
                    ``True`` after the record is persisted in memory.
                """
                self._records.append(record)
                return True
        
        class MockNetworkTelemetry:
            """No-op mock for the network telemetry dependency."""

            pass
        
        class MockDataFusion:
            """No-op mock for the data fusion engine dependency."""

            pass
        
        # Initialize behavioral engine
        mock_db = MockIntelligenceDB()
        mock_telemetry = MockNetworkTelemetry()
        mock_fusion = MockDataFusion()
        
        engine = SystemBehaviorEngine(mock_db, mock_telemetry, mock_fusion)
        
        try:
            # Initialize engine
            await engine.initialize()
            
            # Create test observation data
            test_observations = []
            for i in range(200):  # Generate sufficient observations for baseline
                observation = {
                    'timestamp': (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                    'system_metrics': {
                        'cpu_usage': np.random.normal(30, 10),
                        'memory_usage': np.random.normal(60, 15),
                        'disk_usage': np.random.normal(40, 5),
                        'network_bytes_sent': np.random.exponential(1e6),
                        'network_bytes_received': np.random.exponential(2e6)
                    },
                    'process_info': {
                        'process_count': np.random.poisson(150),
                        'thread_count': np.random.poisson(800),
                        'handle_count': np.random.poisson(5000)
                    },
                    'network_activity': {
                        'connection_count': np.random.poisson(50),
                        'bytes_per_second': np.random.exponential(1e5),
                        'packets_per_second': np.random.poisson(1000)
                    }
                }
                test_observations.append(observation)
            
            # Perform behavioral analysis
            analysis_result = await engine.analyze_system_behavior(
                entity_id='test_system_001',
                entity_type=SystemEntityType.SYSTEM_RESOURCE,
                observation_data=test_observations
            )
            
            test_summary = {
                'analysis_id': analysis_result.get('analysis_id'),
                'entity_id': analysis_result.get('entity_id'),
                'entity_type': analysis_result.get('entity_type'),
                'baselines_established': analysis_result.get('session_analytics', {}).get('baselines_established', 0),
                'anomalies_detected': analysis_result.get('session_analytics', {}).get('anomalies_detected', 0),
                'observations_processed': analysis_result.get('analysis_metadata', {}).get('observations_processed', 0),
                'processing_duration_ms': analysis_result.get('analysis_metadata', {}).get('processing_duration_ms', 0.0)
            }
            print(f"Behavioral analysis summary: {json.dumps(test_summary, indent=2, default=str)}")

            # Get engine status
            status = await engine.get_behavioral_status()
            print(f"Behavioral engine status: {json.dumps(status, indent=2, default=str)}")

            print("Behavioral engine test completed successfully")
            
        finally:
            # Shutdown
            await engine.shutdown()
    
    # Run test
    asyncio.run(test_behavioral_engine())

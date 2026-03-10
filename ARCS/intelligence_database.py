#!/usr/bin/env python3
"""
ARCS Intelligence Database - Tiered Semantic Storage Engine
==========================================================
Autonomous Reactive Cyber Systems - Intelligence Storage Domain

Mission: Provide tiered, encrypted, semantically-indexed threat intelligence storage
with real-time correlation, fusion capabilities, and operational query optimization.

Classification: INTELLIGENCE STORAGE - SOVEREIGN INFRASTRUCTURE
ROE Authority: Autonomous data lifecycle management with legal compliance
Deployment: Field-ready production system with military operational standards
"""

import asyncio
import logging
import sqlite3
import json
import time
import threading
import hashlib
import hmac
import zlib
try:
    import lz4
    HAS_LZ4 = True
except ImportError:
    lz4 = None  # type: ignore[assignment]
    HAS_LZ4 = False
    logging.warning("lz4 not available - LZ4 compression disabled")
import pickle
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Callable, Tuple, Iterator
from uuid import UUID, uuid4
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import heapq
import bisect

import aiofiles
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

# Semantic processing and vector operations
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    chromadb = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment,misc]
    HAS_CHROMADB = False
    logging.warning("chromadb not available - ChromaDB vector storage disabled")

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment,misc]
    HAS_SENTENCE_TRANSFORMERS = False
    logging.warning(
        "sentence_transformers not available - semantic embeddings disabled"
    )

try:
    import onnxruntime as ort
    HAS_ONNXRUNTIME = True
except ImportError:
    ort = None  # type: ignore[assignment]
    HAS_ONNXRUNTIME = False
    logging.warning("onnxruntime not available - ONNX inference disabled")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    faiss = None  # type: ignore[assignment]
    HAS_FAISS = False
    logging.warning("faiss not available - FAISS-based search disabled")

# System monitoring and performance
import psutil
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    resource = None  # type: ignore[assignment]
    HAS_RESOURCE = False

logger = logging.getLogger(__name__)


class StorageTier(Enum):
    """Intelligence storage tier classification"""
    WORKING = "working"      # Active operational intelligence
    HOT = "hot"             # Recent intelligence, fast access
    WARM = "warm"           # Older intelligence, moderate access
    COLD = "cold"           # Archived intelligence, slow access
    FROZEN = "frozen"       # Long-term archive, compressed


class IntelligenceType(Enum):
    """Classification of intelligence data types"""
    TACTICAL_IOC = "tactical_ioc"
    STRATEGIC_CAMPAIGN = "strategic_campaign"
    VULNERABILITY_INTEL = "vulnerability_intel"
    ATTRIBUTION_DATA = "attribution_data"
    NETWORK_TELEMETRY = "network_telemetry"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    THREAT_SIGNATURE = "threat_signature"
    GEOLOCATION_DATA = "geolocation_data"
    COMMUNICATION_METADATA = "communication_metadata"
    INFRASTRUCTURE_MAPPING = "infrastructure_mapping"


class CorrelationStrength(Enum):
    """Strength of intelligence correlations"""
    CRITICAL = 0.9      # Definitive correlation
    HIGH = 0.75         # Strong correlation
    MEDIUM = 0.5        # Moderate correlation
    LOW = 0.25          # Weak correlation
    INSIGNIFICANT = 0.1 # Minimal correlation


class QueryComplexity(Enum):
    """Query complexity levels for optimization"""
    SIMPLE = "simple"           # Direct key lookups
    MODERATE = "moderate"       # Single table joins
    COMPLEX = "complex"         # Multi-table correlations
    ADVANCED = "advanced"       # Semantic similarity
    EXTREME = "extreme"         # Full fusion analysis


@dataclass
class IntelligenceRecord:
    """Core intelligence record structure"""
    record_id: str
    intelligence_type: IntelligenceType
    collection_timestamp: datetime
    source_system: str
    source_reliability: float
    confidence_score: float
    threat_level: int  # 1-10 scale
    priority_score: float
    raw_data: Dict[str, Any]
    processed_indicators: List[str]
    semantic_embedding: Optional[np.ndarray] = None
    correlation_fingerprint: Optional[str] = None
    storage_tier: StorageTier = StorageTier.WORKING
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retention_policy: str = "standard"
    classification_level: str = "UNCLASSIFIED"
    compartment: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CorrelationRelationship:
    """Intelligence correlation relationship"""
    correlation_id: str
    primary_record_id: str
    secondary_record_id: str
    correlation_type: str
    strength: CorrelationStrength
    confidence: float
    evidence_factors: List[str]
    discovered_timestamp: datetime
    correlation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageTierMetrics:
    """Storage tier performance metrics"""
    tier: StorageTier
    record_count: int
    total_size_bytes: int
    compression_ratio: float
    avg_access_time_ms: float
    cache_hit_ratio: float
    last_optimization: datetime
    performance_score: float


@dataclass
class SemanticQuery:
    """Semantic query structure"""
    query_id: str
    query_text: str
    semantic_vector: np.ndarray
    similarity_threshold: float
    max_results: int
    intelligence_types: List[IntelligenceType]
    time_range: Tuple[datetime, datetime]
    priority_threshold: float
    correlation_depth: int
    metadata_filters: Dict[str, Any] = field(default_factory=dict)


class TieredStorageManager:
    """
    Advanced tiered storage management system
    
    Manages intelligent data lifecycle across storage tiers with
    automatic promotion/demotion based on access patterns and priority.
    """
    
    def __init__(self, base_storage_path: Path) -> None:
        """Initialise tiered storage across Working/Hot/Warm/Cold/Frozen tiers.

        Args:
            base_storage_path: Root directory under which tier-specific
                subdirectories are created and managed.
        """
        self.base_path = base_storage_path
        self.tier_paths = {
            StorageTier.WORKING: base_storage_path / "working",
            StorageTier.HOT: base_storage_path / "hot", 
            StorageTier.WARM: base_storage_path / "warm",
            StorageTier.COLD: base_storage_path / "cold",
            StorageTier.FROZEN: base_storage_path / "frozen"
        }
        
        # Create tier directories
        for tier_path in self.tier_paths.values():
            tier_path.mkdir(parents=True, exist_ok=True)
        
        # Tier configuration
        self.tier_config = {
            StorageTier.WORKING: {
                'max_records': 50000,
                'max_age_hours': 24,
                'compression': False,
                'cache_size_mb': 512,
                'access_threshold': 100
            },
            StorageTier.HOT: {
                'max_records': 200000,
                'max_age_hours': 168,  # 1 week
                'compression': False,
                'cache_size_mb': 256,
                'access_threshold': 50
            },
            StorageTier.WARM: {
                'max_records': 1000000,
                'max_age_hours': 720,  # 30 days
                'compression': True,
                'cache_size_mb': 128,
                'access_threshold': 10
            },
            StorageTier.COLD: {
                'max_records': 5000000,
                'max_age_hours': 8760,  # 1 year
                'compression': True,
                'cache_size_mb': 64,
                'access_threshold': 1
            },
            StorageTier.FROZEN: {
                'max_records': -1,  # Unlimited
                'max_age_hours': -1,  # Permanent
                'compression': True,
                'cache_size_mb': 32,
                'access_threshold': 0
            }
        }
        
        # Performance tracking
        self.tier_metrics = {}
        self.promotion_queue = []
        self.demotion_queue = []
        self.optimization_scheduler = {}
        
        # Initialize tier metrics
        for tier in StorageTier:
            self.tier_metrics[tier] = StorageTierMetrics(
                tier=tier,
                record_count=0,
                total_size_bytes=0,
                compression_ratio=1.0,
                avg_access_time_ms=0.0,
                cache_hit_ratio=0.0,
                last_optimization=datetime.now(timezone.utc),
                performance_score=1.0
            )
    
    def calculate_tier_placement(self, record: IntelligenceRecord) -> StorageTier:
        """Calculate optimal storage tier for an intelligence record.

        Uses a weighted composite of age, priority, access frequency,
        threat level, and confidence to place the record in the appropriate
        storage tier.

        Args:
            record: The intelligence record to evaluate.

        Returns:
            The recommended :class:`StorageTier` for the record.
        """
        # Factor weights for tier placement decision
        age_weight = 0.3
        priority_weight = 0.25
        access_weight = 0.2
        threat_weight = 0.15
        confidence_weight = 0.1
        
        # Calculate age factor (newer = higher score)
        age_hours = (datetime.now(timezone.utc) - record.collection_timestamp).total_seconds() / 3600
        age_factor = max(0, 1 - (age_hours / 168))  # Decay over 1 week
        
        # Calculate composite score
        composite_score = (
            age_factor * age_weight +
            record.priority_score * priority_weight +
            min(1.0, record.access_count / 100) * access_weight +
            (record.threat_level / 10) * threat_weight +
            record.confidence_score * confidence_weight
        )
        
        # Determine tier based on composite score
        if composite_score >= 0.8:
            return StorageTier.WORKING
        elif composite_score >= 0.6:
            return StorageTier.HOT
        elif composite_score >= 0.4:
            return StorageTier.WARM
        elif composite_score >= 0.2:
            return StorageTier.COLD
        else:
            return StorageTier.FROZEN
    
    def should_promote(self, record: IntelligenceRecord) -> bool:
        """Determine if a record should be promoted to a higher tier.

        Args:
            record: The intelligence record to evaluate.

        Returns:
            ``True`` if the optimal tier is higher than the current tier.
        """
        current_tier = record.storage_tier
        optimal_tier = self.calculate_tier_placement(record)
        
        # Check if optimal tier is higher than current
        tier_order = list(StorageTier)
        return tier_order.index(optimal_tier) < tier_order.index(current_tier)
    
    def should_demote(self, record: IntelligenceRecord) -> bool:
        """Determine if a record should be demoted to a lower tier.

        Args:
            record: The intelligence record to evaluate.

        Returns:
            ``True`` if the optimal tier is lower than the current tier.
        """
        current_tier = record.storage_tier
        optimal_tier = self.calculate_tier_placement(record)
        
        # Check if optimal tier is lower than current
        tier_order = list(StorageTier)
        return tier_order.index(optimal_tier) > tier_order.index(current_tier)
    
    def compress_data(self, data: bytes, tier: StorageTier) -> bytes:
        """Compress data based on tier requirements.

        Args:
            data: Raw bytes to compress.
            tier: Target storage tier that determines the compression
                algorithm (LZ4 for warm/cold, zlib-9 for frozen).

        Returns:
            Compressed bytes, or the original *data* if the tier does
            not require compression or the required library is unavailable.
        """
        if not self.tier_config[tier]['compression']:
            return data
        
        # Use LZ4 for fast compression on warm/cold tiers
        if tier in [StorageTier.WARM, StorageTier.COLD]:
            if HAS_LZ4:
                return lz4.compress(data)
            logger.warning(
                "LZ4 unavailable; falling back to zlib for tier %s",
                tier.value,
            )
            return zlib.compress(data, level=1)
        
        # Use higher compression for frozen tier
        elif tier == StorageTier.FROZEN:
            return zlib.compress(data, level=9)
        
        return data
    
    def decompress_data(self, compressed_data: bytes, tier: StorageTier) -> bytes:
        """Decompress data based on tier compression method.

        Args:
            compressed_data: Previously compressed bytes.
            tier: The storage tier from which the data originated,
                determining the decompression algorithm.

        Returns:
            Decompressed bytes, or the original *compressed_data* if the
            tier does not use compression.
        """
        if not self.tier_config[tier]['compression']:
            return compressed_data
        
        if tier in [StorageTier.WARM, StorageTier.COLD]:
            if HAS_LZ4:
                return lz4.decompress(compressed_data)
            # Data may have been compressed with zlib as fallback
            return zlib.decompress(compressed_data)
        elif tier == StorageTier.FROZEN:
            return zlib.decompress(compressed_data)
        
        return compressed_data


class SemanticIndexEngine:
    """
    Advanced semantic indexing and search engine
    
    Provides vector embeddings, semantic similarity, and intelligent
    correlation discovery using multiple ML models and techniques.
    """
    
    def __init__(self, model_path: str = "models/") -> None:
        """Initialise the semantic index engine.

        Args:
            model_path: Directory for caching ML models and vector
                storage (ChromaDB, FAISS).
        """
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding models
        self.sentence_transformer = None
        self.tfidf_vectorizer = None
        self.onnx_embedding_session = None
        
        # Vector storage and indexing
        self.chroma_client = None
        self.chroma_collections = {}
        self.faiss_indices = {}
        self.embedding_cache = {}
        
        # Semantic processing components
        self.correlation_patterns = {}
        self.similarity_thresholds = {
            IntelligenceType.TACTICAL_IOC: 0.85,
            IntelligenceType.STRATEGIC_CAMPAIGN: 0.75,
            IntelligenceType.VULNERABILITY_INTEL: 0.8,
            IntelligenceType.ATTRIBUTION_DATA: 0.7,
            IntelligenceType.NETWORK_TELEMETRY: 0.6,
            IntelligenceType.BEHAVIORAL_PATTERN: 0.65,
            IntelligenceType.THREAT_SIGNATURE: 0.9,
            IntelligenceType.GEOLOCATION_DATA: 0.7,
            IntelligenceType.COMMUNICATION_METADATA: 0.6,
            IntelligenceType.INFRASTRUCTURE_MAPPING: 0.75
        }
        
        # Performance optimization
        self.embedding_dimension = 384  # Default for sentence transformers
        self.batch_size = 100
        self.cache_size = 10000
        
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize semantic processing models.

        Loads sentence transformer, TF-IDF vectorizer, ChromaDB vector
        store, and FAISS indices.  Each optional dependency degrades
        gracefully when its library is unavailable.

        Raises:
            RuntimeError: If a critical model fails to load with no
                fallback available.
        """
        try:
            # Initialize sentence transformer for general embeddings
            if HAS_SENTENCE_TRANSFORMERS:
                self.sentence_transformer = SentenceTransformer(
                    'all-MiniLM-L6-v2',
                    cache_folder=str(self.model_path / "sentence_transformers")
                )
                self.embedding_dimension = (
                    self.sentence_transformer.get_sentence_embedding_dimension()
                )
            else:
                logger.warning(
                    "SentenceTransformer unavailable; embeddings will be zero vectors"
                )
            
            # Initialize TF-IDF for keyword-based similarity
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.95
            )
            
            # Initialize ChromaDB for vector storage
            if HAS_CHROMADB:
                self.chroma_client = chromadb.PersistentClient(
                    path=str(self.model_path / "chroma_db"),
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                
                # Create collections for different intelligence types
                for intel_type in IntelligenceType:
                    collection_name = f"intel_{intel_type.value}"
                    try:
                        self.chroma_collections[intel_type] = (
                            self.chroma_client.get_collection(
                                name=collection_name
                            )
                        )
                    except Exception:
                        self.chroma_collections[intel_type] = (
                            self.chroma_client.create_collection(
                                name=collection_name,
                                metadata={"hnsw:space": "cosine"}
                            )
                        )
            else:
                logger.warning("ChromaDB unavailable; vector storage disabled")
            
            # Initialize FAISS indices for each intelligence type
            if HAS_FAISS:
                for intel_type in IntelligenceType:
                    self.faiss_indices[intel_type] = faiss.IndexFlatIP(
                        self.embedding_dimension
                    )
            else:
                logger.warning("FAISS unavailable; FAISS-based search disabled")
            
            logger.info("Semantic index engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic models: {e}")
            raise
    
    def generate_embedding(self, text: str, intelligence_type: IntelligenceType) -> np.ndarray:
        """Generate semantic embedding for text content.

        Args:
            text: The text content to embed.
            intelligence_type: Intelligence category used for type-specific
                weighting of the embedding vector.

        Returns:
            Normalised numpy embedding vector of dimension
            ``self.embedding_dimension``.  Returns a zero vector on failure
            or when the sentence-transformer model is unavailable.
        """
        try:
            # Check cache first
            cache_key = hashlib.sha256(f"{text}_{intelligence_type.value}".encode()).hexdigest()
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            if not HAS_SENTENCE_TRANSFORMERS or self.sentence_transformer is None:
                return np.zeros(self.embedding_dimension)
            
            # Generate embedding using sentence transformer
            embedding = self.sentence_transformer.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            
            # Apply intelligence-type specific transformations
            embedding = self._apply_type_specific_transformation(embedding, intelligence_type)
            
            # Cache the embedding
            if len(self.embedding_cache) < self.cache_size:
                self.embedding_cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return np.zeros(self.embedding_dimension)
    
    def _apply_type_specific_transformation(self, embedding: np.ndarray, 
                                         intelligence_type: IntelligenceType) -> np.ndarray:
        """Apply intelligence-type specific transformations to embeddings.

        Segments the embedding into thirds and scales each segment by
        type-specific weights, then renormalises to unit length.

        Args:
            embedding: Raw embedding vector to transform.
            intelligence_type: Determines the per-segment weight profile.

        Returns:
            The weighted, renormalised embedding vector.
        """
        # Type-specific weight adjustments for different semantic aspects
        type_weights = {
            IntelligenceType.TACTICAL_IOC: [1.2, 1.0, 0.8],  # Emphasize technical indicators
            IntelligenceType.STRATEGIC_CAMPAIGN: [0.8, 1.2, 1.1],  # Emphasize contextual patterns
            IntelligenceType.VULNERABILITY_INTEL: [1.3, 0.9, 1.0],  # Emphasize technical details
            IntelligenceType.ATTRIBUTION_DATA: [0.9, 1.1, 1.2],  # Emphasize behavioral patterns
            IntelligenceType.NETWORK_TELEMETRY: [1.1, 0.9, 0.8],  # Emphasize network patterns
            IntelligenceType.BEHAVIORAL_PATTERN: [0.8, 1.0, 1.3],  # Emphasize behavioral aspects
            IntelligenceType.THREAT_SIGNATURE: [1.4, 0.8, 0.9],  # Emphasize signature patterns
            IntelligenceType.GEOLOCATION_DATA: [0.9, 1.2, 0.8],  # Emphasize geographic aspects
            IntelligenceType.COMMUNICATION_METADATA: [1.0, 1.1, 1.0],  # Balanced approach
            IntelligenceType.INFRASTRUCTURE_MAPPING: [1.1, 1.0, 0.9]  # Infrastructure focus
        }
        
        weights = type_weights.get(intelligence_type, [1.0, 1.0, 1.0])
        
        # Apply weights to different segments of the embedding
        segment_size = len(embedding) // 3
        if segment_size > 0:
            embedding[:segment_size] *= weights[0]
            embedding[segment_size:2*segment_size] *= weights[1]
            embedding[2*segment_size:] *= weights[2]
        
        # Renormalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def add_to_index(self, record: IntelligenceRecord) -> None:
        """Add an intelligence record to all available semantic indices.

        The record is indexed in both ChromaDB (for approximate nearest-
        neighbour search) and FAISS (for inner-product similarity) when
        those libraries are available.

        Args:
            record: The intelligence record to index.  If its
                ``semantic_embedding`` is ``None``, one is generated
                automatically.
        """
        try:
            # Generate text representation for embedding
            text_repr = self._generate_text_representation(record)
            
            # Generate embedding if not already present
            if record.semantic_embedding is None:
                record.semantic_embedding = self.generate_embedding(text_repr, record.intelligence_type)
            
            # Add to ChromaDB collection
            if HAS_CHROMADB and record.intelligence_type in self.chroma_collections:
                collection = self.chroma_collections[record.intelligence_type]
                collection.add(
                    embeddings=[record.semantic_embedding.tolist()],
                    documents=[text_repr],
                    metadatas=[{
                        'record_id': record.record_id,
                        'collection_timestamp': record.collection_timestamp.isoformat(),
                        'confidence_score': record.confidence_score,
                        'threat_level': record.threat_level,
                        'source_system': record.source_system
                    }],
                    ids=[record.record_id]
                )
            
            # Add to FAISS index
            if HAS_FAISS and record.intelligence_type in self.faiss_indices:
                faiss_index = self.faiss_indices[record.intelligence_type]
                faiss_index.add(record.semantic_embedding.reshape(1, -1))
            
            logger.debug(f"Added record {record.record_id} to semantic indices")
            
        except Exception as e:
            logger.error(f"Failed to add record to semantic index: {e}")
    
    def _generate_text_representation(self, record: IntelligenceRecord) -> str:
        """Generate comprehensive text representation of an intelligence record.

        Concatenates processed indicators, raw data values, tags, and
        string-valued metadata into a single whitespace-separated string
        suitable for embedding.

        Args:
            record: The intelligence record to serialise.

        Returns:
            A single text string summarising the record content.
        """
        text_parts = []
        
        # Add processed indicators
        if record.processed_indicators:
            text_parts.append(" ".join(record.processed_indicators))
        
        # Add key raw data elements
        if record.raw_data:
            for key, value in record.raw_data.items():
                if isinstance(value, str):
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, (list, dict)):
                    text_parts.append(f"{key}: {json.dumps(value)}")
                else:
                    text_parts.append(f"{key}: {str(value)}")
        
        # Add tags
        if record.tags:
            text_parts.append(" ".join(record.tags))
        
        # Add metadata
        if record.metadata:
            for key, value in record.metadata.items():
                if isinstance(value, str):
                    text_parts.append(f"{key}: {value}")
        
        return " ".join(text_parts)
    
    def semantic_search(self, query: SemanticQuery) -> List[Tuple[str, float]]:
        """Perform semantic similarity search across intelligence collections.

        Args:
            query: Structured semantic query with vector, thresholds, and
                filters.

        Returns:
            List of ``(record_id, similarity_score)`` tuples sorted by
            descending similarity, capped at ``query.max_results``.
        """
        results = []
        
        if not HAS_CHROMADB:
            logger.warning("ChromaDB unavailable; semantic search skipped")
            return results
        
        try:
            # Search across specified intelligence types
            for intel_type in query.intelligence_types:
                if intel_type not in self.chroma_collections:
                    continue
                collection = self.chroma_collections[intel_type]
                
                # Query ChromaDB collection
                chroma_results = collection.query(
                    query_embeddings=[query.semantic_vector.tolist()],
                    n_results=min(query.max_results, 100),
                    where={
                        "confidence_score": {"$gte": query.metadata_filters.get('min_confidence', 0.0)}
                    } if query.metadata_filters else None
                )
                
                # Process results
                if chroma_results['ids'] and chroma_results['distances']:
                    for record_id, distance in zip(chroma_results['ids'][0], chroma_results['distances'][0]):
                        similarity = 1.0 - distance  # Convert distance to similarity
                        if similarity >= query.similarity_threshold:
                            results.append((record_id, similarity))
            
            # Sort by similarity score
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Return top results
            return results[:query.max_results]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def find_correlations(self, record: IntelligenceRecord, 
                         correlation_threshold: float = 0.7) -> List[CorrelationRelationship]:
        """Find correlations between a record and existing intelligence.

        Args:
            record: The reference record to compare against the corpus.
            correlation_threshold: Minimum cosine similarity to consider
                two records correlated (default ``0.7``).

        Returns:
            List of discovered :class:`CorrelationRelationship` objects
            ranked by similarity.
        """
        correlations = []
        
        if not HAS_CHROMADB:
            logger.warning("ChromaDB unavailable; correlation discovery skipped")
            return correlations
        
        try:
            if record.semantic_embedding is None:
                text_repr = self._generate_text_representation(record)
                record.semantic_embedding = self.generate_embedding(text_repr, record.intelligence_type)
            
            # Search for similar records across all intelligence types
            for intel_type in IntelligenceType:
                if intel_type not in self.chroma_collections:
                    continue
                collection = self.chroma_collections[intel_type]
                
                # Query for similar records
                similar_results = collection.query(
                    query_embeddings=[record.semantic_embedding.tolist()],
                    n_results=50,
                    where={
                        "record_id": {"$ne": record.record_id}  # Exclude self
                    }
                )
                
                # Process correlation candidates
                if similar_results['ids'] and similar_results['distances']:
                    for candidate_id, distance in zip(similar_results['ids'][0], similar_results['distances'][0]):
                        similarity = 1.0 - distance
                        
                        if similarity >= correlation_threshold:
                            # Determine correlation strength
                            if similarity >= 0.9:
                                strength = CorrelationStrength.CRITICAL
                            elif similarity >= 0.8:
                                strength = CorrelationStrength.HIGH
                            elif similarity >= 0.7:
                                strength = CorrelationStrength.MEDIUM
                            else:
                                strength = CorrelationStrength.LOW
                            
                            # Create correlation relationship
                            correlation = CorrelationRelationship(
                                correlation_id=str(uuid4()),
                                primary_record_id=record.record_id,
                                secondary_record_id=candidate_id,
                                correlation_type="semantic_similarity",
                                strength=strength,
                                confidence=similarity,
                                evidence_factors=[f"semantic_similarity_{similarity:.3f}"],
                                discovered_timestamp=datetime.now(timezone.utc),
                                correlation_metadata={
                                    'similarity_score': similarity,
                                    'intelligence_types': [record.intelligence_type.value, intel_type.value],
                                    'discovery_method': 'semantic_embedding'
                                }
                            )
                            
                            correlations.append(correlation)
            
            logger.debug(f"Found {len(correlations)} correlations for record {record.record_id}")
            return correlations
            
        except Exception as e:
            logger.error(f"Correlation discovery failed: {e}")
            return []


class IntelligenceDatabaseEngine:
    """
    Core ARCS Intelligence Database Engine
    
    Provides comprehensive threat intelligence storage, retrieval, and correlation
    capabilities with tiered storage, semantic indexing, and operational optimization.
    """
    
    def __init__(self, database_path: str = "data/intelligence/arcs_intelligence.db",
                 storage_path: str = "data/intelligence/storage/",
                 models_path: str = "models/intelligence/") -> None:
        """Initialise the ARCS Intelligence Database Engine.

        Args:
            database_path: File path for the primary SQLite database.
            storage_path: Root directory for tiered file storage.
            models_path: Directory for ML model caches.
        """
        self.database_path = Path(database_path)
        self.storage_path = Path(storage_path)
        self.models_path = Path(models_path)
        
        # Create directory structure
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize core components
        self.storage_manager = TieredStorageManager(self.storage_path)
        self.semantic_engine = SemanticIndexEngine(str(self.models_path))
        
        # Database connections and pools
        self.primary_db = None
        self.connection_pool = []
        self.pool_size = 10
        self.db_lock = threading.RLock()
        
        # Caching and performance optimization
        self.record_cache = {}
        self.query_cache = {}
        self.correlation_cache = {}
        self.cache_size = 5000
        self.performance_metrics = defaultdict(list)
        
        # Background processing
        self._running = True
        self.background_tasks = []
        self.processing_queue = asyncio.Queue()
        self.maintenance_scheduler = {}
        
        # Encryption and security
        self.encryption_key = None
        self.cipher_suite = None
        
        # Initialize database
        self._initialize_database()
        self._initialize_encryption()
        self._start_background_services()
    
    def _initialize_database(self) -> None:
        """Initialize primary intelligence database.

        Creates the SQLite database with WAL journaling, configures
        performance pragmas, creates the schema, and populates the
        connection pool.

        Raises:
            sqlite3.Error: If database creation or configuration fails.
        """
        try:
            self.primary_db = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )
            
            # Configure database for performance
            self.primary_db.execute("PRAGMA journal_mode=WAL")
            self.primary_db.execute("PRAGMA synchronous=NORMAL")
            self.primary_db.execute("PRAGMA cache_size=50000")
            self.primary_db.execute("PRAGMA temp_store=memory")
            self.primary_db.execute("PRAGMA mmap_size=268435456")  # 256MB
            self.primary_db.execute("PRAGMA optimize")
            
            # Create core tables
            self._create_database_schema()
            
            # Initialize connection pool
            for _ in range(self.pool_size):
                conn = sqlite3.connect(
                    self.database_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.row_factory = sqlite3.Row
                self.connection_pool.append(conn)
            
            logger.info("Intelligence database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_database_schema(self) -> None:
        """Create comprehensive database schema.

        Idempotently creates all core tables, indices, FTS virtual tables,
        and update triggers required by the intelligence engine.
        """
        schema_sql = """
        -- Primary intelligence records table
        CREATE TABLE IF NOT EXISTS intelligence_records (
            record_id TEXT PRIMARY KEY,
            intelligence_type TEXT NOT NULL,
            collection_timestamp TEXT NOT NULL,
            source_system TEXT NOT NULL,
            source_reliability REAL NOT NULL,
            confidence_score REAL NOT NULL,
            threat_level INTEGER NOT NULL,
            priority_score REAL NOT NULL,
            raw_data_compressed BLOB,
            raw_data_hash TEXT,
            processed_indicators TEXT,
            correlation_fingerprint TEXT,
            storage_tier TEXT NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT NOT NULL,
            retention_policy TEXT DEFAULT 'standard',
            classification_level TEXT DEFAULT 'UNCLASSIFIED',
            compartment TEXT,
            tags TEXT,
            metadata_json TEXT,
            semantic_embedding_compressed BLOB,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Intelligence correlations table
        CREATE TABLE IF NOT EXISTS intelligence_correlations (
            correlation_id TEXT PRIMARY KEY,
            primary_record_id TEXT NOT NULL,
            secondary_record_id TEXT NOT NULL,
            correlation_type TEXT NOT NULL,
            strength_value REAL NOT NULL,
            confidence REAL NOT NULL,
            evidence_factors TEXT,
            discovered_timestamp TEXT NOT NULL,
            correlation_metadata TEXT,
            verified BOOLEAN DEFAULT 0,
            verification_timestamp TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (primary_record_id) REFERENCES intelligence_records (record_id),
            FOREIGN KEY (secondary_record_id) REFERENCES intelligence_records (record_id)
        );
        
        -- Query performance and analytics
        CREATE TABLE IF NOT EXISTS query_analytics (
            query_id TEXT PRIMARY KEY,
            query_type TEXT NOT NULL,
            query_complexity TEXT NOT NULL,
            execution_time_ms REAL NOT NULL,
            results_count INTEGER NOT NULL,
            cache_hit BOOLEAN DEFAULT 0,
            timestamp TEXT NOT NULL,
            query_hash TEXT,
            performance_score REAL
        );
        
        -- Storage tier management
        CREATE TABLE IF NOT EXISTS tier_management (
            record_id TEXT PRIMARY KEY,
            current_tier TEXT NOT NULL,
            promotion_score REAL NOT NULL,
            last_tier_change TEXT NOT NULL,
            access_pattern TEXT,
            size_bytes INTEGER NOT NULL,
            compression_ratio REAL DEFAULT 1.0,
            FOREIGN KEY (record_id) REFERENCES intelligence_records (record_id)
        );
        
        -- System performance metrics
        CREATE TABLE IF NOT EXISTS performance_metrics (
            metric_id TEXT PRIMARY KEY,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            measurement_timestamp TEXT NOT NULL,
            metric_metadata TEXT
        );
        
        -- Data retention and lifecycle
        CREATE TABLE IF NOT EXISTS retention_policies (
            policy_id TEXT PRIMARY KEY,
            policy_name TEXT NOT NULL,
            intelligence_types TEXT,
            retention_period_days INTEGER NOT NULL,
            archival_policy TEXT,
            deletion_policy TEXT,
            compliance_requirements TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create performance indices
        CREATE INDEX IF NOT EXISTS idx_records_type_timestamp ON intelligence_records (intelligence_type, collection_timestamp);
        CREATE INDEX IF NOT EXISTS idx_records_threat_priority ON intelligence_records (threat_level, priority_score);
        CREATE INDEX IF NOT EXISTS idx_records_storage_tier ON intelligence_records (storage_tier);
        CREATE INDEX IF NOT EXISTS idx_records_source ON intelligence_records (source_system);
        CREATE INDEX IF NOT EXISTS idx_records_classification ON intelligence_records (classification_level, compartment);
        CREATE INDEX IF NOT EXISTS idx_correlations_primary ON intelligence_correlations (primary_record_id);
        CREATE INDEX IF NOT EXISTS idx_correlations_secondary ON intelligence_correlations (secondary_record_id);
        CREATE INDEX IF NOT EXISTS idx_correlations_strength ON intelligence_correlations (strength_value);
        CREATE INDEX IF NOT EXISTS idx_tier_mgmt_tier ON tier_management (current_tier);
        CREATE INDEX IF NOT EXISTS idx_tier_mgmt_promotion ON tier_management (promotion_score);
        
        -- Create full-text search indices
        CREATE VIRTUAL TABLE IF NOT EXISTS intelligence_fts USING fts5(
            record_id UNINDEXED,
            processed_indicators,
            tags,
            raw_data_text
        );
        
        -- Triggers for automatic updates
        CREATE TRIGGER IF NOT EXISTS update_record_timestamp 
        AFTER UPDATE ON intelligence_records
        BEGIN
            UPDATE intelligence_records SET updated_at = CURRENT_TIMESTAMP WHERE record_id = NEW.record_id;
        END;
        
        CREATE TRIGGER IF NOT EXISTS update_access_count
        AFTER UPDATE OF last_accessed ON intelligence_records
        BEGIN
            UPDATE intelligence_records SET access_count = access_count + 1 WHERE record_id = NEW.record_id;
        END;
        """
        
        self.primary_db.executescript(schema_sql)
        self.primary_db.commit()
    
    def _initialize_encryption(self) -> None:
        """Initialize Fernet encryption for sensitive intelligence data.

        Loads an existing key from disk or generates a new PBKDF2-derived
        key and persists it with restrictive file permissions.

        Raises:
            OSError: If the key file cannot be read or written.
        """
        try:
            key_path = self.database_path.parent / "intelligence.key"
            
            if key_path.exists():
                with open(key_path, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Generate new encryption key
                password = os.urandom(32)
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                self.encryption_key = base64.urlsafe_b64encode(kdf.derive(password))
                
                # Save key securely
                with open(key_path, 'wb') as f:
                    f.write(self.encryption_key)
                os.chmod(key_path, 0o600)
            
            self.cipher_suite = Fernet(self.encryption_key)
            logger.info("Intelligence encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def _start_background_services(self) -> None:
        """Start background processing services.

        Spawns async tasks for tier management, correlation discovery,
        cache optimisation, and performance monitoring.  Requires a
        running ``asyncio`` event loop.
        """
        # Start tier management service
        self.background_tasks.append(
            asyncio.create_task(self._tier_management_service())
        )
        
        # Start correlation discovery service
        self.background_tasks.append(
            asyncio.create_task(self._correlation_service())
        )
        
        # Start cache optimization service
        self.background_tasks.append(
            asyncio.create_task(self._cache_optimization_service())
        )
        
        # Start performance monitoring service
        self.background_tasks.append(
            asyncio.create_task(self._performance_monitoring_service())
        )
        
        logger.info("Background services started")
    
    async def store_intelligence(self, record: IntelligenceRecord) -> bool:
        """Store an intelligence record with full processing pipeline.

        Generates a correlation fingerprint, determines storage tier,
        computes the semantic embedding, encrypts and compresses raw data,
        persists to SQLite and FTS, and indexes in the semantic engine.

        Args:
            record: The intelligence record to store.

        Returns:
            ``True`` on success, ``False`` on failure.
        """
        try:
            start_time = time.time()
            
            # Generate correlation fingerprint
            record.correlation_fingerprint = self._generate_correlation_fingerprint(record)
            
            # Determine optimal storage tier
            record.storage_tier = self.storage_manager.calculate_tier_placement(record)
            
            # Generate semantic embedding
            if record.semantic_embedding is None:
                text_repr = self.semantic_engine._generate_text_representation(record)
                record.semantic_embedding = self.semantic_engine.generate_embedding(
                    text_repr, record.intelligence_type
                )
            
            # Compress and encrypt sensitive data
            raw_data_json = json.dumps(record.raw_data, default=str)
            encrypted_data = self.cipher_suite.encrypt(raw_data_json.encode())
            compressed_data = self.storage_manager.compress_data(encrypted_data, record.storage_tier)
            
            # Compress semantic embedding
            embedding_bytes = record.semantic_embedding.tobytes()
            compressed_embedding = self.storage_manager.compress_data(embedding_bytes, record.storage_tier)
            
            # Calculate data hash for integrity
            data_hash = hashlib.sha256(raw_data_json.encode()).hexdigest()
            
            # Store in primary database
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO intelligence_records
                    (record_id, intelligence_type, collection_timestamp, source_system,
                     source_reliability, confidence_score, threat_level, priority_score,
                     raw_data_compressed, raw_data_hash, processed_indicators,
                     correlation_fingerprint, storage_tier, access_count, last_accessed,
                     retention_policy, classification_level, compartment, tags,
                     metadata_json, semantic_embedding_compressed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.record_id,
                    record.intelligence_type.value,
                    record.collection_timestamp.isoformat(),
                    record.source_system,
                    record.source_reliability,
                    record.confidence_score,
                    record.threat_level,
                    record.priority_score,
                    compressed_data,
                    data_hash,
                    json.dumps(record.processed_indicators),
                    record.correlation_fingerprint,
                    record.storage_tier.value,
                    record.access_count,
                    record.last_accessed.isoformat(),
                    record.retention_policy,
                    record.classification_level,
                    record.compartment,
                    json.dumps(record.tags),
                    json.dumps(record.metadata),
                    compressed_embedding
                ))
                
                # Store in tier management table
                cursor.execute("""
                    INSERT OR REPLACE INTO tier_management
                    (record_id, current_tier, promotion_score, last_tier_change,
                     access_pattern, size_bytes, compression_ratio)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.record_id,
                    record.storage_tier.value,
                    self.storage_manager.calculate_tier_placement(record).value,
                    datetime.now(timezone.utc).isoformat(),
                    "new_record",
                    len(compressed_data),
                    len(compressed_data) / len(raw_data_json.encode()) if raw_data_json else 1.0
                ))
                
                # Store in FTS index
                cursor.execute("""
                    INSERT OR REPLACE INTO intelligence_fts
                    (record_id, processed_indicators, tags, raw_data_text)
                    VALUES (?, ?, ?, ?)
                """, (
                    record.record_id,
                    " ".join(record.processed_indicators),
                    " ".join(record.tags),
                    raw_data_json[:10000]  # Limit text length
                ))
                
                self.primary_db.commit()
            
            # Add to semantic indices
            self.semantic_engine.add_to_index(record)
            
            # Cache the record
            if len(self.record_cache) < self.cache_size:
                self.record_cache[record.record_id] = record
            
            # Update performance metrics
            execution_time = (time.time() - start_time) * 1000
            self.performance_metrics['store_operations'].append(execution_time)
            
            logger.debug(f"Stored intelligence record {record.record_id} in {execution_time:.2f}ms")
            return True
            
        except Exception as e:
            with self.db_lock:
                try:
                    self.primary_db.rollback()
                except Exception:
                    pass
            logger.error(f"Failed to store intelligence record: {e}")
            return False
    
    def _generate_correlation_fingerprint(self, record: IntelligenceRecord) -> str:
        """Generate a unique correlation fingerprint for an intelligence record.

        Combines intelligence type, threat level, sorted indicators, tags,
        source system, and significant raw-data keys into a SHA-256 hash.

        Args:
            record: The intelligence record to fingerprint.

        Returns:
            Hex-encoded SHA-256 fingerprint string.
        """
        # Combine key elements for fingerprinting
        fingerprint_elements = [
            record.intelligence_type.value,
            str(record.threat_level),
            json.dumps(sorted(record.processed_indicators)),
            json.dumps(sorted(record.tags)),
            record.source_system
        ]
        
        # Add significant raw data elements
        if record.raw_data:
            significant_keys = ['ip_address', 'domain', 'hash', 'signature', 'pattern']
            for key in significant_keys:
                if key in record.raw_data:
                    fingerprint_elements.append(f"{key}:{record.raw_data[key]}")
        
        # Generate SHA-256 hash
        fingerprint_text = "|".join(fingerprint_elements)
        return hashlib.sha256(fingerprint_text.encode()).hexdigest()
    
    async def retrieve_intelligence(self, record_id: str) -> Optional[IntelligenceRecord]:
        """Retrieve an intelligence record with full decompression and decryption.

        Checks the in-memory cache first, falling back to a database
        lookup with decryption, decompression, and access-tracking updates.

        Args:
            record_id: Unique identifier of the record.

        Returns:
            The reconstructed :class:`IntelligenceRecord`, or ``None`` if
            not found.
        """
        try:
            start_time = time.time()
            
            # Check cache first
            if record_id in self.record_cache:
                record = self.record_cache[record_id]
                record.access_count += 1
                record.last_accessed = datetime.now(timezone.utc)
                
                # Update access tracking in database
                await self._update_access_tracking(record_id)
                
                execution_time = (time.time() - start_time) * 1000
                self.performance_metrics['retrieve_operations'].append(execution_time)
                return record
            
            # Query database
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute("""
                    SELECT * FROM intelligence_records WHERE record_id = ?
                """, (record_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Reconstruct record from database row
                record = await self._reconstruct_record_from_row(row)
                
                # Cache the record
                if len(self.record_cache) < self.cache_size:
                    self.record_cache[record_id] = record
                
                # Update access tracking
                await self._update_access_tracking(record_id)
                
                execution_time = (time.time() - start_time) * 1000
                self.performance_metrics['retrieve_operations'].append(execution_time)
                
                logger.debug(f"Retrieved intelligence record {record_id} in {execution_time:.2f}ms")
                return record
            
        except Exception as e:
            logger.error(f"Failed to retrieve intelligence record {record_id}: {e}")
            return None
    
    async def _reconstruct_record_from_row(self, row: sqlite3.Row) -> Optional[IntelligenceRecord]:
        """Reconstruct an IntelligenceRecord from a database row.

        Decompresses, decrypts, and deserialises all stored fields
        back into a full :class:`IntelligenceRecord` instance.

        Args:
            row: A ``sqlite3.Row`` (or tuple) from the
                ``intelligence_records`` table.

        Returns:
            The reconstructed record, or ``None`` if reconstruction fails.
        """
        # Decompress and decrypt raw data
        storage_tier = StorageTier(row[12])
        compressed_data = row[8]
        
        decrypted_data = self.storage_manager.decompress_data(compressed_data, storage_tier)
        raw_data_json = self.cipher_suite.decrypt(decrypted_data).decode()
        raw_data = json.loads(raw_data_json)
        
        # Decompress semantic embedding
        if row[20]:  # semantic_embedding_compressed
            compressed_embedding = row[20]
            decompressed_embedding = self.storage_manager.decompress_data(compressed_embedding, storage_tier)
            embedding_array = np.frombuffer(decompressed_embedding, dtype=np.float32)
            embedding_array = embedding_array.reshape(-1)
        else:
            embedding_array = None
        
        # Create record object
        record = IntelligenceRecord(
            record_id=row[0],
            intelligence_type=IntelligenceType(row[1]),
            collection_timestamp=datetime.fromisoformat(row[2]),
            source_system=row[3],
            source_reliability=row[4],
            confidence_score=row[5],
            threat_level=row[6],
            priority_score=row[7],
            raw_data=raw_data,
            processed_indicators=json.loads(row[10]) if row[10] else [],
            semantic_embedding=embedding_array,
            correlation_fingerprint=row[11],
            storage_tier=storage_tier,
            access_count=row[13],
            last_accessed=datetime.fromisoformat(row[14]),
            retention_policy=row[15],
            classification_level=row[16],
            compartment=row[17],
            tags=json.loads(row[18]) if row[18] else [],
            metadata=json.loads(row[19]) if row[19] else {}
        )
        
        return record
    
    async def _update_access_tracking(self, record_id: str) -> None:
        """Update access tracking for an intelligence record.

        Increments the access count and refreshes the ``last_accessed``
        timestamp in the database.

        Args:
            record_id: Unique identifier of the record to update.
        """
        try:
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute("""
                    UPDATE intelligence_records 
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE record_id = ?
                """, (datetime.now(timezone.utc).isoformat(), record_id))
                self.primary_db.commit()
                
        except Exception as e:
            with self.db_lock:
                try:
                    self.primary_db.rollback()
                except Exception:
                    pass
            logger.error(f"Failed to update access tracking: {e}")
    
    async def advanced_query(self, query_params: Dict[str, Any]) -> List[IntelligenceRecord]:
        """Execute an advanced intelligence query with multiple parameters.

        Supports filtering by intelligence type, time range, threat level,
        confidence, source systems, storage tiers, classification, and
        full-text search.  Results are cached when small enough.

        Args:
            query_params: Dictionary of filter keys (``intelligence_types``,
                ``time_range``, ``min_threat_level``, ``max_threat_level``,
                ``min_confidence``, ``source_systems``, ``storage_tiers``,
                ``classification_levels``, ``search_text``, ``order_by``,
                ``limit``).

        Returns:
            List of matching :class:`IntelligenceRecord` instances.
        """
        try:
            start_time = time.time()
            
            # Generate query hash for caching
            query_hash = hashlib.sha256(json.dumps(query_params, sort_keys=True).encode()).hexdigest()
            
            # Check query cache
            if query_hash in self.query_cache:
                results = self.query_cache[query_hash]
                execution_time = (time.time() - start_time) * 1000
                await self._log_query_performance(query_hash, QueryComplexity.SIMPLE, execution_time, len(results), True)
                return results
            
            # Build SQL query
            where_clauses = []
            params = []
            
            # Intelligence type filter
            if 'intelligence_types' in query_params:
                intel_types = [t.value if isinstance(t, IntelligenceType) else t for t in query_params['intelligence_types']]
                placeholders = ','.join(['?' for _ in intel_types])
                where_clauses.append(f"intelligence_type IN ({placeholders})")
                params.extend(intel_types)
            
            # Time range filter
            if 'time_range' in query_params:
                start_time_filter, end_time_filter = query_params['time_range']
                where_clauses.append("collection_timestamp BETWEEN ? AND ?")
                params.extend([start_time_filter.isoformat(), end_time_filter.isoformat()])
            
            # Threat level filter
            if 'min_threat_level' in query_params:
                where_clauses.append("threat_level >= ?")
                params.append(query_params['min_threat_level'])
            
            if 'max_threat_level' in query_params:
                where_clauses.append("threat_level <= ?")
                params.append(query_params['max_threat_level'])
            
            # Confidence score filter
            if 'min_confidence' in query_params:
                where_clauses.append("confidence_score >= ?")
                params.append(query_params['min_confidence'])
            
            # Source system filter
            if 'source_systems' in query_params:
                placeholders = ','.join(['?' for _ in query_params['source_systems']])
                where_clauses.append(f"source_system IN ({placeholders})")
                params.extend(query_params['source_systems'])
            
            # Storage tier filter
            if 'storage_tiers' in query_params:
                tier_values = [t.value if isinstance(t, StorageTier) else t for t in query_params['storage_tiers']]
                placeholders = ','.join(['?' for _ in tier_values])
                where_clauses.append(f"storage_tier IN ({placeholders})")
                params.extend(tier_values)
            
            # Classification filter
            if 'classification_levels' in query_params:
                placeholders = ','.join(['?' for _ in query_params['classification_levels']])
                where_clauses.append(f"classification_level IN ({placeholders})")
                params.extend(query_params['classification_levels'])
            
            # Full-text search
            if 'search_text' in query_params:
                # Use FTS for text search
                fts_query = query_params['search_text']
                where_clauses.append("record_id IN (SELECT record_id FROM intelligence_fts WHERE intelligence_fts MATCH ?)")
                params.append(fts_query)
            
            # Build complete query
            base_query = "SELECT * FROM intelligence_records"
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ordering
            if 'order_by' in query_params:
                base_query += f" ORDER BY {query_params['order_by']}"
            else:
                base_query += " ORDER BY priority_score DESC, collection_timestamp DESC"
            
            # Add limit
            limit = query_params.get('limit', 1000)
            base_query += f" LIMIT {limit}"
            
            # Execute query
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute(base_query, params)
                rows = cursor.fetchall()
            
            # Reconstruct records
            results = []
            for row in rows:
                record = await self._reconstruct_record_from_row(row)
                results.append(record)
            
            # Cache results if reasonable size
            if len(results) <= 100:
                if len(self.query_cache) < 1000:
                    self.query_cache[query_hash] = results
            
            # Log performance
            execution_time = (time.time() - start_time) * 1000
            complexity = self._determine_query_complexity(query_params)
            await self._log_query_performance(query_hash, complexity, execution_time, len(results), False)
            
            logger.info(f"Advanced query returned {len(results)} results in {execution_time:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"Advanced query failed: {e}")
            return []
    
    def _determine_query_complexity(self, query_params: Dict[str, Any]) -> QueryComplexity:
        """Determine complexity level of a query.

        Args:
            query_params: The same parameter dictionary passed to
                :meth:`advanced_query`.

        Returns:
            The estimated :class:`QueryComplexity` level.
        """
        complexity_score = 0
        
        # Count filter types
        if 'intelligence_types' in query_params:
            complexity_score += 1
        if 'time_range' in query_params:
            complexity_score += 1
        if any(k in query_params for k in ['min_threat_level', 'max_threat_level']):
            complexity_score += 1
        if 'search_text' in query_params:
            complexity_score += 2  # FTS is more expensive
        if any(k in query_params for k in ['source_systems', 'storage_tiers']):
            complexity_score += 1
        
        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 4:
            return QueryComplexity.MODERATE
        elif complexity_score <= 6:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.ADVANCED
    
    async def _log_query_performance(self, query_hash: str, complexity: QueryComplexity,
                                   execution_time: float, results_count: int,
                                   cache_hit: bool) -> None:
        """Log query performance metrics for optimisation analysis.

        Args:
            query_hash: SHA-256 hash identifying the query.
            complexity: Estimated complexity level.
            execution_time: Wall-clock execution time in milliseconds.
            results_count: Number of records returned.
            cache_hit: Whether the result was served from cache.
        """
        try:
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute("""
                    INSERT INTO query_analytics
                    (query_id, query_type, query_complexity, execution_time_ms,
                     results_count, cache_hit, timestamp, query_hash, performance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid4()),
                    "advanced_query",
                    complexity.value,
                    execution_time,
                    results_count,
                    cache_hit,
                    datetime.now(timezone.utc).isoformat(),
                    query_hash,
                    max(0, 1000 - execution_time) / 1000  # Performance score 0-1
                ))
                self.primary_db.commit()
                
        except Exception as e:
            with self.db_lock:
                try:
                    self.primary_db.rollback()
                except Exception:
                    pass
            logger.error(f"Failed to log query performance: {e}")
    
    async def semantic_query(self, query_text: str, intelligence_types: List[IntelligenceType] = None,
                           similarity_threshold: float = 0.7, max_results: int = 50) -> List[Tuple[IntelligenceRecord, float]]:
        """Execute a semantic similarity query.

        Generates an embedding for *query_text* and searches the semantic
        index for the most similar intelligence records.

        Args:
            query_text: Free-text description of the desired intelligence.
            intelligence_types: Restrict search to these types; defaults
                to all types.
            similarity_threshold: Minimum cosine similarity (0--1).
            max_results: Maximum number of results to return.

        Returns:
            List of ``(record, similarity_score)`` tuples sorted by
            descending similarity.
        """
        try:
            start_time = time.time()
            
            # Default to all intelligence types if not specified
            if intelligence_types is None:
                intelligence_types = list(IntelligenceType)
            
            # Generate query embedding
            query_embedding = self.semantic_engine.generate_embedding(query_text, intelligence_types[0])
            
            # Create semantic query object
            semantic_query = SemanticQuery(
                query_id=str(uuid4()),
                query_text=query_text,
                semantic_vector=query_embedding,
                similarity_threshold=similarity_threshold,
                max_results=max_results,
                intelligence_types=intelligence_types,
                time_range=(datetime.now(timezone.utc) - timedelta(days=365), datetime.now(timezone.utc)),
                priority_threshold=0.0,
                correlation_depth=1
            )
            
            # Execute semantic search
            search_results = self.semantic_engine.semantic_search(semantic_query)
            
            # Retrieve full records
            results = []
            for record_id, similarity in search_results:
                record = await self.retrieve_intelligence(record_id)
                if record:
                    results.append((record, similarity))
            
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"Semantic query returned {len(results)} results in {execution_time:.2f}ms")
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic query failed: {e}")
            return []
    
    async def discover_correlations(self, record_id: str, 
                                  correlation_threshold: float = 0.7) -> List[CorrelationRelationship]:
        """Discover correlations for a specific intelligence record.

        Retrieves the record, delegates to the semantic engine for
        similarity search, and persists any discovered correlations.

        Args:
            record_id: Unique identifier of the anchor record.
            correlation_threshold: Minimum similarity to consider a
                correlation (default ``0.7``).

        Returns:
            List of newly discovered :class:`CorrelationRelationship`
            objects.
        """
        try:
            record = await self.retrieve_intelligence(record_id)
            if not record:
                return []
            
            # Find correlations using semantic engine
            correlations = self.semantic_engine.find_correlations(record, correlation_threshold)
            
            # Store correlations in database
            for correlation in correlations:
                await self._store_correlation(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Correlation discovery failed for {record_id}: {e}")
            return []
    
    async def _store_correlation(self, correlation: CorrelationRelationship) -> None:
        """Store a correlation relationship in the database.

        Args:
            correlation: The correlation to persist.
        """
        try:
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO intelligence_correlations
                    (correlation_id, primary_record_id, secondary_record_id,
                     correlation_type, strength_value, confidence, evidence_factors,
                     discovered_timestamp, correlation_metadata, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    correlation.correlation_id,
                    correlation.primary_record_id,
                    correlation.secondary_record_id,
                    correlation.correlation_type,
                    correlation.strength.value,
                    correlation.confidence,
                    json.dumps(correlation.evidence_factors),
                    correlation.discovered_timestamp.isoformat(),
                    json.dumps(correlation.correlation_metadata),
                    False  # Not verified yet
                ))
                self.primary_db.commit()
                
        except Exception as e:
            with self.db_lock:
                try:
                    self.primary_db.rollback()
                except Exception:
                    pass
            logger.error(f"Failed to store correlation: {e}")
    
    async def _tier_management_service(self) -> None:
        """Background service for managing storage tiers.

        Runs hourly, evaluating records whose tier has not changed in
        over 24 hours and migrating them to their optimal tier.
        """
        while self._running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Query records that might need tier changes
                with self.db_lock:
                    cursor = self.primary_db.cursor()
                    cursor.execute("""
                        SELECT record_id, current_tier, promotion_score
                        FROM tier_management 
                        WHERE last_tier_change < datetime('now', '-1 day')
                        ORDER BY promotion_score DESC
                        LIMIT 1000
                    """)
                    
                    candidates = cursor.fetchall()
                
                # Process tier change candidates
                for record_id, current_tier, promotion_score in candidates:
                    record = await self.retrieve_intelligence(record_id)
                    if record:
                        new_tier = self.storage_manager.calculate_tier_placement(record)
                        
                        if new_tier != record.storage_tier:
                            await self._migrate_record_tier(record, new_tier)
                
                logger.info(f"Processed {len(candidates)} tier management candidates")
                
            except Exception as e:
                logger.error(f"Tier management service error: {e}")
    
    async def _migrate_record_tier(self, record: IntelligenceRecord,
                                   new_tier: StorageTier) -> None:
        """Migrate a record to a new storage tier.

        Args:
            record: The intelligence record to migrate.
            new_tier: The destination storage tier.
        """
        try:
            old_tier = record.storage_tier
            record.storage_tier = new_tier
            
            # Update database record
            await self.store_intelligence(record)
            
            # Update tier management
            with self.db_lock:
                cursor = self.primary_db.cursor()
                cursor.execute("""
                    UPDATE tier_management
                    SET current_tier = ?, last_tier_change = ?
                    WHERE record_id = ?
                """, (new_tier.value, datetime.now(timezone.utc).isoformat(), record.record_id))
                self.primary_db.commit()
            
            logger.debug(f"Migrated record {record.record_id} from {old_tier.value} to {new_tier.value}")
            
        except Exception as e:
            with self.db_lock:
                try:
                    self.primary_db.rollback()
                except Exception:
                    pass
            logger.error(f"Failed to migrate record tier: {e}")
    
    async def _correlation_service(self) -> None:
        """Background service for discovering correlations.

        Runs every 30 minutes, finding recent records without correlation
        analysis and processing up to 50 candidates per cycle.
        """
        while self._running:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                
                # Find recent records without correlation analysis
                with self.db_lock:
                    cursor = self.primary_db.cursor()
                    cursor.execute("""
                        SELECT record_id FROM intelligence_records
                        WHERE record_id NOT IN (
                            SELECT DISTINCT primary_record_id FROM intelligence_correlations
                        )
                        AND collection_timestamp > datetime('now', '-1 day')
                        ORDER BY priority_score DESC
                        LIMIT 50
                    """)
                    
                    candidates = [row[0] for row in cursor.fetchall()]
                
                # Process correlation discovery
                for record_id in candidates:
                    correlations = await self.discover_correlations(record_id)
                    logger.debug(f"Discovered {len(correlations)} correlations for {record_id}")
                
                logger.info(f"Processed correlation discovery for {len(candidates)} records")
                
            except Exception as e:
                logger.error(f"Correlation service error: {e}")
    
    async def _cache_optimization_service(self) -> None:
        """Background service for cache optimisation.

        Runs every 10 minutes, evicting the least recently accessed
        20% of the record cache when usage exceeds 80% capacity, and
        halving the query cache when it exceeds 1 000 entries.
        """
        while self._running:
            try:
                await asyncio.sleep(600)  # Run every 10 minutes
                
                # Optimize record cache
                if len(self.record_cache) > self.cache_size * 0.8:
                    # Remove least recently accessed records
                    sorted_records = sorted(
                        self.record_cache.items(),
                        key=lambda x: x[1].last_accessed
                    )
                    
                    # Remove oldest 20%
                    remove_count = int(len(sorted_records) * 0.2)
                    for i in range(remove_count):
                        del self.record_cache[sorted_records[i][0]]
                
                # Optimize query cache
                if len(self.query_cache) > 1000:
                    # Simple LRU eviction - remove half
                    cache_items = list(self.query_cache.items())
                    self.query_cache = dict(cache_items[len(cache_items)//2:])
                
                logger.debug("Cache optimization completed")
                
            except Exception as e:
                logger.error(f"Cache optimization error: {e}")
    
    async def _performance_monitoring_service(self) -> None:
        """Background service for performance monitoring.

        Runs every 5 minutes, collecting system memory and CPU metrics,
        per-tier record counts, and average query performance, then
        persisting them for trend analysis.
        """
        while self._running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Collect system metrics
                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                cpu_usage = psutil.Process().cpu_percent()
                
                # Database performance metrics
                with self.db_lock:
                    cursor = self.primary_db.cursor()
                    
                    # Count records by tier
                    cursor.execute("SELECT storage_tier, COUNT(*) FROM intelligence_records GROUP BY storage_tier")
                    tier_counts = dict(cursor.fetchall())
                    
                    # Average query performance
                    cursor.execute("""
                        SELECT AVG(execution_time_ms) 
                        FROM query_analytics 
                        WHERE timestamp > datetime('now', '-1 hour')
                    """)
                    avg_query_time = cursor.fetchone()[0] or 0
                
                # Store performance metrics
                metrics = {
                    'memory_usage_mb': memory_usage,
                    'cpu_usage_percent': cpu_usage,
                    'avg_query_time_ms': avg_query_time,
                    'record_cache_size': len(self.record_cache),
                    'query_cache_size': len(self.query_cache),
                    'tier_counts': tier_counts
                }
                
                await self._store_performance_metrics(metrics)
                
                logger.debug(f"Performance metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
    
    async def _store_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store performance metrics in the database.

        Args:
            metrics: Mapping of metric names to numeric values.  Non-numeric
                values (e.g. dicts) are silently skipped.
        """
        try:
            with self.db_lock:
                cursor = self.primary_db.cursor()
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        cursor.execute("""
                            INSERT INTO performance_metrics
                            (metric_id, metric_name, metric_value, measurement_timestamp)
                            VALUES (?, ?, ?, ?)
                        """, (
                            str(uuid4()),
                            metric_name,
                            metric_value,
                            datetime.now(timezone.utc).isoformat()
                        ))
                self.primary_db.commit()
                
        except Exception as e:
            with self.db_lock:
                try:
                    self.primary_db.rollback()
                except Exception:
                    pass
            logger.error(f"Failed to store performance metrics: {e}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics.

        Returns:
            Dictionary containing record counts by type and tier,
            correlation totals, confidence averages, recent activity
            counts, query performance stats, cache sizes, and per-tier
            storage metrics.
        """
        try:
            stats = {}
            
            with self.db_lock:
                cursor = self.primary_db.cursor()
                
                # Record counts by type
                cursor.execute("""
                    SELECT intelligence_type, COUNT(*) 
                    FROM intelligence_records 
                    GROUP BY intelligence_type
                """)
                stats['records_by_type'] = dict(cursor.fetchall())
                
                # Record counts by tier
                cursor.execute("""
                    SELECT storage_tier, COUNT(*) 
                    FROM intelligence_records 
                    GROUP BY storage_tier
                """)
                stats['records_by_tier'] = dict(cursor.fetchall())
                
                # Total correlations
                cursor.execute("SELECT COUNT(*) FROM intelligence_correlations")
                stats['total_correlations'] = cursor.fetchone()[0]
                
                # Average confidence scores
                cursor.execute("""
                    SELECT intelligence_type, AVG(confidence_score) 
                    FROM intelligence_records 
                    GROUP BY intelligence_type
                """)
                stats['avg_confidence_by_type'] = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) FROM intelligence_records 
                    WHERE collection_timestamp > datetime('now', '-24 hours')
                """)
                stats['records_last_24h'] = cursor.fetchone()[0]
                
                # Performance stats
                cursor.execute("""
                    SELECT AVG(execution_time_ms), MAX(execution_time_ms) 
                    FROM query_analytics 
                    WHERE timestamp > datetime('now', '-24 hours')
                """)
                perf_result = cursor.fetchone()
                stats['avg_query_time_ms'] = perf_result[0] or 0
                stats['max_query_time_ms'] = perf_result[1] or 0
            
            # Cache statistics
            stats['cache_stats'] = {
                'record_cache_size': len(self.record_cache),
                'query_cache_size': len(self.query_cache),
                'correlation_cache_size': len(self.correlation_cache)
            }
            
            # Storage tier metrics
            stats['tier_metrics'] = {
                tier.value: asdict(metrics) 
                for tier, metrics in self.storage_manager.tier_metrics.items()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Gracefully shut down the intelligence database.

        Signals background services to stop, cancels their tasks, and
        closes all database connections.
        """
        logger.info("Shutting down intelligence database...")
        
        # Signal background services to stop
        self._running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close database connections
        if self.primary_db:
            self.primary_db.close()
        
        for conn in self.connection_pool:
            conn.close()
        
        logger.info("Intelligence database shutdown complete")


# Export primary interfaces
__all__ = [
    'IntelligenceDatabaseEngine',
    'IntelligenceRecord', 
    'IntelligenceType',
    'StorageTier',
    'CorrelationRelationship',
    'SemanticQuery',
    'QueryComplexity'
]


if __name__ == "__main__":
    # Development testing and validation
    async def test_intelligence_database() -> None:
        """Comprehensive testing of intelligence database functionality.

        Creates a temporary database, stores a test record, verifies
        retrieval, runs advanced and semantic queries, discovers
        correlations, and prints database statistics.
        """
        
        # Initialize database
        db = IntelligenceDatabaseEngine(
            database_path="test_data/intelligence_test.db",
            storage_path="test_data/storage/",
            models_path="test_models/"
        )
        
        # Create test intelligence record
        test_record = IntelligenceRecord(
            record_id=str(uuid4()),
            intelligence_type=IntelligenceType.TACTICAL_IOC,
            collection_timestamp=datetime.now(timezone.utc),
            source_system="test_system",
            source_reliability=0.9,
            confidence_score=0.85,
            threat_level=7,
            priority_score=0.8,
            raw_data={
                'ip_address': '192.168.1.100',
                'malware_family': 'test_malware',
                'attack_vector': 'phishing',
                'campaign_id': 'test_campaign_001'
            },
            processed_indicators=['192.168.1.100', 'test_malware', 'phishing'],
            tags=['malware', 'network', 'threat'],
            metadata={
                'analyst_notes': 'Test intelligence record',
                'validation_status': 'pending'
            }
        )
        
        # Test storage
        print("Testing intelligence storage...")
        success = await db.store_intelligence(test_record)
        print(f"Storage result: {success}")
        
        # Test retrieval
        print("Testing intelligence retrieval...")
        retrieved_record = await db.retrieve_intelligence(test_record.record_id)
        print(f"Retrieved record: {retrieved_record.record_id if retrieved_record else 'None'}")
        
        # Test advanced query
        print("Testing advanced query...")
        query_params = {
            'intelligence_types': [IntelligenceType.TACTICAL_IOC],
            'min_confidence': 0.8,
            'limit': 10
        }
        results = await db.advanced_query(query_params)
        print(f"Query results: {len(results)} records")
        
        # Test semantic query
        print("Testing semantic query...")
        semantic_results = await db.semantic_query(
            "malware network attack",
            intelligence_types=[IntelligenceType.TACTICAL_IOC],
            max_results=5
        )
        print(f"Semantic results: {len(semantic_results)} records")
        
        # Test correlation discovery
        print("Testing correlation discovery...")
        correlations = await db.discover_correlations(test_record.record_id)
        print(f"Correlations found: {len(correlations)}")
        
        # Get database statistics
        print("Getting database statistics...")
        stats = await db.get_database_stats()
        print(f"Database stats: {json.dumps(stats, indent=2, default=str)}")
        
        # Cleanup
        await db.shutdown()
        print("Test completed successfully")
    
    # Run test
    asyncio.run(test_intelligence_database())
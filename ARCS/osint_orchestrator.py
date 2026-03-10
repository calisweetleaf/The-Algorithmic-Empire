#!/usr/bin/env python3
"""
ARCS OSINT Orchestrator - Intelligence Coordination Authority
============================================================
Autonomous Reactive Cyber Systems - Intelligence Domain Orchestration

Mission: Coordinate sovereign intelligence operations with master orchestrator integration.
ROE Level 1 OBSERVE compliance. Zero external dependencies. Field deployable.

Classification: DEFENSIVE SYSTEMS - SOVEREIGN INTELLIGENCE
"""

import asyncio
import logging
import json
import time
import threading
import hashlib
import sqlite3
import socket
import struct
import ssl
import random
import re
import base64
import zlib
import hmac
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Callable, Tuple
from uuid import UUID, uuid4
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import yaml

import numpy as np
import onnxruntime as ort
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import psutil

try:
    import aiohttp
    import aiofiles
    HAS_AIOHTTP = True
except ImportError:
    aiohttp = None  # type: ignore[assignment]
    aiofiles = None  # type: ignore[assignment]
    HAS_AIOHTTP = False

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    chromadb = None  # type: ignore[assignment]
    HAS_CHROMADB = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment, misc]
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import ARP, Ether
    HAS_SCAPY = True
except ImportError:
    scapy = None  # type: ignore[assignment]
    HAS_SCAPY = False

try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    netifaces = None  # type: ignore[assignment]
    HAS_NETIFACES = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    HAS_SELENIUM = True
except ImportError:
    webdriver = None  # type: ignore[assignment]
    HAS_SELENIUM = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    BeautifulSoup = None  # type: ignore[assignment]
    HAS_BS4 = False

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level indicator classification utilities (deduplicated from classes)
# ---------------------------------------------------------------------------


def is_ip_address(value: str) -> bool:
    """Check if a string is a valid IPv4 address.

    Args:
        value: The string to check.

    Returns:
        True if the string matches IPv4 address format.
    """
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(ip_pattern, value))


def is_domain_name(value: str) -> bool:
    """Check if a string is a valid domain name.

    Args:
        value: The string to check.

    Returns:
        True if the string matches domain name format.
    """
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(domain_pattern, value))


def is_file_hash(value: str) -> bool:
    """Check if a string is a valid file hash (MD5, SHA1, or SHA256).

    Args:
        value: The string to check.

    Returns:
        True if the string matches MD5 (32), SHA1 (40), or SHA256 (64) hex format.
    """
    return len(value) in [32, 40, 64] and all(c in '0123456789abcdefABCDEF' for c in value)


class IntelligenceClassification(Enum):
    CRITICAL_INFRASTRUCTURE_THREAT = auto()
    ADVANCED_PERSISTENT_THREAT = auto()
    TARGETED_INTRUSION = auto()
    CORPORATE_SURVEILLANCE = auto()
    AUTOMATED_PROBES = auto()
    UNKNOWN = auto()


class IntelligenceSource(Enum):
    BROWSER_AUTOMATION = auto()
    NETWORK_MONITORING = auto()
    SYSTEM_TELEMETRY = auto()
    RF_SPECTRUM = auto()
    BEHAVIORAL_ANALYSIS = auto()
    CORRELATION_ENGINE = auto()


class ProcessingStatus(Enum):
    QUEUED = auto()
    PROCESSING = auto()
    CLASSIFIED = auto()
    CORRELATED = auto()
    ROUTED = auto()
    ARCHIVED = auto()
    ERROR = auto()


@dataclass
class IntelligencePackage:
    package_id: str
    classification: IntelligenceClassification
    confidence_score: float
    threat_indicators: List[str]
    attribution_data: Dict[str, Any]
    correlation_markers: List[str]
    raw_intelligence: Dict[str, Any]
    source_metadata: Dict[str, Any]
    collection_timestamp: datetime
    processing_timestamp: Optional[datetime] = None
    quality_score: float = 0.0
    actionable_intelligence: List[str] = field(default_factory=list)
    roe_compliance_flags: List[str] = field(default_factory=list)


@dataclass
class CorrelationResult:
    correlation_id: str
    primary_package_id: str
    related_package_ids: List[str]
    correlation_score: float
    pattern_type: str
    threat_campaign_indicators: List[str]
    attribution_confidence: float
    recommended_escalation: bool
    correlation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IntelligenceQualityAssessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_credibility_scores = {
            IntelligenceSource.BROWSER_AUTOMATION: 0.7,
            IntelligenceSource.NETWORK_MONITORING: 0.9,
            IntelligenceSource.SYSTEM_TELEMETRY: 0.95,
            IntelligenceSource.RF_SPECTRUM: 0.8,
            IntelligenceSource.BEHAVIORAL_ANALYSIS: 0.85,
            IntelligenceSource.CORRELATION_ENGINE: 0.75
        }
        
        self.indicator_weights = {
            'ip_addresses': 0.8,
            'domain_names': 0.7,
            'file_hashes': 0.9,
            'url_patterns': 0.6,
            'network_signatures': 0.85,
            'behavioral_patterns': 0.75,
            'temporal_patterns': 0.7
        }
    
    def assess_intelligence_quality(self, package: IntelligencePackage) -> float:
        source_score = self._assess_source_quality(package)
        indicator_score = self._assess_indicator_quality(package)
        temporal_score = self._assess_temporal_relevance(package)
        completeness_score = self._assess_data_completeness(package)
        
        weights = [0.3, 0.3, 0.2, 0.2]
        scores = [source_score, indicator_score, temporal_score, completeness_score]
        
        quality_score = sum(w * s for w, s in zip(weights, scores))
        return min(max(quality_score, 0.0), 1.0)
    
    def _assess_source_quality(self, package: IntelligencePackage) -> float:
        source_type = package.source_metadata.get('source_type')
        if isinstance(source_type, str):
            try:
                source_enum = IntelligenceSource[source_type.upper()]
                base_score = self.source_credibility_scores.get(source_enum, 0.5)
            except (KeyError, ValueError):
                base_score = 0.5
        else:
            base_score = 0.5
        
        collection_method_score = package.source_metadata.get('collection_method_score', 0.7)
        verification_score = package.source_metadata.get('verification_score', 0.6)
        
        return (base_score * 0.6 + collection_method_score * 0.3 + verification_score * 0.1)
    
    def _assess_indicator_quality(self, package: IntelligencePackage) -> float:
        if not package.threat_indicators:
            return 0.1
        
        indicator_scores = []
        for indicator in package.threat_indicators:
            indicator_type = self._classify_indicator_type(indicator)
            type_weight = self.indicator_weights.get(indicator_type, 0.5)
            specificity_score = self._assess_indicator_specificity(indicator)
            indicator_scores.append(type_weight * specificity_score)
        
        return sum(indicator_scores) / len(indicator_scores)
    
    def _assess_temporal_relevance(self, package: IntelligencePackage) -> float:
        age_hours = (datetime.now(timezone.utc) - package.collection_timestamp).total_seconds() / 3600
        
        if age_hours < 1:
            return 1.0
        elif age_hours < 24:
            return 0.9
        elif age_hours < 168:  # 1 week
            return 0.7
        elif age_hours < 720:  # 1 month
            return 0.5
        else:
            return 0.3
    
    def _assess_data_completeness(self, package: IntelligencePackage) -> float:
        required_fields = [
            'threat_indicators', 'attribution_data', 'source_metadata',
            'collection_timestamp', 'raw_intelligence'
        ]
        
        present_fields = sum(1 for field in required_fields if getattr(package, field, None))
        completeness_ratio = present_fields / len(required_fields)
        
        data_richness = len(package.raw_intelligence) / max(len(package.raw_intelligence), 10)
        
        return (completeness_ratio * 0.7 + min(data_richness, 1.0) * 0.3)
    
    def _classify_indicator_type(self, indicator: str) -> str:
        if self._is_ip_address(indicator):
            return 'ip_addresses'
        elif self._is_domain_name(indicator):
            return 'domain_names'
        elif self._is_file_hash(indicator):
            return 'file_hashes'
        elif self._is_url(indicator):
            return 'url_patterns'
        else:
            return 'behavioral_patterns'
    
    def _assess_indicator_specificity(self, indicator: str) -> float:
        if self._is_file_hash(indicator):
            return 0.95
        elif self._is_ip_address(indicator):
            return 0.8
        elif self._is_domain_name(indicator):
            return 0.7
        elif self._is_url(indicator):
            return 0.6
        else:
            return 0.5
    
    def _is_ip_address(self, value: str) -> bool:
        return is_ip_address(value)
    
    def _is_domain_name(self, value: str) -> bool:
        return is_domain_name(value)
    
    def _is_file_hash(self, value: str) -> bool:
        return is_file_hash(value)
    
    def _is_url(self, value: str) -> bool:
        return value.startswith(('http://', 'https://', 'ftp://'))


class ThreatCorrelationEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.correlation_db_path = Path(config.get('correlation_db_path', 'data/correlations.db'))
        self.vector_db_path = Path(config.get('vector_db_path', 'data/vectors'))
        
        self.correlation_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        self._initialize_correlation_database()
        self._initialize_vector_database()
        
        self.embedding_model = None
        self._initialize_embedding_model()
    
    def _initialize_correlation_database(self):
        conn = sqlite3.connect(str(self.correlation_db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlations (
                correlation_id TEXT PRIMARY KEY,
                primary_package_id TEXT NOT NULL,
                related_package_ids TEXT NOT NULL,
                correlation_score REAL NOT NULL,
                pattern_type TEXT NOT NULL,
                threat_campaign_indicators TEXT NOT NULL,
                attribution_confidence REAL NOT NULL,
                recommended_escalation BOOLEAN NOT NULL,
                correlation_timestamp TEXT NOT NULL,
                INDEX(primary_package_id),
                INDEX(correlation_score),
                INDEX(correlation_timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                pattern_signature BLOB NOT NULL,
                observed_count INTEGER DEFAULT 1,
                first_observed TEXT NOT NULL,
                last_observed TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                INDEX(pattern_type),
                INDEX(confidence_score)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_vector_database(self):
        if not HAS_CHROMADB:
            logger.warning("chromadb not available — vector database disabled")
            self.chroma_client = None
            self.intelligence_collection = None
            return
        try:
            self.chroma_client = chromadb.PersistentClient(path=str(self.vector_db_path))
            
            try:
                self.intelligence_collection = self.chroma_client.get_collection("intelligence_vectors")
            except:
                self.intelligence_collection = self.chroma_client.create_collection(
                    name="intelligence_vectors",
                    metadata={"description": "ARCS Intelligence correlation vectors"}
                )
        except Exception as e:
            logger.error(f"Vector database initialization failed: {e}")
            self.chroma_client = None
            self.intelligence_collection = None
    
    def _initialize_embedding_model(self):
        if not HAS_SENTENCE_TRANSFORMERS:
            logger.warning("sentence_transformers not available — embedding model disabled")
            self.embedding_model = None
            return
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.warning(f"Embedding model initialization failed: {e}")
            self.embedding_model = None
    
    async def correlate_intelligence(self, package: IntelligencePackage) -> List[CorrelationResult]:
        correlations = []
        
        try:
            temporal_correlations = await self._find_temporal_correlations(package)
            correlations.extend(temporal_correlations)
            
            semantic_correlations = await self._find_semantic_correlations(package)
            correlations.extend(semantic_correlations)
            
            indicator_correlations = await self._find_indicator_correlations(package)
            correlations.extend(indicator_correlations)
            
            attribution_correlations = await self._find_attribution_correlations(package)
            correlations.extend(attribution_correlations)
            
            await self._store_correlations(correlations)
            await self._update_threat_patterns(package, correlations)
            
        except Exception as e:
            logger.error(f"Intelligence correlation failed: {e}")
        
        return correlations
    
    async def _find_temporal_correlations(self, package: IntelligencePackage) -> List[CorrelationResult]:
        correlations = []
        
        try:
            conn = sqlite3.connect(str(self.correlation_db_path))
            cursor = conn.cursor()
            
            time_window = datetime.now(timezone.utc) - timedelta(hours=24)
            
            cursor.execute('''
                SELECT correlation_id, primary_package_id, correlation_score, pattern_type
                FROM correlations 
                WHERE correlation_timestamp > ? 
                AND correlation_score > 0.7
                ORDER BY correlation_score DESC
                LIMIT 50
            ''', (time_window.isoformat(),))
            
            recent_correlations = cursor.fetchall()
            
            for corr_id, pkg_id, score, pattern in recent_correlations:
                if await self._calculate_temporal_similarity(package, pkg_id) > 0.6:
                    correlation = CorrelationResult(
                        correlation_id=f"temporal_{int(time.time())}_{hashlib.md5(f'{package.package_id}_{pkg_id}'.encode()).hexdigest()[:8]}",
                        primary_package_id=package.package_id,
                        related_package_ids=[pkg_id],
                        correlation_score=score * 0.8,
                        pattern_type=f"temporal_{pattern}",
                        threat_campaign_indicators=package.threat_indicators[:5],
                        attribution_confidence=0.6,
                        recommended_escalation=score > 0.85
                    )
                    correlations.append(correlation)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Temporal correlation failed: {e}")
        
        return correlations
    
    async def _find_semantic_correlations(self, package: IntelligencePackage) -> List[CorrelationResult]:
        correlations = []
        
        if not self.embedding_model or not self.intelligence_collection:
            return correlations
        
        try:
            package_text = self._create_package_text(package)
            query_embedding = self.embedding_model.encode([package_text])
            
            results = self.intelligence_collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=10,
                include=['metadatas', 'distances']
            )
            
            for i, (distance, metadata) in enumerate(zip(results['distances'][0], results['metadatas'][0])):
                similarity_score = 1.0 - distance
                
                if similarity_score > 0.7 and metadata.get('package_id') != package.package_id:
                    correlation = CorrelationResult(
                        correlation_id=f"semantic_{int(time.time())}_{i}",
                        primary_package_id=package.package_id,
                        related_package_ids=[metadata.get('package_id', 'unknown')],
                        correlation_score=similarity_score,
                        pattern_type="semantic_similarity",
                        threat_campaign_indicators=package.threat_indicators[:3],
                        attribution_confidence=similarity_score * 0.8,
                        recommended_escalation=similarity_score > 0.9
                    )
                    correlations.append(correlation)
            
        except Exception as e:
            logger.error(f"Semantic correlation failed: {e}")
        
        return correlations
    
    async def _find_indicator_correlations(self, package: IntelligencePackage) -> List[CorrelationResult]:
        correlations = []
        
        try:
            conn = sqlite3.connect(str(self.correlation_db_path))
            cursor = conn.cursor()
            
            for indicator in package.threat_indicators[:10]:
                cursor.execute('''
                    SELECT correlation_id, primary_package_id, correlation_score
                    FROM correlations 
                    WHERE threat_campaign_indicators LIKE ?
                    AND correlation_score > 0.6
                    ORDER BY correlation_score DESC
                    LIMIT 5
                ''', (f'%{indicator}%',))
                
                matches = cursor.fetchall()
                
                for corr_id, pkg_id, score in matches:
                    if pkg_id != package.package_id:
                        correlation = CorrelationResult(
                            correlation_id=f"indicator_{int(time.time())}_{hashlib.md5(indicator.encode()).hexdigest()[:8]}",
                            primary_package_id=package.package_id,
                            related_package_ids=[pkg_id],
                            correlation_score=score * 0.9,
                            pattern_type="indicator_overlap",
                            threat_campaign_indicators=[indicator],
                            attribution_confidence=score * 0.7,
                            recommended_escalation=score > 0.8
                        )
                        correlations.append(correlation)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Indicator correlation failed: {e}")
        
        return correlations
    
    async def _find_attribution_correlations(self, package: IntelligencePackage) -> List[CorrelationResult]:
        correlations = []
        
        if not package.attribution_data:
            return correlations
        
        try:
            attribution_signatures = [
                package.attribution_data.get('actor_id', ''),
                package.attribution_data.get('campaign_id', ''),
                package.attribution_data.get('infrastructure_pattern', '')
            ]
            
            attribution_signatures = [sig for sig in attribution_signatures if sig]
            
            if attribution_signatures:
                correlation = CorrelationResult(
                    correlation_id=f"attribution_{int(time.time())}_{hashlib.md5(str(attribution_signatures).encode()).hexdigest()[:8]}",
                    primary_package_id=package.package_id,
                    related_package_ids=[],
                    correlation_score=0.8,
                    pattern_type="attribution_match",
                    threat_campaign_indicators=attribution_signatures,
                    attribution_confidence=0.9,
                    recommended_escalation=True
                )
                correlations.append(correlation)
            
        except Exception as e:
            logger.error(f"Attribution correlation failed: {e}")
        
        return correlations
    
    async def _calculate_temporal_similarity(self, package: IntelligencePackage, target_pkg_id: str) -> float:
        time_diff_hours = 24
        return max(0, 1.0 - (time_diff_hours / 168))
    
    def _create_package_text(self, package: IntelligencePackage) -> str:
        text_parts = [
            package.classification.name,
            ' '.join(package.threat_indicators[:10]),
            ' '.join(package.correlation_markers[:5]),
            str(package.attribution_data)[:500]
        ]
        return ' '.join(filter(None, text_parts))
    
    async def _store_correlations(self, correlations: List[CorrelationResult]) -> None:
        if not correlations:
            return
        
        try:
            conn = sqlite3.connect(str(self.correlation_db_path))
            cursor = conn.cursor()
            
            for correlation in correlations:
                cursor.execute('''
                    INSERT OR REPLACE INTO correlations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    correlation.correlation_id,
                    correlation.primary_package_id,
                    json.dumps(correlation.related_package_ids),
                    correlation.correlation_score,
                    correlation.pattern_type,
                    json.dumps(correlation.threat_campaign_indicators),
                    correlation.attribution_confidence,
                    correlation.recommended_escalation,
                    correlation.correlation_timestamp.isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Correlation storage failed: {e}")
    
    async def _update_threat_patterns(self, package: IntelligencePackage, correlations: List[CorrelationResult]) -> None:
        try:
            pattern_signature = self._generate_pattern_signature(package, correlations)
            
            conn = sqlite3.connect(str(self.correlation_db_path))
            cursor = conn.cursor()
            
            pattern_id = hashlib.md5(pattern_signature).hexdigest()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_patterns 
                (pattern_id, pattern_type, pattern_signature, observed_count, first_observed, last_observed, confidence_score)
                VALUES (?, ?, ?, 
                    COALESCE((SELECT observed_count + 1 FROM threat_patterns WHERE pattern_id = ?), 1),
                    COALESCE((SELECT first_observed FROM threat_patterns WHERE pattern_id = ?), ?),
                    ?, ?)
            ''', (
                pattern_id,
                package.classification.name,
                pattern_signature,
                pattern_id,
                pattern_id,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
                package.confidence_score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Threat pattern update failed: {e}")
    
    def _generate_pattern_signature(self, package: IntelligencePackage, correlations: List[CorrelationResult]) -> bytes:
        signature_data = {
            'classification': package.classification.name,
            'indicators': sorted(package.threat_indicators[:10]),
            'correlation_patterns': [c.pattern_type for c in correlations],
            'attribution_elements': list(package.attribution_data.keys())[:5]
        }
        
        signature_json = json.dumps(signature_data, sort_keys=True)
        return signature_json.encode()


class IntelligenceClassifier:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ml_model = None
        self._initialize_ml_model()
        
        self.classification_rules = {
            IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT: {
                'keywords': ['scada', 'ics', 'industrial', 'power', 'water', 'nuclear', 'critical'],
                'confidence_threshold': 0.9,
                'indicators_required': 3
            },
            IntelligenceClassification.ADVANCED_PERSISTENT_THREAT: {
                'keywords': ['apt', 'persistent', 'campaign', 'nation', 'state', 'sponsored'],
                'confidence_threshold': 0.8,
                'indicators_required': 5
            },
            IntelligenceClassification.TARGETED_INTRUSION: {
                'keywords': ['spear', 'phishing', 'targeted', 'lateral', 'movement', 'privilege'],
                'confidence_threshold': 0.7,
                'indicators_required': 3
            },
            IntelligenceClassification.CORPORATE_SURVEILLANCE: {
                'keywords': ['surveillance', 'tracking', 'corporate', 'espionage', 'data', 'collection'],
                'confidence_threshold': 0.6,
                'indicators_required': 2
            },
            IntelligenceClassification.AUTOMATED_PROBES: {
                'keywords': ['scan', 'probe', 'automated', 'bot', 'crawler', 'enumeration'],
                'confidence_threshold': 0.5,
                'indicators_required': 1
            }
        }
    
    def _initialize_ml_model(self):
        try:
            model_path = self.config.get('classification_model_path', 'models/threat_classification_2b.onnx')
            if Path(model_path).exists():
                self.ml_model = ort.InferenceSession(model_path)
                logger.info("ML classification model loaded successfully")
            else:
                logger.warning(f"ML model not found at {model_path}")
        except Exception as e:
            logger.warning(f"ML model initialization failed: {e}")
    
    async def classify_intelligence(self, raw_intelligence: Dict[str, Any]) -> Tuple[IntelligenceClassification, float]:
        rule_based_result = await self._rule_based_classification(raw_intelligence)
        
        if self.ml_model:
            ml_result = await self._ml_based_classification(raw_intelligence)
            
            combined_confidence = (rule_based_result[1] + ml_result[1]) / 2
            
            if ml_result[1] > rule_based_result[1]:
                return ml_result[0], combined_confidence
            else:
                return rule_based_result[0], combined_confidence
        
        return rule_based_result
    
    async def _rule_based_classification(self, raw_intelligence: Dict[str, Any]) -> Tuple[IntelligenceClassification, float]:
        content_text = self._extract_text_content(raw_intelligence).lower()
        
        classification_scores = {}
        
        for classification, rules in self.classification_rules.items():
            keyword_matches = sum(1 for keyword in rules['keywords'] if keyword in content_text)
            indicator_count = len(raw_intelligence.get('threat_indicators', []))
            
            keyword_score = min(keyword_matches / len(rules['keywords']), 1.0)
            indicator_score = min(indicator_count / rules['indicators_required'], 1.0)
            
            combined_score = (keyword_score * 0.6 + indicator_score * 0.4)
            
            if combined_score >= rules['confidence_threshold']:
                classification_scores[classification] = combined_score
        
        if classification_scores:
            best_classification = max(classification_scores.items(), key=lambda x: x[1])
            return best_classification[0], best_classification[1]
        
        return IntelligenceClassification.UNKNOWN, 0.3
    
    async def _ml_based_classification(self, raw_intelligence: Dict[str, Any]) -> Tuple[IntelligenceClassification, float]:
        try:
            feature_vector = self._create_feature_vector(raw_intelligence)
            
            ml_output = self.ml_model.run(None, {'input': feature_vector.reshape(1, -1)})
            
            classification_probs = ml_output[0][0]
            max_prob_index = np.argmax(classification_probs)
            max_confidence = float(classification_probs[max_prob_index])
            
            classification_mapping = [
                IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT,
                IntelligenceClassification.ADVANCED_PERSISTENT_THREAT,
                IntelligenceClassification.TARGETED_INTRUSION,
                IntelligenceClassification.CORPORATE_SURVEILLANCE,
                IntelligenceClassification.AUTOMATED_PROBES,
                IntelligenceClassification.UNKNOWN
            ]
            
            predicted_classification = classification_mapping[min(max_prob_index, len(classification_mapping) - 1)]
            
            return predicted_classification, max_confidence
            
        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return IntelligenceClassification.UNKNOWN, 0.1
    
    def _extract_text_content(self, raw_intelligence: Dict[str, Any]) -> str:
        text_parts = []
        
        for key, value in raw_intelligence.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(item) for item in value)
            elif isinstance(value, dict):
                text_parts.append(str(value))
        
        return ' '.join(text_parts)[:5000]
    
    def _create_feature_vector(self, raw_intelligence: Dict[str, Any]) -> np.ndarray:
        features = []
        
        indicators = raw_intelligence.get('threat_indicators', [])
        features.append(len(indicators))
        features.append(len([i for i in indicators if self._is_ip_address(i)]))
        features.append(len([i for i in indicators if self._is_domain_name(i)]))
        features.append(len([i for i in indicators if self._is_file_hash(i)]))
        
        content_text = self._extract_text_content(raw_intelligence).lower()
        features.append(len(content_text))
        features.append(content_text.count('malware'))
        features.append(content_text.count('exploit'))
        features.append(content_text.count('vulnerability'))
        
        attribution_data = raw_intelligence.get('attribution_data', {})
        features.append(len(attribution_data))
        features.append(1 if attribution_data.get('actor_id') else 0)
        
        while len(features) < 20:
            features.append(0.0)
        
        return np.array(features[:20], dtype=np.float32)
    
    def _is_ip_address(self, value: str) -> bool:
        return is_ip_address(value)
    
    def _is_domain_name(self, value: str) -> bool:
        return is_domain_name(value)
    
    def _is_file_hash(self, value: str) -> bool:
        return is_file_hash(value)


class MasterOrchestratorInterface:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator_endpoint = config.get('orchestrator_endpoint', 'http://localhost:8080')
        self.auth_token = config.get('auth_token', '')
        self.session = None
        
    async def initialize(self):
        if not HAS_AIOHTTP:
            logger.warning("aiohttp not available — HTTP interface disabled")
            self.session = None
            return
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'ARCS-OSINT/3.0'
            }
        )
    
    async def submit_intelligence_package(self, package: IntelligencePackage) -> Dict[str, Any]:
        if not self.session:
            await self.initialize()
        
        try:
            threat_event_data = {
                'threat_id': package.package_id,
                'classification': package.classification.name,
                'confidence_score': package.confidence_score,
                'threat_tier': self._map_classification_to_tier(package.classification),
                'attribution_data': package.attribution_data,
                'impact_assessment': self._generate_impact_assessment(package),
                'time_sensitivity': self._determine_time_sensitivity(package),
                'intelligence_sources': [source.name for source in self._extract_sources(package)],
                'correlation_patterns': self._format_correlation_patterns(package),
                'recommended_response': self._generate_response_recommendation(package),
                'roe_level': self._determine_roe_level(package),
                'raw_intelligence': package.raw_intelligence,
                'processing_metadata': {
                    'quality_score': package.quality_score,
                    'processing_timestamp': package.processing_timestamp.isoformat() if package.processing_timestamp else None,
                    'actionable_intelligence': package.actionable_intelligence,
                    'roe_compliance_flags': package.roe_compliance_flags
                }
            }
            
            async with self.session.post(
                f'{self.orchestrator_endpoint}/api/v1/threat-events',
                json=threat_event_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Intelligence package submitted successfully: {package.package_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Intelligence submission failed: HTTP {response.status} - {error_text}")
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            logger.error(f"Intelligence submission error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def request_container_overlay(self, container_type: str, authorized_actions: List[str], roe_level: int) -> Dict[str, Any]:
        if not self.session:
            await self.initialize()
        
        try:
            overlay_request = {
                'container_type': container_type,
                'authorized_actions': authorized_actions,
                'roe_level': roe_level,
                'resource_limits': {
                    'memory': '1g',
                    'cpu_count': 1,
                    'timeout': 1800
                },
                'requester': 'osint_orchestrator'
            }
            
            async with self.session.post(
                f'{self.orchestrator_endpoint}/api/v1/container-overlays',
                json=overlay_request
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Container overlay request failed: HTTP {response.status} - {error_text}")
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            logger.error(f"Container overlay request error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _map_classification_to_tier(self, classification: IntelligenceClassification) -> str:
        mapping = {
            IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT: 'critical_infrastructure_attack',
            IntelligenceClassification.ADVANCED_PERSISTENT_THREAT: 'advanced_persistent_threat',
            IntelligenceClassification.TARGETED_INTRUSION: 'targeted_intrusion',
            IntelligenceClassification.CORPORATE_SURVEILLANCE: 'corporate_surveillance',
            IntelligenceClassification.AUTOMATED_PROBES: 'automated_probes',
            IntelligenceClassification.UNKNOWN: 'automated_probes'
        }
        return mapping.get(classification, 'automated_probes')
    
    def _generate_impact_assessment(self, package: IntelligencePackage) -> Dict[str, float]:
        classification_impact = {
            IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT: {'operational': 1.0, 'data': 0.8, 'availability': 1.0},
            IntelligenceClassification.ADVANCED_PERSISTENT_THREAT: {'operational': 0.9, 'data': 0.9, 'availability': 0.7},
            IntelligenceClassification.TARGETED_INTRUSION: {'operational': 0.7, 'data': 0.6, 'availability': 0.5},
            IntelligenceClassification.CORPORATE_SURVEILLANCE: {'operational': 0.3, 'data': 0.8, 'availability': 0.2},
            IntelligenceClassification.AUTOMATED_PROBES: {'operational': 0.1, 'data': 0.0, 'availability': 0.1},
            IntelligenceClassification.UNKNOWN: {'operational': 0.3, 'data': 0.3, 'availability': 0.3}
        }
        
        base_impact = classification_impact.get(package.classification, {'operational': 0.5, 'data': 0.5, 'availability': 0.5})
        
        confidence_modifier = package.confidence_score
        for key in base_impact:
            base_impact[key] *= confidence_modifier
        
        return base_impact
    
    def _determine_time_sensitivity(self, package: IntelligencePackage) -> str:
        if package.classification in [IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT, IntelligenceClassification.ADVANCED_PERSISTENT_THREAT]:
            return 'immediate'
        elif package.classification == IntelligenceClassification.TARGETED_INTRUSION:
            return 'urgent'
        else:
            return 'routine'
    
    def _extract_sources(self, package: IntelligencePackage) -> List[IntelligenceSource]:
        source_type = package.source_metadata.get('source_type', 'UNKNOWN')
        try:
            return [IntelligenceSource[source_type.upper()]]
        except (KeyError, ValueError):
            return [IntelligenceSource.CORRELATION_ENGINE]
    
    def _format_correlation_patterns(self, package: IntelligencePackage) -> Dict[str, Any]:
        return {
            'correlation_markers': package.correlation_markers,
            'pattern_count': len(package.correlation_markers),
            'confidence_distribution': {
                'high': len([m for m in package.correlation_markers if 'high_conf' in m]),
                'medium': len([m for m in package.correlation_markers if 'med_conf' in m]),
                'low': len([m for m in package.correlation_markers if 'low_conf' in m])
            }
        }
    
    def _generate_response_recommendation(self, package: IntelligencePackage) -> str:
        if package.classification == IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT:
            return 'immediate_isolation_and_containment'
        elif package.classification == IntelligenceClassification.ADVANCED_PERSISTENT_THREAT:
            return 'enhanced_monitoring_and_active_defense'
        elif package.classification == IntelligenceClassification.TARGETED_INTRUSION:
            return 'network_hardening_and_user_awareness'
        elif package.classification == IntelligenceClassification.CORPORATE_SURVEILLANCE:
            return 'privacy_enhancement_and_data_protection'
        else:
            return 'baseline_monitoring'
    
    def _determine_roe_level(self, package: IntelligencePackage) -> int:
        confidence_thresholds = {
            4: 0.95,
            3: 0.75,
            2: 0.40,
            1: 0.0
        }
        
        classification_modifiers = {
            IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT: 0.4,
            IntelligenceClassification.ADVANCED_PERSISTENT_THREAT: 0.3,
            IntelligenceClassification.TARGETED_INTRUSION: 0.2,
            IntelligenceClassification.CORPORATE_SURVEILLANCE: 0.1,
            IntelligenceClassification.AUTOMATED_PROBES: 0.0,
            IntelligenceClassification.UNKNOWN: 0.0
        }
        
        modified_confidence = package.confidence_score + classification_modifiers.get(package.classification, 0.0)
        modified_confidence = min(modified_confidence, 1.0)
        
        for roe_level, threshold in confidence_thresholds.items():
            if modified_confidence >= threshold:
                return roe_level
        
        return 1
    
    async def close(self):
        if self.session:
            await self.session.close()


class IntelligenceStorage:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = Path(config.get('storage_path', 'data/intelligence'))
        self.db_path = self.storage_path / 'intelligence.db'
        self.encryption_key = self._initialize_encryption_key()
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_encryption_key(self) -> bytes:
        key_path = self.storage_path / 'encryption.key'
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            return key
    
    def _initialize_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intelligence_packages (
                package_id TEXT PRIMARY KEY,
                classification TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                quality_score REAL NOT NULL,
                collection_timestamp TEXT NOT NULL,
                processing_timestamp TEXT,
                encrypted_data BLOB NOT NULL,
                source_metadata TEXT NOT NULL,
                roe_compliance_flags TEXT,
                INDEX(classification),
                INDEX(confidence_score),
                INDEX(collection_timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                log_id TEXT PRIMARY KEY,
                package_id TEXT NOT NULL,
                processing_stage TEXT NOT NULL,
                processing_status TEXT NOT NULL,
                processing_timestamp TEXT NOT NULL,
                error_message TEXT,
                INDEX(package_id),
                INDEX(processing_stage),
                INDEX(processing_timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def store_intelligence_package(self, package: IntelligencePackage) -> bool:
        try:
            package_data = asdict(package)
            
            sensitive_fields = ['raw_intelligence', 'threat_indicators', 'attribution_data', 'actionable_intelligence']
            sensitive_data = {field: package_data.pop(field, None) for field in sensitive_fields}
            
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(json.dumps(sensitive_data, default=str).encode())
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO intelligence_packages 
                (package_id, classification, confidence_score, quality_score, 
                 collection_timestamp, processing_timestamp, encrypted_data, 
                 source_metadata, roe_compliance_flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                package.package_id,
                package.classification.name,
                package.confidence_score,
                package.quality_score,
                package.collection_timestamp.isoformat(),
                package.processing_timestamp.isoformat() if package.processing_timestamp else None,
                encrypted_data,
                json.dumps(package.source_metadata),
                json.dumps(package.roe_compliance_flags)
            ))
            
            conn.commit()
            conn.close()
            
            await self._log_processing_event(
                package.package_id, 'storage', 'completed', None
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Intelligence package storage failed: {e}")
            await self._log_processing_event(
                package.package_id, 'storage', 'failed', str(e)
            )
            return False
    
    async def retrieve_intelligence_package(self, package_id: str) -> Optional[IntelligencePackage]:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT classification, confidence_score, quality_score, 
                       collection_timestamp, processing_timestamp, encrypted_data,
                       source_metadata, roe_compliance_flags
                FROM intelligence_packages 
                WHERE package_id = ?
            ''', (package_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            classification_str, confidence_score, quality_score, collection_ts, processing_ts, encrypted_data, source_metadata_str, roe_flags_str = row
            
            fernet = Fernet(self.encryption_key)
            decrypted_data = json.loads(fernet.decrypt(encrypted_data).decode())
            
            classification = IntelligenceClassification[classification_str]
            collection_timestamp = datetime.fromisoformat(collection_ts)
            processing_timestamp = datetime.fromisoformat(processing_ts) if processing_ts else None
            source_metadata = json.loads(source_metadata_str)
            roe_compliance_flags = json.loads(roe_flags_str) if roe_flags_str else []
            
            package = IntelligencePackage(
                package_id=package_id,
                classification=classification,
                confidence_score=confidence_score,
                threat_indicators=decrypted_data.get('threat_indicators', []),
                attribution_data=decrypted_data.get('attribution_data', {}),
                correlation_markers=[],
                raw_intelligence=decrypted_data.get('raw_intelligence', {}),
                source_metadata=source_metadata,
                collection_timestamp=collection_timestamp,
                processing_timestamp=processing_timestamp,
                quality_score=quality_score,
                actionable_intelligence=decrypted_data.get('actionable_intelligence', []),
                roe_compliance_flags=roe_compliance_flags
            )
            
            return package
            
        except Exception as e:
            logger.error(f"Intelligence package retrieval failed: {e}")
            return None
    
    async def query_intelligence_packages(self, 
                                        classification_filter: Optional[IntelligenceClassification] = None,
                                        confidence_threshold: float = 0.0,
                                        time_range_hours: int = 24,
                                        limit: int = 100) -> List[IntelligencePackage]:
        
        packages = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            time_cutoff = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            
            query = '''
                SELECT package_id FROM intelligence_packages 
                WHERE confidence_score >= ? 
                AND collection_timestamp >= ?
            '''
            params = [confidence_threshold, time_cutoff.isoformat()]
            
            if classification_filter:
                query += ' AND classification = ?'
                params.append(classification_filter.name)
            
            query += ' ORDER BY confidence_score DESC, collection_timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            package_ids = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            for package_id in package_ids:
                package = await self.retrieve_intelligence_package(package_id)
                if package:
                    packages.append(package)
            
        except Exception as e:
            logger.error(f"Intelligence package query failed: {e}")
        
        return packages
    
    async def _log_processing_event(self, package_id: str, stage: str, status: str, error_message: Optional[str]) -> None:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            log_id = f"{package_id}_{stage}_{int(time.time())}"
            
            cursor.execute('''
                INSERT INTO processing_log 
                (log_id, package_id, processing_stage, processing_status, 
                 processing_timestamp, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                log_id,
                package_id,
                stage,
                status,
                datetime.now(timezone.utc).isoformat(),
                error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Processing log failed: {e}")


class OSINTOrchestrator:
    def __init__(self, config_path: str = '/etc/arcs/osint_orchestrator.yaml'):
        self.config_path = Path(config_path)
        self.config = self._load_configuration()
        
        self.intelligence_queue = asyncio.Queue(maxsize=1000)
        self.processing_queue = asyncio.Queue(maxsize=500)
        self.routing_queue = asyncio.Queue(maxsize=200)
        
        self.quality_assessor = IntelligenceQualityAssessor(self.config.get('quality_assessment', {}))
        self.correlation_engine = ThreatCorrelationEngine(self.config.get('correlation', {}))
        self.classifier = IntelligenceClassifier(self.config.get('classification', {}))
        self.storage = IntelligenceStorage(self.config.get('storage', {}))
        self.orchestrator_interface = MasterOrchestratorInterface(self.config.get('orchestrator_interface', {}))
        
        self.osint_module_interface = None
        self.active_processors = []
        self.processing_metrics = {
            'packages_processed': 0,
            'classifications_completed': 0,
            'correlations_found': 0,
            'packages_routed': 0,
            'errors_encountered': 0,
            'average_processing_time': 0.0,
            'start_time': datetime.now(timezone.utc)
        }
        
        self.shutdown_event = asyncio.Event()
        
        logger.info("ARCS OSINT Orchestrator initialized")
    
    def _load_configuration(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            default_config = {
                'processing': {
                    'max_concurrent_processors': 10,
                    'processing_timeout': 300,
                    'correlation_enabled': True,
                    'quality_assessment_enabled': True
                },
                'quality_assessment': {
                    'minimum_quality_threshold': 0.3,
                    'auto_discard_low_quality': True
                },
                'correlation': {
                    'correlation_db_path': 'data/intelligence/correlations.db',
                    'vector_db_path': 'data/intelligence/vectors',
                    'max_correlations_per_package': 10
                },
                'classification': {
                    'classification_model_path': 'models/threat_classification_2b.onnx',
                    'confidence_threshold': 0.5
                },
                'storage': {
                    'storage_path': 'data/intelligence',
                    'retention_days': 365,
                    'compression_enabled': True
                },
                'orchestrator_interface': {
                    'orchestrator_endpoint': 'http://localhost:8080',
                    'auth_token': 'arcs_osint_token',
                    'retry_attempts': 3,
                    'retry_delay': 5
                },
                'osint_module': {
                    'module_endpoint': 'http://localhost:8081',
                    'collection_interval': 1800,
                    'max_collection_threads': 5
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            return default_config
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def initialize(self) -> bool:
        try:
            logger.info("Initializing ARCS OSINT Orchestrator")
            
            await self.orchestrator_interface.initialize()
            
            await self._start_processing_workers()
            
            await self._start_monitoring_tasks()
            
            logger.info("ARCS OSINT Orchestrator fully operational")
            return True
            
        except Exception as e:
            logger.error(f"OSINT Orchestrator initialization failed: {e}")
            return False
    
    async def _start_processing_workers(self):
        max_processors = self.config['processing']['max_concurrent_processors']
        
        for i in range(max_processors):
            processor_task = asyncio.create_task(self._intelligence_processing_worker(f"processor_{i}"))
            self.active_processors.append(processor_task)
        
        routing_task = asyncio.create_task(self._intelligence_routing_worker())
        self.active_processors.append(routing_task)
        
        logger.info(f"Started {max_processors + 1} processing workers")
    
    async def _start_monitoring_tasks(self):
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.active_processors.append(monitoring_task)
        
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self.active_processors.append(metrics_task)
    
    async def _intelligence_processing_worker(self, worker_id: str) -> None:
        while not self.shutdown_event.is_set():
            try:
                raw_intelligence = await asyncio.wait_for(
                    self.intelligence_queue.get(), timeout=1.0
                )
                
                if raw_intelligence is None:
                    break
                
                processing_start = time.time()
                
                package = await self._process_raw_intelligence(raw_intelligence, worker_id)
                
                if package:
                    await self.routing_queue.put(package)
                    
                    processing_time = time.time() - processing_start
                    self.processing_metrics['packages_processed'] += 1
                    
                    current_avg = self.processing_metrics['average_processing_time']
                    processed_count = self.processing_metrics['packages_processed']
                    self.processing_metrics['average_processing_time'] = (
                        (current_avg * (processed_count - 1) + processing_time) / processed_count
                    )
                
                self.intelligence_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processing worker {worker_id} error: {e}")
                self.processing_metrics['errors_encountered'] += 1
                await asyncio.sleep(1)
    
    async def _intelligence_routing_worker(self):
        while not self.shutdown_event.is_set():
            try:
                package = await asyncio.wait_for(
                    self.routing_queue.get(), timeout=1.0
                )
                
                if package is None:
                    break
                
                await self._route_intelligence_package(package)
                
                self.processing_metrics['packages_routed'] += 1
                self.routing_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Routing worker error: {e}")
                self.processing_metrics['errors_encountered'] += 1
                await asyncio.sleep(1)
    
    async def _process_raw_intelligence(self, raw_intelligence: Dict[str, Any], worker_id: str) -> Optional[IntelligencePackage]:
        try:
            package_id = f"osint_{int(time.time())}_{hashlib.md5(str(raw_intelligence).encode()).hexdigest()[:8]}"
            
            classification, confidence_score = await self.classifier.classify_intelligence(raw_intelligence)
            self.processing_metrics['classifications_completed'] += 1
            
            threat_indicators = self._extract_threat_indicators(raw_intelligence)
            attribution_data = self._extract_attribution_data(raw_intelligence)
            
            package = IntelligencePackage(
                package_id=package_id,
                classification=classification,
                confidence_score=confidence_score,
                threat_indicators=threat_indicators,
                attribution_data=attribution_data,
                correlation_markers=[],
                raw_intelligence=raw_intelligence,
                source_metadata=raw_intelligence.get('source_metadata', {}),
                collection_timestamp=datetime.fromisoformat(raw_intelligence.get('collection_timestamp', datetime.now(timezone.utc).isoformat())),
                processing_timestamp=datetime.now(timezone.utc)
            )
            
            if self.config['quality_assessment']['quality_assessment_enabled']:
                package.quality_score = self.quality_assessor.assess_intelligence_quality(package)
                
                if (package.quality_score < self.config['quality_assessment']['minimum_quality_threshold'] and
                    self.config['quality_assessment']['auto_discard_low_quality']):
                    logger.debug(f"Discarding low quality intelligence package: {package_id}")
                    return None
            
            if self.config['correlation']['correlation_enabled']:
                correlations = await self.correlation_engine.correlate_intelligence(package)
                package.correlation_markers = [f"correlation_{c.correlation_id}" for c in correlations]
                self.processing_metrics['correlations_found'] += len(correlations)
            
            package.actionable_intelligence = self._generate_actionable_intelligence(package)
            package.roe_compliance_flags = self._assess_roe_compliance(package)
            
            await self.storage.store_intelligence_package(package)
            
            logger.debug(f"Processed intelligence package: {package_id} by {worker_id}")
            return package
            
        except Exception as e:
            logger.error(f"Intelligence processing failed: {e}")
            return None
    
    def _extract_threat_indicators(self, raw_intelligence: Dict[str, Any]) -> List[str]:
        indicators = []
        
        if 'threat_indicators' in raw_intelligence:
            indicators.extend(raw_intelligence['threat_indicators'])
        
        if 'iocs' in raw_intelligence:
            ioc_data = raw_intelligence['iocs']
            if isinstance(ioc_data, dict):
                for ioc_type, ioc_list in ioc_data.items():
                    if isinstance(ioc_list, list):
                        indicators.extend(ioc_list)
        
        content_text = str(raw_intelligence.get('content', ''))
        indicators.extend(self._extract_indicators_from_text(content_text))
        
        return list(set(indicators))[:50]
    
    def _extract_attribution_data(self, raw_intelligence: Dict[str, Any]) -> Dict[str, Any]:
        attribution = {}
        
        if 'attribution' in raw_intelligence:
            attribution.update(raw_intelligence['attribution'])
        
        if 'metadata' in raw_intelligence:
            metadata = raw_intelligence['metadata']
            if 'source_credibility' in metadata:
                attribution['source_credibility'] = metadata['source_credibility']
            if 'collection_method' in metadata:
                attribution['collection_method'] = metadata['collection_method']
        
        return attribution
    
    def _extract_indicators_from_text(self, text: str) -> List[str]:
        import re
        indicators = []
        
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        indicators.extend(re.findall(ip_pattern, text))
        
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        indicators.extend(re.findall(domain_pattern, text))
        
        hash_pattern = r'\b[a-fA-F0-9]{32,64}\b'
        indicators.extend(re.findall(hash_pattern, text))
        
        return indicators
    
    def _generate_actionable_intelligence(self, package: IntelligencePackage) -> List[str]:
        actionable = []
        
        if package.classification == IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT:
            actionable.extend([
                "immediate_network_isolation_recommended",
                "critical_system_protection_required",
                "emergency_response_team_notification"
            ])
        elif package.classification == IntelligenceClassification.ADVANCED_PERSISTENT_THREAT:
            actionable.extend([
                "enhanced_monitoring_deployment",
                "network_segmentation_hardening",
                "threat_hunting_activation"
            ])
        elif package.classification == IntelligenceClassification.TARGETED_INTRUSION:
            actionable.extend([
                "user_awareness_campaign",
                "endpoint_protection_enhancement",
                "access_control_review"
            ])
        elif package.classification == IntelligenceClassification.CORPORATE_SURVEILLANCE:
            actionable.extend([
                "privacy_protection_measures",
                "data_classification_review",
                "communication_security_enhancement"
            ])
        
        if package.confidence_score > 0.8:
            actionable.append("high_confidence_intelligence")
        
        if len(package.threat_indicators) > 10:
            actionable.append("multiple_indicators_correlation")
        
        return actionable
    
    def _assess_roe_compliance(self, package: IntelligencePackage) -> List[str]:
        compliance_flags = []
        
        compliance_flags.append("roe_level_1_observe_compliant")
        
        if package.classification in [
            IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT,
            IntelligenceClassification.ADVANCED_PERSISTENT_THREAT
        ]:
            compliance_flags.append("escalation_consideration_required")
        
        if package.confidence_score > 0.9:
            compliance_flags.append("high_confidence_authorization")
        
        if len(package.threat_indicators) > 20:
            compliance_flags.append("extensive_indicator_set")
        
        return compliance_flags
    
    async def _route_intelligence_package(self, package: IntelligencePackage) -> None:
        try:
            submission_result = await self.orchestrator_interface.submit_intelligence_package(package)
            
            if submission_result.get('success', False):
                logger.info(f"Intelligence package routed successfully: {package.package_id}")
                
                if package.classification in [
                    IntelligenceClassification.CRITICAL_INFRASTRUCTURE_THREAT,
                    IntelligenceClassification.ADVANCED_PERSISTENT_THREAT
                ] and package.confidence_score > 0.8:
                    
                    overlay_result = await self.orchestrator_interface.request_container_overlay(
                        container_type='osint_collection',
                        authorized_actions=['passive_monitoring', 'intelligence_gathering'],
                        roe_level=1
                    )
                    
                    if overlay_result.get('success', False):
                        logger.info(f"Container overlay requested for enhanced collection: {package.package_id}")
            else:
                logger.error(f"Intelligence package routing failed: {submission_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Intelligence package routing error: {e}")
    
    async def _monitoring_loop(self):
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(60)
                
                queue_sizes = {
                    'intelligence_queue': self.intelligence_queue.qsize(),
                    'processing_queue': self.processing_queue.qsize(),
                    'routing_queue': self.routing_queue.qsize()
                }
                
                if any(size > 100 for size in queue_sizes.values()):
                    logger.warning(f"High queue sizes detected: {queue_sizes}")
                
                uptime = (datetime.now(timezone.utc) - self.processing_metrics['start_time']).total_seconds() / 3600
                logger.info(f"OSINT Orchestrator status - Uptime: {uptime:.1f}h, "
                           f"Processed: {self.processing_metrics['packages_processed']}, "
                           f"Routed: {self.processing_metrics['packages_routed']}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    async def _metrics_collection_loop(self):
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(300)
                
                metrics_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'processing_metrics': self.processing_metrics.copy(),
                    'queue_sizes': {
                        'intelligence_queue': self.intelligence_queue.qsize(),
                        'processing_queue': self.processing_queue.qsize(),
                        'routing_queue': self.routing_queue.qsize()
                    },
                    'system_metrics': {
                        'cpu_usage': psutil.cpu_percent(),
                        'memory_usage': psutil.virtual_memory().percent,
                        'disk_usage': psutil.disk_usage('/').percent
                    }
                }
                
                metrics_file = Path('data/metrics/osint_orchestrator_metrics.json')
                metrics_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(metrics_file, 'w') as f:
                    json.dump(metrics_data, f, indent=2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
    
    async def submit_raw_intelligence(self, raw_intelligence: Dict[str, Any]) -> bool:
        try:
            await self.intelligence_queue.put(raw_intelligence)
            return True
        except Exception as e:
            logger.error(f"Intelligence submission failed: {e}")
            return False
    
    async def get_operational_status(self) -> Dict[str, Any]:
        uptime = (datetime.now(timezone.utc) - self.processing_metrics['start_time']).total_seconds() / 3600
        
        return {
            'status': 'operational',
            'uptime_hours': uptime,
            'processing_metrics': self.processing_metrics.copy(),
            'queue_status': {
                'intelligence_queue': self.intelligence_queue.qsize(),
                'processing_queue': self.processing_queue.qsize(),
                'routing_queue': self.routing_queue.qsize()
            },
            'worker_status': {
                'active_processors': len([p for p in self.active_processors if not p.done()]),
                'failed_processors': len([p for p in self.active_processors if p.done() and p.exception()])
            },
            'configuration': {
                'correlation_enabled': self.config['correlation']['correlation_enabled'],
                'quality_assessment_enabled': self.config['quality_assessment']['quality_assessment_enabled'],
                'max_concurrent_processors': self.config['processing']['max_concurrent_processors']
            },
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self):
        logger.info("Initiating OSINT Orchestrator shutdown")
        
        self.shutdown_event.set()
        
        await self.intelligence_queue.put(None)
        await self.routing_queue.put(None)
        
        for processor in self.active_processors:
            processor.cancel()
        
        await asyncio.gather(*self.active_processors, return_exceptions=True)
        
        await self.orchestrator_interface.close()
        
        logger.info("OSINT Orchestrator shutdown complete")


async def create_osint_orchestrator(config_path: str = '/etc/arcs/osint_orchestrator.yaml') -> OSINTOrchestrator:
    orchestrator = OSINTOrchestrator(config_path)
    
    if await orchestrator.initialize():
        return orchestrator
    else:
        raise RuntimeError("OSINT Orchestrator initialization failed")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ARCS OSINT Orchestrator')
    parser.add_argument('--config', default='/etc/arcs/osint_orchestrator.yaml',
                       help='Configuration file path')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        orchestrator = await create_osint_orchestrator(args.config)
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(orchestrator.shutdown())
        
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("ARCS OSINT Orchestrator operational - Processing intelligence")
        
        await orchestrator.shutdown_event.wait()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
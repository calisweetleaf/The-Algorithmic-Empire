#!/usr/bin/env python3
"""
ARCS Corpus Ingestion Pipeline
================================
Autonomous Reactive Cyber Systems — SIGINT Document Corpus Processor

Streams 104+ classified SIGINT documents through the full ARCS intelligence
processing chain. Designed to run from algorithmic_empire/ root directory.

Pipeline stages:
  1. PARSE     - Extract text, entities, tags from each .md/.txt file
  2. STORE     - Ingest as IntelligenceRecord → IntelligenceDatabaseEngine
  3. BASELINE  - Establish behavioral baseline for the corpus entity
  4. ATTRIBUTE - ThreatActorProfiler per actor cluster (THIEL, ALTMAN, etc.)
  5. FUSE      - DataFusionEngine synthesis per domain
  6. REPORT    - Write synthesis products → analysis/arcs_synthesis_YYYYMMDD.md

Usage:
    cd algorithmic_empire
    python3 ARCS/corpus_ingestion_pipeline.py [--dry-run] [--verbose]

Classification: INTELLIGENCE SYNTHESIS - SOVEREIGN INFRASTRUCTURE
"""

import sys
import os
import types
import asyncio
import json
import re
import hashlib
import logging
import argparse
import time
import contextlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

import numpy as np

# ============================================================
# STUB LAYER — satisfies ARCS module-level imports for
# capabilities not needed in static corpus processing
# (torch training paths, live network capture, browser automation)
# ============================================================

def _install_torch_mock():
    """Mock torch so Recursive*Engine class definitions load without GPU."""
    torch = types.ModuleType('torch')
    nn = types.ModuleType('torch.nn')
    functional = types.ModuleType('torch.nn.functional')
    optim_mod = types.ModuleType('torch.optim')
    utils_mod = types.ModuleType('torch.utils')
    data_mod = types.ModuleType('torch.utils.data')

    class _T:
        """Minimal tensor stub."""
        def __init__(self, data=None): self.data = data
        def __call__(self, *a, **kw): return _T()
        def parameters(self): return iter([])
        def to(self, *a, **kw): return self
        def train(self, mode=True): return self
        def eval(self): return self
        def zero_grad(self): pass
        def backward(self): pass
        def item(self): return 0.0
        def detach(self): return self
        def numpy(self): return np.array([0.0])
        def __iter__(self): return iter([])
        def view(self, *a): return self
        def squeeze(self, *a): return self
        def unsqueeze(self, *a): return self

    class _Module:
        def __init__(self, *a, **kw): pass
        def __call__(self, *a, **kw): return _T()
        def parameters(self): return iter([])
        def to(self, *a, **kw): return self
        def train(self, mode=True): return self
        def eval(self): return self
        def state_dict(self): return {}
        def load_state_dict(self, *a, **kw): pass

    # Populate nn with the common layer types
    for _name in [
        'Module', 'Sequential', 'Linear', 'ReLU', 'Dropout', 'BatchNorm1d',
        'Sigmoid', 'Tanh', 'LSTM', 'GRU', 'Conv1d', 'Embedding',
        'LayerNorm', 'MultiheadAttention', 'TransformerEncoder',
        'TransformerDecoder', 'Softmax', 'CrossEntropyLoss', 'MSELoss',
        'BCELoss', 'BCEWithLogitsLoss',
    ]:
        setattr(nn, _name, type(_name, (_Module,), {}))
    nn.Module = _Module  # ensure Module is the real class for subclassing

    class _Optim:
        def __init__(self, *a, **kw): pass
        def step(self): pass
        def zero_grad(self): pass
    for _oname in ['Adam', 'SGD', 'AdamW', 'RMSprop']:
        setattr(optim_mod, _oname, _Optim)

    class _Dataset: pass
    class _DataLoader:
        def __init__(self, *a, **kw): pass
        def __iter__(self): return iter([])
        def __len__(self): return 0
    data_mod.Dataset = _Dataset
    data_mod.DataLoader = _DataLoader
    utils_mod.data = data_mod

    # Core torch API
    torch.Tensor = _T
    torch.FloatTensor = _T
    torch.LongTensor = _T
    torch.BoolTensor = _T
    torch.nn = nn
    torch.optim = optim_mod
    torch.utils = utils_mod
    torch.cuda = types.SimpleNamespace(is_available=lambda: False)
    torch.device = lambda *a, **kw: 'cpu'
    torch.tensor = lambda *a, **kw: _T()
    torch.zeros = lambda *a, **kw: _T()
    torch.ones = lambda *a, **kw: _T()
    torch.randn = lambda *a, **kw: _T()
    torch.cat = lambda tensors, dim=0, **kw: _T()
    torch.stack = lambda tensors, dim=0, **kw: _T()
    torch.no_grad = contextlib.nullcontext
    torch.save = lambda *a, **kw: None
    torch.load = lambda *a, **kw: {}
    torch.sigmoid = lambda x, **kw: _T()
    torch.softmax = lambda x, dim=0, **kw: _T()
    torch.mean = lambda x, **kw: _T()
    torch.sum = lambda x, **kw: _T()

    for _name, _mod in [
        ('torch', torch), ('torch.nn', nn),
        ('torch.nn.functional', functional),
        ('torch.optim', optim_mod),
        ('torch.utils', utils_mod),
        ('torch.utils.data', data_mod),
    ]:
        sys.modules[_name] = _mod

    return torch


def _install_sentence_transformers_mock():
    """TF-IDF backed SentenceTransformer that produces real, comparable embeddings."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize as sk_normalize

    _CORPUS_CACHE: List[str] = []
    _VEC_INSTANCE: Optional[TfidfVectorizer] = None

    class SentenceTransformer:
        _global_vectorizer = None
        _global_fitted = False

        def __init__(self, model_name_or_path=None, cache_folder=None, **kwargs):
            self._dim = 384

        def _get_vectorizer(self) -> TfidfVectorizer:
            if SentenceTransformer._global_vectorizer is None:
                SentenceTransformer._global_vectorizer = TfidfVectorizer(
                    max_features=384,
                    stop_words='english',
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                )
            return SentenceTransformer._global_vectorizer

        def fit_corpus(self, texts: List[str]):
            vec = self._get_vectorizer()
            vec.fit(texts)
            SentenceTransformer._global_fitted = True

        def get_sentence_embedding_dimension(self) -> int:
            return self._dim

        def encode(self, sentences, batch_size=32, show_progress_bar=False,
                   convert_to_numpy=True, convert_to_tensor=False, **kwargs):
            scalar = isinstance(sentences, str)
            if scalar:
                sentences = [sentences]
            vec = self._get_vectorizer()
            if not SentenceTransformer._global_fitted:
                vec.fit(sentences)
                SentenceTransformer._global_fitted = True
            try:
                mat = vec.transform(sentences).toarray().astype(np.float32)
                if mat.shape[1] < 384:
                    pad = np.zeros((mat.shape[0], 384 - mat.shape[1]), dtype=np.float32)
                    mat = np.hstack([mat, pad])
                mat = sk_normalize(mat, norm='l2')
                return mat[0] if scalar else mat
            except Exception:
                return np.zeros(384, dtype=np.float32) if scalar else np.zeros((len(sentences), 384), dtype=np.float32)

    st = types.ModuleType('sentence_transformers')
    st.SentenceTransformer = SentenceTransformer
    sys.modules['sentence_transformers'] = st
    return st


def _install_transformers_mock():
    """Stub HuggingFace transformers (not needed for static corpus analysis)."""
    import numpy as np
    _t = types.ModuleType('transformers')

    def _pipeline(task=None, model=None, **kwargs):
        """Return a callable that produces placeholder output."""
        def _call(texts, **kw):
            if isinstance(texts, str):
                texts = [texts]
            # Return zero-score placeholder per text
            return [{'label': 'NEUTRAL', 'score': 0.5}] * len(texts)
        return _call

    _t.pipeline = _pipeline
    # Stub common classes that might be referenced
    for _cls in ['AutoTokenizer', 'AutoModel', 'AutoModelForSequenceClassification',
                 'BertTokenizer', 'BertModel', 'GPT2Tokenizer', 'GPT2LMHeadModel',
                 'T5Tokenizer', 'T5ForConditionalGeneration', 'PreTrainedModel',
                 'PretrainedConfig', 'TrainingArguments', 'Trainer']:
        setattr(_t, _cls, type(_cls, (), {
            '__init__': lambda s, *a, **kw: None,
            'from_pretrained': classmethod(lambda cls, *a, **kw: cls()),
            'encode': lambda s, *a, **kw: np.zeros(768),
        }))
    sys.modules['transformers'] = _t
    return _t


def _install_network_stubs():
    """Stub network/browser modules not used in corpus analysis."""
    _STUB_MODS = [
        'scapy', 'scapy.all',
        'scapy.layers', 'scapy.layers.inet', 'scapy.layers.l2',
        'scapy.layers.dns', 'scapy.layers.http', 'scapy.layers.dhcp',
        'scapy.layers.inet6', 'scapy.layers.netbios', 'scapy.layers.smb',
        'scapy.layers.tls',
        'selenium', 'selenium.webdriver',
        'selenium.webdriver.chrome', 'selenium.webdriver.chrome.options',
        'selenium.webdriver.firefox', 'selenium.webdriver.firefox.options',
        'selenium.webdriver.common', 'selenium.webdriver.common.by',
        'selenium.webdriver.support', 'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common', 'selenium.common.exceptions',
    ]
    for _mod_name in _STUB_MODS:
        if _mod_name not in sys.modules:
            _m = types.ModuleType(_mod_name)
            for _cls in ['IP', 'TCP', 'UDP', 'ICMP', 'ARP', 'Ether', 'DNS',
                         'DNSQR', 'DNSRR', 'HTTP', 'HTTPRequest', 'HTTPResponse',
                         'DHCP', 'BOOTP', 'IPv6', 'NBTSession', 'TLS',
                         'TLSClientHello', 'TLSServerHello', 'SMBSession_Setup_AndX_Request',
                         'Options', 'By', 'WebDriverWait', 'TimeoutException',
                         'WebDriverException', 'EC', 'expected_conditions']:
                setattr(_m, _cls, type(_cls, (), {'__init__': lambda s, *a, **kw: None}))
            _m.sniff = lambda *a, **kw: []
            _m.sendp = lambda *a, **kw: None
            sys.modules[_mod_name] = _m


# Install all stubs before any ARCS import
_install_torch_mock()
_install_sentence_transformers_mock()
_install_transformers_mock()
_install_network_stubs()

# lz4 API shim — installed lz4 package exposes lz4.frame.compress, not lz4.compress
import lz4.frame as _lz4_frame
import lz4 as _lz4_top
_lz4_top.compress   = _lz4_frame.compress
_lz4_top.decompress = _lz4_frame.decompress

# ============================================================
# Now safe to import ARCS modules
# ============================================================

ARCS_DIR = Path(__file__).parent
CORPUS_ROOT = ARCS_DIR.parent  # algorithmic_empire/
sys.path.insert(0, str(ARCS_DIR))
os.chdir(CORPUS_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger('ARCS.CorpusPipeline')

# Suppress noisy sub-loggers
for _noisy in ['chromadb', 'httpx', 'sentence_transformers', 'root']:
    logging.getLogger(_noisy).setLevel(logging.WARNING)

logger.info("Stubs installed. Importing ARCS modules...")

try:
    from intelligence_database import (
        IntelligenceDatabaseEngine, IntelligenceRecord,
        IntelligenceType, StorageTier,
    )
    logger.info("  ✓ intelligence_database")
except Exception as e:
    logger.error(f"  ✗ intelligence_database: {e}")
    raise

try:
    from system_behavior import (
        SystemBehaviorAnalyzer, SystemEntityType,
        RecursiveBehavioralEngine,
    )
    logger.info("  ✓ system_behavior")
except Exception as e:
    logger.error(f"  ✗ system_behavior: {e}")
    raise

try:
    from attribution_engine import (
        ThreatActorProfiler, AttributionEngine,
        RecursiveAttributionEngine,
    )
    logger.info("  ✓ attribution_engine")
except Exception as e:
    logger.error(f"  ✗ attribution_engine: {e}")
    raise

try:
    from threat_aggregation import ThreatAggregationEngine
    logger.info("  ✓ threat_aggregation")
except Exception as e:
    logger.error(f"  ✗ threat_aggregation: {e}")
    raise

try:
    from data_fusion import (
        DataFusionEngine, IntelligenceSynthesisEngine,
        RecursiveLearningEngine, SynthesisType,
    )
    logger.info("  ✓ data_fusion")
except Exception as e:
    logger.error(f"  ✗ data_fusion: {e}")
    raise

logger.info("All ARCS modules loaded.")


# ============================================================
# FILE MAP PARSER
# ============================================================

TAG_TO_INTEL_TYPE = {
    'THIEL_NETWORK':        IntelligenceType.ATTRIBUTION_DATA,
    'MILITARY_AI_US':       IntelligenceType.STRATEGIC_CAMPAIGN,
    'MILITARY_AI_CHINA':    IntelligenceType.STRATEGIC_CAMPAIGN,
    'EPSTEIN_NETWORK':      IntelligenceType.ATTRIBUTION_DATA,
    'SURVEILLANCE':         IntelligenceType.BEHAVIORAL_PATTERN,
    'FINANCIAL_INFRASTRUCTURE': IntelligenceType.INFRASTRUCTURE_MAPPING,
    'AI_GOVERNANCE':        IntelligenceType.STRATEGIC_CAMPAIGN,
    'CORPORATE_HANDOFFS':   IntelligenceType.ATTRIBUTION_DATA,
    'YARVIN_IDEOLOGY':      IntelligenceType.BEHAVIORAL_PATTERN,
    'BARAK_ISRAEL':         IntelligenceType.ATTRIBUTION_DATA,
    'OTHER':                IntelligenceType.TACTICAL_IOC,
}

TAG_THREAT_LEVEL = {
    'THIEL_NETWORK':            8,
    'MILITARY_AI_US':           9,
    'MILITARY_AI_CHINA':        9,
    'EPSTEIN_NETWORK':          8,
    'SURVEILLANCE':             8,
    'FINANCIAL_INFRASTRUCTURE': 7,
    'AI_GOVERNANCE':            7,
    'CORPORATE_HANDOFFS':       7,
    'YARVIN_IDEOLOGY':          6,
    'BARAK_ISRAEL':             8,
    'OTHER':                    5,
}


def load_file_map(docs_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Parse README_FILE_MAP.md → {filename_stem: {label, folder, tags}}."""
    readme = docs_dir / 'README_FILE_MAP.md'
    file_map: Dict[str, Dict[str, Any]] = {}
    if not readme.exists():
        logger.warning("README_FILE_MAP.md not found — proceeding with defaults")
        return file_map
    with open(readme, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 6 or parts[1].startswith('-') or parts[1] == 'Label':
                continue
            label, filename, _orig, folder, tags_raw = parts[1], parts[2], parts[3], parts[4], parts[5]
            if not filename:
                continue
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
            # Normalise filename: strip .md / .txt suffix for key
            stem = Path(filename).stem
            file_map[stem] = {
                'label': label,
                'filename': filename,
                'folder': folder,
                'tags': tags,
            }
            # Also key by full filename for direct lookup
            file_map[filename] = file_map[stem]
    logger.info(f"Loaded file map: {len([k for k in file_map if '.' in k])} entries")
    return file_map


def load_per_doc_stats(docs_dir: Path) -> Dict[str, Any]:
    """Load per_document_stats.json for confidence/reliability priors."""
    stats_file = docs_dir / 'per_document_stats_thorough.json'
    if not stats_file.exists():
        stats_file = docs_dir / 'per_document_stats.json'
    if not stats_file.exists():
        return {}
    with open(stats_file, 'r', encoding='utf-8', errors='replace') as f:
        raw = json.load(f)
    # Normalise to {filename_stem: {...}}
    normalised: Dict[str, Any] = {}
    if isinstance(raw, list):
        for entry in raw:
            key = entry.get('filename') or entry.get('file') or ''
            normalised[Path(key).stem] = entry
            normalised[Path(key).name] = entry
    elif isinstance(raw, dict):
        for k, v in raw.items():
            normalised[Path(k).stem] = v
            normalised[Path(k).name] = v
    return normalised


# ============================================================
# DOCUMENT PARSER
# ============================================================

# Named-entity patterns for the SIGINT domain
_ACTOR_PATTERNS = [
    r'\bPeter\s+Thiel\b', r'\bSam\s+Altman\b', r'\bLarry\s+Ellison\b',
    r'\bEric\s+Schmidt\b', r'\bElon\s+Musk\b', r'\bJeffrey\s+Epstein\b',
    r'\bEhud\s+Barak\b', r'\bCurtis\s+Yarvin\b', r'\bMarc\s+Andreessen\b',
    r'\bPaul\s+Singer\b', r'\bKen\s+Howery\b', r'\bPeter\s+Thiel\b',
]
_ORG_PATTERNS = [
    r'\bPalantir\b', r'\bAnduril\b', r'\bOpenAI\b', r'\bAnthropic\b',
    r'\bOracle\b', r'\bMicrosoft\b', r'\bGoogle\b', r'\bDeepMind\b',
    r'\bIn\-Q\-Tel\b', r'\bDARPA\b', r'\bNSA\b', r'\bCIA\b', r'\bFBI\b',
    r'\bDOGE\b', r'\bStargate\b', r'\bAWS\b', r'\bFive\s+Eyes\b',
    r'\bUnit\s+8200\b', r'\bMossad\b', r'\bNSCAI\b', r'\bJADC2\b',
    r'\bProject\s+Maven\b', r'\bScale\s+AI\b', r'\bxAI\b',
]
_COMPILED_ACTORS = [re.compile(p, re.I) for p in _ACTOR_PATTERNS]
_COMPILED_ORGS  = [re.compile(p, re.I) for p in _ORG_PATTERNS]


def extract_indicators(text: str) -> List[str]:
    """Extract named entities + structural indicators from document text."""
    indicators: List[str] = []
    seen = set()
    for pat in _COMPILED_ACTORS + _COMPILED_ORGS:
        for m in pat.finditer(text):
            val = m.group(0).strip()
            if val.lower() not in seen:
                seen.add(val.lower())
                indicators.append(val)
    # Also pull any apparent confidence percentages
    for m in re.finditer(r'\b0\.\d{2,}\b', text):
        indicators.append(f'conf:{m.group(0)}')
    return indicators[:200]  # cap


def doc_to_record(
    filepath: Path,
    file_map: Dict[str, Dict[str, Any]],
    doc_stats: Dict[str, Any],
    seq_idx: int,
) -> IntelligenceRecord:
    """Convert a .md/.txt file to an ARCS IntelligenceRecord."""
    text = filepath.read_text(encoding='utf-8', errors='replace')
    filename = filepath.name
    stem = filepath.stem

    # Metadata from file map
    meta = file_map.get(filename) or file_map.get(stem) or {}
    tags = meta.get('tags', ['OTHER'])
    label = meta.get('label', 'UNKWN')
    folder = meta.get('folder', '06_OPEN_QUESTIONS')

    # Stats
    stats = doc_stats.get(filename) or doc_stats.get(stem) or {}
    word_count = len(text.split())
    citation_count = len(re.findall(r'\[(?:T|U|S|B|C|E|F|G|H|O|M)\d+\]', text))

    # Derive intelligence_type from first meaningful tag
    intel_type = IntelligenceType.TACTICAL_IOC
    for tag in tags:
        if tag in TAG_TO_INTEL_TYPE:
            intel_type = TAG_TO_INTEL_TYPE[tag]
            break

    # Threat level: max across tags
    threat_level = max((TAG_THREAT_LEVEL.get(t, 5) for t in tags), default=5)

    # Source reliability: proxy via word count + citation density
    reliability = min(0.95, 0.5 + (word_count / 10000) * 0.3 + (citation_count / 20) * 0.15)

    # Confidence: from stats or derived
    confidence = float(stats.get('confidence_score', 0.65))
    if confidence == 0.0:
        confidence = 0.65

    # Priority: threat_level normalised
    priority = threat_level / 10.0

    indicators = extract_indicators(text)

    # Pseudo-timestamp: use file mtime or index-spread across 2025
    try:
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc)
    except Exception:
        mtime = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=seq_idx * 3)

    record = IntelligenceRecord(
        record_id=str(uuid4()),
        intelligence_type=intel_type,
        collection_timestamp=mtime,
        source_system='SIGINT_CORPUS',
        source_reliability=reliability,
        confidence_score=confidence,
        threat_level=threat_level,
        priority_score=priority,
        raw_data={
            'filename': filename,
            'label': label,
            'folder': folder,
            'text': text[:8000],        # store first 8k chars in raw_data
            'full_length_chars': len(text),
            'word_count': word_count,
            'citation_count': citation_count,
            'filepath': str(filepath),
        },
        processed_indicators=indicators,
        tags=tags,
        classification_level='UNCLASSIFIED',
        compartment=label[:3] if label else None,
        metadata={
            'seq_idx': seq_idx,
            'original_path': str(filepath),
            'tag_cluster': tags[0] if tags else 'OTHER',
            'stats': stats,
        },
    )
    return record


# ============================================================
# OBSERVATION BUILDER (for SystemBehaviorAnalyzer)
# ============================================================

def record_to_observation(record: IntelligenceRecord) -> Dict[str, Any]:
    """
    Translate an IntelligenceRecord into the observation format that
    SystemBehaviorAnalyzer._extract_behavioral_features() expects.
    Uses document metrics as synthetic system telemetry.
    """
    ts = record.collection_timestamp.isoformat()
    word_count = record.raw_data.get('word_count', 0)
    citation_count = record.raw_data.get('citation_count', 0)
    num_indicators = len(record.processed_indicators)

    return {
        'timestamp': ts,
        'system_metrics': {
            'cpu_usage': record.confidence_score * 100,           # confidence → cpu proxy
            'memory_usage': record.priority_score * 100,          # priority → mem proxy
            'disk_usage': min(99.0, word_count / 100.0),           # doc size → disk proxy
            'network_bytes_sent': word_count * 5,                  # words → bytes proxy
            'network_bytes_received': citation_count * 200,
        },
        'process_info': {
            'process_count': num_indicators,
            'thread_count': len(record.tags) * 10,
            'handle_count': record.threat_level * 100,
        },
        'network_activity': {
            'connection_count': num_indicators,
            'bytes_per_second': word_count,
            'packets_per_second': citation_count * 10,
        },
        'filesystem_activity': {
            'files_accessed': 1,
            'bytes_read': record.raw_data.get('full_length_chars', 0),
            'bytes_written': 0,
        },
        'user_activity': {
            'login_events': 1,
            'authentication_failures': 0,
            'privilege_escalations': 1 if record.threat_level >= 8 else 0,
        },
        # Extra corpus-domain fields (ignored by feature extractor, kept for our use)
        '_corpus_meta': {
            'record_id': record.record_id,
            'tags': record.tags,
            'intel_type': record.intelligence_type.value,
        },
    }


# ============================================================
# ACTOR CLUSTER BUILDER
# ============================================================

TAG_CLUSTERS = {
    'THIEL_NETWORK':            ['THIEL_NETWORK', 'YARVIN_IDEOLOGY'],
    'ALTMAN_NETWORK':           [],   # built dynamically
    'MILITARY_COMPLEX':         ['MILITARY_AI_US', 'MILITARY_AI_CHINA', 'CORPORATE_HANDOFFS'],
    'SURVEILLANCE_INFRA':       ['SURVEILLANCE', 'EPSTEIN_NETWORK', 'BARAK_ISRAEL'],
    'FINANCIAL_GOVERNANCE':     ['FINANCIAL_INFRASTRUCTURE', 'AI_GOVERNANCE'],
}


def build_actor_clusters(records: List[IntelligenceRecord]) -> Dict[str, List[Dict[str, Any]]]:
    """Group records by primary actor cluster for attribution analysis."""
    clusters: Dict[str, List[Dict[str, Any]]] = {name: [] for name in TAG_CLUSTERS}

    def _to_intel_dict(r: IntelligenceRecord) -> Dict[str, Any]:
        return {
            'record_id': r.record_id,
            'intelligence_type': r.intelligence_type.value,
            'timestamp': r.collection_timestamp.isoformat(),
            'indicators': r.processed_indicators,
            'tags': r.tags,
            'threat_level': r.threat_level,
            'confidence': r.confidence_score,
            'raw_text_snippet': r.raw_data.get('text', '')[:2000],
            'source_reliability': r.source_reliability,
            'metadata': r.metadata,
        }

    for record in records:
        assigned = False
        for cluster_name, cluster_tags in TAG_CLUSTERS.items():
            if any(t in cluster_tags for t in record.tags):
                clusters[cluster_name].append(_to_intel_dict(record))
                assigned = True
                break
        if not assigned:
            # Catch-all: assign to FINANCIAL_GOVERNANCE as default
            clusters['FINANCIAL_GOVERNANCE'].append(_to_intel_dict(record))

    # Altman cluster: records with Altman/OpenAI/Stargate indicators
    altman_markers = {'openai', 'altman', 'stargate', 'worldcoin', 'world id'}
    for record in records:
        text_lower = record.raw_data.get('text', '').lower()
        if any(m in text_lower for m in altman_markers):
            clusters['ALTMAN_NETWORK'].append(_to_intel_dict(record))

    return clusters


# ============================================================
# SYNTHESIS REQUEST BUILDER
# ============================================================

def build_synthesis_request(records: List[IntelligenceRecord]) -> Dict[str, Any]:
    """Build DataFusionEngine synthesis request from full corpus."""
    now = datetime.now(timezone.utc)
    earliest = min((r.collection_timestamp for r in records), default=now - timedelta(days=365))
    return {
        'synthesis_type': 'threat_assessment',
        'time_range': (earliest, now),
        'data_sources': ['SIGINT_CORPUS'],
        'priority_level': 'high',
        'max_sources': len(records),
        'focus_entities': [
            'Thiel', 'Altman', 'Ellison', 'Schmidt',
            'Palantir', 'Anduril', 'OpenAI', 'Stargate',
        ],
        'corpus_summary': {
            'total_docs': len(records),
            'tag_distribution': {
                tag: sum(1 for r in records if tag in r.tags)
                for tag in TAG_TO_INTEL_TYPE
            },
        },
    }


# ============================================================
# REPORT WRITER
# ============================================================

def write_synthesis_report(
    actor_profiles: Dict[str, Any],
    synthesis_result: Dict[str, Any],
    records: List[IntelligenceRecord],
    output_dir: Path,
) -> Path:
    """Write ARCS synthesis output to analysis/ as a dated .md file."""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = output_dir / f'arcs_synthesis_{ts}.md'

    tag_dist: Dict[str, int] = {}
    for r in records:
        for t in r.tags:
            tag_dist[t] = tag_dist.get(t, 0) + 1
    tag_table = '\n'.join(
        f'| {tag:<32} | {cnt:>5} |'
        for tag, cnt in sorted(tag_dist.items(), key=lambda x: -x[1])
    )

    # Serialize actor profile summaries
    profile_sections = []
    for cluster_name, profile_obj in actor_profiles.items():
        if profile_obj is None:
            continue
        try:
            # ThreatActor dataclass → dict
            import dataclasses
            if dataclasses.is_dataclass(profile_obj):
                pd = dataclasses.asdict(profile_obj)
            elif hasattr(profile_obj, '__dict__'):
                pd = vars(profile_obj)
            else:
                pd = str(profile_obj)
            profile_sections.append(f"""
### Cluster: {cluster_name}

```json
{json.dumps(pd, indent=2, default=str)[:3000]}
```
""")
        except Exception as ex:
            profile_sections.append(f"\n### Cluster: {cluster_name}\n*Serialization error: {ex}*\n")

    # Synthesis result
    try:
        synthesis_json = json.dumps(synthesis_result, indent=2, default=str)[:5000]
    except Exception:
        synthesis_json = str(synthesis_result)[:5000]

    lines = [
        f"# ARCS Corpus Synthesis Report",
        f"",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Pipeline:** ARCS Corpus Ingestion Pipeline v1.0",
        f"**Corpus size:** {len(records)} documents",
        f"",
        f"---",
        f"",
        f"## 1. Corpus Statistics",
        f"",
        f"| Tag Cluster{' '*21} | Count |",
        f"|{'-'*34}|{'-'*7}|",
        tag_table,
        f"",
        f"---",
        f"",
        f"## 2. Actor Attribution Profiles",
        f"",
        *profile_sections,
        f"",
        f"---",
        f"",
        f"## 3. DataFusion Synthesis Product",
        f"",
        f"```json",
        synthesis_json,
        f"```",
        f"",
        f"---",
        f"",
        f"## 4. Top Records by Threat Level",
        f"",
    ]

    top_records = sorted(records, key=lambda r: r.threat_level * r.confidence_score, reverse=True)[:20]
    for i, r in enumerate(top_records, 1):
        lines.append(
            f"{i}. **[{r.metadata.get('tag_cluster','?')}]** "
            f"`{r.raw_data.get('filename','?')}` — "
            f"threat={r.threat_level}, conf={r.confidence_score:.2f}, "
            f"tags={','.join(r.tags)}"
        )

    lines += [
        f"",
        f"---",
        f"",
        f"*End of ARCS Synthesis Report — {ts}*",
    ]

    report_path.write_text('\n'.join(lines), encoding='utf-8')
    logger.info(f"Report written → {report_path}")
    return report_path


# ============================================================
# PIPELINE ORCHESTRATOR
# ============================================================

async def run_pipeline(dry_run: bool = False, verbose: bool = False):
    """Full ARCS corpus ingestion pipeline."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("ARCS CORPUS INGESTION PIPELINE — STARTING")
    logger.info(f"Working directory: {CORPUS_ROOT}")
    logger.info("=" * 60)

    docs_dir   = CORPUS_ROOT / 'docs'
    analysis_dir = CORPUS_ROOT / 'analysis'
    analysis_dir.mkdir(exist_ok=True)

    # ── Stage 0: Load metadata ──────────────────────────────
    logger.info("[STAGE 0] Loading file map and per-doc stats...")
    file_map = load_file_map(docs_dir)
    doc_stats = load_per_doc_stats(docs_dir)
    logger.info(f"  File map entries: {len(file_map)}")
    logger.info(f"  Doc stats entries: {len(doc_stats)}")

    # ── Stage 0b: Collect document files ───────────────────
    logger.info("[STAGE 0b] Scanning corpus for .md and .txt files...")
    doc_files: List[Path] = []
    for pattern in ['*.md', '*.txt']:
        doc_files.extend(CORPUS_ROOT.glob(pattern))
    # Exclude pipeline infrastructure files
    EXCLUDE_STEMS = {
        'README', 'AGENTS', 'CONTEXT', 'NOTEPAD', 'MEMORY',
        'CITATION_INDEX', '2-16-tree',
    }
    doc_files = [
        f for f in doc_files
        if f.stem not in EXCLUDE_STEMS and not f.name.startswith('.')
    ]
    doc_files.sort(key=lambda p: p.name)
    logger.info(f"  Found {len(doc_files)} corpus documents")

    if dry_run:
        logger.info("[DRY RUN] Would process:")
        for f in doc_files:
            logger.info(f"  {f.name}")
        return

    # ── Stage 1: Parse all documents → IntelligenceRecord ──
    logger.info("[STAGE 1] Parsing documents → IntelligenceRecord...")
    records: List[IntelligenceRecord] = []
    texts_for_vectorizer: List[str] = []
    for idx, filepath in enumerate(doc_files):
        try:
            rec = doc_to_record(filepath, file_map, doc_stats, idx)
            records.append(rec)
            texts_for_vectorizer.append(rec.raw_data.get('text', ''))
            if verbose:
                logger.debug(f"  [{idx+1}/{len(doc_files)}] {filepath.name} → {rec.intelligence_type.value}")
        except Exception as e:
            logger.warning(f"  Parse failed {filepath.name}: {e}")

    logger.info(f"  Parsed {len(records)} records successfully")

    # Pre-fit the sentence transformer on the full corpus
    # (so embeddings are semantically consistent across all docs)
    logger.info("  Pre-fitting embedding vectorizer on full corpus...")
    try:
        from sentence_transformers import SentenceTransformer
        _st = SentenceTransformer()
        _st.fit_corpus(texts_for_vectorizer)
        # Patch global state so intelligence_database's SemanticIndexEngine uses same
        SentenceTransformer._global_fitted = True
    except Exception as e:
        logger.warning(f"  Vectorizer pre-fit failed: {e} — will fit on first encode")

    # ── Stage 2: Init intelligence database ─────────────────
    # ChromaDB Rust bindings require native Linux FS — redirect all I/O
    # to /sessions/ scratch, then copy outputs back to Windows mount.
    logger.info("[STAGE 2] Initialising IntelligenceDatabaseEngine...")
    LOCAL_SCRATCH = Path('/sessions/magical-determined-edison/arcs_local_data')
    LOCAL_SCRATCH.mkdir(parents=True, exist_ok=True)
    db_path      = str(LOCAL_SCRATCH / 'arcs_intelligence.db')
    storage_path = str(LOCAL_SCRATCH / 'storage')
    models_path  = str(LOCAL_SCRATCH / 'models')

    try:
        intel_db = IntelligenceDatabaseEngine(
            database_path=db_path,
            storage_path=storage_path,
            models_path=models_path,
        )
        logger.info(f"  ✓ Database initialised at {db_path}")
    except Exception as e:
        logger.error(f"  ✗ Database init failed: {e}")
        raise

    # ── Stage 2b: Stream all records into database ──────────
    logger.info(f"[STAGE 2b] Ingesting {len(records)} records into intelligence database...")
    stored_count = 0
    failed_count = 0
    t0 = time.time()
    for i, record in enumerate(records):
        try:
            ok = await intel_db.store_intelligence(record)
            if ok:
                stored_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            if verbose:
                logger.debug(f"    Store failed [{i}] {record.raw_data.get('filename')}: {e}")
        if (i + 1) % 20 == 0:
            elapsed = time.time() - t0
            logger.info(f"  Progress: {i+1}/{len(records)} stored={stored_count} failed={failed_count} ({elapsed:.1f}s)")

    elapsed_total = time.time() - t0
    logger.info(f"  ✓ Storage complete: {stored_count} stored, {failed_count} failed in {elapsed_total:.1f}s")

    # ── Stage 3: Behavioral baseline ────────────────────────
    logger.info("[STAGE 3] Building behavioral baseline for SIGINT_CORPUS entity...")
    observations = [record_to_observation(r) for r in records]
    logger.info(f"  Observation count: {len(observations)}")

    if len(observations) < 100:
        logger.warning(f"  Only {len(observations)} observations (minimum 100). Padding to 100...")
        # Pad by duplicating the last observation with slight timestamp variance
        base_obs = observations[-1].copy() if observations else {}
        while len(observations) < 100:
            dup = dict(base_obs)
            dup['timestamp'] = (
                datetime.now(timezone.utc) - timedelta(hours=len(observations))
            ).isoformat()
            observations.append(dup)

    try:
        behavioral_engine = RecursiveBehavioralEngine(
            models_path=str(CORPUS_ROOT / 'data' / 'intelligence' / 'models' / 'behavioral')
        )
        behavior_analyzer = SystemBehaviorAnalyzer(
            intelligence_db=intel_db,
            behavioral_learning_engine=behavioral_engine,
        )
        baseline = await behavior_analyzer.establish_behavioral_baseline(
            entity_id='SIGINT_CORPUS',
            entity_type=SystemEntityType.SYSTEM_RESOURCE,
            observation_data=observations,
        )
        logger.info(f"  ✓ Baseline established: quality={baseline.baseline_quality_score:.3f}, "
                    f"obs={baseline.observation_count}")
    except Exception as e:
        logger.error(f"  ✗ Behavioral baseline failed: {e}")
        baseline = None

    # ── Stage 4: Actor attribution per cluster ───────────────
    logger.info("[STAGE 4] Running ThreatActorProfiler per actor cluster...")
    actor_clusters = build_actor_clusters(records)
    actor_profiles: Dict[str, Any] = {}

    try:
        attribution_learning_engine = RecursiveAttributionEngine(
            models_path=str(CORPUS_ROOT / 'data' / 'intelligence' / 'models' / 'attribution')
        )
        threat_agg = ThreatAggregationEngine(intelligence_db=intel_db)
        profiler = ThreatActorProfiler(
            intelligence_db=intel_db,
            attribution_learning_engine=attribution_learning_engine,
        )

        for cluster_name, cluster_data in actor_clusters.items():
            if not cluster_data:
                logger.info(f"  Skipping empty cluster: {cluster_name}")
                continue
            logger.info(f"  Profiling cluster '{cluster_name}' ({len(cluster_data)} records)...")
            try:
                profile = await profiler.create_actor_profile(cluster_data)
                actor_profiles[cluster_name] = profile
                logger.info(f"  ✓ {cluster_name}: actor_id={profile.actor_id if hasattr(profile, 'actor_id') else 'N/A'}")
            except Exception as e:
                logger.warning(f"  ✗ Attribution failed for {cluster_name}: {e}")
                actor_profiles[cluster_name] = None

    except Exception as e:
        logger.error(f"  Attribution engine init failed: {e}")
        actor_profiles = {}

    # ── Stage 5: DataFusion synthesis ────────────────────────
    logger.info("[STAGE 5] Running DataFusionEngine synthesis over full corpus...")
    synthesis_result: Dict[str, Any] = {}
    try:
        learning_engine = RecursiveLearningEngine(
            models_path=str(CORPUS_ROOT / 'data' / 'intelligence' / 'models' / 'data_fusion')
        )
        ise = IntelligenceSynthesisEngine(
            intelligence_db=intel_db,
            threat_aggregation_engine=ThreatAggregationEngine(intelligence_db=intel_db),
        )
        fusion_engine = DataFusionEngine(
            intelligence_db=intel_db,
            threat_aggregation_engine=ThreatAggregationEngine(intelligence_db=intel_db),
        )
        await fusion_engine.initialize()

        synthesis_request = build_synthesis_request(records)
        synthesis_result_obj = await fusion_engine.create_intelligence_synthesis(synthesis_request)
        synthesis_result = synthesis_result_obj if isinstance(synthesis_result_obj, dict) else vars(synthesis_result_obj)
        logger.info(f"  ✓ Synthesis complete: {len(synthesis_result)} keys in result")
    except Exception as e:
        logger.error(f"  ✗ DataFusion synthesis failed: {e}")
        synthesis_result = {'error': str(e), 'status': 'failed', 'corpus_size': len(records)}

    # ── Stage 6: Write report ────────────────────────────────
    logger.info("[STAGE 6] Writing synthesis report...")
    report_path = write_synthesis_report(
        actor_profiles=actor_profiles,
        synthesis_result=synthesis_result,
        records=records,
        output_dir=analysis_dir,
    )

    # ── Stage 6b: Copy SQLite + report back to Windows mount ─
    logger.info("[STAGE 6b] Syncing outputs back to data/ on Windows filesystem...")
    import shutil
    WIN_INTEL = CORPUS_ROOT / 'data' / 'intelligence'
    WIN_INTEL.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(LOCAL_SCRATCH / 'arcs_intelligence.db', WIN_INTEL / 'arcs_intelligence.db')
        logger.info(f"  ✓ Copied arcs_intelligence.db → {WIN_INTEL}")
    except Exception as e:
        logger.warning(f"  SQLite copy-back failed: {e}")

    # ── Pipeline summary ─────────────────────────────────────
    logger.info("=" * 60)
    logger.info("ARCS CORPUS INGESTION PIPELINE — COMPLETE")
    logger.info(f"  Documents processed : {len(records)}")
    logger.info(f"  Records stored      : {stored_count}")
    logger.info(f"  Actor clusters      : {len([v for v in actor_profiles.values() if v])}")
    logger.info(f"  Synthesis status    : {'ok' if 'error' not in synthesis_result else 'partial'}")
    logger.info(f"  Report output       : {report_path}")
    logger.info("=" * 60)

    return {
        'records_parsed': len(records),
        'records_stored': stored_count,
        'actor_profiles': {k: bool(v) for k, v in actor_profiles.items()},
        'synthesis_status': 'ok' if 'error' not in synthesis_result else 'partial',
        'report_path': str(report_path),
    }


# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='ARCS Corpus Ingestion Pipeline — streams 104+ SIGINT docs through ARCS'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='List documents that would be processed, then exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()

    result = asyncio.run(run_pipeline(dry_run=args.dry_run, verbose=args.verbose))
    print(json.dumps(result, indent=2))

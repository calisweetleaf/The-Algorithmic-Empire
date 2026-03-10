#!/usr/bin/env python3
"""
SOMNUS V2 File System
=====================
Sovereign, self-sustaining file processing pipeline.
No paid APIs. No cloud dependencies. Graceful degradation by design.

Modules:
    sovereignty      — Dependency profiles, protocol adapters, capability registry
    enhanced_file_manager — Streaming upload manager with type classification
    persistent_processing_queue — Durable task queue with adaptive scaling
    semantic_chunking_rewrite — Enterprise semantic text chunking (NLP)
    universal_file_processors — Multi-format file processors (creative/CAD/scientific/blockchain/media)

Usage:
    from v2_file_system.sovereignty import (
        HYBRID_LOCAL, CapabilityRegistry, NullMemorySink, NullCacheStore
    )
    from v2_file_system.enhanced_file_manager import EnhancedFileUploadManager
"""

# Version and metadata
__version__ = "2.0.0-sovereign"
__author__ = "Somnus Sovereign Systems"

# Re-export sovereignty layer (always available)
from .sovereignty import (
    SovereigntyMode,
    DependencyProfile,
    FULL_LOCAL,
    HYBRID_LOCAL,
    DEVELOPMENT,
    DEFAULT_PROFILE,
    MemorySink,
    CacheStore,
    NullMemorySink,
    NullCacheStore,
    InMemoryCacheStore,
    CapabilityRegistry,
    FeatureStatus,
    BootCheckResult,
    check_feature_gate,
    validate_module_import,
    validate_all_v2_modules,
)

# Moonshine pipeline — DPO training pair generation for Aeron
from .moonshine_output import (
    DPOPair,
    MoonshineConversation,
    MoonshineInputAdapter,
    MessageSegmenter,
    ArtifactDetector,
    CorrectionDetector,
    MoonshineOutputAdapter,
)

__all__ = [
    # Version
    "__version__",
    # Sovereignty
    "SovereigntyMode",
    "DependencyProfile",
    "FULL_LOCAL",
    "HYBRID_LOCAL",
    "DEVELOPMENT",
    "DEFAULT_PROFILE",
    # Protocols & Adapters
    "MemorySink",
    "CacheStore",
    "NullMemorySink",
    "NullCacheStore",
    "InMemoryCacheStore",
    # Capability
    "CapabilityRegistry",
    "FeatureStatus",
    "BootCheckResult",
    "check_feature_gate",
    "validate_module_import",
    "validate_all_v2_modules",
    # Moonshine pipeline
    "DPOPair",
    "MoonshineConversation",
    "MoonshineInputAdapter",
    "MessageSegmenter",
    "ArtifactDetector",
    "CorrectionDetector",
    "MoonshineOutputAdapter",
]

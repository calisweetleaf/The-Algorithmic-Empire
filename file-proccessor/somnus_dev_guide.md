# SOMNUS File Processing System
## Internal Development Guide & Architecture Reference

> **Executive Summary**: SOMNUS implements a production-grade, modular file processing ecosystem supporting 50+ file formats through specialized processors, streaming uploads, persistent task queuing, local AI model integration, and semantic content analysis. This document serves as the definitive reference for system architecture, integration patterns, and development roadmap.

---

## 🏗️ System Architecture Overview

### Core Design Principles
- **Universal Processing Interface**: All file processors extend `BaseFileProcessor` with standardized `ProcessingResult` output
- **Graceful Degradation**: System operates with reduced functionality when optional dependencies unavailable
- **Local-First AI**: Privacy-preserving processing using local GGUF models, Whisper, and embedding engines
- **Security-First Design**: Multi-layer validation, content scanning, and user isolation throughout
- **Async-Native**: Full async/await implementation for optimal I/O performance
- **Resource-Aware Scaling**: Adaptive worker management based on real-time system metrics

### Integration Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    SOMNUS CORE SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│ SomnusCache │ SecurityOrchestrator │ MemorySystem │ Artifacts │
├─────────────────────────────────────────────────────────────┤
│                File Processing Layer                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│ │   Upload    │ │    Queue    │ │  Processors │             │
│ │  Manager    │ │   System    │ │   (Base)    │             │
│ └─────────────┘ └─────────────┘ └─────────────┘             │
├─────────────────────────────────────────────────────────────┤
│              Specialized Processors                        │
│ Creative │ CAD │ Scientific │ Blockchain │ Media │ Semantic │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Current File Structure

### Core System Files

#### `universal_file_processor.py`
**Purpose**: Foundation classes and specialized processors for comprehensive file format support
- `BaseFileProcessor`: Abstract interface defining processor contract
- `ProcessingCapabilities`: Runtime capability detection with graceful degradation
- `ProcessingResult`: Standardized output structure
- **Specialized Processors**:
  - `CreativeFileProcessor`: PSD, AI, SVG, Sketch, Figma, XD
  - `CADFileProcessor`: DWG, DXF, STL, OBJ, PLY, Blender
  - `ScientificFileProcessor`: MATLAB, HDF5, DICOM, NetCDF
  - `BlockchainFileProcessor`: Solidity, Vyper, Move
  - `MediaFileProcessor`: Audio/Video with FFmpeg/Librosa
  - `FallbackProcessor`: Unknown formats with heuristic analysis

#### `file_upload_manager.py` 
**Purpose**: Production streaming upload system with comprehensive validation
- `EnhancedFileUploadManager`: Main upload orchestration
- `StreamingFileHandler`: Chunked upload processing with hash validation
- `FileTypeClassifier`: Content-aware classification using magic bytes + patterns
- `SecurityValidator`: Multi-layer security scanning (virus, content, macros)
- `GGUFEmbeddingEngine`: Local embedding generation with caching

#### `processing_queue_system.py`
**Purpose**: Persistent task queue with adaptive resource management
- `PersistentProcessingEngine`: Main queue orchestration with auto-scaling
- `ResourceMonitor`: Real-time CPU/memory/disk monitoring
- `PersistentQueue`: Cache-backed priority queue with task persistence
- `TaskProcessor`: Individual processors with retry logic and error handling

#### `vl_processing_pipeline.py`
**Purpose**: Video processing with local vision-language models
- `VideoFileProcessor`: Extends BaseFileProcessor for video analysis
- `LocalVLEngine`: GGUF-based vision-language model management
- `LocalAudioProcessor`: Whisper-based audio transcription
- `VideoMetadataExtractor`: Comprehensive video metadata extraction

#### `semantic_chunking_engine.py` ⚠️ **REQUIRES REWRITE**
**Current Status**: Standalone module not integrated with SOMNUS architecture
**Issues**: 
- No BaseFileProcessor inheritance
- Missing ProcessingContext integration
- No security/cache/memory system integration
- Standalone result objects instead of ProcessingResult

---

## 🔄 Planned Semantic Chunking Rewrite

### Integration Requirements

#### 1. Core Structure Compliance
```python
class SemanticChunkingProcessor(BaseFileProcessor):
    """SOMNUS-integrated semantic text chunking processor"""
    
    def can_process(self, file_path: Path, mime_type: str) -> bool:
        """Check if file contains text suitable for semantic chunking"""
        return mime_type.startswith('text/') or self._is_text_extractable(file_path)
    
    def get_supported_extensions(self) -> Set[str]:
        """Return extensions for text-based files"""
        return {'.txt', '.md', '.rst', '.log', '.json', '.xml', '.yaml', '.csv'}
    
    async def process_file(self, file_path: Path, metadata: Dict[str, Any]) -> ProcessingResult:
        """Process file through semantic chunking pipeline"""
        context = ProcessingContext.from_metadata(metadata)
        return await self._execute_chunking_pipeline(file_path, context)
```

#### 2. Processing Context Integration
```python
@dataclass
class ProcessingContext:
    task_id: str
    session_id: str
    user_id: str
    progress_callback: Optional[Callable] = None
    security_orchestrator: Optional[Any] = None
    cache_manager: Optional[Any] = None
    memory_manager: Optional[Any] = None
    artifact_builder: Optional[Any] = None
    
    def update_progress(self, stage: str, percent: float, message: str = ""):
        """Update processing progress with callback and logging"""
```

#### 3. System Integration Points

**Cache Integration**:
```python
async def _check_cache_for_chunks(self, content_hash: str) -> Optional[List[TextChunk]]:
    cache_key = f"semantic_chunks:{content_hash}"
    return await self.cache_manager.get(cache_key)

async def _cache_chunks(self, content_hash: str, chunks: List[TextChunk]):
    cache_key = f"semantic_chunks:{content_hash}"
    await self.cache_manager.set(cache_key, chunks, ttl_seconds=86400)
```

**Security Integration**:
```python
async def _validate_chunks_security(self, chunks: List[TextChunk], context: ProcessingContext):
    """Validate all chunks through security orchestrator"""
    for chunk in chunks:
        security_result = await context.security_orchestrator.validate_message_and_execute(
            chunk.text, context.session_id, context.user_id
        )
        if not security_result.safe:
            chunk.security_warnings.append(security_result.reason)
```

**Memory System Integration**:
```python
async def _store_chunks_in_memory(self, chunks: List[TextChunk], context: ProcessingContext):
    """Store validated chunks in SOMNUS memory system"""
    for chunk in chunks:
        if chunk.is_safe:
            await context.memory_manager.push(
                content=chunk.text,
                metadata={
                    'chunk_id': chunk.chunk_id,
                    'source_file': chunk.parent_document_id,
                    'semantic_coherence': chunk.semantic_coherence,
                    'chunk_index': chunk.chunk_index
                },
                tags=['semantic_chunk', chunk.content_type.value],
                session_id=context.session_id
            )
```

#### 4. Enhanced Chunking Strategies

**Content-Aware Strategy Selection**:
- **Code Files**: Structure-based chunking respecting function/class boundaries
- **Documentation**: Header-based hierarchical chunking
- **Transcripts**: Speaker/timestamp boundary chunking
- **Research Papers**: Section-based chunking with citation preservation
- **Mixed Content**: Hybrid approach with content type detection per section

**Quality Metrics Enhancement**:
- Semantic coherence scoring using local embedding models
- Information density calculation
- Boundary quality assessment
- Cross-chunk relationship mapping

---

## 🔧 Development Implementation Plan

### Phase 1: Core Rewrite (Week 1)
1. **Create SemanticChunkingProcessor class** extending BaseFileProcessor
2. **Implement ProcessingContext integration** with progress tracking
3. **Add cache/security/memory integration points** 
4. **Migrate chunking strategies** to new architecture
5. **Add TextSanitizer integration** for input cleaning

### Phase 2: Enhanced Features (Week 2)
1. **Implement content-aware strategy selection** based on file type
2. **Add local embedding model integration** for semantic boundary detection
3. **Enhance quality metrics calculation** with coherence scoring
4. **Add cross-chunk relationship mapping**
5. **Implement artifact generation** for chunking results

### Phase 3: Optimization & Testing (Week 3)
1. **Performance optimization** for large document processing
2. **Memory usage optimization** for embedding operations
3. **Integration testing** with full SOMNUS pipeline
4. **Load testing** with various file types and sizes
5. **Documentation completion** and API finalization

---

## 📊 Supported File Format Matrix

### Current Support (50+ formats)

| Category | Formats | Processor | Features |
|----------|---------|-----------|----------|
| **Creative** | PSD, AI, SVG, Sketch, Figma, XD, EPS, INDD | CreativeFileProcessor | Layer extraction, text extraction, thumbnail generation |
| **CAD/3D** | DWG, DXF, STL, OBJ, PLY, Blender, FBX, 3DS | CADFileProcessor | Mesh analysis, material extraction, dimension calculation |
| **Scientific** | MATLAB, HDF5, DICOM, NetCDF, FITS, .nii | ScientificFileProcessor | Dataset structure, metadata extraction, anonymization |
| **Blockchain** | .sol, .vyper, .move, .rs, .go | BlockchainFileProcessor | Contract analysis, function extraction, security patterns |
| **Media** | MP4, AVI, MP3, WAV, FLAC, WebM, MKV | MediaFileProcessor | Metadata extraction, transcription, frame analysis |
| **Documents** | PDF, DOCX, PPT, Excel, TXT, MD | Various | OCR, structure analysis, table extraction |
| **Code** | Python, JS, Java, C++, HTML, CSS, SQL | CodeProcessor | Syntax analysis, function extraction, dependency mapping |
| **Data** | JSON, XML, CSV, Parquet, YAML, TOML | DataProcessor | Schema analysis, validation, structure extraction |

### Planned Additions
- **Archive Formats**: Enhanced ZIP/TAR analysis with recursive processing
- **Database Files**: SQLite, Access, PostgreSQL dump analysis
- **Specialized Formats**: GIS files (Shapefile, KML), BIM files (IFC)

---

## 🔌 Integration APIs

### Core Processing Interface
```python
# Universal processor entry point
async def process_file_universal(
    file_path: Path,
    user_id: str,
    session_id: str,
    processing_options: Dict[str, Any] = None
) -> ProcessingResult:
    """Main entry point for any file processing in SOMNUS"""
```

### Semantic Chunking Interface  
```python
# Semantic chunking specific interface
def get_semantic_chunking_processor() -> SemanticChunkingProcessor:
    """Factory function for semantic chunking processor"""
    
async def chunk_file(
    file_path: Path,
    context: ProcessingContext,
    chunking_config: ChunkingConfig = None
) -> ProcessingResult:
    """Process file through semantic chunking pipeline"""

async def chunk_text(
    raw_text: str,
    context: ProcessingContext, 
    chunking_config: ChunkingConfig = None
) -> ProcessingResult:
    """Process raw text through semantic chunking pipeline"""
```

---

## 🛡️ Security & Privacy Architecture

### Multi-Layer Security
1. **Input Validation**: File type verification, size limits, extension checking
2. **Content Scanning**: Virus scanning, malware detection, suspicious pattern analysis
3. **Text Security**: Content filtering, PII detection, inappropriate content blocking
4. **Processing Isolation**: User session isolation, resource limits, sandbox execution

### Privacy-First Design
- **Local Model Processing**: All AI/ML operations use local models (GGUF, Whisper)
- **No External API Calls**: Zero dependency on external AI services
- **Data Minimization**: Only necessary metadata stored, automatic cleanup
- **User Consent**: Explicit consent for processing and storage operations

---

## 📈 Performance & Scalability

### Resource Management
- **Adaptive Worker Scaling**: Automatic adjustment based on system load
- **Memory-Aware Processing**: Intelligent model loading based on available memory
- **Progressive Degradation**: Graceful fallbacks when resources constrained
- **Efficient Caching**: Multi-level caching with TTL and LRU policies

### Performance Targets
- **Upload Processing**: < 5 seconds for files up to 100MB
- **Text Chunking**: < 2 seconds for documents up to 1MB
- **Video Processing**: < 30 seconds for 10-minute videos
- **Memory Usage**: < 4GB for full system operation

---

## 🚀 Development Environment Setup

### Prerequisites
```bash
# Core dependencies
pip install aiofiles numpy pillow opencv-python
pip install pypdf python-docx pandas chardet
pip install psutil asyncio pathlib

# Optional AI/ML dependencies  
pip install llama-cpp-python whisper torch
pip install sentence-transformers transformers

# Specialized format dependencies (optional)
pip install psd-tools ezdxf trimesh h5py
pip install pydicom librosa ffmpeg-python
```

### Configuration
```python
# config/somnus_config.py
SOMNUS_CONFIG = {
    'max_workers': 4,
    'max_memory_mb': 4096,
    'upload_dir': 'data/uploads',
    'cache_ttl_seconds': 86400,
    'model_directory': 'models/',
    'enable_local_models': True,
    'enable_video_processing': True,
    'enable_semantic_chunking': True
}
```

---

## 📋 Testing Strategy

### Unit Testing
- **Processor Tests**: Each processor tested with sample files
- **Integration Tests**: Full pipeline testing with real-world scenarios  
- **Performance Tests**: Load testing with various file sizes
- **Security Tests**: Malicious file handling and content validation

### Test Data Requirements
- Sample files for each supported format (< 10MB each)
- Malicious file samples for security testing
- Large files for performance testing (up to 500MB)
- Multilingual content for internationalization testing

---

## 🔮 Future Roadmap

### Short Term (Next 3 Months)
- Complete semantic chunking rewrite and integration
- Enhanced video processing with scene detection
- Improved scientific data format support
- Performance optimization for large file processing

### Medium Term (6 Months)
- Multi-language processing pipeline
- Advanced document understanding with layout analysis
- Real-time collaborative processing
- Enhanced caching with distributed cache support

### Long Term (12 Months)
- Custom model training pipeline integration
- Advanced semantic search capabilities
- Multi-modal content understanding
- Enterprise deployment features

---

## 📚 Reference Documentation

### Key Classes & Interfaces
- `BaseFileProcessor`: Foundation for all file processors
- `ProcessingResult`: Standardized output structure
- `ProcessingContext`: Execution context with system integration
- `SecurityOrchestrator`: Content validation and safety
- `SomnusCache`: Distributed caching system
- `MemorySystem`: Semantic content storage

### Configuration Files
- `config/processor_config.py`: Processor-specific settings
- `config/model_config.py`: Local model configuration
- `config/security_config.py`: Security policies and limits

### Utilities
- `TextSanitizer`: Input text cleaning and normalization
- `FileValidator`: File integrity and safety validation
- `MetadataExtractor`: Universal metadata extraction
- `ProgressTracker`: Processing progress management

---

*This document serves as the authoritative reference for SOMNUS file processing system development. Keep updated as system evolves.*
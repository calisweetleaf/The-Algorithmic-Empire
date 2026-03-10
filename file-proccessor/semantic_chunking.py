#!/usr/bin/env python3
"""
SOMNUS Semantic Chunking Processor
Integrated semantic text chunking processor compliant with SOMNUS architecture
"""

import asyncio
import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from collections import Counter

# Import SOMNUS universal processor base classes
from universal_file_processors import (
    BaseFileProcessor, ProcessingResult, ProcessingCapabilities
)

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types for specialized chunking strategies"""
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    CODE = "code"
    DOCUMENTATION = "documentation"
    RESEARCH_PAPER = "research_paper"
    CONVERSATION = "conversation"
    VIDEO_TRANSCRIPT = "video_transcript"
    TECHNICAL_MANUAL = "technical_manual"
    LEGAL_DOCUMENT = "legal_document"
    STRUCTURED_DATA = "structured_data"
    MIXED_CONTENT = "mixed_content"


class ChunkingStrategy(str, Enum):
    """Available chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SENTENCE_BOUNDARY = "sentence_boundary"
    PARAGRAPH_BOUNDARY = "paragraph_boundary"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    STRUCTURAL = "structural"
    HYBRID = "hybrid"
    CONTENT_AWARE = "content_aware"


@dataclass
class ProcessingContext:
    """Processing context for SOMNUS integration"""
    task_id: str
    session_id: str
    user_id: str
    file_path: Optional[Path] = None
    
    # System integration points
    progress_callback: Optional[Callable[[float, str], None]] = None
    security_orchestrator: Optional[Any] = None
    cache_manager: Optional[Any] = None
    memory_manager: Optional[Any] = None
    artifact_builder: Optional[Any] = None
    
    # Processing state
    current_stage: str = "initializing"
    progress_percent: float = 0.0
    start_time: float = field(default_factory=time.time)
    
    def update_progress(self, stage: str, percent: float, message: str = ""):
        """Update processing progress with callback and logging"""
        self.current_stage = stage
        self.progress_percent = percent
        
        if self.progress_callback:
            try:
                self.progress_callback(percent, f"{stage}: {message}")
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
        
        logger.info(f"Semantic chunking [{self.task_id}]: {stage} ({percent:.1f}%) - {message}")
    
    def log_error(self, message: str):
        """Log error with context"""
        logger.error(f"Semantic chunking [{self.task_id}]: {message}")


@dataclass
class ChunkingConfig:
    """Configuration for chunking operations"""
    target_chunk_size: int = 1000
    max_chunk_size: int = 1500
    min_chunk_size: int = 200
    overlap_size: int = 200
    overlap_percentage: float = 0.15
    strategy: ChunkingStrategy = ChunkingStrategy.CONTENT_AWARE
    content_type: ContentType = ContentType.PLAIN_TEXT
    similarity_threshold: float = 0.7
    preserve_code_blocks: bool = True
    preserve_tables: bool = True
    preserve_lists: bool = True
    min_sentences_per_chunk: int = 2


@dataclass
class SemanticChunk:
    """Individual semantic text chunk"""
    chunk_id: str
    text: str
    content_type: ContentType
    chunk_index: int
    
    # Position metadata
    start_char: int
    end_char: int
    word_count: int
    sentence_count: int
    estimated_tokens: int
    
    # Quality metrics
    semantic_coherence: float = 0.0
    boundary_quality: float = 0.0
    information_density: float = 0.0
    
    # Relationship metadata
    parent_document_id: str = ""
    previous_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None
    
    # Security and processing
    security_warnings: List[str] = field(default_factory=list)
    is_safe: bool = True
    processing_time: float = 0.0
    
    # Semantic features
    key_phrases: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    
    @property
    def char_count(self) -> int:
        return len(self.text)
    
    @property
    def is_high_quality(self) -> bool:
        """Check if chunk meets quality thresholds"""
        return (
            self.semantic_coherence > 0.6 and
            self.boundary_quality > 0.5 and
            self.word_count >= 50 and
            self.is_safe
        )


class TextSanitizer:
    """Text sanitization utilities"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize input text for processing"""
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_file(file_path: Path) -> str:
        """Extract text content from file"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin1', 'cp1252', 'ascii']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except:
                    continue
        
        raise ValueError(f"Unable to decode text from {file_path}")


class ContentTypeDetector:
    """Detect content type for optimal chunking strategy"""
    
    def __init__(self):
        self.code_patterns = {
            'python': [r'def\s+\w+\(', r'import\s+\w+', r'class\s+\w+:', r'if\s+__name__\s*=='],
            'javascript': [r'function\s+\w+\(', r'const\s+\w+\s*=', r'=>\s*{', r'require\('],
            'markdown': [r'^#+\s', r'\*\*.*\*\*', r'\[.*\]\(.*\)', r'```'],
            'json': [r'{\s*".*":', r'\[\s*{', r'}\s*,\s*{'],
            'yaml': [r'^\w+:', r'^\s+-\s', r'---$'],
        }
        
        self.structure_patterns = {
            'research_paper': [r'abstract', r'introduction', r'methodology', r'results', r'conclusion'],
            'technical_manual': [r'installation', r'configuration', r'troubleshooting'],
            'legal_document': [r'whereas', r'therefore', r'plaintiff', r'defendant'],
        }
    
    def detect_content_type(self, text: str, filename: str = "") -> ContentType:
        """Detect content type from text and filename"""
        text_lower = text.lower()
        
        # Check filename extension
        if filename:
            ext = Path(filename).suffix.lower()
            if ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs']:
                return ContentType.CODE
            elif ext in ['.md', '.markdown']:
                return ContentType.MARKDOWN
        
        # Pattern-based detection
        code_score = self._calculate_pattern_score(text, self.code_patterns)
        if code_score > 0.1:
            return ContentType.CODE
        
        # Check for markdown
        if self._has_markdown_patterns(text):
            return ContentType.MARKDOWN
        
        # Check for structured documents
        for doc_type, patterns in self.structure_patterns.items():
            if sum(1 for pattern in patterns if pattern in text_lower) >= 2:
                if doc_type == 'research_paper':
                    return ContentType.RESEARCH_PAPER
                elif doc_type == 'technical_manual':
                    return ContentType.TECHNICAL_MANUAL
                elif doc_type == 'legal_document':
                    return ContentType.LEGAL_DOCUMENT
        
        # Check for conversation patterns
        if self._has_conversation_patterns(text):
            return ContentType.CONVERSATION
        
        return ContentType.PLAIN_TEXT
    
    def _calculate_pattern_score(self, text: str, patterns: Dict[str, List[str]]) -> float:
        """Calculate pattern matching score"""
        total_patterns = sum(len(p) for p in patterns.values())
        matches = 0
        
        for language, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                    matches += 1
        
        return matches / max(total_patterns, 1)
    
    def _has_markdown_patterns(self, text: str) -> bool:
        """Check for markdown patterns"""
        markdown_indicators = [r'^#+\s', r'\*\*.*\*\*', r'\[.*\]\(.*\)', r'```']
        return sum(1 for pattern in markdown_indicators 
                  if re.search(pattern, text, re.MULTILINE)) >= 2
    
    def _has_conversation_patterns(self, text: str) -> bool:
        """Check for conversation patterns"""
        conversation_patterns = [r'^\w+:', r'Speaker \d+:', r'\[\d{2}:\d{2}\]']
        return sum(1 for pattern in conversation_patterns
                  if re.search(pattern, text, re.MULTILINE)) >= 1


class StructuralAnalyzer:
    """Analyze document structure for intelligent chunking"""
    
    def analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure"""
        lines = text.split('\n')
        structure = {
            'headers': [],
            'code_blocks': [],
            'paragraphs': [],
            'tables': [],
            'lists': []
        }
        
        in_code_block = False
        current_paragraph = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Code blocks
            if '```' in line:
                in_code_block = not in_code_block
                if not in_code_block:
                    structure['code_blocks'].append({'line': i, 'content': line})
                continue
            
            if in_code_block:
                continue
            
            # Headers
            if re.match(r'^#+\s', line_stripped):
                structure['headers'].append({
                    'line': i,
                    'text': line_stripped,
                    'level': line_stripped.count('#')
                })
            
            # Lists
            elif re.match(r'^\s*[-*]\s', line) or re.match(r'^\s*\d+\.\s', line):
                structure['lists'].append({'line': i, 'text': line_stripped})
            
            # Tables
            elif '|' in line and line.count('|') >= 2:
                structure['tables'].append({'line': i, 'text': line_stripped})
            
            # Paragraphs
            elif line_stripped:
                current_paragraph.append((i, line_stripped))
            else:
                if current_paragraph:
                    structure['paragraphs'].append({
                        'start_line': current_paragraph[0][0],
                        'end_line': current_paragraph[-1][0],
                        'text': ' '.join([p[1] for p in current_paragraph])
                    })
                    current_paragraph = []
        
        return structure
    
    def get_structural_boundaries(self, structure: Dict[str, Any], text: str) -> List[int]:
        """Get chunk boundaries based on document structure"""
        lines = text.split('\n')
        boundaries = {0}  # Always start with beginning
        
        # Add boundaries at major headers
        for header in structure['headers']:
            if header['level'] <= 2:
                boundaries.add(header['line'])
        
        # Add boundaries around code blocks
        for code_block in structure['code_blocks']:
            boundaries.add(code_block['line'])
        
        # Convert to character positions
        char_boundaries = []
        for line_num in sorted(boundaries):
            if line_num < len(lines):
                char_pos = sum(len(lines[i]) + 1 for i in range(line_num))
                char_boundaries.append(min(char_pos, len(text)))
        
        if not char_boundaries or char_boundaries[-1] != len(text):
            char_boundaries.append(len(text))
        
        return sorted(list(set(char_boundaries)))


class SemanticChunkingProcessor(BaseFileProcessor):
    """SOMNUS-integrated semantic text chunking processor"""
    
    def __init__(self, capabilities: ProcessingCapabilities, executor: ThreadPoolExecutor):
        super().__init__(capabilities, executor)
        self.processor_name = "SemanticChunkingProcessor"
        
        # Initialize components
        self.text_sanitizer = TextSanitizer()
        self.content_detector = ContentTypeDetector()
        self.structural_analyzer = StructuralAnalyzer()
        
        # Cache for processed content
        self._similarity_cache = {}
    
    def get_supported_extensions(self) -> Set[str]:
        """Get supported file extensions for text chunking"""
        return {
            '.txt', '.md', '.rst', '.log', '.readme',
            '.json', '.xml', '.yaml', '.yml', '.toml',
            '.csv', '.tsv', '.jsonl',
            '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs',
            '.html', '.htm', '.css', '.sql',
            '.tex', '.bib', '.rtf'
        }
    
    def can_process(self, file_path: Path, mime_type: str) -> bool:
        """Check if file contains text suitable for semantic chunking"""
        ext = file_path.suffix.lower()
        
        # Check supported extensions
        if ext in self.get_supported_extensions():
            return True
        
        # Check MIME type
        if mime_type.startswith('text/'):
            return True
        
        # Check if file is text-extractable
        return self._is_text_extractable(file_path, mime_type)
    
    def _is_text_extractable(self, file_path: Path, mime_type: str) -> bool:
        """Check if text can be extracted from file"""
        try:
            # Try to read as text file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(1024)
                # Check if mostly printable characters
                printable_ratio = sum(1 for c in sample if c.isprintable() or c.isspace()) / len(sample)
                return printable_ratio > 0.7
        except:
            return False
    
    async def process_file(self, file_path: Path, metadata: Dict[str, Any]) -> ProcessingResult:
        """Process file through semantic chunking pipeline"""
        start_time = time.time()
        
        # Create processing context
        context = ProcessingContext(
            task_id=metadata.get('task_id', f"chunk_{int(time.time())}"),
            session_id=metadata.get('session_id', 'unknown'),
            user_id=metadata.get('user_id', 'unknown'),
            file_path=file_path,
            progress_callback=metadata.get('progress_callback'),
            security_orchestrator=metadata.get('security_orchestrator'),
            cache_manager=metadata.get('cache_manager'),
            memory_manager=metadata.get('memory_manager'),
            artifact_builder=metadata.get('artifact_builder')
        )
        
        try:
            context.update_progress("reading", 5.0, "Reading file content")
            
            # Extract text from file
            raw_text = self.text_sanitizer.extract_text_from_file(file_path)
            
            # Process extracted text
            return await self.chunk_text(raw_text, context)
            
        except Exception as e:
            context.log_error(f"File processing failed: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time,
                processor_used=self.processor_name
            )
    
    async def chunk_text(self, raw_text: str, context: ProcessingContext) -> ProcessingResult:
        """Process raw text through semantic chunking pipeline"""
        start_time = time.time()
        
        try:
            # Generate content hash for caching
            content_hash = hashlib.sha256(raw_text.encode()).hexdigest()
            cache_key = f"semantic_chunks:{content_hash}"
            
            context.update_progress("cache_check", 10.0, "Checking cache")
            
            # Check cache first
            if context.cache_manager:
                cached_result = await context.cache_manager.get(cache_key)
                if cached_result:
                    context.update_progress("cache_hit", 100.0, "Retrieved from cache")
                    return ProcessingResult(**cached_result)
            
            context.update_progress("sanitization", 15.0, "Sanitizing text")
            
            # Sanitize input text
            sanitized_text = self.text_sanitizer.sanitize_text(raw_text)
            
            if not sanitized_text.strip():
                return ProcessingResult(
                    success=False,
                    error_message="No text content found after sanitization",
                    processing_time=time.time() - start_time,
                    processor_used=self.processor_name
                )
            
            context.update_progress("analysis", 25.0, "Analyzing content structure")
            
            # Detect content type and analyze structure
            filename = str(context.file_path.name) if context.file_path else ""
            content_type = self.content_detector.detect_content_type(sanitized_text, filename)
            
            # Create chunking configuration
            config = ChunkingConfig(
                content_type=content_type,
                strategy=self._select_optimal_strategy(content_type)
            )
            
            context.update_progress("chunking", 40.0, f"Chunking using {config.strategy.value}")
            
            # Perform chunking
            chunks = await self._execute_chunking_strategy(sanitized_text, config, context)
            
            context.update_progress("security", 60.0, "Validating chunks security")
            
            # Security validation
            validated_chunks = await self._validate_chunks_security(chunks, context)
            
            context.update_progress("memory", 75.0, "Storing in memory system")
            
            # Store in memory system
            if context.memory_manager:
                await self._store_chunks_in_memory(validated_chunks, context)
            
            context.update_progress("artifacts", 85.0, "Creating artifacts")
            
            # Create artifacts
            if context.artifact_builder:
                await self._create_chunking_artifacts(validated_chunks, context)
            
            # Generate final result
            extracted_text = self._synthesize_chunk_text(validated_chunks)
            
            result_metadata = {
                'total_chunks': len(validated_chunks),
                'content_type': content_type.value,
                'chunking_strategy': config.strategy.value,
                'safe_chunks': len([c for c in validated_chunks if c.is_safe]),
                'avg_chunk_size': np.mean([len(c.text) for c in validated_chunks]) if validated_chunks else 0,
                'avg_semantic_coherence': np.mean([c.semantic_coherence for c in validated_chunks]) if validated_chunks else 0
            }
            
            processing_result = ProcessingResult(
                success=True,
                extracted_text=extracted_text,
                metadata=result_metadata,
                processing_time=time.time() - start_time,
                processor_used=self.processor_name,
                capabilities_used=['semantic_chunking', 'content_analysis']
            )
            
            context.update_progress("caching", 95.0, "Caching results")
            
            # Cache results
            if context.cache_manager:
                await context.cache_manager.set(cache_key, processing_result.__dict__)
            
            context.update_progress("complete", 100.0, "Processing complete")
            
            return processing_result
            
        except Exception as e:
            context.log_error(f"Text chunking failed: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time,
                processor_used=self.processor_name
            )
    
    def _select_optimal_strategy(self, content_type: ContentType) -> ChunkingStrategy:
        """Select optimal chunking strategy based on content type"""
        strategy_map = {
            ContentType.CODE: ChunkingStrategy.STRUCTURAL,
            ContentType.MARKDOWN: ChunkingStrategy.STRUCTURAL,
            ContentType.DOCUMENTATION: ChunkingStrategy.STRUCTURAL,
            ContentType.RESEARCH_PAPER: ChunkingStrategy.STRUCTURAL,
            ContentType.TECHNICAL_MANUAL: ChunkingStrategy.STRUCTURAL,
            ContentType.VIDEO_TRANSCRIPT: ChunkingStrategy.PARAGRAPH_BOUNDARY,
            ContentType.CONVERSATION: ChunkingStrategy.SENTENCE_BOUNDARY,
            ContentType.LEGAL_DOCUMENT: ChunkingStrategy.PARAGRAPH_BOUNDARY,
            ContentType.STRUCTURED_DATA: ChunkingStrategy.STRUCTURAL,
            ContentType.MIXED_CONTENT: ChunkingStrategy.HYBRID,
            ContentType.PLAIN_TEXT: ChunkingStrategy.SENTENCE_BOUNDARY
        }
        
        return strategy_map.get(content_type, ChunkingStrategy.HYBRID)
    
    async def _execute_chunking_strategy(
        self,
        text: str,
        config: ChunkingConfig,
        context: ProcessingContext
    ) -> List[SemanticChunk]:
        """Execute the selected chunking strategy"""
        
        if config.strategy == ChunkingStrategy.STRUCTURAL:
            return await self._chunk_structural(text, config, context)
        elif config.strategy == ChunkingStrategy.SENTENCE_BOUNDARY:
            return await self._chunk_sentence_boundary(text, config, context)
        elif config.strategy == ChunkingStrategy.PARAGRAPH_BOUNDARY:
            return await self._chunk_paragraph_boundary(text, config, context)
        elif config.strategy == ChunkingStrategy.HYBRID:
            return await self._chunk_hybrid(text, config, context)
        else:
            # Default to sentence boundary
            return await self._chunk_sentence_boundary(text, config, context)
    
    async def _chunk_structural(
        self,
        text: str,
        config: ChunkingConfig,
        context: ProcessingContext
    ) -> List[SemanticChunk]:
        """Chunk text using document structure analysis"""
        structure = self.structural_analyzer.analyze_structure(text)
        boundaries = self.structural_analyzer.get_structural_boundaries(structure, text)
        
        chunks = []
        document_id = context.task_id
        
        for i in range(len(boundaries) - 1):
            start_pos = boundaries[i]
            end_pos = boundaries[i + 1]
            
            chunk_text = text[start_pos:end_pos].strip()
            
            if chunk_text and len(chunk_text) >= config.min_chunk_size:
                chunk = await self._create_chunk(
                    text=chunk_text,
                    chunk_index=i,
                    start_char=start_pos,
                    end_char=end_pos,
                    config=config,
                    document_id=document_id
                )
                chunks.append(chunk)
        
        return chunks
    
    async def _chunk_sentence_boundary(
        self,
        text: str,
        config: ChunkingConfig,
        context: ProcessingContext
    ) -> List[SemanticChunk]:
        """Chunk text respecting sentence boundaries"""
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        document_id = context.task_id
        char_position = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if (current_size + sentence_size > config.target_chunk_size and 
                current_chunk and len(current_chunk) >= config.min_sentences_per_chunk):
                
                # Create chunk
                chunk_text = ' '.join(current_chunk).strip()
                chunk_start = char_position - current_size
                
                chunk = await self._create_chunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    start_char=max(0, chunk_start),
                    end_char=char_position,
                    config=config,
                    document_id=document_id
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                if config.overlap_size > 0 and len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], sentence]
                    current_size = len(current_chunk[-2]) + sentence_size
                else:
                    current_chunk = [sentence]
                    current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
            
            char_position += sentence_size + 1  # +1 for space
        
        # Handle remaining sentences
        if current_chunk:
            chunk_text = ' '.join(current_chunk).strip()
            chunk_start = char_position - current_size
            
            chunk = await self._create_chunk(
                text=chunk_text,
                chunk_index=chunk_index,
                start_char=max(0, chunk_start),
                end_char=len(text),
                config=config,
                document_id=document_id
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _chunk_paragraph_boundary(
        self,
        text: str,
        config: ChunkingConfig,
        context: ProcessingContext
    ) -> List[SemanticChunk]:
        """Chunk text by paragraph boundaries"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        document_id = context.task_id
        char_position = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            if current_size + paragraph_size > config.target_chunk_size and current_chunk:
                # Create chunk
                chunk_text = '\n\n'.join(current_chunk).strip()
                chunk_start = char_position - current_size
                
                chunk = await self._create_chunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    start_char=max(0, chunk_start),
                    end_char=char_position,
                    config=config,
                    document_id=document_id
                )
                chunks.append(chunk)
                chunk_index += 1
                
                current_chunk = [paragraph]
                current_size = paragraph_size
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size
            
            char_position += paragraph_size + 2  # +2 for \n\n
        
        # Handle remaining paragraphs
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk).strip()
            chunk_start = char_position - current_size
            
            chunk = await self._create_chunk(
                text=chunk_text,
                chunk_index=chunk_index,
                start_char=max(0, chunk_start),
                end_char=len(text),
                config=config,
                document_id=document_id
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _chunk_hybrid(
        self,
        text: str,
        config: ChunkingConfig,
        context: ProcessingContext
    ) -> List[SemanticChunk]:
        """Hybrid chunking combining structure and semantic analysis"""
        # First try structural chunking
        structure = self.structural_analyzer.analyze_structure(text)
        
        if len(structure['headers']) > 0 or len(structure['code_blocks']) > 0:
            chunks = await self._chunk_structural(text, config, context)
        else:
            chunks = await self._chunk_sentence_boundary(text, config, context)
        
        # Post-process large chunks
        final_chunks = []
        for chunk in chunks:
            if len(chunk.text) > config.max_chunk_size:
                # Subdivide large chunks
                sub_config = ChunkingConfig(
                    target_chunk_size=config.target_chunk_size // 2,
                    max_chunk_size=config.max_chunk_size,
                    content_type=config.content_type
                )
                sub_chunks = await self._chunk_sentence_boundary(chunk.text, sub_config, context)
                
                # Update chunk IDs
                for i, sub_chunk in enumerate(sub_chunks):
                    sub_chunk.chunk_id = f"{chunk.chunk_id}_sub_{i}"
                    sub_chunk.chunk_index = len(final_chunks)
                    final_chunks.append(sub_chunk)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    async def _create_chunk(
        self,
        text: str,
        chunk_index: int,
        start_char: int,
        end_char: int,
        config: ChunkingConfig,
        document_id: str
    ) -> SemanticChunk:
        """Create a SemanticChunk with quality metrics"""
        
        chunk = SemanticChunk(
            chunk_id=f"{document_id}_chunk_{chunk_index:04d}",
            text=text,
            content_type=config.content_type,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            word_count=len(text.split()),
            sentence_count=len(self._split_sentences(text)),
            estimated_tokens=len(text) // 4,
            parent_document_id=document_id
        )
        
        # Calculate quality metrics
        chunk.semantic_coherence = await self._calculate_semantic_coherence(text)
        chunk.information_density = self._calculate_information_density(text)
        chunk.boundary_quality = 0.8  # Default good boundary quality
        
        # Extract features
        chunk.key_phrases = self._extract_key_phrases(text)
        chunk.topics = self._extract_topics(text)
        
        return chunk
    
    async def _validate_chunks_security(
        self,
        chunks: List[SemanticChunk],
        context: ProcessingContext
    ) -> List[SemanticChunk]:
        """Validate all chunks through security orchestrator"""
        if not context.security_orchestrator:
            return chunks
        
        validated_chunks = []
        
        for chunk in chunks:
            try:
                # Validate chunk content
                security_result = await context.security_orchestrator.validate_message_and_execute(
                    chunk.text,
                    session_id=context.session_id,
                    user_id=context.user_id
                )
                
                if security_result.get('safe', True):
                    chunk.is_safe = True
                else:
                    chunk.is_safe = False
                    chunk.security_warnings.append(security_result.get('reason', 'Security validation failed'))
                
                validated_chunks.append(chunk)
                
            except Exception as e:
                context.log_error(f"Security validation failed for chunk {chunk.chunk_id}: {e}")
                chunk.is_safe = False
                chunk.security_warnings.append(f"Security validation error: {str(e)}")
                validated_chunks.append(chunk)
        
        return validated_chunks
    
    async def _store_chunks_in_memory(
        self,
        chunks: List[SemanticChunk],
        context: ProcessingContext
    ):
        """Store validated chunks in SOMNUS memory system"""
        for chunk in chunks:
            if chunk.is_safe:
                try:
                    await context.memory_manager.push(
                        content=chunk.text,
                        metadata={
                            'chunk_id': chunk.chunk_id,
                            'source_file': str(context.file_path) if context.file_path else 'text_input',
                            'chunk_index': chunk.chunk_index,
                            'semantic_coherence': chunk.semantic_coherence,
                            'information_density': chunk.information_density,
                            'content_type': chunk.content_type.value,
                            'word_count': chunk.word_count,
                            'key_phrases': chunk.key_phrases,
                            'topics': chunk.topics
                        },
                        tags=['semantic_chunk', chunk.content_type.value, context.task_id],
                        session_id=context.session_id
                    )
                except Exception as e:
                    context.log_error(f"Memory storage failed for chunk {chunk.chunk_id}: {e}")
    
    async def _create_chunking_artifacts(
        self,
        chunks: List[SemanticChunk],
        context: ProcessingContext
    ):
        """Create artifacts for chunking results"""
        try:
            # Create main chunking summary artifact
            chunking_summary = {
                'type': 'semantic_chunking_result',
                'source_file': str(context.file_path) if context.file_path else 'text_input',
                'total_chunks': len(chunks),
                'safe_chunks': len([c for c in chunks if c.is_safe]),
                'content_type': chunks[0].content_type.value if chunks else 'unknown',
                'processing_time': time.time() - context.start_time,
                'chunks': [
                    {
                        'chunk_id': chunk.chunk_id,
                        'text_preview': chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                        'word_count': chunk.word_count,
                        'semantic_coherence': chunk.semantic_coherence,
                        'information_density': chunk.information_density,
                        'key_phrases': chunk.key_phrases[:5],  # Top 5 phrases
                        'is_safe': chunk.is_safe
                    }
                    for chunk in chunks
                ]
            }
            
            await context.artifact_builder.create_artifact(
                artifact_type='semantic_chunking_summary',
                content=chunking_summary,
                session_id=context.session_id,
                user_id=context.user_id,
                metadata={
                    'source_file': str(context.file_path) if context.file_path else 'text_input',
                    'task_id': context.task_id,
                    'total_chunks': len(chunks)
                }
            )
            
        except Exception as e:
            context.log_error(f"Artifact creation failed: {e}")
    
    def _synthesize_chunk_text(self, chunks: List[SemanticChunk]) -> str:
        """Synthesize chunk information for ProcessingResult"""
        if not chunks:
            return "No chunks generated"
        
        safe_chunks = [c for c in chunks if c.is_safe]
        
        summary_parts = [
            f"Semantic chunking completed: {len(chunks)} total chunks, {len(safe_chunks)} safe chunks",
            f"Content type: {chunks[0].content_type.value}",
            f"Average chunk size: {np.mean([len(c.text) for c in chunks]):.0f} characters",
            f"Average semantic coherence: {np.mean([c.semantic_coherence for c in chunks]):.2f}",
            ""
        ]
        
        # Include preview of first few chunks
        for i, chunk in enumerate(safe_chunks[:3]):
            preview = chunk.text[:150] + "..." if len(chunk.text) > 150 else chunk.text
            summary_parts.append(f"Chunk {i+1}: {preview}")
            summary_parts.append("")
        
        if len(safe_chunks) > 3:
            summary_parts.append(f"... and {len(safe_chunks) - 3} more chunks")
        
        return "\n".join(summary_parts)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be enhanced with NLTK if available
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    async def _calculate_semantic_coherence(self, text: str) -> float:
        """Calculate semantic coherence score"""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 1:
            return 1.0
        
        # Simple coherence based on word overlap between sentences
        similarities = []
        for i in range(len(sentences) - 1):
            similarity = self._calculate_sentence_similarity(sentences[i], sentences[i + 1])
            similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.5
    
    def _calculate_sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate similarity between sentences using word overlap"""
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_information_density(self, text: str) -> float:
        """Calculate information density (unique words per total words)"""
        words = text.lower().split()
        
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        return unique_words / total_words
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        words = text.lower().split()
        
        # Filter stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Get most frequent words
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(10)]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topic keywords from text"""
        topics = []
        text_lower = text.lower()
        
        # Simple topic detection
        topic_keywords = {
            'technical': ['algorithm', 'data', 'analysis', 'method', 'system'],
            'programming': ['code', 'function', 'variable', 'class', 'object'],
            'business': ['business', 'strategy', 'market', 'customer', 'revenue'],
            'research': ['research', 'study', 'experiment', 'hypothesis', 'conclusion']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics


def get_semantic_chunking_processor(
    capabilities: ProcessingCapabilities = None,
    executor: ThreadPoolExecutor = None
) -> SemanticChunkingProcessor:
    """Factory function for semantic chunking processor"""
    if capabilities is None:
        capabilities = ProcessingCapabilities()
    
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=2)
    
    return SemanticChunkingProcessor(capabilities, executor)


# Example usage
if __name__ == "__main__":
    async def main():
        # Create processor
        processor = get_semantic_chunking_processor()
        
        # Example text processing
        sample_text = """
        This is a sample document that will be processed through the semantic chunking system.
        
        It contains multiple paragraphs and different types of content to demonstrate the chunking capabilities.
        
        The system should identify appropriate boundaries and create meaningful chunks.
        """
        
        # Create context
        context = ProcessingContext(
            task_id="test_chunk_001",
            session_id="test_session",
            user_id="test_user"
        )
        
        # Process text
        result = await processor.chunk_text(sample_text, context)
        
        print(f"Processing result: {result.success}")
        print(f"Chunks created: {result.metadata.get('total_chunks', 0)}")
        print(f"Processing time: {result.processing_time:.2f}s")
    
    asyncio.run(main())

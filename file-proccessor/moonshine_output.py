#!/usr/bin/env python3
"""
Moonshine Output Schema & Adapters
====================================
Standardized output formats for the Moonshine corpus-analytics pipeline.
Processes 1,385 ChatGPT conversation exports to generate DPO training pairs
for the 400M-parameter Aeron model.

OUTPUT DOES NOT MATTER TO PROJECT MOONSHINE

Classes
-------
DPOPair               — Dataclass for a single DPO training pair (JSONL record)
MoonshineConversation — Parsed ChatGPT conversation with rich metadata
MoonshineInputAdapter — Parses ChatGPT JSON export format
MessageSegmenter      — Classifies message content into semantic buckets
ArtifactDetector      — Counts code blocks, tables, terminal output, manifests
CorrectionDetector    — Detects user correction events for DPO pair generation
MoonshineOutputAdapter — Exports to SQLite / JSONL / CSV / Parquet

Design constraints
------------------
- Fully async (asyncio) throughout
- No paid API calls — all logic is local
- Never raises uncaught exceptions; always logs and degrades gracefully
- Patient/user data is never stored in plain text beyond what was in the source
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional heavy dependencies — graceful degradation
# ---------------------------------------------------------------------------
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False


# ===========================================================================
# DPOPair — one JSONL record in the DPO training file
# ===========================================================================

@dataclass
class DPOPair:
    """A single Direct Preference Optimisation training pair.

    Fields
    ------
    prompt            : The user turn (or reconstructed prompt context).
    rejected          : The original assistant response that was corrected.
    chosen            : The improved/corrected assistant response.
    correction_type   : One of "logic_error", "syntax_error", "incomplete",
                        "unclear", "style".
    confidence        : Float in [0.0, 1.0].  How confident the detector is
                        that this is a genuine correction event.
    source_conversation: UUID of the source conversation (str form).
    message_indices   : Dict with keys "user_msg", "assistant_msg",
                        "correction_msg" mapping to 0-based message indices.
    """

    prompt: str
    rejected: str
    chosen: str
    correction_type: str
    confidence: float
    source_conversation: str
    message_indices: Dict[str, int]

    # Validation constants
    VALID_CORRECTION_TYPES: frozenset = field(
        default=frozenset({"logic_error", "syntax_error", "incomplete", "unclear", "style"}),
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"DPOPair.confidence must be in [0.0, 1.0], got {self.confidence}")
        if self.correction_type not in self.VALID_CORRECTION_TYPES:
            raise ValueError(
                f"DPOPair.correction_type must be one of {self.VALID_CORRECTION_TYPES}, "
                f"got '{self.correction_type}'"
            )

    def to_jsonl_dict(self) -> Dict[str, Any]:
        """Serialize to a dict suitable for JSONL output."""
        return {
            "prompt": self.prompt,
            "rejected": self.rejected,
            "chosen": self.chosen,
            "correction_type": self.correction_type,
            "confidence": round(self.confidence, 6),
            "source_conversation": self.source_conversation,
            "message_indices": self.message_indices,
        }


# ===========================================================================
# MoonshineConversation — rich parsed ChatGPT conversation
# ===========================================================================

@dataclass
class MoonshineConversation:
    """A fully parsed ChatGPT conversation with Moonshine-specific metadata.

    Populated by MoonshineInputAdapter; consumed by all downstream components.
    """

    conversation_id: str                       # UUID from source or generated
    title: str
    model_version: str                         # e.g. "gpt-4", "gpt-4o"
    period: str                                # ISO date of first message (YYYY-MM)
    messages: List[Dict[str, Any]]             # Raw parsed message dicts
    turn_count: int = 0
    total_tokens: int = 0                      # Estimated via word count * 1.3
    topic_primary: str = ""
    artifact_count: int = 0
    correction_events: int = 0
    information_gain: float = 0.0              # Vocabulary richness proxy
    tone_cluster: str = "neutral"              # "technical", "casual", "neutral"
    segments: List[Dict[str, Any]] = field(default_factory=list)
    dpo_pairs: List[DPOPair] = field(default_factory=list)

    # ── Derived properties ──────────────────────────────────────────────────

    @property
    def csv_row(self) -> Dict[str, Any]:
        """Return a flat dict matching the CSV field spec."""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "turn_count": self.turn_count,
            "total_tokens": self.total_tokens,
            "topic_primary": self.topic_primary,
            "artifact_count": self.artifact_count,
            "correction_events": self.correction_events,
            "information_gain": round(self.information_gain, 4),
            "tone_cluster": self.tone_cluster,
            "period": self.period,
            "model_version": self.model_version,
        }


# ===========================================================================
# MoonshineInputAdapter — parses ChatGPT JSON export format
# ===========================================================================

class MoonshineInputAdapter:
    """Parses ChatGPT conversation export JSON files into MoonshineConversation objects.

    ChatGPT export format (conversations.json):
        A JSON array of conversation objects.  Each conversation has:
            id, title, create_time, update_time, mapping (dict of nodes)

    Each node in mapping has:
        id, message (nullable), parent (nullable), children (list of ids)

    Each message has:
        id, author.role ("user"|"assistant"|"tool"|"system"),
        content.content_type ("text"|"code"|"tether_browsing_display" etc.),
        content.parts (list of str or nested dicts),
        create_time (unix timestamp float or None)
    """

    _UNKNOWN_TITLE = "(untitled)"
    _TOKEN_RATIO = 1.3  # rough chars-to-tokens conversion factor

    def __init__(
        self,
        segmenter: Optional["MessageSegmenter"] = None,
        artifact_detector: Optional["ArtifactDetector"] = None,
        correction_detector: Optional["CorrectionDetector"] = None,
    ):
        self.segmenter = segmenter or MessageSegmenter()
        self.artifact_detector = artifact_detector or ArtifactDetector()
        self.correction_detector = correction_detector or CorrectionDetector()

    # ── Public API ──────────────────────────────────────────────────────────

    async def parse_file(self, file_path: Path) -> List[MoonshineConversation]:
        """Parse a ChatGPT conversations.json export file.

        Returns a list of MoonshineConversation objects, one per conversation.
        """
        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, file_path.read_bytes)
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("MoonshineInputAdapter.parse_file failed for %s: %s", file_path, exc)
            return []

        if not isinstance(data, list):
            # Some exports wrap the array in {"conversations": [...]}
            if isinstance(data, dict) and 'conversations' in data:
                data = data['conversations']
            else:
                logger.error("Unexpected ChatGPT export format in %s", file_path)
                return []

        results: List[MoonshineConversation] = []
        for raw_conv in data:
            try:
                conv = await self._parse_conversation(raw_conv)
                results.append(conv)
            except Exception as exc:
                logger.warning(
                    "Failed to parse conversation %s: %s",
                    raw_conv.get('id', 'unknown'), exc
                )
        logger.info("MoonshineInputAdapter: parsed %d conversations from %s", len(results), file_path)
        return results

    async def parse_single(self, raw: Dict[str, Any]) -> MoonshineConversation:
        """Parse a single raw conversation dict."""
        return await self._parse_conversation(raw)

    # ── Internals ───────────────────────────────────────────────────────────

    async def _parse_conversation(self, raw: Dict[str, Any]) -> MoonshineConversation:
        conv_id = raw.get('id') or str(uuid.uuid4())
        title = (raw.get('title') or self._UNKNOWN_TITLE).strip()

        # Reconstruct linear message list from the mapping DAG
        mapping = raw.get('mapping', {})
        messages = list(self._linearize_messages(mapping))

        # Date/period from create_time or first message
        create_time: Optional[float] = raw.get('create_time')
        if not create_time and messages:
            create_time = messages[0].get('create_time')
        period = self._ts_to_period(create_time)

        # Model version — found in tool messages or assistant metadata
        model_version = self._extract_model_version(raw, messages)

        # Turn count (user + assistant messages only)
        turn_count = sum(
            1 for m in messages
            if m.get('role') in {'user', 'assistant'}
        )

        # Total tokens (estimated)
        all_text = ' '.join(m.get('content', '') for m in messages if m.get('content'))
        total_tokens = int(len(all_text) / self._TOKEN_RATIO)

        # Build MoonshineConversation (we'll enrich it below)
        conv = MoonshineConversation(
            conversation_id=conv_id,
            title=title,
            model_version=model_version,
            period=period,
            messages=messages,
            turn_count=turn_count,
            total_tokens=total_tokens,
        )

        # Enrichment — run all detectors
        conv.segments = self.segmenter.segment_messages(messages)
        conv.artifact_count = self.artifact_detector.count_artifacts(messages)
        dpo_pairs = self.correction_detector.detect_pairs(conv)
        conv.dpo_pairs = dpo_pairs
        conv.correction_events = len(dpo_pairs)
        conv.information_gain = self._compute_information_gain(all_text)
        conv.tone_cluster = self.segmenter.classify_tone(messages)
        conv.topic_primary = self._infer_topic(messages)

        return conv

    def _linearize_messages(self, mapping: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Walk the DAG in creation order and yield simplified message dicts."""
        if not mapping:
            return

        # Find root node (no parent, or parent not in mapping)
        root_id: Optional[str] = None
        for node_id, node in mapping.items():
            parent = node.get('parent')
            if parent is None or parent not in mapping:
                root_id = node_id
                break

        if root_id is None:
            return

        # BFS / iterative DFS in insertion order — ChatGPT exports are trees
        stack = [root_id]
        visited: set = set()
        idx = 0

        while stack:
            current_id = stack.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            node = mapping.get(current_id)
            if node is None:
                continue

            msg = node.get('message')
            if msg:
                simplified = self._simplify_message(msg, idx)
                if simplified:
                    yield simplified
                    idx += 1

            # Queue children in order
            children = node.get('children', [])
            stack.extend(children)

    def _simplify_message(self, msg: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Extract a flat message dict from a raw ChatGPT message node."""
        if not isinstance(msg, dict):
            return None

        author = msg.get('author', {})
        role = author.get('role', 'unknown') if isinstance(author, dict) else 'unknown'
        if role == 'system':
            return None  # Skip system prompts

        content_obj = msg.get('content', {})
        content_text = ''
        if isinstance(content_obj, dict):
            parts = content_obj.get('parts', [])
            text_parts = []
            for part in parts:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and 'text' in part:
                    text_parts.append(str(part['text']))
            content_text = '\n'.join(text_parts)
        elif isinstance(content_obj, str):
            content_text = content_obj

        return {
            'index': index,
            'role': role,
            'content': content_text.strip(),
            'create_time': msg.get('create_time'),
            'id': msg.get('id', ''),
        }

    def _extract_model_version(self, raw: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
        """Best-effort model extraction from conversation metadata."""
        # Some exports have it at top level
        if 'default_model_slug' in raw:
            return str(raw['default_model_slug'])
        # Or in conversation_template_id
        tmpl = raw.get('conversation_template_id', '')
        if tmpl:
            return str(tmpl)
        return 'unknown'

    def _ts_to_period(self, ts: Optional[float]) -> str:
        if ts is None:
            return 'unknown'
        try:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return dt.strftime('%Y-%m')
        except (OSError, ValueError, OverflowError):
            return 'unknown'

    def _compute_information_gain(self, text: str) -> float:
        """Vocabulary richness as type-token ratio (capped at 1.0)."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        if not tokens:
            return 0.0
        return min(1.0, len(set(tokens)) / len(tokens))

    def _infer_topic(self, messages: List[Dict[str, Any]]) -> str:
        """Heuristic topic inference from first user message."""
        for msg in messages:
            if msg.get('role') == 'user' and msg.get('content'):
                content = msg['content'].lower()
                topic_keywords = {
                    'code': ['python', 'javascript', 'code', 'function', 'class', 'bug', 'error'],
                    'math': ['equation', 'formula', 'integral', 'derivative', 'solve', 'proof'],
                    'writing': ['write', 'essay', 'article', 'draft', 'rewrite', 'summarize'],
                    'data': ['csv', 'dataframe', 'sql', 'query', 'database', 'table'],
                    'ml': ['model', 'training', 'neural', 'machine learning', 'dataset'],
                    'system': ['linux', 'bash', 'shell', 'install', 'configure', 'docker'],
                }
                for topic, kws in topic_keywords.items():
                    if any(kw in content for kw in kws):
                        return topic
                return 'general'
        return 'unknown'


# ===========================================================================
# MessageSegmenter
# ===========================================================================

class MessageSegmenter:
    """Classifies message content into semantic segment types.

    Segment types
    -------------
    code     : Contains fenced code blocks (``` ... ```) or inline code
    prose    : Long-form explanatory text
    meta     : Short operational turns (greetings, confirmations, meta-commentary)
    casual   : Informal conversational turns
    """

    # Fenced code block: ```[optional lang]\n...\n```
    _CODE_FENCE_RE = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    # Inline code: `...`
    _INLINE_CODE_RE = re.compile(r'`[^`\n]+`')
    # Terminal output indicators
    _TERMINAL_RE = re.compile(r'^\s*\$\s', re.MULTILINE)

    # Casual / meta phrases
    _META_PHRASES = frozenset({
        'ok', 'okay', 'sure', 'thanks', 'thank you', 'got it', 'understood',
        'yes', 'no', 'yep', 'nope', 'sounds good', 'great', 'perfect', 'nice',
        'hello', 'hi', 'hey', 'bye', 'goodbye',
    })

    def segment_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return a list of segment dicts, one per message."""
        segments = []
        for msg in messages:
            content = msg.get('content', '')
            seg_type = self._classify_content(content)
            segments.append({
                'message_index': msg.get('index', -1),
                'role': msg.get('role', 'unknown'),
                'segment_type': seg_type,
                'char_count': len(content),
                'word_count': len(content.split()),
                'has_code': bool(self._CODE_FENCE_RE.search(content)),
            })
        return segments

    def _classify_content(self, content: str) -> str:
        """Return 'code' | 'prose' | 'meta' | 'casual'."""
        stripped = content.strip()
        if not stripped:
            return 'meta'

        # Code check first — highest priority
        if self._CODE_FENCE_RE.search(stripped):
            return 'code'

        word_count = len(stripped.split())

        # Very short messages are meta or casual
        if word_count <= 5:
            lower = stripped.lower().rstrip('.,!?')
            if lower in self._META_PHRASES:
                return 'meta'
            return 'casual'

        # Inline code without fences — still code-ish
        inline_hits = len(self._INLINE_CODE_RE.findall(stripped))
        if inline_hits >= 2 and word_count < 40:
            return 'code'

        # Heuristic: casual if many sentence fragments / short sentences
        sentences = re.split(r'[.!?]+', stripped)
        avg_words_per_sentence = word_count / max(len(sentences), 1)
        if avg_words_per_sentence < 8 and word_count < 60:
            return 'casual'

        return 'prose'

    def classify_tone(self, messages: List[Dict[str, Any]]) -> str:
        """Classify the overall tone of a conversation.

        Returns 'technical', 'casual', or 'neutral'.
        """
        if not messages:
            return 'neutral'

        type_counts: Dict[str, int] = {'code': 0, 'prose': 0, 'meta': 0, 'casual': 0}
        for msg in messages:
            seg = self._classify_content(msg.get('content', ''))
            type_counts[seg] = type_counts.get(seg, 0) + 1

        total = sum(type_counts.values()) or 1
        code_ratio = type_counts['code'] / total
        casual_ratio = (type_counts['casual'] + type_counts['meta']) / total

        if code_ratio >= 0.25:
            return 'technical'
        if casual_ratio >= 0.5:
            return 'casual'
        return 'neutral'


# ===========================================================================
# ArtifactDetector
# ===========================================================================

class ArtifactDetector:
    """Counts structured artifacts embedded in message content.

    Artifact types
    --------------
    code_block     : Fenced code blocks (``` ... ```)
    terminal_output: Shell/terminal session blocks (lines starting with $ or >)
    table          : Markdown tables (lines with | separators)
    manifest       : File listings, requirements.txt, package.json style content
    """

    _CODE_FENCE_RE = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    _TERMINAL_LINE_RE = re.compile(r'^\s*[\$>]\s', re.MULTILINE)
    _TABLE_ROW_RE = re.compile(r'^\|.+\|', re.MULTILINE)
    _MANIFEST_RE = re.compile(
        r'^(\S+==[\d.]+|"[\w\-@/.]+":\s*"[\^~><=\d.]+"|[\w\-]+\s+\d+\.\d+)',
        re.MULTILINE,
    )

    def count_artifacts(self, messages: List[Dict[str, Any]]) -> int:
        """Return total artifact count across all messages."""
        return sum(
            self.count_in_message(msg.get('content', ''))
            for msg in messages
        )

    def count_in_message(self, content: str) -> int:
        """Count distinct artifacts in a single message."""
        if not content:
            return 0

        total = 0
        total += len(self._CODE_FENCE_RE.findall(content))

        # Terminal output blocks (outside fenced code)
        clean = self._CODE_FENCE_RE.sub('', content)
        terminal_lines = self._TERMINAL_LINE_RE.findall(clean)
        if terminal_lines:
            total += 1  # Count as one terminal block

        # Markdown tables
        table_lines = self._TABLE_ROW_RE.findall(clean)
        if len(table_lines) >= 2:
            total += 1

        # Manifest snippets
        manifest_hits = self._MANIFEST_RE.findall(clean)
        if len(manifest_hits) >= 3:
            total += 1

        return total

    def detail_artifacts(self, content: str) -> Dict[str, int]:
        """Return per-type artifact counts for a single message."""
        clean = self._CODE_FENCE_RE.sub('', content)
        return {
            'code_block': len(self._CODE_FENCE_RE.findall(content)),
            'terminal_output': 1 if self._TERMINAL_LINE_RE.search(clean) else 0,
            'table': 1 if len(self._TABLE_ROW_RE.findall(clean)) >= 2 else 0,
            'manifest': 1 if len(self._MANIFEST_RE.findall(clean)) >= 3 else 0,
        }


# ===========================================================================
# CorrectionDetector
# ===========================================================================

class CorrectionDetector:
    """Detects user correction events and generates DPO pairs.

    A correction event is when a user message follows an assistant message
    and signals that the assistant's response was wrong, incomplete, or unclear.
    The next assistant response (after the correction) becomes the 'chosen'
    response, and the original becomes 'rejected'.

    Correction patterns (case-insensitive):
        "no that's wrong", "let me rephrase", "actually", "i meant",
        "not quite", "revise", "rewrite", "fix this", "incorrect",
        "that's not right", "wrong answer", "you misunderstood",
        "that's incorrect", "please correct", "try again"

    Validation constraints:
        - Both rejected and chosen must be >= 50 chars
        - Similarity between rejected and chosen: 0.30 <= sim <= 0.95
          (too low = unrelated; too high = no real improvement)
    """

    _CORRECTION_PATTERNS = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in [
            r"\bno[\s,]+that'?s?\s+wrong\b",
            r"\blet me\s+rephrase\b",
            r"\bactually[,\s]",
            r"\bi\s+meant\b",
            r"\bnot\s+quite\b",
            r"\bplease\s+revise\b",
            r"\bplease\s+rewrite\b",
            r"\bfix\s+this\b",
            r"\bincorrect\b",
            r"\bthat'?s?\s+not\s+right\b",
            r"\bwrong\s+answer\b",
            r"\byou\s+misunderstood\b",
            r"\bthat'?s?\s+incorrect\b",
            r"\bplease\s+correct\b",
            r"\btry\s+again\b",
            r"\bno,?\s+you\b",
            r"\bthat'?s?\s+not\s+what\s+I\b",
        ]
    ]

    _MIN_RESPONSE_LEN = 50
    _MIN_SIMILARITY = 0.30
    _MAX_SIMILARITY = 0.95

    def detect_pairs(self, conv: MoonshineConversation) -> List[DPOPair]:
        """Return all DPO pairs detected in a MoonshineConversation."""
        messages = conv.messages
        pairs: List[DPOPair] = []

        for i, msg in enumerate(messages):
            if msg.get('role') != 'user':
                continue
            if i < 1:
                continue

            # Look back for the most recent assistant message
            prev_assistant_idx = self._find_prev_assistant(messages, i)
            if prev_assistant_idx is None:
                continue

            user_content = msg.get('content', '')
            if not self._is_correction(user_content):
                continue

            rejected = messages[prev_assistant_idx].get('content', '')
            if len(rejected) < self._MIN_RESPONSE_LEN:
                continue

            # Look ahead for the next assistant message
            next_assistant_idx = self._find_next_assistant(messages, i)
            if next_assistant_idx is None:
                continue

            chosen = messages[next_assistant_idx].get('content', '')
            if len(chosen) < self._MIN_RESPONSE_LEN:
                continue

            similarity = self._compute_similarity(rejected, chosen)
            if not (self._MIN_SIMILARITY <= similarity <= self._MAX_SIMILARITY):
                continue

            correction_type = self._classify_correction_type(user_content, rejected, chosen)
            confidence = self._compute_confidence(similarity, user_content)

            # Build prompt from context: system-style recap of prior turns
            prompt = self._build_prompt_context(messages, prev_assistant_idx)

            try:
                pair = DPOPair(
                    prompt=prompt,
                    rejected=rejected,
                    chosen=chosen,
                    correction_type=correction_type,
                    confidence=confidence,
                    source_conversation=conv.conversation_id,
                    message_indices={
                        'user_msg': i,
                        'assistant_msg': prev_assistant_idx,
                        'correction_msg': next_assistant_idx,
                    },
                )
                pairs.append(pair)
            except ValueError as exc:
                logger.debug("Skipping invalid DPO pair: %s", exc)

        return pairs

    def _find_prev_assistant(
        self, messages: List[Dict[str, Any]], before_idx: int
    ) -> Optional[int]:
        """Return index of the most recent assistant message before before_idx."""
        for i in range(before_idx - 1, -1, -1):
            if messages[i].get('role') == 'assistant':
                return i
        return None

    def _find_next_assistant(
        self, messages: List[Dict[str, Any]], after_idx: int
    ) -> Optional[int]:
        """Return index of the next assistant message after after_idx."""
        for i in range(after_idx + 1, len(messages)):
            if messages[i].get('role') == 'assistant':
                return i
        return None

    def _is_correction(self, text: str) -> bool:
        """Return True if the text contains a correction signal."""
        return any(p.search(text) for p in self._CORRECTION_PATTERNS)

    def _compute_similarity(self, a: str, b: str) -> float:
        """Compute text similarity in [0.0, 1.0] using SequenceMatcher."""
        # Use first 2000 chars to keep it fast on large responses
        return SequenceMatcher(None, a[:2000], b[:2000]).ratio()

    def _classify_correction_type(self, user_msg: str, rejected: str, chosen: str) -> str:
        """Heuristically classify the type of correction."""
        lower = user_msg.lower()

        # Syntax errors — mentions code errors explicitly
        if re.search(r'\b(syntax|traceback|exception|error|crash|bug)\b', lower):
            return 'syntax_error'

        # Incomplete responses
        if re.search(r'\b(incomplete|missing|finish|continue|rest|more|full)\b', lower):
            return 'incomplete'

        # Logic errors
        if re.search(r'\b(wrong|incorrect|logic|mistake|actually|no[,\s])\b', lower):
            return 'logic_error'

        # Clarity corrections
        if re.search(r'\b(unclear|confus|rephrase|simpler|explain|i meant)\b', lower):
            return 'unclear'

        # Default to style
        return 'style'

    def _compute_confidence(self, similarity: float, user_msg: str) -> float:
        """Compute confidence score based on similarity and signal strength."""
        # Base confidence from similarity — closer to midpoint = more confident
        # Optimal similarity for a genuine correction is ~0.50-0.70
        sim_score = 1.0 - abs(similarity - 0.60) / 0.60

        # Boost if multiple correction patterns match
        pattern_hits = sum(1 for p in self._CORRECTION_PATTERNS if p.search(user_msg))
        pattern_boost = min(0.20, pattern_hits * 0.05)

        # Boost for longer user correction messages (more specific = more confident)
        length_boost = min(0.10, len(user_msg) / 5000)

        raw = max(0.0, min(1.0, sim_score + pattern_boost + length_boost))
        return round(raw, 4)

    def _build_prompt_context(
        self,
        messages: List[Dict[str, Any]],
        up_to_idx: int,
    ) -> str:
        """Build a prompt context string from the conversation up to up_to_idx."""
        context_messages = messages[max(0, up_to_idx - 3): up_to_idx + 1]
        parts = []
        for msg in context_messages:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '').strip()
            if content:
                parts.append(f"[{role}]: {content}")
        return '\n\n'.join(parts)


# ===========================================================================
# MoonshineOutputAdapter
# ===========================================================================

class MoonshineOutputAdapter:
    """Exports MoonshineConversation objects to all Moonshine output formats.

    Supported output formats:
        SQLite  — 3-table schema: conversations, messages, segments
        JSONL   — DPO training pairs, one JSON object per line
        CSV     — Conversation metadata table
        Parquet — Columnar format via pyarrow (graceful degradation to CSV)
    """

    # ── SQLite schema ───────────────────────────────────────────────────────

    _DDL = """
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id   TEXT PRIMARY KEY,
        title             TEXT,
        turn_count        INTEGER,
        total_tokens      INTEGER,
        topic_primary     TEXT,
        artifact_count    INTEGER,
        correction_events INTEGER,
        information_gain  REAL,
        tone_cluster      TEXT,
        period            TEXT,
        model_version     TEXT
    );

    CREATE TABLE IF NOT EXISTS messages (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id   TEXT REFERENCES conversations(conversation_id),
        message_index     INTEGER,
        role              TEXT,
        content           TEXT,
        create_time       REAL
    );

    CREATE TABLE IF NOT EXISTS segments (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id   TEXT REFERENCES conversations(conversation_id),
        message_index     INTEGER,
        role              TEXT,
        segment_type      TEXT,
        char_count        INTEGER,
        word_count        INTEGER,
        has_code          INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_messages_conv
        ON messages(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_segments_conv
        ON segments(conversation_id);
    """

    # ── CSV field order ─────────────────────────────────────────────────────

    _CSV_FIELDS = [
        'conversation_id', 'title', 'turn_count', 'total_tokens',
        'topic_primary', 'artifact_count', 'correction_events',
        'information_gain', 'tone_cluster', 'period', 'model_version',
    ]

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── SQLite ──────────────────────────────────────────────────────────────

    async def write_sqlite(
        self,
        conversations: Sequence[MoonshineConversation],
        db_path: Optional[Path] = None,
    ) -> Path:
        """Write all conversations into a SQLite database.

        Returns the path to the written database file.
        """
        if db_path is None:
            db_path = self.output_dir / 'moonshine.db'

        loop = asyncio.get_event_loop()

        def _write():
            conn = sqlite3.connect(str(db_path))
            conn.executescript(self._DDL)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

            try:
                for conv in conversations:
                    # Upsert conversation row
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO conversations
                            (conversation_id, title, turn_count, total_tokens,
                             topic_primary, artifact_count, correction_events,
                             information_gain, tone_cluster, period, model_version)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            conv.conversation_id, conv.title, conv.turn_count,
                            conv.total_tokens, conv.topic_primary,
                            conv.artifact_count, conv.correction_events,
                            conv.information_gain, conv.tone_cluster,
                            conv.period, conv.model_version,
                        )
                    )

                    # Messages
                    for msg in conv.messages:
                        conn.execute(
                            """
                            INSERT INTO messages
                                (conversation_id, message_index, role, content, create_time)
                            VALUES (?,?,?,?,?)
                            """,
                            (
                                conv.conversation_id,
                                msg.get('index', -1),
                                msg.get('role', 'unknown'),
                                msg.get('content', ''),
                                msg.get('create_time'),
                            )
                        )

                    # Segments
                    for seg in conv.segments:
                        conn.execute(
                            """
                            INSERT INTO segments
                                (conversation_id, message_index, role,
                                 segment_type, char_count, word_count, has_code)
                            VALUES (?,?,?,?,?,?,?)
                            """,
                            (
                                conv.conversation_id,
                                seg.get('message_index', -1),
                                seg.get('role', 'unknown'),
                                seg.get('segment_type', 'prose'),
                                seg.get('char_count', 0),
                                seg.get('word_count', 0),
                                1 if seg.get('has_code') else 0,
                            )
                        )

                conn.commit()
            except Exception as exc:
                conn.rollback()
                raise exc
            finally:
                conn.close()

        await loop.run_in_executor(None, _write)
        logger.info("MoonshineOutputAdapter: wrote SQLite to %s (%d convs)", db_path, len(conversations))
        return db_path

    # ── JSONL (DPO pairs) ───────────────────────────────────────────────────

    async def write_dpo_jsonl(
        self,
        conversations: Sequence[MoonshineConversation],
        jsonl_path: Optional[Path] = None,
    ) -> Path:
        """Write all DPO pairs to a JSONL file.

        Each line is a JSON-encoded DPOPair.to_jsonl_dict().
        """
        if jsonl_path is None:
            jsonl_path = self.output_dir / 'dpo_pairs.jsonl'

        loop = asyncio.get_event_loop()
        total_pairs = 0

        def _write():
            nonlocal total_pairs
            with open(str(jsonl_path), 'w', encoding='utf-8') as fh:
                for conv in conversations:
                    for pair in conv.dpo_pairs:
                        try:
                            line = json.dumps(pair.to_jsonl_dict(), ensure_ascii=False)
                            fh.write(line + '\n')
                            total_pairs += 1
                        except (TypeError, ValueError) as exc:
                            logger.warning("Skipping malformed DPOPair: %s", exc)

        await loop.run_in_executor(None, _write)
        logger.info(
            "MoonshineOutputAdapter: wrote %d DPO pairs to %s",
            total_pairs, jsonl_path
        )
        return jsonl_path

    # ── CSV metadata ────────────────────────────────────────────────────────

    async def write_metadata_csv(
        self,
        conversations: Sequence[MoonshineConversation],
        csv_path: Optional[Path] = None,
    ) -> Path:
        """Write conversation metadata to a CSV file."""
        if csv_path is None:
            csv_path = self.output_dir / 'conversations_metadata.csv'

        loop = asyncio.get_event_loop()

        def _write():
            with open(str(csv_path), 'w', newline='', encoding='utf-8') as fh:
                writer = csv.DictWriter(fh, fieldnames=self._CSV_FIELDS, extrasaction='ignore')
                writer.writeheader()
                for conv in conversations:
                    try:
                        writer.writerow(conv.csv_row)
                    except Exception as exc:
                        logger.warning("Skipping conversation in CSV: %s", exc)

        await loop.run_in_executor(None, _write)
        logger.info(
            "MoonshineOutputAdapter: wrote metadata CSV to %s (%d rows)",
            csv_path, len(conversations)
        )
        return csv_path

    # ── Parquet ─────────────────────────────────────────────────────────────

    async def write_parquet(
        self,
        conversations: Sequence[MoonshineConversation],
        parquet_path: Optional[Path] = None,
    ) -> Path:
        """Write conversation metadata to Parquet.

        Falls back to CSV if pyarrow is not installed.
        """
        if not PARQUET_AVAILABLE:
            logger.warning(
                "pyarrow not installed — falling back to CSV output for Parquet request"
            )
            return await self.write_metadata_csv(conversations, parquet_path)

        if parquet_path is None:
            parquet_path = self.output_dir / 'conversations_metadata.parquet'

        loop = asyncio.get_event_loop()

        def _write():
            rows = [conv.csv_row for conv in conversations]
            if not rows:
                logger.warning("No conversations to write to Parquet")
                return

            # Build pyarrow table column by column
            table_dict: Dict[str, List[Any]] = {field: [] for field in self._CSV_FIELDS}
            for row in rows:
                for f in self._CSV_FIELDS:
                    table_dict[f].append(row.get(f))

            schema = pa.schema([
                pa.field('conversation_id', pa.string()),
                pa.field('title', pa.string()),
                pa.field('turn_count', pa.int32()),
                pa.field('total_tokens', pa.int32()),
                pa.field('topic_primary', pa.string()),
                pa.field('artifact_count', pa.int32()),
                pa.field('correction_events', pa.int32()),
                pa.field('information_gain', pa.float32()),
                pa.field('tone_cluster', pa.string()),
                pa.field('period', pa.string()),
                pa.field('model_version', pa.string()),
            ])

            arrays = []
            for f in self._CSV_FIELDS:
                col_data = table_dict[f]
                # Cast numerics
                if f in {'turn_count', 'total_tokens', 'artifact_count', 'correction_events'}:
                    arrays.append(pa.array([int(v) if v is not None else 0 for v in col_data], type=pa.int32()))
                elif f == 'information_gain':
                    arrays.append(pa.array([float(v) if v is not None else 0.0 for v in col_data], type=pa.float32()))
                else:
                    arrays.append(pa.array([str(v) if v is not None else '' for v in col_data], type=pa.string()))

            table = pa.table(dict(zip(self._CSV_FIELDS, arrays)), schema=schema)
            pq.write_table(table, str(parquet_path), compression='snappy')

        await loop.run_in_executor(None, _write)
        logger.info(
            "MoonshineOutputAdapter: wrote Parquet to %s (%d rows)",
            parquet_path, len(conversations)
        )
        return parquet_path

    # ── Convenience: write all formats in one call ──────────────────────────

    async def write_all(
        self,
        conversations: Sequence[MoonshineConversation],
        db_path: Optional[Path] = None,
        jsonl_path: Optional[Path] = None,
        csv_path: Optional[Path] = None,
        parquet_path: Optional[Path] = None,
    ) -> Dict[str, Path]:
        """Write all output formats concurrently.

        Returns a dict mapping format name -> output path.
        """
        start = time.monotonic()

        sqlite_task = asyncio.create_task(self.write_sqlite(conversations, db_path))
        jsonl_task = asyncio.create_task(self.write_dpo_jsonl(conversations, jsonl_path))
        csv_task = asyncio.create_task(self.write_metadata_csv(conversations, csv_path))
        parquet_task = asyncio.create_task(self.write_parquet(conversations, parquet_path))

        results = await asyncio.gather(
            sqlite_task, jsonl_task, csv_task, parquet_task,
            return_exceptions=True
        )

        output: Dict[str, Path] = {}
        labels = ['sqlite', 'jsonl', 'csv', 'parquet']
        for label, result in zip(labels, results):
            if isinstance(result, Exception):
                logger.error("MoonshineOutputAdapter.write_all: %s failed: %s", label, result)
            else:
                output[label] = result

        elapsed = time.monotonic() - start
        logger.info(
            "MoonshineOutputAdapter.write_all: completed in %.2fs for %d conversations",
            elapsed, len(conversations)
        )
        return output

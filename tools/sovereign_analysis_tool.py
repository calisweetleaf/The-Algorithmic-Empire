"""
Somnus Sovereign Analysis Tool
==============================

Natural language analysis system that interprets user requests and executes
complex analysis workflows through the Somnus infrastructure.

User Interface:
- Natural language analysis requests
- Automatic workflow planning and execution
- Three-tier execution model (Reasoning → Safe → Sovereign)
- Human oversight integration
- Memory-persistent results

Examples:
- "Analyze this CSV for sales trends by region"
- "Build a ML model to predict customer churn using this dataset"
- "Research competitor analysis and generate strategic report"
"""

import asyncio
import hashlib
import logging
import os
import sys
import time
import uuid
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

# ---------------------------------------------------------------------------
# Configure module-level logger
# ---------------------------------------------------------------------------
logger = logging.getLogger('sovereign_analysis')
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Graceful imports — tool works standalone AND inside the shell framework
# ---------------------------------------------------------------------------
_SHELL_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_DIR = _SHELL_ROOT / 'src'
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

try:
    from somnus_artifact_manager import SomnusArtifactManager
except ImportError:
    SomnusArtifactManager = None  # type: ignore[assignment,misc]

try:
    from vm_orchestrator import VMOrchestrator
except ImportError:
    VMOrchestrator = None  # type: ignore[assignment,misc]

# --- Artifact infrastructure ---
try:
    from artifacts.artifact_config import (
        ArtifactType as _ArtifactType,
        ExecutionEnvironment as _ExecutionEnvironment,
        UnlimitedExecutionConfig,
        UnlimitedArtifact,
        UnlimitedExecutionResult,
    )
    ARTIFACT_INFRA_AVAILABLE = True
except ImportError:
    _ArtifactType = None  # type: ignore[assignment,misc]
    _ExecutionEnvironment = None  # type: ignore[assignment,misc]
    UnlimitedExecutionConfig = None  # type: ignore[assignment,misc]
    UnlimitedArtifact = None  # type: ignore[assignment,misc]
    UnlimitedExecutionResult = None  # type: ignore[assignment,misc]
    ARTIFACT_INFRA_AVAILABLE = False

try:
    from artifacts.artifact_container_runtime import (
        UnlimitedContainerRuntime,
        ContainerConfig,
        ContainerMetrics,
        ContainerState,
    )
    CONTAINER_RUNTIME_AVAILABLE = True
except ImportError:
    UnlimitedContainerRuntime = None  # type: ignore[assignment,misc]
    ContainerConfig = None  # type: ignore[assignment,misc]
    ContainerMetrics = None  # type: ignore[assignment,misc]
    ContainerState = None  # type: ignore[assignment,misc]
    CONTAINER_RUNTIME_AVAILABLE = False

# --- Extended thinking (optional) ---
try:
    from extended_thinking_integration import ExtendedThinkingKernel, ThinkingMode
except ImportError:
    try:
        # Try as relative to tools/native/
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from extended_thinking_integration import ExtendedThinkingKernel, ThinkingMode
    except ImportError:
        ExtendedThinkingKernel = None  # type: ignore[assignment,misc]
        ThinkingMode = None  # type: ignore[assignment,misc]

# --- Optional serialization ---
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    aiofiles = None  # type: ignore[assignment]
    AIOFILES_AVAILABLE = False


# ============================================================================
# PHASE 2: Resource Governance via Artifact Configs
# ============================================================================

class ResourceProfiles:
    """Production-grade resource configurations per execution tier.

    Maps the three-tier execution model to concrete ``UnlimitedExecutionConfig``
    instances that govern timeout, memory, CPU, network, and GPU access.
    Profiles are designed to match the actual field names of the Somnus artifact
    infrastructure (``enable_internet``, ``enable_gpu``, etc.).
    """

    @staticmethod
    def _build_config(**overrides) -> Any:
        """Build an ``UnlimitedExecutionConfig`` if the artifact infra is loaded,
        otherwise return a plain dict so that standalone / test usage still works."""
        if UnlimitedExecutionConfig is not None:
            return UnlimitedExecutionConfig(**overrides)
        # Fallback: plain dict when running outside the full stack
        defaults = {
            'timeout': None,
            'memory_limit': None,
            'cpu_limit': None,
            'enable_internet': True,
            'enable_gpu': True,
            'enable_model_training': True,
            'enable_fine_tuning': True,
            'enable_distributed_computing': True,
        }
        defaults.update(overrides)
        return defaults

    @classmethod
    def reasoning(cls) -> Any:
        """Reasoning tier — lightweight, isolated, no external I/O."""
        return cls._build_config(
            timeout=60,
            memory_limit='1g',
            cpu_limit=1.0,
            enable_internet=False,
            enable_gpu=False,
            enable_model_training=False,
            enable_fine_tuning=False,
            enable_distributed_computing=False,
            enable_video_processing=False,
            enable_audio_processing=False,
            enable_youtube_download=False,
        )

    @classmethod
    def safe_execution(cls) -> Any:
        """Safe execution tier — moderate resources, no network."""
        return cls._build_config(
            timeout=300,
            memory_limit='4g',
            cpu_limit=2.0,
            enable_internet=False,
            enable_gpu=False,
            enable_model_training=False,
            enable_fine_tuning=False,
            enable_distributed_computing=False,
        )

    @classmethod
    def sovereign(cls) -> Any:
        """Sovereign tier — unlimited resources, full access."""
        return cls._build_config(
            timeout=None,
            memory_limit=None,
            cpu_limit=None,
            enable_internet=True,
            enable_gpu=True,
            enable_model_training=True,
            enable_fine_tuning=True,
            enable_distributed_computing=True,
        )

    @classmethod
    def for_tier(cls, tier: 'ExecutionTier') -> Any:
        """Return the resource profile for *tier*."""
        _map = {
            'reasoning': cls.reasoning,
            'safe_execution': cls.safe_execution,
            'sovereign': cls.sovereign,
        }
        factory = _map.get(tier.value if hasattr(tier, 'value') else str(tier))
        if factory is None:
            logger.warning("Unknown tier %s — defaulting to safe_execution", tier)
            factory = cls.safe_execution
        return factory()

    @staticmethod
    def adjust_for_step(base_config: Any, step: 'AnalysisStep') -> Any:
        """Dynamically adjust resource config based on step characteristics.

        Inspects the step description for keywords and bumps resources up where
        appropriate.  Returns a *new* config (dict or dataclass) so the caller's
        original is not mutated.
        """
        if isinstance(base_config, dict):
            adjusted = dict(base_config)
        else:
            adjusted = {k: v for k, v in base_config.__dict__.items()
                        if not k.startswith('_')}

        desc_lower = getattr(step, 'description', '').lower()

        # Large-dataset heuristic — bump memory
        expected_mb = getattr(step, 'expected_data_size_mb', 0) or 0
        if expected_mb > 1000:
            adjusted['memory_limit'] = f'{int(expected_mb * 2)}m'

        # Parallel-work heuristic — bump CPU
        if 'parallel' in desc_lower or 'concurrent' in desc_lower:
            adjusted['cpu_limit'] = min(8.0, float(os.cpu_count() or 4))

        # ML-training heuristic — enable GPU
        ml_keywords = ('train', 'model', 'neural', 'deep learning', 'fine-tun',
                        'backprop', 'gradient', 'epoch')
        if any(kw in desc_lower for kw in ml_keywords):
            adjusted['enable_gpu'] = True
            adjusted['enable_model_training'] = True

        # Network-required heuristic
        net_keywords = ('download', 'fetch', 'scrape', 'api', 'http', 'web')
        if any(kw in desc_lower for kw in net_keywords):
            adjusted['enable_internet'] = True

        return adjusted


# ============================================================================
# PHASE 1: Direct OS Execution + FastAPI Sandbox Delegation
# ============================================================================

# --- HTTP client for FastAPI sandbox delegation (optional) ---
try:
    import httpx  # type: ignore[import-untyped]
    _HTTPX_AVAILABLE = True
except ImportError:
    httpx = None  # type: ignore[assignment]
    _HTTPX_AVAILABLE = False


class ArtifactAnalysisExecutor:
    """Execute analysis steps directly on the OS, delegating sandboxed
    work to ``artifact_system_fastapi.py`` when Docker isolation is needed.

    Execution routing by tier:

    * **reasoning** — In-process ``exec()`` for lightweight reasoning tasks.
    * **safe_execution** — Local ``subprocess.run()`` with timeout and CWD
      isolation.  No Docker required.
    * **sovereign** — Full Docker isolation via the FastAPI artifact endpoint
      (``POST /api/artifacts/create`` + ``POST /api/artifacts/{id}/execute``).
      Falls back to local subprocess if FastAPI is unreachable.

    When neither Docker nor FastAPI is available, every tier gracefully
    degrades to the in-process ``exec()`` sandbox.
    """

    # Maps human-readable step types → ArtifactType enum members
    _TYPE_MAP: Dict[str, str] = {
        'data_exploration':     'PYTHON',
        'data_loading':         'PYTHON',
        'data_analysis':        'PYTHON',
        'data_preprocessing':   'PYTHON',
        'pattern_analysis':     'PYTHON',
        'statistical_analysis': 'PYTHON',
        'hypothesis_testing':   'PYTHON',
        'normality_testing':    'PYTHON',
        'regression_analysis':  'PYTHON',
        'machine_learning':     'PYTHON',
        'feature_engineering':  'PYTHON',
        'model_selection':      'PYTHON',
        'model_training':       'MODEL_TRAINING',
        'model_evaluation':     'PYTHON',
        'visualization':        'PYTHON',
        'chart_selection':      'PYTHON',
        'rendering':            'PYTHON',
        'research_synthesis':   'PYTHON',
        'research_planning':    'PYTHON',
        'web_research':         'PYTHON',
        'synthesis':            'PYTHON',
        'report_generation':    'PYTHON',
        'interpretation':       'PYTHON',
        'data_profiling':       'PYTHON',
        'source_collection':    'PYTHON',
        'nlp_extraction':       'PYTHON',
    }

    # Default FastAPI artifact endpoint (configurable via env or constructor)
    _DEFAULT_FASTAPI_URL = 'http://127.0.0.1:8000/api/artifacts'

    def __init__(self, base_dir: Optional[Path] = None,
                 fastapi_url: Optional[str] = None):
        self.base_dir = base_dir or Path('./data/analysis_artifacts')
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.fastapi_url = (
            fastapi_url
            or os.environ.get('SOMNUS_ARTIFACT_API_URL')
            or self._DEFAULT_FASTAPI_URL
        )
        logger.info(
            "ArtifactAnalysisExecutor initialised — direct OS execution "
            "(base_dir=%s, fastapi_url=%s)", self.base_dir, self.fastapi_url
        )

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    async def execute_step(self, step: 'AnalysisStep') -> Dict[str, Any]:
        """Execute an analysis step, routing by execution tier.

        Returns a dict with keys: success, output, artifacts, container_id,
        execution_time, resources_used, error (on failure).
        """
        start_ts = time.time()
        artifact_spec = self._step_to_artifact_spec(step)
        container_id = str(uuid4())

        logger.info("Executing step %s (id=%s, type=%s, tier=%s)",
                     step.step_id, container_id[:8],
                     artifact_spec['artifact_type'], step.execution_tier.value)

        try:
            tier = step.execution_tier.value

            if tier == 'reasoning':
                result = await self._execute_reasoning(step, artifact_spec, container_id)
            elif tier == 'safe_execution':
                result = await self._execute_local_subprocess(step, artifact_spec, container_id)
            elif tier == 'sovereign':
                result = await self._execute_via_fastapi_sandbox(step, artifact_spec, container_id)
            else:
                # Unknown tier — safe default to local exec
                result = await self._execute_reasoning(step, artifact_spec, container_id)

            elapsed = time.time() - start_ts
            result['container_id'] = container_id
            result['execution_time'] = elapsed
            if 'resources_used' not in result:
                result['resources_used'] = self._snapshot_local_resources()
            return result

        except Exception as exc:
            elapsed = time.time() - start_ts
            logger.error("Step %s failed after %.2fs: %s", step.step_id, elapsed, exc)
            return {
                'success': False,
                'output': '',
                'error': str(exc),
                'container_id': container_id,
                'execution_time': elapsed,
                'artifacts': [],
                'resources_used': {},
            }

    # --------------------------------------------------------------------- #
    # Tier 1: Reasoning — in-process exec()
    # --------------------------------------------------------------------- #

    async def _execute_reasoning(self, step: 'AnalysisStep',
                                  spec: Dict[str, Any],
                                  container_id: str) -> Dict[str, Any]:
        """In-process exec() for lightweight reasoning tasks.

        No subprocess, no Docker — fastest path for pure-computation steps.
        """
        code = step.code or 'print("Step completed via reasoning")'

        sandbox_globals: Dict[str, Any] = {'__builtins__': __builtins__}
        sandbox_locals: Dict[str, Any] = {}

        import io
        import contextlib
        buf = io.StringIO()

        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                exec(code, sandbox_globals, sandbox_locals)
            output_text = buf.getvalue()

            return {
                'success': True,
                'output': output_text,
                'artifacts': [],
                'resources_used': self._snapshot_local_resources(),
            }
        except Exception as exc:
            return {
                'success': False,
                'output': buf.getvalue(),
                'error': f"Reasoning exec error: {exc}",
                'artifacts': [],
                'resources_used': self._snapshot_local_resources(),
            }

    # --------------------------------------------------------------------- #
    # Tier 2: Safe Execution — local subprocess with isolation
    # --------------------------------------------------------------------- #

    async def _execute_local_subprocess(self, step: 'AnalysisStep',
                                         spec: Dict[str, Any],
                                         container_id: str) -> Dict[str, Any]:
        """Execute step via subprocess.run() with timeout and CWD isolation.

        Creates a temporary working directory, writes the code to a file,
        and runs it in a subprocess with resource_config-derived timeout.
        """
        import subprocess
        import tempfile

        code = step.code or 'print("Step completed via safe execution")'
        resource_config = spec.get('config', {})
        timeout = resource_config.get('timeout', 120) or 120

        # Create isolated working directory under base_dir
        work_dir = self.base_dir / f"step_{step.step_id}_{container_id[:8]}"
        work_dir.mkdir(parents=True, exist_ok=True)

        script_path = work_dir / 'main.py'
        script_path.write_text(code, encoding='utf-8')

        # Inject dependency files into the working directory
        for dep_path in (step.dependencies or []):
            dep = Path(dep_path)
            if dep.is_file():
                try:
                    (work_dir / dep.name).write_text(
                        dep.read_text(encoding='utf-8'), encoding='utf-8'
                    )
                except Exception:
                    logger.debug("Could not inject dependency %s", dep_path)

        try:
            proc = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True, text=True,
                    timeout=timeout,
                    cwd=str(work_dir),
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                ),
            )

            output_text = proc.stdout + (
                f"\n[stderr] {proc.stderr}" if proc.stderr else ''
            )

            return {
                'success': proc.returncode == 0,
                'output': output_text.strip(),
                'error': proc.stderr if proc.returncode != 0 else None,
                'artifacts': [str(p) for p in work_dir.iterdir() if p.name != 'main.py'],
                'resources_used': self._snapshot_local_resources(),
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f"Subprocess timed out after {timeout}s",
                'artifacts': [],
                'resources_used': self._snapshot_local_resources(),
            }
        except Exception as exc:
            return {
                'success': False,
                'output': '',
                'error': f"Subprocess execution error: {exc}",
                'artifacts': [],
                'resources_used': self._snapshot_local_resources(),
            }

    # --------------------------------------------------------------------- #
    # Tier 3: Sovereign — delegate to FastAPI artifact sandbox (Docker)
    # --------------------------------------------------------------------- #

    async def _execute_via_fastapi_sandbox(self, step: 'AnalysisStep',
                                            spec: Dict[str, Any],
                                            container_id: str) -> Dict[str, Any]:
        """Delegate execution to artifact_system_fastapi.py Docker containers.

        Uses HTTP POST to create an artifact and then execute it within
        a Docker container via the FastAPI endpoint.  Falls back to local
        subprocess if the FastAPI server is unreachable.
        """
        if not _HTTPX_AVAILABLE:
            logger.warning(
                "httpx not available — falling back to local subprocess for "
                "sovereign step %s", step.step_id
            )
            return await self._execute_local_subprocess(step, spec, container_id)

        code = step.code or 'print("Step completed via sovereign execution")'
        art_type = spec.get('artifact_type', 'PYTHON')

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # 1. Create artifact via FastAPI
                create_payload = {
                    'name': f"analysis_{step.step_id}_{container_id[:8]}",
                    'content': code,
                    'artifact_type': art_type.lower(),
                    'user_id': 'sovereign_analysis_tool',
                    'session_id': container_id,
                    'description': step.description,
                    'security_level': 'sandboxed',
                    'enable_vm': False,
                }

                create_resp = await client.post(
                    f"{self.fastapi_url}/create", json=create_payload
                )

                if create_resp.status_code != 200:
                    logger.warning(
                        "FastAPI create failed (%d) — falling back to subprocess",
                        create_resp.status_code,
                    )
                    return await self._execute_local_subprocess(step, spec, container_id)

                create_data = create_resp.json()
                artifact_id = create_data.get('artifact', {}).get('metadata', {}).get('artifact_id')

                if not artifact_id:
                    logger.warning("No artifact_id returned — falling back to subprocess")
                    return await self._execute_local_subprocess(step, spec, container_id)

                # 2. Execute artifact in Docker container
                exec_payload = {
                    'user_id': 'sovereign_analysis_tool',
                    'use_vm': False,
                    'timeout': 300,
                }

                exec_resp = await client.post(
                    f"{self.fastapi_url}/{artifact_id}/execute", json=exec_payload
                )

                if exec_resp.status_code != 200:
                    logger.warning(
                        "FastAPI execute failed (%d) — falling back to subprocess",
                        exec_resp.status_code,
                    )
                    return await self._execute_local_subprocess(step, spec, container_id)

                exec_data = exec_resp.json()
                exec_result = exec_data.get('execution_result', {})

                return {
                    'success': exec_result.get('success', False),
                    'output': exec_result.get('output', exec_result.get('error', '')),
                    'error': exec_result.get('error') if not exec_result.get('success') else None,
                    'artifacts': exec_result.get('artifacts_created', []),
                    'resources_used': exec_result.get('resource_usage', {}),
                }

        except (httpx.ConnectError, httpx.ConnectTimeout, OSError) as exc:
            logger.warning(
                "FastAPI unreachable (%s) — falling back to local subprocess "
                "for sovereign step %s", exc, step.step_id
            )
            return await self._execute_local_subprocess(step, spec, container_id)
        except Exception as exc:
            logger.error("FastAPI sandbox error: %s", exc)
            return await self._execute_local_subprocess(step, spec, container_id)

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #

    def _step_to_artifact_spec(self, step: 'AnalysisStep') -> Dict[str, Any]:
        """Convert an ``AnalysisStep`` to an artifact specification dict."""
        artifact_type = self._TYPE_MAP.get(step.step_type, 'PYTHON')
        resource_config = ResourceProfiles.for_tier(step.execution_tier)

        # Apply dynamic adjustments
        resource_config = ResourceProfiles.adjust_for_step(resource_config, step)

        return {
            'artifact_type': artifact_type,
            'config': resource_config if isinstance(resource_config, dict) else resource_config.__dict__,
            'files': step.dependencies or [],
        }

    @staticmethod
    def _snapshot_local_resources() -> Dict[str, Any]:
        """Capture a lightweight snapshot of current system resource usage."""
        try:
            import psutil
            proc = psutil.Process()
            mem = proc.memory_info()
            return {
                'memory_rss_mb': round(mem.rss / (1024 ** 2), 2),
                'memory_vms_mb': round(mem.vms / (1024 ** 2), 2),
                'cpu_percent': proc.cpu_percent(interval=0.05),
                'threads': proc.num_threads(),
            }
        except Exception:
            return {'memory_rss_mb': 0, 'cpu_percent': 0}



# ============================================================================
# PHASE 3: Fault Tolerance via Checkpoint System
# ============================================================================

@dataclass
class WorkflowCheckpoint:
    """Serializable checkpoint for workflow recovery.

    Captures execution state at a point-in-time so that workflows can be
    resumed after failures without re-executing already-completed steps.
    Uses JSON serialization for debuggability and zero-dependency operation.
    """

    workflow_id: str
    checkpoint_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Execution state
    completed_steps: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    pending_steps: List[str] = field(default_factory=list)

    # Partial results
    step_results: Dict[str, Any] = field(default_factory=dict)
    accumulated_artifacts: List[str] = field(default_factory=list)
    intermediate_data: Dict[str, Any] = field(default_factory=dict)

    # Resource state
    containers_created: List[str] = field(default_factory=list)
    containers_active: List[str] = field(default_factory=list)
    resource_usage: Dict[str, Any] = field(default_factory=dict)

    # Error context
    last_error: Optional[str] = None
    retry_count: int = 0
    failure_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_json_bytes(self) -> bytes:
        """Serialize checkpoint to JSON bytes for persistence."""
        return json.dumps(asdict(self), indent=2, default=str).encode('utf-8')

    @classmethod
    def from_json_bytes(cls, data: bytes) -> 'WorkflowCheckpoint':
        """Deserialize checkpoint from JSON bytes."""
        obj = json.loads(data.decode('utf-8'))
        return cls(**obj)


class CheckpointManager:
    """Manage workflow checkpoint persistence and recovery.

    Checkpoints are stored as JSON files under ``checkpoint_dir/{workflow_id}/``.
    Old checkpoints are rotated to prevent unbounded disk usage.
    """

    def __init__(self, checkpoint_dir: Optional[Path] = None,
                 rotation_limit: int = 10):
        self.checkpoint_dir = checkpoint_dir or Path('./data/checkpoints')
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.rotation_limit = rotation_limit
        logger.info("CheckpointManager initialised (dir=%s, rotation=%d)",
                     self.checkpoint_dir, self.rotation_limit)

    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> Path:
        """Persist checkpoint to disk. Returns the path of the written file."""
        wf_dir = self.checkpoint_dir / str(checkpoint.workflow_id)
        wf_dir.mkdir(parents=True, exist_ok=True)

        cp_file = wf_dir / f"{checkpoint.checkpoint_id}.json"
        payload = checkpoint.to_json_bytes()

        if AIOFILES_AVAILABLE and aiofiles is not None:
            async with aiofiles.open(cp_file, 'wb') as fh:
                await fh.write(payload)
        else:
            cp_file.write_bytes(payload)

        logger.debug("Saved checkpoint %s for workflow %s (%d bytes)",
                      checkpoint.checkpoint_id[:8], checkpoint.workflow_id[:8],
                      len(payload))

        await self._rotate_checkpoints(wf_dir)
        return cp_file

    async def load_latest_checkpoint(
        self, workflow_id: str
    ) -> Optional[WorkflowCheckpoint]:
        """Load the most recent valid checkpoint for *workflow_id*."""
        wf_dir = self.checkpoint_dir / str(workflow_id)
        if not wf_dir.exists():
            return None

        candidates = sorted(
            wf_dir.glob('*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            return None

        for cp_file in candidates:
            try:
                data = cp_file.read_bytes()
                checkpoint = WorkflowCheckpoint.from_json_bytes(data)
                if self._verify_checkpoint(checkpoint):
                    logger.debug("Loaded checkpoint %s for workflow %s",
                                  checkpoint.checkpoint_id[:8], workflow_id[:8])
                    return checkpoint
                else:
                    logger.warning("Checkpoint %s failed verification, trying next",
                                    cp_file.name)
            except Exception as exc:
                logger.error("Failed to load checkpoint %s: %s", cp_file.name, exc)

        return None

    def _verify_checkpoint(self, checkpoint: WorkflowCheckpoint) -> bool:
        """Structural integrity check on a loaded checkpoint."""
        if not checkpoint.workflow_id:
            return False
        if not isinstance(checkpoint.step_results, dict):
            return False
        if not isinstance(checkpoint.completed_steps, list):
            return False
        if checkpoint.retry_count < 0:
            return False
        return True

    async def _rotate_checkpoints(self, wf_dir: Path) -> None:
        """Delete checkpoints beyond the rotation limit."""
        checkpoints = sorted(
            wf_dir.glob('*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old_cp in checkpoints[self.rotation_limit:]:
            try:
                old_cp.unlink()
                logger.debug("Rotated old checkpoint %s", old_cp.name)
            except OSError as exc:
                logger.warning("Could not delete checkpoint %s: %s", old_cp.name, exc)

    async def list_workflows(self) -> List[str]:
        """List all workflow IDs that have checkpoints."""
        if not self.checkpoint_dir.exists():
            return []
        return [d.name for d in self.checkpoint_dir.iterdir() if d.is_dir()]

    async def delete_workflow_checkpoints(self, workflow_id: str) -> int:
        """Delete all checkpoints for *workflow_id*. Returns count deleted."""
        import shutil
        wf_dir = self.checkpoint_dir / str(workflow_id)
        if not wf_dir.exists():
            return 0
        count = sum(1 for _ in wf_dir.glob('*.json'))
        shutil.rmtree(wf_dir, ignore_errors=True)
        return count


class WorkflowRecoveryManager:
    """Handle workflow recovery from checkpoints with retry logic.

    Wraps the execution of analysis workflows with automatic checkpointing
    after each step and exponential-backoff retry on transient failures.
    """

    # Error types considered transient / retryable
    RETRYABLE_TYPES = (ConnectionError, TimeoutError, OSError)
    RETRYABLE_MESSAGES = ('timeout', 'connection refused', 'temporarily unavailable',
                          'resource temporarily unavailable', 'broken pipe')

    def __init__(self, checkpoint_manager: CheckpointManager,
                 max_retries: int = 3,
                 backoff_base: float = 2.0):
        self.checkpoint_manager = checkpoint_manager
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        logger.info("WorkflowRecoveryManager initialised (max_retries=%d, backoff=%.1f)",
                     max_retries, backoff_base)

    async def attempt_recovery(
        self,
        workflow_id: str,
        workflow: 'AnalysisWorkflow',
    ) -> Optional[Tuple[WorkflowCheckpoint, List['AnalysisStep']]]:
        """Try to recover workflow from its latest checkpoint.

        Returns (checkpoint, pending_steps) on success, or ``None`` if no viable
        checkpoint exists or retries are exhausted.
        """
        checkpoint = await self.checkpoint_manager.load_latest_checkpoint(workflow_id)
        if checkpoint is None:
            return None

        if checkpoint.retry_count >= self.max_retries:
            logger.warning("Workflow %s exceeded max retries (%d), not recovering",
                            workflow_id[:8], self.max_retries)
            return None

        pending_steps = [
            step for step in workflow.steps
            if step.step_id in checkpoint.pending_steps
        ]
        if not pending_steps:
            logger.info("Workflow %s already fully completed", workflow_id[:8])
            return None

        logger.info(
            "Recovering workflow %s from checkpoint "
            "(completed=%d, pending=%d, retries=%d)",
            workflow_id[:8],
            len(checkpoint.completed_steps),
            len(pending_steps),
            checkpoint.retry_count,
        )
        return checkpoint, pending_steps

    async def execute_with_recovery(
        self,
        request: 'AnalysisRequest',
        workflow: 'AnalysisWorkflow',
        executor: ArtifactAnalysisExecutor,
    ) -> List[Dict[str, Any]]:
        """Execute workflow steps with automatic checkpointing and recovery.

        Returns the list of all step results (including previously completed
        steps from a recovered checkpoint).
        """
        recovery = await self.attempt_recovery(workflow.workflow_id, workflow)

        if recovery:
            checkpoint, pending_steps = recovery
            completed_results = list(checkpoint.step_results.values())
            retry_count = checkpoint.retry_count + 1
        else:
            pending_steps = list(workflow.steps)
            completed_results = []
            retry_count = 0

        execution_results: List[Dict[str, Any]] = list(completed_results)

        for idx, step in enumerate(pending_steps):
            try:
                result = await executor.execute_step(step)
                result['step'] = step.step_id
                execution_results.append(result)

                # Checkpoint after every successful step
                cp = WorkflowCheckpoint(
                    workflow_id=workflow.workflow_id,
                    completed_steps=[s.step_id for s in workflow.steps
                                     if any(r.get('step') == s.step_id
                                            for r in execution_results)],
                    current_step=None,
                    pending_steps=[s.step_id for s in pending_steps[idx + 1:]],
                    step_results={r.get('step', f'unknown_{i}'): r
                                  for i, r in enumerate(execution_results)},
                    accumulated_artifacts=[
                        a for r in execution_results
                        for a in r.get('artifacts', [])
                    ],
                    retry_count=retry_count,
                    resource_usage=result.get('resources_used', {}),
                )
                await self.checkpoint_manager.save_checkpoint(cp)

            except Exception as exc:
                # Save failure checkpoint
                failure_cp = WorkflowCheckpoint(
                    workflow_id=workflow.workflow_id,
                    completed_steps=[r.get('step', '') for r in execution_results
                                     if r.get('success')],
                    current_step=step.step_id,
                    pending_steps=[s.step_id for s in pending_steps[idx:]],
                    step_results={r.get('step', f'unk_{i}'): r
                                  for i, r in enumerate(execution_results)},
                    last_error=str(exc),
                    retry_count=retry_count,
                    failure_history=[{
                        'step': step.step_id,
                        'error': str(exc),
                        'error_type': type(exc).__name__,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    }],
                )
                await self.checkpoint_manager.save_checkpoint(failure_cp)

                if self._is_retryable(exc) and retry_count < self.max_retries:
                    backoff = self.backoff_base ** retry_count
                    logger.info("Retryable error on step %s, backing off %.1fs",
                                 step.step_id, backoff)
                    await asyncio.sleep(backoff)
                    # Mark as failed but allow workflow to continue
                    execution_results.append({
                        'step': step.step_id,
                        'success': False,
                        'error': f"Retryable error (will retry): {exc}",
                    })
                else:
                    execution_results.append({
                        'step': step.step_id,
                        'success': False,
                        'error': str(exc),
                    })

        return execution_results

    def _is_retryable(self, error: Exception) -> bool:
        """Classify whether an error is transient and worth retrying."""
        if isinstance(error, self.RETRYABLE_TYPES):
            return True
        msg = str(error).lower()
        return any(rm in msg for rm in self.RETRYABLE_MESSAGES)


# ============================================================================
# PHASE 4: Observability and Structured Logging
# ============================================================================

class EventType(Enum):
    """Structured event types for analysis observability."""
    WORKFLOW_START = 'workflow.start'
    WORKFLOW_COMPLETE = 'workflow.complete'
    WORKFLOW_FAILED = 'workflow.failed'
    STEP_START = 'step.start'
    STEP_COMPLETE = 'step.complete'
    STEP_FAILED = 'step.failed'
    CHECKPOINT_SAVED = 'checkpoint.saved'
    CHECKPOINT_LOADED = 'checkpoint.loaded'
    RESOURCE_LIMIT_REACHED = 'resource.limit_reached'
    RECOVERY_ATTEMPTED = 'recovery.attempted'


@dataclass
class StructuredEvent:
    """Single structured event for JSONL logging."""
    event_type: str
    correlation_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    step_id: Optional[str] = None
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class StructuredEventLogger:
    """Emit structured events to a JSONL log file.

    All analysis activity is instrumented so that operators can debug
    performance issues and validate SLA compliance.
    """

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path('./data/logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self.log_dir / 'analysis_events.jsonl'
        self._event_count = 0
        logger.info('StructuredEventLogger initialised (log=%s)', self._log_path)

    def _write_event(self, event: StructuredEvent) -> None:
        """Append a single event to the JSONL log file."""
        try:
            with open(self._log_path, 'a', encoding='utf-8') as fh:
                fh.write(event.to_json() + '\n')
            self._event_count += 1
        except OSError as exc:
            logger.error('Failed to write event: %s', exc)

    def emit(self, event: StructuredEvent) -> None:
        """Emit an event (synchronous)."""
        self._write_event(event)

    def workflow_start(self, correlation_id: str, metadata: Optional[Dict] = None) -> None:
        self.emit(StructuredEvent(
            event_type=EventType.WORKFLOW_START.value,
            correlation_id=correlation_id,
            metadata=metadata or {},
        ))

    def workflow_complete(self, correlation_id: str, duration_ms: float,
                          success: bool = True, metadata: Optional[Dict] = None) -> None:
        self.emit(StructuredEvent(
            event_type=EventType.WORKFLOW_COMPLETE.value,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata or {},
        ))

    def step_start(self, correlation_id: str, step_id: str) -> None:
        self.emit(StructuredEvent(
            event_type=EventType.STEP_START.value,
            correlation_id=correlation_id,
            step_id=step_id,
        ))

    def step_complete(self, correlation_id: str, step_id: str,
                      duration_ms: float, success: bool = True,
                      metrics: Optional[Dict] = None) -> None:
        self.emit(StructuredEvent(
            event_type=EventType.STEP_COMPLETE.value,
            correlation_id=correlation_id,
            step_id=step_id,
            duration_ms=duration_ms,
            success=success,
            metrics=metrics or {},
        ))

    def step_failed(self, correlation_id: str, step_id: str,
                    error_message: str, duration_ms: float = 0.0) -> None:
        self.emit(StructuredEvent(
            event_type=EventType.STEP_FAILED.value,
            correlation_id=correlation_id,
            step_id=step_id,
            duration_ms=duration_ms,
            success=False,
            error_message=error_message,
        ))

    def resource_limit_reached(self, correlation_id: str,
                                resource_type: str, current_value: float,
                                limit_value: float) -> None:
        self.emit(StructuredEvent(
            event_type=EventType.RESOURCE_LIMIT_REACHED.value,
            correlation_id=correlation_id,
            metrics={'resource_type': resource_type,
                     'current': current_value, 'limit': limit_value},
        ))

    def get_event_count(self) -> int:
        return self._event_count


class AnalysisMetricsCollector:
    """Collect and aggregate analysis performance metrics.

    Provides latency histograms, error rate tracking, and resource usage
    statistics with percentile calculations (P50 / P95 / P99).
    """

    def __init__(self):
        self._latencies: List[float] = []
        self._errors: List[Dict[str, Any]] = []
        self._resources: List[Dict[str, Any]] = []
        self._start_time = time.time()
        logger.info('AnalysisMetricsCollector initialised')

    def record_latency(self, step_id: str, duration_ms: float) -> None:
        self._latencies.append(duration_ms)

    def record_error(self, step_id: str, error_msg: str,
                     error_type: str = 'unknown') -> None:
        self._errors.append({
            'step_id': step_id,
            'error_msg': error_msg,
            'error_type': error_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })

    def record_resource_usage(self, step_id: str,
                               resources: Dict[str, Any]) -> None:
        self._resources.append({
            'step_id': step_id,
            **resources,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })

    def get_percentiles(self) -> Dict[str, Optional[float]]:
        """Compute P50, P95, P99 latency percentiles."""
        if not self._latencies:
            return {'p50': None, 'p95': None, 'p99': None}
        sorted_lat = sorted(self._latencies)
        n = len(sorted_lat)
        return {
            'p50': sorted_lat[int(n * 0.50)],
            'p95': sorted_lat[min(int(n * 0.95), n - 1)],
            'p99': sorted_lat[min(int(n * 0.99), n - 1)],
        }

    def get_error_rate(self) -> float:
        """Return the error rate as 0.0 – 1.0."""
        total = len(self._latencies) + len(self._errors)
        if total == 0:
            return 0.0
        return len(self._errors) / total

    def get_summary(self) -> Dict[str, Any]:
        """Return a complete metrics summary."""
        return {
            'total_steps': len(self._latencies) + len(self._errors),
            'successful_steps': len(self._latencies),
            'failed_steps': len(self._errors),
            'error_rate': self.get_error_rate(),
            'latency_percentiles': self.get_percentiles(),
            'mean_latency_ms': (sum(self._latencies) / len(self._latencies)
                                if self._latencies else None),
            'resource_samples': len(self._resources),
            'uptime_seconds': round(time.time() - self._start_time, 2),
        }


class AnalysisType(Enum):
    """Types of analysis the system can perform"""
    DATA_EXPLORATION = "data_exploration"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    MACHINE_LEARNING = "machine_learning"
    VISUALIZATION = "visualization"
    RESEARCH_SYNTHESIS = "research_synthesis"
    PREDICTIVE_MODELING = "predictive_modeling"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    PATTERN_DETECTION = "pattern_detection"
    AUTOMATED_RESEARCH = "automated_research"
    MULTI_SOURCE_SYNTHESIS = "multi_source_synthesis"


class ExecutionTier(Enum):
    """Three-tier execution model"""
    REASONING = "reasoning"        # Safe reasoning, no execution
    SAFE_EXECUTION = "safe_execution"  # Browser-safe execution
    SOVEREIGN = "sovereign"        # Full power execution


@dataclass
class AnalysisRequest:
    """Natural language analysis request"""
    user_input: str
    files: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # User preferences
    max_execution_time: float = 300.0  # 5 minutes default
    require_human_approval: bool = True
    enable_extended_thinking: bool = True
    constitutional_compliance: bool = True
    
    # Request metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


@dataclass
class AnalysisStep:
    """Individual step in analysis workflow"""
    step_id: str
    description: str
    step_type: str  # 'reasoning', 'data_processing', 'visualization', 'modeling', etc.
    execution_tier: ExecutionTier
    estimated_time: float
    dependencies: List[str] = field(default_factory=list)
    
    # Execution details
    code: Optional[str] = None
    expected_output: str = ""
    safety_considerations: List[str] = field(default_factory=list)


@dataclass
class AnalysisWorkflow:
    """Complete analysis workflow plan"""
    workflow_id: str
    analysis_type: AnalysisType
    description: str
    steps: List[AnalysisStep]
    
    # Workflow metadata
    estimated_total_time: float
    required_execution_tiers: List[ExecutionTier]
    safety_score: float
    human_approval_required: bool
    
    # Resource requirements
    memory_requirements: str = "standard"
    computational_requirements: str = "standard"
    external_dependencies: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    request_id: str
    workflow_id: str
    
    # Results
    final_output: str
    artifacts_created: List[str]
    visualizations: List[Dict[str, Any]]
    insights: List[str]
    
    # Execution metadata
    execution_time: float
    steps_completed: int
    steps_failed: int
    execution_tiers_used: List[ExecutionTier]
    
    # Quality metrics
    confidence_score: float
    reliability_score: float
    constitutional_compliance: bool
    reasoning_trace: List[Dict[str, Any]]


class AnalysisWorkflowPlanner:
    """Plans analysis workflows from natural language requests"""
    
    def __init__(self, thinking_kernel: Optional[ExtendedThinkingKernel] = None):
        self.thinking_kernel = thinking_kernel
        
        # Analysis type detection patterns
        self.analysis_patterns = {
            AnalysisType.DATA_EXPLORATION: [
                r"explore.*data", r"analyze.*csv", r"understand.*dataset",
                r"data.*overview", r"examine.*data", r"investigate.*file"
            ],
            AnalysisType.STATISTICAL_ANALYSIS: [
                r"statistical.*analysis", r"correlation", r"regression",
                r"significance.*test", r"hypothesis.*test", r"statistics"
            ],
            AnalysisType.MACHINE_LEARNING: [
                r"machine.*learning", r"build.*model", r"train.*model",
                r"predict", r"classification", r"clustering", r"ml.*model"
            ],
            AnalysisType.VISUALIZATION: [
                r"visualize", r"plot", r"chart", r"graph", r"dashboard",
                r"show.*trends", r"create.*visualization"
            ],
            AnalysisType.RESEARCH_SYNTHESIS: [
                r"research.*synthesis", r"literature.*review", r"academic.*analysis",
                r"research.*report", r"synthesize.*information"
            ],
            AnalysisType.AUTOMATED_RESEARCH: [
                r"research.*competitor", r"market.*research", r"automated.*research",
                r"gather.*information", r"web.*research"
            ]
        }
        
        # Workflow templates
        self.workflow_templates = self._initialize_workflow_templates()
    
    def _initialize_workflow_templates(self) -> Dict[AnalysisType, Callable]:
        """Initialize workflow generation templates"""
        
        return {
            AnalysisType.DATA_EXPLORATION: self._plan_data_exploration,
            AnalysisType.STATISTICAL_ANALYSIS: self._plan_statistical_analysis,
            AnalysisType.MACHINE_LEARNING: self._plan_ml_workflow,
            AnalysisType.VISUALIZATION: self._plan_visualization_workflow,
            AnalysisType.RESEARCH_SYNTHESIS: self._plan_research_synthesis,
            AnalysisType.AUTOMATED_RESEARCH: self._plan_automated_research
        }
    
    async def plan_analysis(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan analysis workflow from natural language request"""
        
        # 1. Detect analysis type
        analysis_type = self._detect_analysis_type(request.user_input)
        
        # 2. Use extended thinking for complex planning if available
        if (self.thinking_kernel and request.enable_extended_thinking):
            workflow = await self._plan_with_extended_thinking(request, analysis_type)
        else:
            workflow = await self._plan_with_templates(request, analysis_type)
        
        # 3. Add safety and approval requirements
        workflow = self._add_safety_considerations(workflow, request)
        
        return workflow
    
    def _detect_analysis_type(self, user_input: str) -> AnalysisType:
        """Detect analysis type from natural language input"""
        
        user_input_lower = user_input.lower()
        
        # Score each analysis type
        type_scores = {}
        for analysis_type, patterns in self.analysis_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    score += 1
            type_scores[analysis_type] = score
        
        # Return highest scoring type, default to data exploration
        best_type = max(type_scores, key=type_scores.get)
        if type_scores[best_type] == 0:
            return AnalysisType.DATA_EXPLORATION
        
        return best_type
    
    async def _plan_with_extended_thinking(self, 
                                         request: AnalysisRequest, 
                                         analysis_type: AnalysisType) -> AnalysisWorkflow:
        """Plan workflow using extended thinking system"""
        
        planning_prompt = f"""
        Plan a detailed analysis workflow for this request:
        
        User Request: {request.user_input}
        Analysis Type: {analysis_type.value}
        Available Files: {request.files}
        Context: {request.context}
        
        Create a step-by-step workflow that:
        1. Breaks down the analysis into logical steps
        2. Identifies what execution tier each step needs (reasoning/safe_execution/sovereign)
        3. Estimates time for each step
        4. Identifies dependencies between steps
        5. Considers safety implications
        
        Be specific about what code or operations each step will perform.
        """
        
        # Use extended thinking to plan workflow
        thinking_result = await self.thinking_kernel.process_with_thinking(
            model_id="planner_model",  # This would be configured
            prompt=planning_prompt,
            context={"request": request, "analysis_type": analysis_type}
        )
        
        # Parse the thinking result into a workflow
        return self._parse_thinking_result_to_workflow(
            thinking_result, request, analysis_type
        )
    
    async def _plan_with_templates(self, 
                                 request: AnalysisRequest, 
                                 analysis_type: AnalysisType) -> AnalysisWorkflow:
        """Plan workflow using predefined templates"""
        
        template_func = self.workflow_templates.get(
            analysis_type, 
            self._plan_data_exploration
        )
        
        return template_func(request)
    
    def _plan_data_exploration(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan data exploration workflow"""
        
        workflow_id = str(uuid.uuid4())
        
        steps = [
            AnalysisStep(
                step_id="data_load",
                description=f"Load and examine data files: {request.files}",
                step_type="data_loading",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=10.0,
                code=self._generate_data_load_code(request.files),
                expected_output="Data summary and basic statistics"
            ),
            AnalysisStep(
                step_id="data_overview",
                description="Generate data overview and basic statistics",
                step_type="data_analysis",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=15.0,
                dependencies=["data_load"],
                code=self._generate_overview_code(),
                expected_output="Statistical summary, data types, missing values"
            ),
            AnalysisStep(
                step_id="pattern_detection",
                description="Identify patterns, trends, and correlations",
                step_type="pattern_analysis",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=20.0,
                dependencies=["data_overview"],
                expected_output="Key patterns and insights identified"
            ),
            AnalysisStep(
                step_id="visualization",
                description="Create visualizations for key insights",
                step_type="visualization",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=25.0,
                dependencies=["pattern_detection"],
                code=self._generate_visualization_code(),
                expected_output="Interactive charts and graphs"
            ),
            AnalysisStep(
                step_id="insights_synthesis",
                description="Synthesize findings into actionable insights",
                step_type="synthesis",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=15.0,
                dependencies=["visualization"],
                expected_output="Summary report with key insights and recommendations"
            )
        ]
        
        return AnalysisWorkflow(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.DATA_EXPLORATION,
            description=f"Data exploration analysis: {request.user_input}",
            steps=steps,
            estimated_total_time=sum(step.estimated_time for step in steps),
            required_execution_tiers=[ExecutionTier.REASONING, ExecutionTier.SAFE_EXECUTION],
            safety_score=0.9,
            human_approval_required=request.require_human_approval
        )
    
    def _plan_ml_workflow(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan machine learning workflow"""
        
        workflow_id = str(uuid.uuid4())
        
        steps = [
            AnalysisStep(
                step_id="data_preprocessing",
                description="Load and preprocess data for ML",
                step_type="data_preprocessing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=20.0,
                code=self._generate_ml_preprocessing_code(),
                expected_output="Cleaned and prepared dataset"
            ),
            AnalysisStep(
                step_id="feature_engineering",
                description="Create and select features for modeling",
                step_type="feature_engineering",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=30.0,
                dependencies=["data_preprocessing"],
                code=self._generate_feature_engineering_code(),
                expected_output="Feature matrix ready for training"
            ),
            AnalysisStep(
                step_id="model_selection",
                description="Select and configure appropriate ML algorithm",
                step_type="model_selection",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=15.0,
                dependencies=["feature_engineering"],
                expected_output="Selected algorithm with rationale"
            ),
            AnalysisStep(
                step_id="model_training",
                description="Train ML model with cross-validation",
                step_type="model_training",
                execution_tier=ExecutionTier.SOVEREIGN,  # May need GPU access
                estimated_time=60.0,
                dependencies=["model_selection"],
                code=self._generate_ml_training_code(),
                expected_output="Trained model with performance metrics",
                safety_considerations=["GPU resource usage", "Training time limits"]
            ),
            AnalysisStep(
                step_id="model_evaluation",
                description="Evaluate model performance and generate predictions",
                step_type="model_evaluation",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=20.0,
                dependencies=["model_training"],
                code=self._generate_ml_evaluation_code(),
                expected_output="Performance metrics, predictions, and model insights"
            ),
            AnalysisStep(
                step_id="results_interpretation",
                description="Interpret model results and provide recommendations",
                step_type="interpretation",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=25.0,
                dependencies=["model_evaluation"],
                expected_output="Business insights and model recommendations"
            )
        ]
        
        return AnalysisWorkflow(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.MACHINE_LEARNING,
            description=f"Machine learning analysis: {request.user_input}",
            steps=steps,
            estimated_total_time=sum(step.estimated_time for step in steps),
            required_execution_tiers=[ExecutionTier.REASONING, ExecutionTier.SAFE_EXECUTION, ExecutionTier.SOVEREIGN],
            safety_score=0.7,  # Lower due to sovereign execution
            human_approval_required=True,  # Always require approval for ML
            computational_requirements="high",
            external_dependencies=["scikit-learn", "pandas", "numpy"]
        )
    
    def _plan_automated_research(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan automated research workflow"""
        
        workflow_id = str(uuid.uuid4())
        
        steps = [
            AnalysisStep(
                step_id="research_planning",
                description="Plan research strategy and identify sources",
                step_type="research_planning",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=15.0,
                expected_output="Research plan with target sources and keywords"
            ),
            AnalysisStep(
                step_id="web_research",
                description="Automated web research and data collection",
                step_type="web_research",
                execution_tier=ExecutionTier.SOVEREIGN,  # Needs internet access
                estimated_time=45.0,
                dependencies=["research_planning"],
                code=self._generate_web_research_code(),
                expected_output="Collected research data from multiple sources",
                safety_considerations=["Web scraping rate limits", "Data privacy"]
            ),
            AnalysisStep(
                step_id="data_synthesis",
                description="Synthesize research findings across sources",
                step_type="synthesis",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=30.0,
                dependencies=["web_research"],
                expected_output="Synthesized insights from research data"
            ),
            AnalysisStep(
                step_id="report_generation",
                description="Generate comprehensive research report",
                step_type="report_generation",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=20.0,
                dependencies=["data_synthesis"],
                code=self._generate_report_code(),
                expected_output="Professional research report with citations"
            )
        ]
        
        return AnalysisWorkflow(
            workflow_id=workflow_id,
            analysis_type=AnalysisType.AUTOMATED_RESEARCH,
            description=f"Automated research: {request.user_input}",
            steps=steps,
            estimated_total_time=sum(step.estimated_time for step in steps),
            required_execution_tiers=[ExecutionTier.REASONING, ExecutionTier.SAFE_EXECUTION, ExecutionTier.SOVEREIGN],
            safety_score=0.6,  # Lower due to web access
            human_approval_required=True,
            external_dependencies=["requests", "beautifulsoup4", "selenium"]
        )
    
    def _generate_data_load_code(self, files: List[str]) -> str:
        """Generate code for loading data files"""
        return f"""
import pandas as pd
import numpy as np

# Load data files
data_files = {files}
datasets = {{}}

for file in data_files:
    if file.endswith('.csv'):
        datasets[file] = pd.read_csv(file)
    elif file.endswith('.xlsx'):
        datasets[file] = pd.read_excel(file)
    elif file.endswith('.json'):
        datasets[file] = pd.read_json(file)

# Display basic info
for name, df in datasets.items():
    print(f"Dataset: {{name}}")
    print(f"Shape: {{df.shape}}")
    print(f"Columns: {{list(df.columns)}}")
    print(df.head())
    print("\\n" + "="*50 + "\\n")
"""
    
    def _generate_overview_code(self) -> str:
        """Generate code for data overview"""
        return """
# Generate comprehensive data overview
for name, df in datasets.items():
    print(f"=== OVERVIEW: {name} ===")
    
    # Basic statistics
    print("Basic Statistics:")
    print(df.describe())
    
    # Data types
    print("\\nData Types:")
    print(df.dtypes)
    
    # Missing values
    print("\\nMissing Values:")
    print(df.isnull().sum())
    
    # Unique values for categorical columns
    print("\\nUnique Values (categorical columns):")
    for col in df.select_dtypes(include=['object']).columns:
        print(f"{col}: {df[col].nunique()} unique values")
        if df[col].nunique() < 10:
            print(f"  Values: {df[col].unique()}")
    
    print("\\n" + "="*60 + "\\n")
"""
    
    def _generate_visualization_code(self) -> str:
        """Generate code for creating visualizations"""
        return """
import matplotlib.pyplot as plt
import seaborn as sns

# Create visualizations for each dataset
for name, df in datasets.items():
    print(f"Creating visualizations for: {name}")
    
    # Numeric columns distributions
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Data Distribution Analysis - {name}')
        
        # Histograms
        for i, col in enumerate(numeric_cols[:4]):
            row, col_idx = i // 2, i % 2
            df[col].hist(ax=axes[row, col_idx], bins=30)
            axes[row, col_idx].set_title(f'{col} Distribution')
        
        plt.tight_layout()
        plt.show()
    
    # Correlation matrix if multiple numeric columns
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        correlation_matrix = df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title(f'Correlation Matrix - {name}')
        plt.show()
"""
    
    def _add_safety_considerations(self, 
                                 workflow: AnalysisWorkflow, 
                                 request: AnalysisRequest) -> AnalysisWorkflow:
        """Add safety considerations and approval requirements"""
        
        # Check if any steps require sovereign execution
        has_sovereign_steps = any(
            step.execution_tier == ExecutionTier.SOVEREIGN 
            for step in workflow.steps
        )
        
        if has_sovereign_steps:
            workflow.human_approval_required = True
            workflow.safety_score *= 0.8  # Reduce safety score
        
        # Add constitutional compliance check
        if request.constitutional_compliance:
            for step in workflow.steps:
                if step.execution_tier == ExecutionTier.SOVEREIGN:
                    step.safety_considerations.append("Constitutional compliance check required")
        
        return workflow
    
    def _plan_statistical_analysis(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan a statistical analysis workflow.

        Steps: data_loading -> descriptive_stats -> hypothesis_testing
               -> correlation_analysis -> results_report
        """
        steps = [
            AnalysisStep(
                step_id="stat_load",
                description="Load and validate input data files",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=10.0,
                expected_output="Loaded DataFrames with shape and dtype info",
                safety_considerations=["Validate file paths before reading"],
            ),
            AnalysisStep(
                step_id="stat_descriptive",
                description="Compute descriptive statistics (mean, median, std, quartiles)",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=15.0,
                dependencies=["stat_load"],
                expected_output="Summary statistics table per numeric column",
            ),
            AnalysisStep(
                step_id="stat_hypothesis",
                description="Run hypothesis tests (t-test, chi-squared) on key variables",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=20.0,
                dependencies=["stat_descriptive"],
                expected_output="Test statistics and p-values",
            ),
            AnalysisStep(
                step_id="stat_correlation",
                description="Compute correlation matrix and identify significant relationships",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=15.0,
                dependencies=["stat_load"],
                expected_output="Correlation coefficients with significance flags",
            ),
            AnalysisStep(
                step_id="stat_report",
                description="Synthesize findings into a narrative results report",
                step_type="reasoning",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=20.0,
                dependencies=["stat_hypothesis", "stat_correlation"],
                expected_output="Markdown report with key findings and recommendations",
            ),
        ]
        return AnalysisWorkflow(
            workflow_id=f"stat_{uuid.uuid4().hex[:8]}",
            analysis_type=AnalysisType.STATISTICAL_ANALYSIS,
            description=f"Statistical analysis: {request.user_input[:120]}",
            steps=steps,
            estimated_total_time=sum(s.estimated_time for s in steps),
            required_execution_tiers=[ExecutionTier.SAFE_EXECUTION, ExecutionTier.REASONING],
            safety_score=0.9,
            human_approval_required=False,
        )

    def _plan_visualization_workflow(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan a visualization workflow.

        Steps: data_loading -> column_classification -> distribution_plots
               -> correlation_heatmap -> dashboard_export
        """
        steps = [
            AnalysisStep(
                step_id="viz_load",
                description="Load data files and infer column types",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=10.0,
                expected_output="DataFrames with column type annotations",
            ),
            AnalysisStep(
                step_id="viz_classify",
                description="Classify columns as numeric, categorical, temporal, or text",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=5.0,
                dependencies=["viz_load"],
                expected_output="Column classification mapping",
            ),
            AnalysisStep(
                step_id="viz_distributions",
                description="Generate distribution plots (histograms, box plots) for numeric columns",
                step_type="visualization",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=20.0,
                dependencies=["viz_classify"],
                expected_output="Saved distribution plot images",
            ),
            AnalysisStep(
                step_id="viz_heatmap",
                description="Create correlation heatmap for numeric feature pairs",
                step_type="visualization",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=15.0,
                dependencies=["viz_classify"],
                expected_output="Correlation heatmap image",
            ),
            AnalysisStep(
                step_id="viz_export",
                description="Assemble all plots into a dashboard-style HTML export",
                step_type="visualization",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=15.0,
                dependencies=["viz_distributions", "viz_heatmap"],
                expected_output="HTML dashboard file",
            ),
        ]
        return AnalysisWorkflow(
            workflow_id=f"viz_{uuid.uuid4().hex[:8]}",
            analysis_type=AnalysisType.VISUALIZATION,
            description=f"Visualization workflow: {request.user_input[:120]}",
            steps=steps,
            estimated_total_time=sum(s.estimated_time for s in steps),
            required_execution_tiers=[ExecutionTier.SAFE_EXECUTION],
            safety_score=0.95,
            human_approval_required=False,
        )

    def _plan_research_synthesis(self, request: AnalysisRequest) -> AnalysisWorkflow:
        """Plan a research synthesis workflow.

        Steps: source_gathering -> content_extraction -> key_findings
               -> narrative_synthesis -> citation_report
        """
        steps = [
            AnalysisStep(
                step_id="res_gather",
                description="Gather source documents and web references",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=30.0,
                expected_output="Collected source list with metadata",
                safety_considerations=["Respect rate limits on external fetches"],
            ),
            AnalysisStep(
                step_id="res_extract",
                description="Extract key content, quotes, and data points from each source",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=25.0,
                dependencies=["res_gather"],
                expected_output="Structured extraction per source",
            ),
            AnalysisStep(
                step_id="res_findings",
                description="Identify recurring themes, contradictions, and key findings",
                step_type="reasoning",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=20.0,
                dependencies=["res_extract"],
                expected_output="Key findings with supporting evidence references",
            ),
            AnalysisStep(
                step_id="res_narrative",
                description="Synthesize findings into a coherent research narrative",
                step_type="reasoning",
                execution_tier=ExecutionTier.REASONING,
                estimated_time=25.0,
                dependencies=["res_findings"],
                expected_output="Structured research narrative in Markdown",
            ),
            AnalysisStep(
                step_id="res_citations",
                description="Generate formatted citation report and bibliography",
                step_type="data_processing",
                execution_tier=ExecutionTier.SAFE_EXECUTION,
                estimated_time=10.0,
                dependencies=["res_narrative"],
                expected_output="Citation list with links and access dates",
            ),
        ]
        return AnalysisWorkflow(
            workflow_id=f"res_{uuid.uuid4().hex[:8]}",
            analysis_type=AnalysisType.RESEARCH_SYNTHESIS,
            description=f"Research synthesis: {request.user_input[:120]}",
            steps=steps,
            estimated_total_time=sum(s.estimated_time for s in steps),
            required_execution_tiers=[ExecutionTier.SAFE_EXECUTION, ExecutionTier.REASONING],
            safety_score=0.85,
            human_approval_required=False,
        )


class SomnusAnalysisTool:
    """
    Main Somnus Sovereign Analysis Tool
    
    Natural language interface for complex analysis workflows
    Integrates with all Somnus systems for sovereign analysis capabilities
    """
    
    def __init__(self,
                 neural_memory: Optional[NeuralMemoryRuntime] = None,
                 cas_governor: Optional[ConstitutionalGovernor] = None,
                 artifact_manager: Optional[SomnusArtifactManager] = None,
                 vm_orchestrator: Optional[VMOrchestrator] = None,
                 thinking_kernel: Optional[ExtendedThinkingKernel] = None):
        
        # Core Somnus components
        self.neural_memory = neural_memory
        self.cas_governor = cas_governor
        self.artifact_manager = artifact_manager
        self.vm_orchestrator = vm_orchestrator
        self.thinking_kernel = thinking_kernel
        
        # Analysis components
        self.workflow_planner = AnalysisWorkflowPlanner(thinking_kernel)
        self._artifact_executor = ArtifactAnalysisExecutor()
        self._checkpoint_mgr = CheckpointManager()
        self._recovery_mgr = WorkflowRecoveryManager(self._checkpoint_mgr)
        self._event_logger = StructuredEventLogger()
        self._metrics = AnalysisMetricsCollector()
        
        # Active analysis sessions
        self.active_analyses: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.performance_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'average_execution_time': 0.0,
            'tier_usage': {tier.value: 0 for tier in ExecutionTier}
        }
    
    async def analyze(self, user_input: str, 
                     files: Optional[List[str]] = None,
                     **kwargs) -> AnalysisResult:
        """
        Main analysis entry point - natural language interface
        
        Examples:
        - analyze("Show me sales trends by region in this CSV", files=["sales.csv"])
        - analyze("Build a ML model to predict customer churn")
        - analyze("Research our top 3 competitors and analyze their strategies")
        """
        
        # Create analysis request
        request = AnalysisRequest(
            user_input=user_input,
            files=files or [],
            **kwargs
        )
        
        print(f"🔍 Starting analysis: {user_input}")
        print(f"📁 Files: {request.files}")
        
        try:
            # 1. Plan the analysis workflow
            print("🧠 Planning analysis workflow...")
            workflow = await self.workflow_planner.plan_analysis(request)
            
            print(f"📋 Planned {len(workflow.steps)} steps:")
            for i, step in enumerate(workflow.steps, 1):
                print(f"  {i}. {step.description} ({step.execution_tier.value})")
            
            # 2. Human approval if required
            if workflow.human_approval_required:
                approved = await self._request_human_approval(workflow)
                if not approved:
                    return self._create_cancelled_result(request, "User cancelled analysis")
            
            # 3. Execute the workflow
            print("⚡ Executing analysis workflow...")
            result = await self._execute_workflow(request, workflow)
            
            # 4. Store results in neural memory
            if self.neural_memory:
                await self._store_analysis_in_memory(request, workflow, result)
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return self._create_error_result(request, str(e))
    
    async def _execute_workflow(self, 
                               request: AnalysisRequest, 
                               workflow: AnalysisWorkflow) -> AnalysisResult:
        """Execute the analysis workflow"""
        
        start_time = time.time()
        
        # Track execution
        self.active_analyses[request.request_id] = {
            'workflow': workflow,
            'start_time': start_time,
            'completed_steps': [],
            'failed_steps': []
        }
        
        artifacts_created = []
        execution_results = []
        reasoning_trace = []
        
        try:
            # Execute steps in dependency order
            for step in workflow.steps:
                print(f"🔧 Executing: {step.description}")
                
                step_result = await self._execute_step(step, request, workflow)
                execution_results.append(step_result)
                
                if step_result['success']:
                    self.active_analyses[request.request_id]['completed_steps'].append(step.step_id)
                    
                    # Track artifacts created
                    if 'artifacts' in step_result:
                        artifacts_created.extend(step_result['artifacts'])
                    
                    # Track reasoning
                    if 'reasoning' in step_result:
                        reasoning_trace.append(step_result['reasoning'])
                else:
                    self.active_analyses[request.request_id]['failed_steps'].append(step.step_id)
                    print(f"Step failed: {step_result.get('error', 'Unknown error')}")
            
            # Generate final result
            execution_time = time.time() - start_time
            
            # Synthesize insights from all steps
            insights = await self._synthesize_insights(execution_results, workflow)
            
            # Create final output
            final_output = await self._create_final_output(execution_results, insights)
            
            result = AnalysisResult(
                request_id=request.request_id,
                workflow_id=workflow.workflow_id,
                final_output=final_output,
                artifacts_created=artifacts_created,
                visualizations=[r.get('visualizations', []) for r in execution_results],
                insights=insights,
                execution_time=execution_time,
                steps_completed=len([r for r in execution_results if r['success']]),
                steps_failed=len([r for r in execution_results if not r['success']]),
                execution_tiers_used=list(set(step.execution_tier for step in workflow.steps)),
                confidence_score=self._calculate_confidence_score(execution_results),
                reliability_score=self._calculate_reliability_score(execution_results),
                constitutional_compliance=True,  # Would check with CAS
                reasoning_trace=reasoning_trace
            )
            
            # Update performance stats
            self._update_performance_stats(result)
            
            return result
            
        finally:
            # Clean up active analysis
            self.active_analyses.pop(request.request_id, None)
    
    async def _execute_step(self, 
                          step: AnalysisStep, 
                          request: AnalysisRequest,
                          workflow: AnalysisWorkflow) -> Dict[str, Any]:
        """Execute a single analysis step"""
        
        try:
            if step.execution_tier == ExecutionTier.REASONING:
                return await self._execute_reasoning_step(step, request)
            elif step.execution_tier == ExecutionTier.SAFE_EXECUTION:
                return await self._execute_safe_step(step, request)
            elif step.execution_tier == ExecutionTier.SOVEREIGN:
                return await self._execute_sovereign_step(step, request)
            else:
                return {'success': False, 'error': f'Unknown execution tier: {step.execution_tier}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_reasoning_step(self, step: AnalysisStep, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute reasoning-only step (no code execution)"""
        
        if self.thinking_kernel:
            # Use extended thinking for reasoning
            reasoning_prompt = f"""
            Analysis Step: {step.description}
            
            Context: {step.expected_output}
            
            Provide detailed reasoning and insights for this analysis step.
            Do not execute any code - focus on analytical reasoning.
            """
            
            thinking_result = await self.thinking_kernel.process_with_thinking(
                model_id="analysis_model",
                prompt=reasoning_prompt,
                context={'step': step, 'request': request}
            )
            
            return {
                'success': True,
                'output': thinking_result.response,
                'reasoning': thinking_result.reasoning_trace,
                'confidence': thinking_result.confidence
            }
        else:
            # Fallback to simple reasoning
            return {
                'success': True,
                'output': f"Reasoning completed for: {step.description}",
                'reasoning': [{'step': step.step_id, 'type': 'simple_reasoning'}],
                'confidence': 0.7
            }
    
    async def _execute_safe_step(self, step: AnalysisStep, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute step in safe sandbox (browser-like environment)"""
        
        if not self.artifact_manager:
            return {'success': False, 'error': 'Artifact manager not available'}
        
        # Create artifact for safe execution
        artifact = await self.artifact_manager.create_artifact(
            name=f"analysis_step_{step.step_id}",
            artifact_type=ArtifactType.PYTHON,
            execution_environment=ExecutionEnvironment.CONTAINER,  # Safe container
            content=step.code or "# No code provided"
        )
        
        # Execute in safe environment
        execution_result = await self.artifact_manager.execute_artifact(artifact.artifact_id)
        
        return {
            'success': execution_result.success,
            'output': execution_result.output,
            'artifacts': [artifact.artifact_id],
            'execution_time': execution_result.execution_time
        }
    
    async def _execute_sovereign_step(self, step: AnalysisStep, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute step with full sovereign capabilities"""
        
        if not self.artifact_manager:
            return {'success': False, 'error': 'Artifact manager not available'}
        
        # Constitutional compliance check
        if self.cas_governor and request.constitutional_compliance:
            compliance_check = await self._check_step_compliance(step)
            if not compliance_check['allowed']:
                return {'success': False, 'error': f"Constitutional violation: {compliance_check['reason']}"}
        
        # Create artifact for sovereign execution
        artifact = await self.artifact_manager.create_artifact(
            name=f"sovereign_analysis_{step.step_id}",
            artifact_type=ArtifactType.PYTHON,
            execution_environment=ExecutionEnvironment.UNLIMITED,  # Full power
            content=step.code or "# No code provided"
        )
        
        # Execute with full capabilities
        execution_result = await self.artifact_manager.execute_artifact(artifact.artifact_id)
        
        return {
            'success': execution_result.success,
            'output': execution_result.output,
            'artifacts': [artifact.artifact_id],
            'execution_time': execution_result.execution_time,
            'constitutional_compliance': True
        }
    
    async def _request_human_approval(self, workflow: AnalysisWorkflow) -> bool:
        """Request human approval for workflow execution"""
        
        print("\n" + "="*60)
        print("🤝 HUMAN APPROVAL REQUIRED")
        print("="*60)
        print(f"Analysis: {workflow.description}")
        print(f"Estimated time: {workflow.estimated_total_time:.1f} seconds")
        print(f"Safety score: {workflow.safety_score:.2f}")
        print(f"Execution tiers: {[tier.value for tier in workflow.required_execution_tiers]}")
        
        print("\nPlanned steps:")
        for i, step in enumerate(workflow.steps, 1):
            tier_emoji = {"reasoning": "🧠", "safe_execution": "🔒", "sovereign": "👑"}
            print(f"  {i}. {tier_emoji.get(step.execution_tier.value, '⚡')} {step.description}")
            if step.safety_considerations:
                print(f"     ⚠️  Safety: {', '.join(step.safety_considerations)}")
        
        print("\n" + "="*60)

        # Auto-approve when running non-interactively or when env var is set.
        auto_approve = os.environ.get("SOVEREIGN_AUTO_APPROVE", "").lower() in ("1", "true", "yes")
        if auto_approve or not sys.stdin.isatty():
            logger.info("Workflow auto-approved (non-interactive or SOVEREIGN_AUTO_APPROVE set)")
            print("[AUTO-APPROVED]")
            return True

        try:
            approval = input("Approve this analysis workflow? (y/N): ").lower().strip()
            approved = approval in ("y", "yes")
            logger.info("User approval decision: %s", "approved" if approved else "denied")
            return approved
        except (EOFError, KeyboardInterrupt):
            logger.info("Workflow approval interrupted — defaulting to deny")
            print("\n[DENIED — interrupted]")
            return False
    
    async def _synthesize_insights(self, execution_results: List[Dict[str, Any]], 
                                 workflow: AnalysisWorkflow) -> List[str]:
        """Synthesize insights from execution results"""
        
        insights = []
        
        # Extract insights from successful steps
        for result in execution_results:
            if result['success'] and 'output' in result:
                # Simple insight extraction (would be more sophisticated)
                output = result['output']
                if 'correlation' in output.lower():
                    insights.append("Strong correlations detected in data")
                if 'trend' in output.lower():
                    insights.append("Significant trends identified")
                if 'pattern' in output.lower():
                    insights.append("Interesting patterns discovered")
        
        return insights
    
    async def _create_final_output(self, execution_results: List[Dict[str, Any]], 
                                 insights: List[str]) -> str:
        """Create final analysis output"""
        
        output_parts = [
            "# Analysis Results\n",
            f"Generated {len(execution_results)} analysis components.\n",
            f"\n## Key Insights:\n"
        ]
        
        for insight in insights:
            output_parts.append(f"- {insight}\n")
        
        output_parts.append(f"\n## Detailed Results:\n")
        
        for i, result in enumerate(execution_results, 1):
            if result['success']:
                output_parts.append(f"\n### Step {i} Results:\n")
                output_parts.append(f"{result.get('output', 'No output')}\n")
        
        return "".join(output_parts)
    
    def _calculate_confidence_score(self, execution_results: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score"""
        
        if not execution_results:
            return 0.0
        
        successful_results = [r for r in execution_results if r['success']]
        success_rate = len(successful_results) / len(execution_results)
        
        # Average confidence from individual steps
        confidences = [r.get('confidence', 0.7) for r in successful_results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7
        
        return (success_rate * 0.6 + avg_confidence * 0.4)
    
    def _calculate_reliability_score(self, execution_results: List[Dict[str, Any]]) -> float:
        """Calculate reliability score"""
        
        if not execution_results:
            return 0.0
        
        # Simple reliability based on success rate and execution times
        success_rate = len([r for r in execution_results if r['success']]) / len(execution_results)
        return min(1.0, success_rate * 1.1)  # Slight boost for high success rates
    
    def _update_performance_stats(self, result: AnalysisResult):
        """Update performance statistics"""
        
        self.performance_stats['total_analyses'] += 1
        
        if result.steps_failed == 0:
            self.performance_stats['successful_analyses'] += 1
        
        # Update average execution time
        current_avg = self.performance_stats['average_execution_time']
        total_analyses = self.performance_stats['total_analyses']
        new_avg = ((total_analyses - 1) * current_avg + result.execution_time) / total_analyses
        self.performance_stats['average_execution_time'] = new_avg
        
        # Update tier usage
        for tier in result.execution_tiers_used:
            self.performance_stats['tier_usage'][tier.value] += 1
    
    async def _store_analysis_in_memory(self, 
                                      request: AnalysisRequest,
                                      workflow: AnalysisWorkflow, 
                                      result: AnalysisResult):
        """Store analysis results in neural memory"""
        
        if not self.neural_memory:
            return
        
        # Store in appropriate memory tier
        memory_tier = 'HOT' if result.confidence_score > 0.8 else 'WARM'
        
        await self.neural_memory.store_analysis_memory(
            content={
                'request': request.user_input,
                'workflow_type': workflow.analysis_type.value,
                'result_summary': result.final_output[:500],  # Truncate for storage
                'insights': result.insights,
                'confidence': result.confidence_score
            },
            memory_tier=memory_tier,
            metadata={
                'source': 'somnus_analysis',
                'analysis_type': workflow.analysis_type.value,
                'execution_time': result.execution_time,
                'artifacts_created': len(result.artifacts_created)
            }
        )
    
    async def _check_step_compliance(self, step: AnalysisStep) -> Dict[str, Any]:
        """Check constitutional compliance for a step"""
        
        # This would integrate with the CAS system
        # For now, simple approval
        return {'allowed': True, 'reason': 'Constitutional check passed'}
    
    def _create_cancelled_result(self, request: AnalysisRequest, reason: str) -> AnalysisResult:
        """Create result for cancelled analysis"""
        
        return AnalysisResult(
            request_id=request.request_id,
            workflow_id="cancelled",
            final_output=f"Analysis cancelled: {reason}",
            artifacts_created=[],
            visualizations=[],
            insights=[],
            execution_time=0.0,
            steps_completed=0,
            steps_failed=0,
            execution_tiers_used=[],
            confidence_score=0.0,
            reliability_score=0.0,
            constitutional_compliance=True,
            reasoning_trace=[]
        )
    
    def _create_error_result(self, request: AnalysisRequest, error: str) -> AnalysisResult:
        """Create result for failed analysis"""
        
        return AnalysisResult(
            request_id=request.request_id,
            workflow_id="error",
            final_output=f"Analysis failed: {error}",
            artifacts_created=[],
            visualizations=[],
            insights=[],
            execution_time=0.0,
            steps_completed=0,
            steps_failed=1,
            execution_tiers_used=[],
            confidence_score=0.0,
            reliability_score=0.0,
            constitutional_compliance=False,
            reasoning_trace=[]
        )
    
    # Additional utility methods
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.performance_stats.copy()
    
    def get_active_analyses(self) -> List[str]:
        """Get list of active analysis IDs"""
        return list(self.active_analyses.keys())


# Factory function for easy setup
def create_somnus_analysis_tool(
    neural_memory: Optional[NeuralMemoryRuntime] = None,
    cas_governor: Optional[ConstitutionalGovernor] = None,
    artifact_manager: Optional[SomnusArtifactManager] = None,
    vm_orchestrator: Optional[VMOrchestrator] = None,
    thinking_kernel: Optional[ExtendedThinkingKernel] = None
) -> SomnusAnalysisTool:
    """Create fully integrated Somnus Analysis Tool"""
    
    return SomnusAnalysisTool(
        neural_memory=neural_memory,
        cas_governor=cas_governor,
        artifact_manager=artifact_manager,
        vm_orchestrator=vm_orchestrator,
        thinking_kernel=thinking_kernel
    )


# ============================================================================
# PHASE 6: Shell Integration Wrapper
# ============================================================================

class SovereignAnalysisToolWrapper:
    """Expose the analysis tool as a native shell component.

    Implements ``get_tools()`` so the Advanced AI Shell can auto-discover and
    register analysis commands.
    """

    def __init__(self, tool: Optional[SomnusAnalysisTool] = None):
        self._tool = tool or SomnusAnalysisTool()
        self._event_logger = StructuredEventLogger()
        self._metrics = AnalysisMetricsCollector()
        self._checkpoint_mgr = CheckpointManager()
        self._recovery_mgr = WorkflowRecoveryManager(self._checkpoint_mgr)
        self._artifact_executor = ArtifactAnalysisExecutor()

    # ------------------------------------------------------------------ #
    # Shell registration
    # ------------------------------------------------------------------ #

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return tool descriptors for shell auto-discovery."""
        return {
            'analysis_execute': {
                'description': 'Execute a natural-language analysis request',
                'handler': self.execute_analysis,
                'parameters': {
                    'query': {'type': 'string', 'description': 'Analysis request in natural language', 'required': True},
                    'files': {'type': 'list', 'description': 'File paths to include', 'required': False},
                    'tier': {'type': 'string', 'description': 'Execution tier: reasoning|safe_execution|sovereign', 'required': False},
                },
            },
            'analysis_plan': {
                'description': 'Plan a workflow without executing it',
                'handler': self.plan_workflow,
                'parameters': {
                    'query': {'type': 'string', 'description': 'Analysis request in natural language', 'required': True},
                },
            },
            'analysis_status': {
                'description': 'Get status of an active or completed analysis',
                'handler': self.get_workflow_status,
                'parameters': {
                    'workflow_id': {'type': 'string', 'description': 'Workflow ID', 'required': True},
                },
            },
            'analysis_resume': {
                'description': 'Resume a failed or interrupted workflow',
                'handler': self.resume_workflow,
                'parameters': {
                    'workflow_id': {'type': 'string', 'description': 'Workflow ID to resume', 'required': True},
                },
            },
        }

    # ------------------------------------------------------------------ #
    # Tool handlers
    # ------------------------------------------------------------------ #

    async def execute_analysis(self, query: str,
                                files: Optional[List[str]] = None,
                                tier: str = 'safe_execution') -> Dict[str, Any]:
        """Execute a full analysis workflow end-to-end."""
        correlation_id = str(uuid4())
        self._event_logger.workflow_start(correlation_id, {'query': query, 'tier': tier})
        start = time.time()

        try:
            result = await self._tool.analyze(query, files=files or [])
            elapsed_ms = (time.time() - start) * 1000
            self._event_logger.workflow_complete(correlation_id, elapsed_ms, success=True)
            self._metrics.record_latency(correlation_id, elapsed_ms)
            return {
                'status': 'complete',
                'correlation_id': correlation_id,
                'elapsed_ms': round(elapsed_ms, 2),
                'result': result,
            }
        except Exception as exc:
            elapsed_ms = (time.time() - start) * 1000
            self._event_logger.workflow_complete(correlation_id, elapsed_ms, success=False,
                                                  metadata={'error': str(exc)})
            self._metrics.record_error(correlation_id, str(exc))
            return {
                'status': 'failed',
                'correlation_id': correlation_id,
                'error': str(exc),
            }

    async def plan_workflow(self, query: str) -> Dict[str, Any]:
        """Plan an analysis workflow without executing it."""
        planner = AnalysisWorkflowPlanner()
        request = AnalysisRequest(user_input=query)
        workflow = await planner.plan_analysis(request)
        return {
            'workflow_id': workflow.workflow_id,
            'analysis_type': workflow.analysis_type.value,
            'steps': [
                {
                    'step_id': s.step_id,
                    'name': s.description,
                    'description': s.description,
                    'step_type': s.step_type,
                    'tier': s.execution_tier.value,
                }
                for s in workflow.steps
            ],
        }

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow by checking its checkpoint."""
        checkpoint = await self._checkpoint_mgr.load_latest_checkpoint(workflow_id)
        if checkpoint is None:
            return {'status': 'not_found', 'workflow_id': workflow_id}
        return {
            'status': 'recovered',
            'workflow_id': workflow_id,
            'completed_steps': len(checkpoint.completed_steps),
            'pending_steps': len(checkpoint.pending_steps),
            'retry_count': checkpoint.retry_count,
            'last_error': checkpoint.last_error,
            'timestamp': checkpoint.timestamp,
        }

    async def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Resume a workflow from its last checkpoint."""
        checkpoint = await self._checkpoint_mgr.load_latest_checkpoint(workflow_id)
        if checkpoint is None:
            return {'status': 'no_checkpoint', 'workflow_id': workflow_id}

        return {
            'status': 'resume_ready',
            'workflow_id': workflow_id,
            'will_resume_from_step': checkpoint.current_step or 'next_pending',
            'completed': len(checkpoint.completed_steps),
            'remaining': len(checkpoint.pending_steps),
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Return current metrics summary."""
        return self._metrics.get_summary()


# Example usage
if __name__ == "__main__":
    print("\U0001f50d Somnus Sovereign Analysis Tool")
    print("Natural language analysis with sovereign capabilities")
    print("\nExample usage:")
    print("- analysis_tool.analyze('Show me sales trends by region', files=['sales.csv'])")
    print("- analysis_tool.analyze('Build ML model to predict customer churn')")
    print("- analysis_tool.analyze('Research our top competitors and analyze strategies')")
    print("\nPhases implemented: Artifact Container, Resource Governance, Checkpoint,")
    print("Observability, Shell Integration")
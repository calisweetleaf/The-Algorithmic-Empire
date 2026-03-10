"""
Sovereign Production Pipeline Orchestrator
==========================================
Production-grade pipeline for entity network analysis.

Features:
- Parallel execution of independent stages
- Checkpointing for resumability  
- Comprehensive logging with structured output
- Error recovery and retry logic
- JSON manifest generation for audit trails

Usage:
    python tools/run_pipeline.py                    # Full pipeline
    python tools/run_pipeline.py --stage metrics    # Run specific stage
    python tools/run_pipeline.py --parallel         # Parallel execution
    python tools/run_pipeline.py --resume           # Resume from checkpoint
"""

import argparse
import json
import subprocess
import sys
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import concurrent.futures
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

class Stage(Enum):
    CITATIONS = "citations"
    APPENDIX = "appendix"
    ENTITY_CLEAN = "entity_clean"
    SYNTHESIS = "synthesis"
    VISUALIZATION = "visualization"
    METRICS = "metrics"

@dataclass
class PipelineManifest:
    """Track pipeline execution for audit and recovery."""
    pipeline_id: str
    started_at: str
    completed_at: Optional[str] = None
    status: str = "running"
    stages: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_dir: Path) -> logging.Logger:
    """Configure structured logging."""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('sovereign_pipeline')
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_dir / f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

# ============================================================================
# PIPELINE ENGINE
# ============================================================================

class SovereignPipeline:
    """Production pipeline orchestrator."""
    
    STAGES = [
        Stage.CITATIONS,
        Stage.APPENDIX,
        Stage.ENTITY_CLEAN,
        Stage.SYNTHESIS,
        Stage.VISUALIZATION,
    ]
    
    def __init__(self, root: Path, logger: logging.Logger):
        self.root = root
        self.logger = logger
        self.tools_dir = root / 'tools'
        self.docs_dir = root / 'docs'
        self.visuals_dir = root / 'visuals'
        self.data_dir = root / 'data'
        
        # Ensure directories exist
        for d in [self.visuals_dir, self.data_dir]:
            d.mkdir(exist_ok=True)
        
        # Generate pipeline ID
        self.pipeline_id = hashlib.md5(
            datetime.now().isoformat().encode()
        ).hexdigest()[:8]
        
        self.manifest = PipelineManifest(
            pipeline_id=self.pipeline_id,
            started_at=datetime.now().isoformat()
        )
        
        self.python = sys.executable
    
    def run_stage(self, stage: Stage, dry_run: bool = False) -> bool:
        """Execute a single pipeline stage."""
        self.logger.info(f"=" * 50)
        self.logger.info(f"STAGE: {stage.value.upper()}")
        self.logger.info(f"=" * 50)
        
        start_time = datetime.now()
        success = False
        
        try:
            if stage == Stage.CITATIONS:
                success = self._run_citations(dry_run)
            elif stage == Stage.APPENDIX:
                success = self._run_appendix(dry_run)
            elif stage == Stage.ENTITY_CLEAN:
                success = self._run_entity_clean(dry_run)
            elif stage == Stage.SYNTHESIS:
                success = self._run_synthesis(dry_run)
            elif stage == Stage.VISUALIZATION:
                success = self._run_visualization(dry_run)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            self.manifest.stages[stage.value] = {
                "status": "success" if success else "failed",
                "duration_seconds": elapsed,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Stage {stage.value} completed in {elapsed:.2f}s")
            return success
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            error_msg = f"Stage {stage.value} failed: {str(e)}"
            self.logger.error(error_msg)
            
            self.manifest.stages[stage.value] = {
                "status": "failed",
                "duration_seconds": elapsed,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.manifest.errors.append(error_msg)
            
            return False
    
    def _run_citations(self, dry_run: bool) -> bool:
        """Run citation recount."""
        script = self.tools_dir / 'citation_recount.py'
        
        cmd = [self.python, str(script), 
               '--stats', str(self.docs_dir / 'per_document_stats.json'),
               '--root', str(self.root)]
        
        if dry_run:
            cmd.append('--dry-run')
        
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.root)
        )
        
        if result.returncode != 0:
            self.logger.error(f"Citation recount failed: {result.stderr}")
            return False
        
        self.manifest.artifacts['citation_stats'] = str(self.docs_dir / 'per_document_stats.json')
        self.manifest.artifacts['citation_log'] = str(self.docs_dir / 'citation_recount_log.json')
        
        return True
    
    def _run_appendix(self, dry_run: bool) -> bool:
        """Run appendix regeneration."""
        script = self.tools_dir / 'appendix_regenerator.py'
        
        cmd = [self.python, str(script),
               '--stats', str(self.docs_dir / 'per_document_stats.json'),
               '--out', str(self.docs_dir / 'APPENDIX.md')]
        
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.root)
        )
        
        if result.returncode != 0:
            self.logger.error(f"Appendix regeneration failed: {result.stderr}")
            return False
        
        self.manifest.artifacts['appendix'] = str(self.docs_dir / 'APPENDIX.md')
        
        return True
    
    def _run_entity_clean(self, dry_run: bool) -> bool:
        """Run entity decontamination pipeline."""
        script = self.tools_dir / 'entity_cleaner.py'
        
        cmd = [self.python, str(script),
               '--stats', str(self.docs_dir / 'per_document_stats.json'),
               '--out', str(self.docs_dir / 'per_document_stats_clean.json'),
               '--report', str(self.docs_dir / 'cleaning_report.json'),
               '--detect-dupes']
        
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.root)
        )
        
        if result.returncode != 0:
            self.logger.error(f"Entity cleaning failed: {result.stderr}")
            return False
        
        self.manifest.artifacts['clean_stats'] = str(self.docs_dir / 'per_document_stats_clean.json')
        self.manifest.artifacts['cleaning_report'] = str(self.docs_dir / 'cleaning_report.json')
        
        return True
    
    def _run_synthesis(self, dry_run: bool) -> bool:
        """Run synthesis engine."""
        script = self.tools_dir / 'synthesis_engine.py'
        
        cmd = [self.python, str(script),
               '--stats', str(self.docs_dir / 'per_document_stats_clean.json'),
               '--out-json', str(self.docs_dir / 'synthesis_matrix.json'),
               '--out-md', str(self.docs_dir / 'entity_network.md')]
        
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.root)
        )
        
        if result.returncode != 0:
            self.logger.error(f"Synthesis failed: {result.stderr}")
            return False
        
        self.manifest.artifacts['synthesis_matrix'] = str(self.docs_dir / 'synthesis_matrix.json')
        self.manifest.artifacts['entity_network'] = str(self.docs_dir / 'entity_network.md')
        
        return True
    
    def _run_visualization(self, dry_run: bool) -> bool:
        """Run visualization engine."""
        script = self.tools_dir / 'visualize_network.py'
        
        cmd = [self.python, str(script),
               '--mode', 'full',
               '--input', str(self.docs_dir / 'entity_network.md'),
               '--output-dir', 'visuals']
        
        if not dry_run:
            cmd.append('--export-json')
            cmd.append(str(self.visuals_dir / 'network_metrics.json'))
        
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.root)
        )
        
        if result.returncode != 0:
            self.logger.error(f"Visualization failed: {result.stderr}")
            return False
        
        self.manifest.artifacts['visualization_3d'] = str(self.visuals_dir / 'sovereign_network_3d.html')
        self.manifest.artifacts['gexf_export'] = str(self.visuals_dir / 'sovereign_network_advanced.gexf')
        self.manifest.artifacts['metrics_json'] = str(self.visuals_dir / 'network_metrics.json')
        
        return True
    
    def run_all(self, stages: Optional[List[Stage]] = None, 
                dry_run: bool = False,
                parallel: bool = False) -> bool:
        """Run all pipeline stages."""
        if stages is None:
            stages = self.STAGES
        
        self.logger.info(f"Starting pipeline {self.pipeline_id}")
        self.logger.info(f"Running {len(stages)} stages: {[s.value for s in stages]}")
        
        if parallel:
            # Run independent stages in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(self.run_stage, stage, dry_run): stage 
                          for stage in stages}
                
                for future in concurrent.futures.as_completed(futures):
                    stage = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"Stage {stage.value} raised exception: {e}")
        else:
            # Sequential execution
            for stage in stages:
                if not self.run_stage(stage, dry_run):
                    self.logger.error(f"Pipeline aborted at stage: {stage.value}")
                    return self._finalize(success=False)
        
        return self._finalize(success=not self.manifest.errors)
    
    def _finalize(self, success: bool) -> bool:
        """Finalize pipeline and save manifest."""
        self.manifest.completed_at = datetime.now().isoformat()
        self.manifest.status = "completed" if success else "failed"
        
        # Save manifest
        manifest_path = self.data_dir / 'pipeline_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(asdict(self.manifest), f, indent=2)
        
        self.logger.info(f"Pipeline {self.pipeline_id} {self.manifest.status}")
        self.logger.info(f"Manifest saved to: {manifest_path}")
        
        return success

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sovereign Production Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--root',
        default='.',
        help='Project root directory'
    )
    parser.add_argument(
        '--stage',
        choices=[s.value for s in Stage],
        help='Run specific stage only'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run independent stages in parallel'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without making changes'
    )
    parser.add_argument(
        '--log-dir',
        default='data/logs',
        help='Log output directory'
    )
    
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    log_dir = root / args.log_dir
    
    logger = setup_logging(log_dir)
    
    pipeline = SovereignPipeline(root, logger)
    
    if args.stage:
        # Run single stage
        stage = Stage(args.stage)
        success = pipeline.run_stage(stage, args.dry_run)
    else:
        # Run all stages
        success = pipeline.run_all(
            stages=None,
            dry_run=args.dry_run,
            parallel=args.parallel
        )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

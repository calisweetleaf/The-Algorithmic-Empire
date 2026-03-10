#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Sets up a Python virtual environment for SOMNUS File Processor

.DESCRIPTION
    This script creates a Python virtual environment, installs all dependencies,
    and downloads required NLTK/spaCy data for production use.

.PARAMETER InstallMode
    Installation mode: 'core', 'recommended', 'full', or 'dev'
    - core: Only required dependencies
    - recommended: Core + sentence-transformers + spacy (default)
    - full: All optional dependencies
    - dev: Full + development tools

.EXAMPLE
    .\setup_venv.ps1
    .\setup_venv.ps1 -InstallMode full
    .\setup_venv.ps1 -InstallMode dev
#>

param(
    [ValidateSet('core', 'recommended', 'full', 'dev')]
    [string]$InstallMode = 'recommended'
)

$ErrorActionPreference = 'Stop'

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warn { Write-Host $args -ForegroundColor Yellow }

Write-Info "============================================"
Write-Info "  SOMNUS File Processor - Environment Setup"
Write-Info "============================================"
Write-Host ""

# Check Python version
Write-Info "Checking Python version..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found. Please install Python 3.10+ and add it to PATH."
    exit 1
}
Write-Success "Found: $pythonVersion"

# Extract version number and check
$versionMatch = [regex]::Match($pythonVersion, '(\d+)\.(\d+)')
if ($versionMatch.Success) {
    $major = [int]$versionMatch.Groups[1].Value
    $minor = [int]$versionMatch.Groups[2].Value
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-Error "Python 3.10+ is required. Found: $major.$minor"
        exit 1
    }
}

# Create virtual environment
$venvPath = ".\.venv"
if (Test-Path $venvPath) {
    Write-Warn "Virtual environment already exists at $venvPath"
    $response = Read-Host "Delete and recreate? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Info "Removing existing virtual environment..."
        Remove-Item -Recurse -Force $venvPath
    } else {
        Write-Info "Using existing virtual environment..."
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Info "Creating virtual environment..."
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    Write-Success "Virtual environment created at $venvPath"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
$activateScript = "$venvPath\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Activation script not found at $activateScript"
    exit 1
}
. $activateScript

# Upgrade pip
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Warn "pip upgrade had issues, continuing..."
}

# Install dependencies based on mode
Write-Info "Installing dependencies (mode: $InstallMode)..."
switch ($InstallMode) {
    'core' {
        pip install -r requirements.txt --only-binary :all: 2>$null
        if ($LASTEXITCODE -ne 0) {
            pip install -r requirements.txt
        }
    }
    'recommended' {
        pip install -e ".[recommended]" --only-binary :all: 2>$null
        if ($LASTEXITCODE -ne 0) {
            pip install -e ".[recommended]"
        }
    }
    'full' {
        pip install -e ".[full]" --only-binary :all: 2>$null
        if ($LASTEXITCODE -ne 0) {
            pip install -e ".[full]"
        }
    }
    'dev' {
        pip install -e ".[full,dev]" --only-binary :all: 2>$null
        if ($LASTEXITCODE -ne 0) {
            pip install -e ".[full,dev]"
        }
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    exit 1
}
Write-Success "Dependencies installed successfully"

# Download NLTK data
Write-Info "Downloading NLTK data..."
python -c @"
import nltk
import ssl

# Handle SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

datasets = [
    'punkt', 'averaged_perceptron_tagger', 'wordnet', 'stopwords',
    'vader_lexicon', 'omw-1.4', 'maxent_ne_chunker', 'words'
]

for dataset in datasets:
    try:
        nltk.download(dataset, quiet=True)
        print(f'  ✓ {dataset}')
    except Exception as e:
        print(f'  ✗ {dataset}: {e}')
"@

if ($LASTEXITCODE -ne 0) {
    Write-Warn "Some NLTK data may not have downloaded correctly"
}

# Download spaCy model if recommended or full
if ($InstallMode -in @('recommended', 'full', 'dev')) {
    Write-Info "Downloading spaCy English model..."
    python -m spacy download en_core_web_sm 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "spaCy model download failed - you can run this manually later:"
        Write-Warn "  python -m spacy download en_core_web_sm"
    } else {
        Write-Success "spaCy model downloaded"
    }
}

# Verify installation
Write-Info "Verifying installation..."
python -c @"
import sys
print(f'Python: {sys.version}')

# Check core imports
try:
    import numpy
    print(f'  ✓ numpy {numpy.__version__}')
except ImportError as e:
    print(f'  ✗ numpy: {e}')

try:
    import scipy
    print(f'  ✓ scipy {scipy.__version__}')
except ImportError as e:
    print(f'  ✗ scipy: {e}')

try:
    import sklearn
    print(f'  ✓ scikit-learn {sklearn.__version__}')
except ImportError as e:
    print(f'  ✗ scikit-learn: {e}')

try:
    import nltk
    print(f'  ✓ nltk {nltk.__version__}')
except ImportError as e:
    print(f'  ✗ nltk: {e}')

try:
    import networkx
    print(f'  ✓ networkx {networkx.__version__}')
except ImportError as e:
    print(f'  ✗ networkx: {e}')

try:
    import PIL
    print(f'  ✓ Pillow {PIL.__version__}')
except ImportError as e:
    print(f'  ✗ Pillow: {e}')

try:
    import aiofiles
    print(f'  ✓ aiofiles')
except ImportError as e:
    print(f'  ✗ aiofiles: {e}')

try:
    import ratelimit
    print(f'  ✓ ratelimit')
except ImportError as e:
    print(f'  ✗ ratelimit: {e}')

try:
    import pydantic
    print(f'  ✓ pydantic {pydantic.__version__}')
except ImportError as e:
    print(f'  ✗ pydantic: {e}')

# Check optional imports
print('')
print('Optional dependencies:')

try:
    from sentence_transformers import SentenceTransformer
    print(f'  ✓ sentence-transformers')
except ImportError:
    print(f'  - sentence-transformers (not installed)')

try:
    import spacy
    print(f'  ✓ spacy {spacy.__version__}')
except ImportError:
    print(f'  - spacy (not installed)')

try:
    import cv2
    print(f'  ✓ opencv {cv2.__version__}')
except ImportError:
    print(f'  - opencv (not installed)')

try:
    import librosa
    print(f'  ✓ librosa {librosa.__version__}')
except ImportError:
    print(f'  - librosa (not installed)')
"@

Write-Host ""
Write-Success "============================================"
Write-Success "  Setup Complete!"
Write-Success "============================================"
Write-Host ""
Write-Info "To activate the environment in future sessions:"
Write-Info "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Info "To run tests (if dev mode):"
Write-Info "  pytest tests/"
Write-Host ""
Write-Info "To use the processors:"
Write-Info "  from semantic_chunking_rewrite import SemanticChunkingProcessor"
Write-Info "  from universal_file_processors import ProcessingCapabilities"
Write-Host ""

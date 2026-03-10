# SOMNUS Universal Processor - Format Support Matrix

## Production Status: READY FOR USE

This document clarifies which file formats have **full processing** vs. **fallback/metadata-only processing**.

### ✅ Fully Supported Formats

These formats have complete extraction with content analysis:

**Documents:**

- `.pdf` - Full text extraction, page metadata
- `.docx` - Paragraph extraction, table detection
- `.doc` - Basic text extraction
- `.txt` - Full text with encoding detection
- `.md` - Full markdown text
- `.csv` - Data analysis with pandas
- `.xlsx/.xls` - Excel sheets analysis
- `.json` - Structured data parsing
- `.yaml/.yml` - Configuration parsing
- `.toml` - Configuration parsing
- `.ini/.cfg` - Configuration parsing

**Images (with OCR):**

- `.jpg/.jpeg` - OCR text extraction
- `.png` - OCR text extraction
- `.gif/.bmp/.webp/.tiff` - Basic metadata
- `.svg` - XML structure and text extraction

**Code Files:**

- `.py/.js/.html/.css` - Full text with line analysis
- `.java/.cpp/.c/.h/.cs/.php/.rb/.go/.rs` - Source code extraction
- `.sql/.swift/.kt/.ts/.jsx/.tsx/.vue/.svelte` - Full text extraction

**Archives:**

- `.zip` - File listing and recursive text extraction
- `.tar/.gz/.bz2/.xz` - Archive content listing

**CAD/3D (when libraries available):**

- `.psd` - Layer text extraction (requires psd-tools)
- `.dwg/.dxf` - CAD entity extraction (requires ezdxf)
- `.stl/.obj/.ply` - 3D mesh analysis (requires trimesh)

**Scientific (when libraries available):**

- `.mat` - MATLAB data (requires scipy)
- `.hdf5/.h5` - HDF5 datasets (requires h5py)
- `.dcm/.dicom` - Medical imaging metadata (requires pydicom)

**Media (when libraries available):**

- `.mp3/.wav/.flac/.ogg/.m4a` - Audio metadata (requires librosa/ffmpeg)
- `.mp4/.avi/.mkv/.mov` - Video metadata (requires ffmpeg)

### ⚠️ Fallback Processing (Metadata Only)

These formats return basic metadata with clear descriptions of what tools are needed:

**Creative Design:**

- `.sketch` - Sketch format (needs Sketch app/API)
- `.fig` - Figma format (needs Figma API)
- `.xd` - Adobe XD format (needs Adobe XD)
- `.indd` - InDesign format (needs InDesign)
- `.ai/.eps` - Illustrator files (limited text extraction)

**Advanced 3D:**

- `.step/.stp` - STEP CAD models (needs OpenCASCADE)
- `.iges/.igs` - IGES CAD models (needs OpenCASCADE)
- `.blend` - Blender scenes (needs Blender installation)

**Advanced Scientific:**

- `.nii/.nii.gz` - Neuroimaging (needs nibabel)
- `.fif` - MEG/EEG (needs mne-python)
- `.edf` - EEG data (needs pyEDFlib)

### ❌ Unsupported / Binary Detection

These are treated as binary with string extraction:

- `.exe/.dll/.so/.bin` - Executables (security-blocked)
- Printer-specific formats
- Proprietary binary formats

## 📊 Processing Capabilities API

Use this to programmatically check format support:

```python
from universal_file_processors import ProcessingCapabilities, CreativeFileProcessor

capabilities = ProcessingCapabilities()
print(capabilities.get_summary())

# Check specific processor
processor = CreativeFileProcessor(capabilities, executor)
if processor.can_process(file_path, mime_type):
    result = await processor.process_file(file_path, metadata)
```

## 🛡️ Security Note

**Executable formats** (`.exe`, `.bat`, `.cmd`, `.msi`, `.dll`) are **security-blocked** and will be marked as `SecurityLevel.BLOCKED`.

## 🔄 Graceful Degradation

All processors follow this pattern:

1. Check if specialized libraries are available
2. If available: Full extraction
3. If not available: Informative fallback with metadata
4. Never fail silently - always return `ProcessingResult` with success status

This ensures **production reliability** even when optional dependencies are missing.

---

**Last Updated:** 2025-01-14
**Production Status:** ✅ Ready for Deployment

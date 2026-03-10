## Process Log

**Date/Time:** 2026-02-08 08:24:18

### Phase 1 – Unpack & Inventory

- Unzipped SIGINT.zip into ./sigint_raw using the unzip command.
- Wrote a Python script to recursively traverse sigint_raw and collect text-like files (.pdf, .md, .txt, .docx, .html).
- Saved this list as inventory.json with id, filename, relative path and extension for 150 candidate documents.

### Phase 2 – Per-Document Metrics

- Developed a script using pdfinfo and pdftotext (Poppler) to extract page counts and text for PDF files.
- For markdown, text and HTML files, calculated approximate page counts using 500 words per page.
- Implemented citation counting by first searching for a 'references' section and falling back to heuristic patterns such as bracketed numerals or author-year citations.
- Extracted major names by identifying repeated sequences of 2–4 capitalised words.
- Stored these metrics along with document metadata in meta/per_document_stats.json.

### Phase 3 – Light Categorization & Labeling

- Defined a palette of topic tags (THIEL_NETWORK, EPSTEIN_NETWORK, BARAK_ISRAEL, YARVIN_IDEOLOGY, CORPORATE_HANDOFFS, MILITARY_AI_US, MILITARY_AI_CHINA, AI_GOVERNANCE, SURVEILLANCE, FINANCIAL_INFRASTRUCTURE, OTHER).
- Wrote heuristics to assign tags based on filename keywords and extracted major names.
- Assigned unique label identifiers (e.g., T01, E02, U03) derived from the primary tag using a letter plus index.

### Phase 4 – File Tree / Project Structure

- Created the sigint_structured directory with subfolders 00_METHOD, 01_TIMELINE, 02_ACTORS, 03_INFRA, 04_STACK, 05_NETWORK, 06_OPEN_QUESTIONS and 99_MODEL.
- Generated README_FILE_MAP.md containing a mapping of each label to the original file path, suggested folder, and topic tags.

### Phase 5 – Build APPENDIX.md

- Constructed APPENDIX.md with an index of documents by label, grouping by topic buckets, global statistics, and a list of skipped non-text files.
- Global stats reported 150 documents, with combined page and citation counts computed from the per-document metrics.
- Identified 6 non-text files (images or other media) and logged them in the skipped files section.

### Phase 6 – Summary & Observations

- The citation counts for markdown and text files are heuristic and may underestimate or overestimate actual citations.
- PDF parsing used external utilities due to the absence of Python PDF libraries. Some PDFs may yield incomplete text extraction, but page counts are accurate.
- Tagging is based on simple keyword matching and may not capture nuanced themes. Documents tagged as OTHER require manual review for more precise classification.

---

## Re-processing on 2026-02-08 09:06:09

- Executed `process_sigint_thorough.py` to capture additional single-occurrence entity names and refine citation heuristics.
- Updated per-document statistics in `per_document_stats_thorough.json`.
- Regenerated `README_FILE_MAP.md` and `APPENDIX.md` from the thorough metadata to reflect the new names and counts.

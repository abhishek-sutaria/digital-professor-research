# Workflow 3 Quick Start

## ⚠️ Important: Google Scholar Blocking

Google Scholar often blocks automated searches. **Use Scholar ID for best results.**

## Quick Start (Recommended Method)

### Step 1: Find Scholar ID
1. Go to [scholar.google.com](https://scholar.google.com)
2. Search for the person (e.g., "Kevin Lane Keller")
3. Click their profile
4. Copy ID from URL: `scholar.google.com/citations?user=<ID>`

### Step 2: Run Workflow 3
```bash
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ
```

That's it! The system will:
- ✓ Fetch papers from Google Scholar
- ✓ Download available PDFs
- ✓ Generate report with inline citations
- ✓ Create detailed checklist

## Alternative Methods

### Option 2: Use Person Name (May Fail)
```bash
python workflow3_paper_profile/main.py "Kevin Lane Keller"
```
**Note:** If Google Scholar blocks this, the system automatically falls back to CrossRef/Semantic Scholar.

### Option 3: Use Workflow 2 (Alternative with More Advanced Features)
```bash
python scripts/generate_digital_twin_report.py --scholar-id x8xNLZQAAAAJ
```

## What's Implemented

Workflow 3 is fully built with all requested features:
- ✓ Inline citations after each paragraph
- ✓ Downloaded papers folder
- ✓ Detailed checklist (HTML/CSV/JSON)
- ✓ 10 comprehensive sections
- ✓ Metadata-only citations
- ✓ Section-to-paper tracking
- ✓ **Enhanced paper downloader** with multiple sources:
  - JSTOR (with institutional access detection)
  - Google Scholar (extracts all available URLs)
  - Unpaywall (open access PDFs)
  - arXiv (preprints)
  - DOI resolution (publisher PDFs)
- ✓ **Comprehensive URL extraction** from `epubs_src_bib_info` (ResearchGate, etc)

## Testing

### Test with Scholar ID (Recommended)
```bash
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ \
    --output-dir ./workflow3_output \
    --max-papers 50 \
    --rate-limit 2.0
```

### Test with Name (Fallback Mode)
```bash
python workflow3_paper_profile/main.py "Kevin Lane Keller" \
    --output-dir ./workflow3_output \
    --max-papers 50 \
    --rate-limit 2.0
```

### Expected Outputs
- `workflow3_output/Kevin_Lane_Keller_profile.pdf` - Report with inline citations
- `workflow3_output/Kevin_Lane_Keller_papers/` - Downloaded PDFs
- `workflow3_output/Kevin_Lane_Keller_checklist.html` - Interactive checklist
- `workflow3_output/Kevin_Lane_Keller_checklist.csv` - Spreadsheet format
- `workflow3_output/Kevin_Lane_Keller_checklist.json` - JSON format

## Implementation Status

All components completed and enhanced:
1. ✓ `citation_tracker.py` - Tracks citations across sections
2. ✓ `person_searcher.py` - **Enhanced** with comprehensive URL extraction from Google Scholar
3. ✓ `paper_download_manager.py` - **Replaces** basic downloader with multi-source support
4. ✓ `content_analyzer.py` - Analyzes PDFs (creates metadata-only placeholders when needed)
5. ✓ `report_generator.py` - 10-section report with inline citations
6. ✓ `checklist_generator.py` - Detailed usage tracking with download status
7. ✓ `main.py` - Orchestrator with Scholar ID support
8. ✓ `QUICK_START.md` - This documentation

## Recent Enhancements (Nov 2024)

The paper downloading system has been significantly upgraded:
- **Multi-source downloading**: JSTOR, Scholar, Unpaywall, arXiv, DOI resolution
- **Better URL extraction**: Uses `scholarly.fill()` to get all available URLs per paper
- **Robust fallbacks**: DOI-based search, institutional access detection
- **Success tracking**: Clear reporting of what was downloaded vs. what's unavailable
- **Graceful degradation**: System generates report even when papers can't be downloaded

## Example Output

When you run the system, you'll get:
- A comprehensive PDF report with inline citations
- A folder with all successfully downloaded papers
- A detailed checklist showing:
  - Which papers were downloaded vs. metadata-only
  - Where each paper was cited (which sections)
  - Access suggestions for unavailable papers


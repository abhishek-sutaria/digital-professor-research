# Person Information Scraper & Digital Twin Generator

A comprehensive system for collecting detailed information about individuals from multiple sources and generating structured reports optimized for creating digital twins using LLMs. The system includes three distinct workflows, each optimized for different use cases.

## Overview

This project provides three complementary workflows:

1. **Workflow 1: General Person Profile Scraper** - Multi-source scraping for comprehensive profiles
2. **Workflow 2: Digital Twin Report Generator** - Academic paper-based intellectual profiles
3. **Workflow 3: Paper-Referenced Profile Generator** - Academic profiles with inline citations

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Workflow 1: General Person Profile Scraper](#workflow-1-general-person-profile-scraper)
- [Workflow 2: Digital Twin Report Generator](#workflow-2-digital-twin-report-generator)
- [Workflow 3: Paper-Referenced Profile Generator](#workflow-3-paper-referenced-profile-generator)
- [Common Features](#common-features)
- [Troubleshooting](#troubleshooting)
- [Legal and Ethical Considerations](#legal-and-ethical-considerations)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd person-information-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   UNPAYWALL_EMAIL=your@email.com  # Optional, for Unpaywall API
   ```

4. **Get API keys**:
   - **Gemini API**: Get from [Google AI Studio](https://aistudio.google.com/)
   - **Unpaywall**: Optional, for open-access paper discovery

## Configuration

Edit `config.py` to customize:

- Rate limiting settings
- Content limits
- Output preferences
- API configurations
- Download source preferences (arXiv, DOI resolution, Unpaywall)

## Workflow 1: General Person Profile Scraper

A comprehensive web scraping tool that collects detailed information about a person from multiple sources and generates a structured 30-50 page PDF report.

### Features

- **Multi-Source Scraping**: Google Scholar, Wikipedia, News Articles, YouTube, GitHub, LinkedIn, University Profiles
- **Intelligent Person Verification**: Cross-source validation with confidence scoring
- **AI-Powered Synthesis**: Uses Google's Gemini API for content analysis and synthesis
- **Comprehensive Output**: 30-50 page PDF report + ZIP file of research papers
- **Caching System**: SQLite-based caching for efficient re-runs
- **Rate Limiting**: Respectful scraping with proper delays and retry logic

### Usage

**Basic Usage**:
```bash
python main.py "Seth Godin"
```

**Advanced Options**:
```bash
# Specify output directory
python main.py "Gary Vaynerchuk" --output-dir ./profiles

# Force refresh cached data
python main.py "Ann Handley" --force-refresh

# Enable verbose logging
python main.py "David Ogilvy" --verbose
```

### Output Files

- `{person_name}_profile.pdf`: 30-50 page comprehensive report
- `{person_name}_papers.zip`: ZIP file containing research papers
- `{person_name}_raw_data.json`: Raw scraped data in JSON format
- `scraping_cache.db`: SQLite database with cached data

### Report Structure

1. Executive Summary (2 pages)
2. Personality Profile (6-8 pages)
3. Domain Expertise & Knowledge (12-15 pages)
4. Professional Background & Journey (4-5 pages)
5. Content & Writing Style Analysis (5-7 pages)
6. Thought Leadership & Public Presence (5-7 pages)
7. Network & Influence (3-4 pages)
8. Appendix (2-3 pages)

## Workflow 2: Digital Twin Report Generator

A system for creating AI-generated digital twin profiles from research publications. This workflow focuses on academic researchers and generates 50-60 page intellectual profiles.

### Features

- **Flexible Paper Selection**: Choose papers by citations, first-author status, or hybrid scoring
- **Multi-Source Downloads**: Attempts downloads from Google Scholar, arXiv, Unpaywall, CrossRef/DOI, and more
- **Comprehensive Checklist**: Clear status showing what was retrieved and access suggestions
- **AI-Powered Synthesis**: Uses Google's Gemini API to generate cohesive narratives
- **Source Attribution**: Every major point linked to source papers
- **50-60 Page Reports**: Comprehensive documentation suitable for AI training

### Usage

**Basic Usage**:
```bash
python scripts/generate_digital_twin_report.py --author-name "Kevin Lane Keller"
```

**Using Scholar ID (Recommended)**:
```bash
python scripts/generate_digital_twin_report.py --scholar-id x8xNLZQAAAAJ
```

**Advanced Options**:
```bash
# Select top 70 papers
python scripts/generate_digital_twin_report.py --author-name "Author Name" --top-n 70

# Use first-author priority strategy
python scripts/generate_digital_twin_report.py --author-name "Author Name" --strategy first-author

# Custom output directory
python scripts/generate_digital_twin_report.py --author-name "Author Name" --output-dir ./my_output

# Adjust rate limiting
python scripts/generate_digital_twin_report.py --author-name "Author Name" --rate-limit 2.0
```

### Paper Selection Strategies

1. **Citations (Default)**: Ranks papers by total citation count
2. **First-Author**: Prioritizes papers where the author is first author
3. **Hybrid**: Combines citations (70% weight) with author position bonus (30% weight)

### Output Files

- `{author_name}_digital_twin_report.pdf`: Main 50-60 page report
- `{author_name}_checklist.html`: Human-readable checklist with status
- `{author_name}_checklist.csv`: Spreadsheet-friendly format
- `{author_name}_checklist.json`: Machine-readable status data
- `{author_name}_synthesis.json`: Complete AI-generated content
- `papers/`: Directory with downloaded PDFs

## Workflow 3: Paper-Referenced Profile Generator

A comprehensive system for creating AI-generated digital twin profiles with research paper citations, inline references, and detailed usage tracking. **This is the recommended workflow for academic researchers.**

### Features

- **Inline Citations**: Every paragraph cites its source with format `[From: Paper Title, Author Year]`
- **Downloaded Papers Folder**: All successfully retrieved PDFs organized by paper
- **Detailed Checklist**: Shows which papers were used in which sections
- **Multi-Source Paper Discovery**: Google Scholar + CrossRef/Semantic Scholar
- **Comprehensive Coverage**: Includes books and articles for non-academic authors
- **Enhanced Downloader**: Multi-source downloads from JSTOR, Scholar, Unpaywall, arXiv, DOI

### Quick Start (Recommended)

**Step 1: Find Scholar ID**
1. Go to [scholar.google.com](https://scholar.google.com)
2. Search for the person (e.g., "Kevin Lane Keller")
3. Click their profile
4. Copy ID from URL: `scholar.google.com/citations?user=<ID>`

**Step 2: Run Workflow 3**
```bash
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ
```

For detailed instructions, see `workflow3_paper_profile/QUICK_START.md`.

### Usage

**Using Scholar ID (Recommended - Most Reliable)**:
```bash
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ
```

**Using Person Name**:
```bash
python workflow3_paper_profile/main.py "Kevin Lane Keller"
```

**Advanced Options**:
```bash
# Custom output directory
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ --output-dir ./keller_profile

# Limit number of papers
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ --max-papers 50

# Adjust rate limiting
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ --rate-limit 2.0

# Enable verbose logging
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ --verbose
```

### Report Structure (10 Comprehensive Sections)

1. Executive Summary (2-3 pages)
2. Personality Profile & Communication Style (6-8 pages)
3. Intellectual Profile & Mindset (8-10 pages)
4. Domain Expertise & Knowledge Base (10-12 pages)
5. Research Methodology & Approach (6-8 pages)
6. Professional Background & Journey (4-5 pages)
7. Evolution of Ideas & Thinking (6-8 pages)
8. Thought Leadership & Public Presence (5-7 pages)
9. Collaboration & Network Influence (4-5 pages)
10. Complete Bibliography & References (3-4 pages)

### Output Files

- `{person_name}_profile.pdf`: Comprehensive report (50-70 pages) with inline citations
- `{person_name}_papers/`: Folder containing all successfully downloaded PDFs
- `{person_name}_checklist.html`: Interactive checklist with download status
- `{person_name}_checklist.csv`: Spreadsheet format
- `{person_name}_checklist.json`: Machine-readable format

### Citation Format

Every paragraph in the report ends with a citation:
- Downloaded papers: `[From: Paper Title, Author Year]`
- Metadata-only papers: `[From: Paper Title, Author Year - metadata only]`

### Download Success Rates

Expected success rates vary by author type:

| Author Type | Expected Download Rate | Reason |
|-------------|----------------------|--------|
| Modern Researchers (2020s) | 40-60% | More open access |
| Established Researchers (2000s) | 20-40% | Mix of OA and paywall |
| Early Career (2010s+) | 30-50% | arXiv access |
| Authors with Books | 10-20% | Books often paywalled |
| Pre-2000s | 5-15% | Limited digital archives |

**Note:** The system works effectively even with low download rates because unavailable papers are still cited using metadata, and the checklist provides clear access suggestions.

## Common Features

### Data Sources

All workflows support scraping from:
- **Google Scholar**: Research papers, citations, h-index, co-authors
- **Wikipedia**: Biographical information, structured data
- **News Articles**: Media coverage, interviews, mentions
- **University Profiles**: Academic information, research interests

### Download Sources

Workflows 2 and 3 support multi-source paper downloads:
1. **Google Scholar**: Direct PDF links from eprint_url/pub_url
2. **JSTOR**: With institutional access detection
3. **Unpaywall**: Legal open-access versions via DOI
4. **arXiv**: Direct PDF access for preprints
5. **CrossRef/DOI**: Resolves to publisher PDFs when available
6. **Semantic Scholar**: API access for academic papers

### Caching System

All workflows use SQLite-based caching:
- Stores scraped data for efficient re-runs
- Reduces redundant API calls
- Can be refreshed with `--force-refresh` flag

### Rate Limiting

All workflows respect rate limits:
- Configurable delays between requests
- Automatic retry with exponential backoff
- Prevents IP blocking

## Troubleshooting

### Google Scholar Blocking (Most Common Issue)

**Problem:** "Found 0 papers" or "No scholar author found"

**Solutions:**
1. **Use Scholar ID** (most reliable):
   ```bash
   python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ
   ```
2. Wait and retry (blocks are often temporary)
3. Use VPN to change IP address
4. Automatic fallback to CrossRef/Semantic Scholar (Workflow 3)

### API Key Errors

- Ensure your Gemini API key is correctly set in `.env`
- Verify the key has sufficient quota
- Check `.env` file format (no quotes around values)

### Low Download Success

- This is normal for many authors (especially for books or paywalled content)
- Check the checklist HTML for access suggestions
- Use institutional library access for unavailable papers
- Reports still generate effectively with metadata-only citations

### Rate Limiting Issues

- Increase `--rate-limit` parameter
- Run during off-peak hours
- Consider using `--max-papers` to limit scope

### PDF Generation Errors

- Ensure you have write permissions in the output directory
- Check that ReportLab is installed: `pip install reportlab`
- Review logs for specific error messages

## Legal and Ethical Considerations

- Only scrapes publicly available information
- Respects website terms of service
- Implements proper rate limiting
- Includes disclaimers about data usage
- Provides source citations for all content
- For Workflow 2 (IU): Access only IU-licensed content; credentials from environment only

## Project Structure

```
.
├── main.py                          # Workflow 1 entry point
├── workflow3_paper_profile/         # Workflow 3 directory
│   ├── main.py                      # Workflow 3 entry point
│   ├── lib/                         # Workflow 3 libraries
│   │   ├── person_searcher.py       # Person and paper search
│   │   ├── paper_download_manager.py # Multi-source downloads
│   │   ├── content_analyzer.py     # PDF content analysis
│   │   ├── citation_tracker.py      # Citation tracking
│   │   ├── report_generator.py      # Report generation
│   │   └── checklist_generator.py   # Checklist creation
│   └── QUICK_START.md               # Quick reference
├── scripts/
│   ├── generate_digital_twin_report.py  # Workflow 2 entry point
│   └── download_top_scholar_papers.py  # IU-specific workflow
├── lib/                             # Shared libraries
│   ├── scholar_client.py            # Google Scholar client
│   ├── paper_download_manager.py    # Multi-source downloader
│   └── ...
├── scrapers/                        # Web scrapers
│   ├── google_scholar_scraper.py
│   ├── wikipedia_scraper.py
│   └── ...
├── processors/                      # Data processors
│   ├── content_synthesizer.py       # AI synthesis
│   ├── pdf_generator.py            # PDF generation
│   └── ...
└── config.py                        # Configuration
```

## Examples

### Workflow 1: Marketing Professionals
```bash
python main.py "Seth Godin"
python main.py "Gary Vaynerchuk"
python main.py "Ann Handley"
```

### Workflow 2: Academic Researchers
```bash
python scripts/generate_digital_twin_report.py --scholar-id x8xNLZQAAAAJ --top-n 70
```

### Workflow 3: Paper-Referenced Profiles
```bash
python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ --max-papers 100
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub
4. Check workflow-specific documentation

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for ensuring compliance with applicable laws and website terms of service. The tool only scrapes publicly available information and includes appropriate disclaimers.

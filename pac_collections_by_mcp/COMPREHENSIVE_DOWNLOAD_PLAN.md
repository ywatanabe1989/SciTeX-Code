# PAC Collection Download Plan - Comprehensive Report

## Executive Summary

I have analyzed the Phase-Amplitude Coupling (PAC) bibtex file containing **75 research papers** and created a comprehensive download strategy. The papers have been categorized by source, prioritized by accessibility, and organized for efficient batch downloading.

## Analysis Results

### Paper Distribution by Source
| Source | Count | Difficulty | Auth Required | Priority |
|--------|-------|------------|---------------|----------|
| Semantic Scholar | 40 | Easy-Medium | No | HIGH |
| DOI Direct | 14 | Medium | Yes | MEDIUM |
| IEEE Xplore | 8 | Medium-Hard | Yes | MEDIUM |
| PubMed/PMC | 7 | Easy | No | HIGH |
| ScienceDirect | 5 | Medium | Yes | MEDIUM |
| arXiv | 1 | Easy | No | HIGH |

### Priority Groups for Download

#### Priority 1: Open Access & Free Papers (48 papers)
**Estimated Success Rate: 95-100%**
**Estimated Time: 2-4 hours**

- **arXiv** (1 paper): Direct PDF download
- **PubMed/PMC** (7 papers): Free full-text via PMC when available
- **Semantic Scholar** (40 papers): API access or direct download

#### Priority 2: University Authenticated Access (27 papers)  
**Estimated Success Rate: 85-95%**
**Estimated Time: 4-8 hours**

- **ScienceDirect** (5 papers): Elsevier via OpenAthens
- **IEEE Xplore** (8 papers): University IEEE subscription
- **DOI Direct** (14 papers): University library resolution

## Recommended Implementation Strategy

### Phase 1: Infrastructure Setup
1. **Verify Authentication**: Ensure OpenAthens cookies are current
2. **Directory Structure**: Create organized storage in `~/.scitex/scholar/library/pac/`
3. **Tool Verification**: Confirm browser extensions and Zotero translators are available

### Phase 2: Batch Downloads

#### Batch 1A: Immediate Downloads (No Auth) - 8 papers
```bash
# arXiv paper
wget [arxiv_url] -O paper.pdf

# PubMed/PMC free papers
# Use PMC API or direct links for full-text PDFs
```

#### Batch 1B: Semantic Scholar Papers - 40 papers
```bash
# Use Semantic Scholar API or crawl4ai for systematic download
python -m scitex.scholar.download --source semantic_scholar --project pac --batch-size 10
```

#### Batch 2: Authenticated Downloads - 27 papers
```bash
# Requires OpenAthens authentication
python -m scitex.scholar.download --auth openathens --project pac
```

### Phase 3: Quality Assurance
1. **PDF Validation**: Verify downloaded files contain research content
2. **Metadata Extraction**: Ensure proper title, author, journal information
3. **Naming Convention**: Apply `FIRSTAUTHOR-YEAR-JOURNAL.pdf` format
4. **Database Storage**: Organize in structured format with 8-digit IDs

## High-Value Paper Highlights

### Open Access Gems (Immediate Download)
1. **Tensorpac toolbox** (Combrisson 2020) - Python toolbox for PAC analysis
2. **Phase-amplitude coupling review** (Multiple Frontiers papers)
3. **Methodological papers** - Critical for PAC research methodology

### Key Paywalled Papers (University Access Required)
1. **Canolty & Knight (2010)** - Foundational cross-frequency coupling paper
2. **Tort et al. (2010)** - Standard PAC measurement methodology  
3. **Jensen et al. (2016)** - Discriminating valid from spurious PAC indices

## Technical Implementation Details

### Available Resources
- **Authentication**: OpenAthens (University of Melbourne)
- **Browser Extensions**: Stealth mode, cookie acceptance, captcha solving
- **PDF Extraction**: Zotero translators
- **Automation**: crawl4ai MCP server for web automation
- **Storage**: Structured library system with symlinks

### Download Workflow
1. **Session Setup**: Load authentication cookies
2. **Stealth Browsing**: Use Chrome extensions for undetected access
3. **PDF Detection**: Leverage Zotero translators for PDF URLs
4. **Content Validation**: Verify full-text research content
5. **Metadata Storage**: Save to structured JSON format
6. **File Organization**: Store with proper naming and symlinks

### Parallel Processing Strategy
- **Batch Size**: Process 5-10 papers simultaneously for auth-required sources
- **Rate Limiting**: Respect publisher terms with appropriate delays
- **Error Handling**: Skip problematic papers, continue with others
- **Resume Capability**: Track progress for interrupted downloads

## Expected Challenges and Solutions

### Challenge 1: IEEE Access Restrictions
**Solution**: Use university VPN + OpenAthens authentication

### Challenge 2: Captcha Systems
**Solution**: Utilize 2captcha integration with API key

### Challenge 3: Dynamic Content Loading
**Solution**: Use crawl4ai with JavaScript execution for React-based sites

### Challenge 4: Rate Limiting
**Solution**: Implement exponential backoff and distributed downloads

## Success Metrics

### Quantitative Goals
- **Target Success Rate**: 85%+ overall (64+ papers successfully downloaded)
- **Priority 1 Success**: 95%+ (46+ open access papers)
- **Priority 2 Success**: 85%+ (23+ authenticated papers)

### Quality Metrics
- All PDFs contain full research content (not just abstracts)
- Proper metadata extraction and storage
- Consistent file naming and organization
- Complete bibliographic information preserved

## Fallback Strategies

1. **Manual Collection**: Open failed papers in browser tabs for Zotero collection
2. **Alternative Sources**: Check Unpaywall, CORE, BASE for open access versions
3. **Author Contact**: Request preprints directly from authors
4. **Inter-library Loan**: For critical papers not accessible through university

## Files Generated

1. **`pac_collection_download_plan.json`** - Complete analysis results
2. **`pac_detailed_inventory.json`** - Paper-by-paper breakdown
3. **`download_commands.sh`** - Executable download scripts
4. **`download_strategy_summary.md`** - Strategy overview
5. **`COMPREHENSIVE_DOWNLOAD_PLAN.md`** - This comprehensive report

## Next Actions

1. **Review and Approve**: Validate the download strategy and paper priorities
2. **Execute Phase 1**: Start with open access downloads for immediate results
3. **Setup Authentication**: Ensure OpenAthens credentials are current
4. **Monitor Progress**: Use the provided scripts to track download status
5. **Handle Exceptions**: Address any authentication or access issues as they arise

This strategy maximizes download success while minimizing manual intervention and respecting publisher terms of service. The systematic approach ensures comprehensive coverage of the PAC research literature for your academic work.
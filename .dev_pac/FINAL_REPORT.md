# PAC Collection PDF Download - Final Report

## Summary
**Date**: 2025-08-06  
**Total Papers**: 66  
**PDFs Downloaded**: 17 (25.8% coverage)  
**Papers in Chrome for Zotero**: ~15  
**IEEE Papers (not accessible)**: 12  

## Successfully Downloaded (17 PDFs)

### Scientific Reports (9/10 - 90%)
- ✅ Alvarado-Rojas-2014
- ✅ Assi-2018
- ✅ Cmpora-2019
- ✅ Edakawa-2016
- ✅ Gagliano-2019
- ✅ Pilet-2025
- ✅ Raghavan-2024
- ✅ Winter-2020
- ✅ Xie-2017
- ❌ Ujma-2022 (DOI issue)

### Frontiers Journals (7/7 - 100%)
- ✅ Amiri-2016 (Human Neuroscience)
- ✅ Bosl-2021 (Neurology)
- ✅ Li-2023 (Neuroscience)
- ✅ Li-2023 (Physiology)
- ✅ Liu-2021 (Neurology)
- ✅ Liu-2024 (Neuroinformatics)
- ✅ Ma-2021 (Neurology)
- ✅ Marzulli-2025 (Human Neuroscience)

## Opened in Chrome with Authentication

### Elsevier Journals (7 papers)
- Gagliano-2018-Epilepsy-Research
- Marcoleta-2020-Biomedical-Physics
- Mierlo-2014-Progress-in-Neurobiology
- Richner-2019-Journal-of-Neural-Engineering
- Rong-2020-Engineering
- Tang-2015-Bio-Medical-Materials
- (1 more)

### Nature Journals (2 papers)
- Asano-2023-Nature-Communications
- Chang-2018-Nature-Neuroscience

### Other Neuroscience Journals
Multiple papers from Journal of Neuroscience, Brain Communications, Cognitive Neurodynamics, etc.

## Not Accessible

### IEEE Papers (12 papers - no institutional subscription)
- Ahmad-2020
- Alvarado-Rojas-2011
- Garcia-2024
- Li-2021
- Liu-2016
- Mendoza-Cardenas-2021 (2 papers)
- Miao-2021
- Parvez-2016
- Wang-2020
- Yuan-2015
- Zhou-2016

### MDPI Papers (6 papers - technical issues)
- Kapoor-2022-Sensors
- Li-2021-Brain-Sciences
- Ramachandran-2018-Sensors
- Seo-2020-Mathematics
- Shirzadi-2024-Diagnostics
- Song-2022-Sensors

## Next Steps

1. **Chrome + Zotero Connector** (Currently Open)
   - Go to Chrome browser
   - Click Zotero Connector icon
   - Right-click → "Save All Tabs to Zotero"
   - This will capture metadata and attempt PDF downloads

2. **Manual Download for IEEE**
   - IEEE papers require separate subscription
   - Consider institutional VPN or library portal
   - Or request through interlibrary loan

3. **MDPI Papers**
   - These are open access but had download issues
   - Try manual download from journal websites
   - URLs: mdpi.com/journal/[journal-name]

## Scripts Created

All scripts are in `.dev_pac/` directory:

1. `batch_download_pac.py` - Main downloader for open access
2. `check_status.py` - Status checker
3. `batch_open_in_chrome.py` - Opens all URLs in Chrome
4. `zotero_connector_capture.py` - Zotero integration
5. `open_accessible_papers.py` - Opens subscribed journals

## Technical Notes

- **Authentication**: Chrome Profile 1 with OpenAthens (University of Melbourne)
- **Chrome Extensions**: Zotero Connector installed and working
- **Open Access Success**: Scientific Reports (90%), Frontiers (100%)
- **Subscription Access**: Elsevier, Nature, most neuroscience journals
- **Not Subscribed**: IEEE papers

## Coverage by Publisher

| Publisher | Downloaded | Total | Coverage |
|-----------|------------|-------|----------|
| Scientific Reports | 9 | 10 | 90% |
| Frontiers | 7 | 7 | 100% |
| IEEE | 0 | 12 | 0% (not subscribed) |
| Elsevier | 0 | 7 | 0% (in Chrome) |
| MDPI | 0 | 6 | 0% (failed) |
| Other | 1 | 24 | 4% |
| **TOTAL** | **17** | **66** | **25.8%** |

---

*Report generated after comprehensive download attempts using multiple strategies including direct downloads, authenticated browser access, and Zotero Connector integration.*
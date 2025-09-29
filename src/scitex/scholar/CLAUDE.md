<!-- ---
!-- Timestamp: 2025-09-21 20:22:01
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/CLAUDE.md
!-- --- -->

## Develop Scholar module
Now we are facing challenges with automating literature search, which is one of the modules for automatic scientific research project, SciTeX (https://scitex.ai).

Scholar related temporal files, including auth cookies and cache files, should be placed under `~/.scitex/scholar` (= "$SCITEX_DIR/scholar")

Planned workflow is:
1. Manual Login to OpenAthens (Unimelb)
   - `scitex.scholar.auth`
   - `python -m scitex.scholar.authenticate openathens`

2. Keep the authentication info to cookies
   - `scitex.scholar.auth`
   - [ ] Cookie is stored at: `` (find the actual json file here)
   - [ ] Especially, in the cookifile, which entry is important?

3. Use AI2 products to get related articles as bib file
   - e.g., `./src/scitex/scholar/docs/papers.bib`

4. Resolve DOIs from piece of information such as title in a resumable manner
   - `python -m scitex.scholar.resolve_dois --title ...`
   - `python -m scitex.scholar.resolve_dois --bibtex /path/to/bibtex-file.bib`
   - `python -m scitex.scholar.resolve_dois --bibtex src/scitex/scholar/docs/papers.bib --resume`
     - I think this should be more intuitively work for resumablly
   - Resume to handle rate limit
   - Progress and ETA should be shown like rsync
   - Performance enhancement by reducing overlaps, optimizing retry logics
     - [ ] All the 75 entires are resolved their dois

5. Resolve publisher url using OpenURL for OpenAthens (Unimelb) in a resumable manner
   - `scitex.scholar.open_url.OpenURLResolver`
   - We wanted to use ZenRows but it seems difficult to pass auth info to remote browsers
   - For local version, it seems ZenRows functionality like stealth access are limited
   - Progress and ETA should be shown like rsync

### !!! IMPORTANT: Maybe this step is not fully incorporated yet!!!
6. Enrich the bib file to add metadata in a resumable manner
   - `python -m scitex.scholar.enrich_bibtex /path/to/bibtex-file.bib`
   - `scitex.scholar.Papers.from_bibtex`
   - `scitex.scholar.enrich_bibtex`
   - `/path/to/.tmp-bibtex-file.bib` would be intuitive
   - [ ] Enriching metadata using google scholar and crawl4ai might be also another method
   - Progress and ETA should be shown like rsync
   - [ ] `./src/scitex/scholar/docs/papers-enriched.bib`
   - [ ] `./src/scitex/scholar/docs/papers-enriched.csv`
     - [ ] All the 75 entires are enriched
   - All metadata should have their source explicitly in the bib files
     - `title` should have `title_source` as well
     - In the same way, `xxxx` should have `xxxx_source` all the time

### YES, now this step, the largest challenge, is handled well !!!
7. Download PDFs using AI agents (you, Claude) in an exploratory manner
   - Claude Code
   - Cookie acceptance
   - Captcha handling
   - Zotero translators
   - Store pdfs in this format: `FIRSTAUTHOR-YEAR-JOURNAL.pdf`
   - Headless mode and screencaptures will be better to avoid interferences
   - Skip unsolvable problems and work on other entries, while escalating to the user
     - [ ] PDF files for all the 75 entries are downloaded
     - [ ] Open undownloaded papers urls (dois) as tabs on a browser will be beneficial for user to download using zotero connector

# this is not implemented yet
8. Confirm downloaded PDFs are the main contents
   - Extract sections

# Now this is implemented
9. Organize everything in a database

   ```
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/<original-name-from-the-journal>.pdf
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/attachments/<original-name-from-the-journal>.pdf
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/attachments/<original-name-from-the-journal>.pdf
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/metadata.json
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/screenshots/<timestamp>-description.jpg
   ~/.scitex/scholar/library/<project>/8-DIGITS-ID/screenshots/<timestamp>-description.jpg   
   ~/.scitex/scholar/library/<project-human-readable>/AUTHOR-YEAR-JOURNAL -> .../8-DIGITS-ID
   ```

   

10. Allow for semantic vector search

Environment variables are available at:
`/home/ywatanabe/.dotfiles/.bash.d/secrets/000_ENV_UNIMELB.src`
`/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src`

# IMPORTANT
Python env is in the current directory. Do not change directory as bash handles python environments based on working directory.

## Browser extentions
- [Lean Library](https://chromewebstore.google.com/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa?hl=en)
- [Zotero Connector](https://chromewebstore.google.com/detail/zotero-connector/ekhagklcjbdpajgpjgmbionohlpdbjgc?hl=en)
- [Accept all cookies](https://chromewebstore.google.com/detail/accept-all-cookies/ofpnikijgfhlmmjlpkfaifhhdonchhoi?hl=en)
- [Captcha Solver](https://chromewebstore.google.com/detail/captcha-solver-auto-recog/ifibfemgeogfhoebkmokieepdoobkbpo?hl=en)
  - $SCITEX_SCHOLAR_2CAPTCHA_API_KEY

## PDF download workflow
BrowserManager + Authenticator + Chrome extensions (stealth + auth info))
-> Part of metadata such as title
-> DOI 
-> OpenURL
-> Final URL
-> Find PDF URLS using zetero translators
-> Download PDFs
-> Organize PDFs based on expected structure

## PDF downloaders
Which downloaders should we keep...? ~/proj/scitex_repo/src/scitex/scholar/download/
We need cleanup using safe_rm.sh

## No need metadata
we do not need journal_rank and h_index

## Resolve circular dependency and organize SoC
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_BrowserAuthenticator.py`
  - This should be not specific to unimelb
  - We need to map library authenticators and sso (openathens -> unimelb)
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/sso_automations/_UniversityOfMelbourneSSOAutomator.py`
  - The issue was importing `UniversityOfMelbourneSSOAutomator` which creates a circular dependency since that class imports `BrowserAuthenticator`.
  - This should handle unimelb-specific logics


## DOI resolver
- [x] All info should be saved to library as json file
- [x] All info shoudl be associated with source all the time
- [x] If one field is already filled, no need to override, just skip that field, assuming once entered info is correct 
- [x] How project name, like pac, specified?
  - [x] Is it possible to copy bibtex file when dois are resolved from_bibtex?
  - [x] Is it possible to prepare a summary table to show the results of from_bibtex?
  - [x] For exmaple, ~/.scitex/scholar/library/pac/info/files-bib/summary.csv
  - [x] For exmaple, ~/.scitex/scholar/library/pac/info/filesname-2-bib/summary.csv

## Papers for development
We need to avoid regression using variety of samples. For paywalled/open-access papers, use the followings respectively:
- `~/proj/scitex_repo/scholar/docs/papers_paywalled.json`
- `~/proj/scitex_repo/scholar/docs/papers_openaccess.json`

## Technical Debt - Storage Architecture
**Issue**: Current storage structure mixes master storage with project directories
**Current (Working but Suboptimal)**:
```
~/.scitex/scholar/library/
├── master/8DIGIT01/  # ✓ Correct
├── project/
│   ├── 8DIGIT02/     # ❌ Should be symlink to master
│   ├── Author-Year -> ../master/8DIGIT03  # ❌ Human-readable not needed
│   └── info/files-bib/  # ❌ Should be info/filename/filename.bib
```

**Desired Architecture**:
```
~/.scitex/scholar/library/
├── master/8DIGIT01/  # All actual data storage
├── project/
│   ├── info/filename/filename.bib  # Project metadata
│   ├── 8DIGIT01 -> ../master/8DIGIT01  # Direct symlinks only
│   └── 8DIGIT02 -> ../master/8DIGIT02
```

**Decision**: Keep current working system, refactor later when time permits
**Priority**: Low (system works correctly, just suboptimal structure)

## Metadata Enrichment
- [ ] Once DOI is resolved, next process is metadata enrichment. Especially:
  - [ ] abstract
  - [ ] citation count
  - [ ] journal impact factor


- [ ] Please download the PDF files of the pac collection, listed below
  - `/home/ywatanabe/.scitex/scholar/library/pac`
- Authentication is available in `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth`
- Chrome Extensions are available in `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/utils/_ChromeExtensionManager.py`
- Crawl4ai is available in `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/crawl4ai_integration.py`
- Zotero Translators are available in `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/_ZoteroTranslatorRunner.py`
- cache are available there
  `/home/ywatanabe/.scitex/scholar/cache/chrome/auth`
  `/home/ywatanabe/.scitex/scholar/cache/chrome/_extension`
  `/home/ywatanabe/.scitex/scholar/cache/chrome/extension -> Profile 1`
  `/home/ywatanabe/.scitex/scholar/cache/chrome/Profile 1`
  Profile 1 is manually created browser profile; _extension is the one created programatically using scitex.scholar

  
- [ ] Aazhang-2017-IEEE-Transactions-on-Signal-Processing -> ../MASTER/F99329E1 (No DOI)
- [ ] Agarwal-2018-MATEC-Web-of-Conferences -> ../MASTER/4A0327A5
- [ ] Ahmad-2020-2020-IEEE-Region-10-Symposium-TENSYMP -> ../MASTER/164DD9BF (IEEE - not subscribed)
- [ ] Alhudhaif-2021-PeerJ-Computer-Science -> ../MASTER/3A48D547
- [ ] Alotaiby-2017-Computational-Intelligence-and-Neuroscience -> ../MASTER/4A6C3067
- [ ] Alvarado-Rojas-2011-2011-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-and-Biology-Society -> ../MASTER/B36DE522 (IEEE - not subscribed)
- [x] Alvarado-Rojas-2014-Scientific-Reports -> ../MASTER/16830DAC ✅ Downloaded
- [x] Amiri-2016-Frontiers-in-Human-Neuroscience -> ../MASTER/E6A3AF59 ✅ Downloaded
- [ ] Asano-2023-Nature-Communications -> ../MASTER/0C8F17CA (In Chrome for Zotero)
- [ ] Ashokkumar-2023-Wireless-Personal-Communications -> ../MASTER/B6C5C2AC
- [x] Assi-2018-Scientific-Reports -> ../MASTER/86D49E5E ✅ Downloaded
- [x] Bosl-2021-Frontiers-in-Neurology -> ../MASTER/26E1350B ✅ Downloaded
- [ ] Chang-2018-Nature-Neuroscience -> ../MASTER/A9D6B0E4 (In Chrome for Zotero)
- [x] Cmpora-2019-Scientific-Reports -> ../MASTER/96EFCB15 ✅ Downloaded
- [x] Edakawa-2016-Scientific-Reports -> ../MASTER/27CE930A ✅ Downloaded 
- [ ] El-Samie-2014-EURASIP-Journal-on-Advances-in-Signal-Processing -> ../MASTER/2CEBD4C1 
- [ ] Gagliano-2018-Epilepsy-Research -> ../MASTER/A72E87D0 (In Chrome for Zotero)
- [x] Gagliano-2019-Scientific-Reports -> ../MASTER/ED7E7BB8 ✅ Downloaded
- [ ] Garcia-2024-2024-46th-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-and-Biology-Society-EMBC (IEEE - not subscribed)
- [ ] Ghiasvand-2020-The-Neuroscience-Journal-of-Shefaye-Khatam -> ../MASTER/1F60D8D6
- [ ] Grigorovsky-2020-Brain-Communications -> ../MASTER/9A77D799 
- [ ] Hasan-2017-Applied-Bionics-and-Biomechanics -> ../MASTER/C9499509
- [ ] Jin-2022-2022-41st-Chinese-Control-Conference-CCC -> ../MASTER/FD084C7A
- [ ] Kapoor-2022-Sensors -> ../MASTER/BAC5A831 (MDPI - failed)
- [ ] Li-2021-Brain-Sciences -> ../MASTER/389212D2 (MDPI - failed)
- [ ] Li-2021-IEEE-Transactions-on-Biomedical-Engineering -> ../MASTER/F4B572EA (IEEE - not subscribed)
- [x] Li-2023-Frontiers-in-Neuroscience -> ../MASTER/1D3D59B7 ✅ Downloaded
- [x] Li-2023-Frontiers-in-Physiology -> ../MASTER/C86A349E ✅ Downloaded
- [ ] Liu-2016-Conference-proceedings-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-and-Biology-Socie (IEEE - not subscribed)
- [x] Liu-2021-Frontiers-in-Neurology -> ../MASTER/6FBC385E ✅ Downloaded
- [x] Liu-2024-Frontiers-in-Neuroinformatics -> ../MASTER/3E42A141 ✅ Downloaded
- [x] Ma-2021-Frontiers-in-Neurology -> ../MASTER/C6528D0E ✅ Downloaded
- [ ] Marcoleta-2020-Biomedical-Physics-amp-Engineering-Express -> ../MASTER/3BDC1B0E (In Chrome for Zotero)
- [x] Marzulli-2025-Frontiers-in-Human-Neuroscience -> ../MASTER/EA0A7E5E ✅ Downloaded
- [ ] Mendoza-Cardenas-2021-2021-10th-International-IEEE-EMBS-Conference-on-Neural-Engineering-NER -> ../MASTER/8B351253 (IEEE - not subscribed)
- [ ] Mendoza-Cardenas-2021-2021-43rd-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-amp-Biology-Socie (IEEE - not subscribed)
- [ ] Miao-2021-2021-43rd-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-amp-Biology-Society-EMBC -> ../MASTER/10BDDE3C (IEEE - not subscribed)
- [ ] Miao-2021-Cognitive-Neurodynamics -> ../MASTER/6244D82B
- [ ] Mierlo-2014-Progress-in-Neurobiology -> ../MASTER/3E6C777F (In Chrome for Zotero)
- [ ] Mukamel-2014-The-Journal-of-Neuroscience -> ../MASTER/E9314839
- [ ] Natu-2022-Computational-and-Mathematical-Methods-in-Medicine -> ../MASTER/11E29EDE
- [ ] Parvez-2016-IEEE-Transactions-on-Neural-Systems-and-Rehabilitation-Engineering -> ../MASTER/6497F609 (IEEE - not subscribed)
- [x] Pilet-2025-Scientific-Reports -> ../MASTER/30AE20CD ✅ Downloaded
- [x] Raghavan-2024-Scientific-Reports -> ../MASTER/A7F46FE2 ✅ Downloaded
- [ ] Ramachandran-2018-Sensors -> ../MASTER/21308B16 (MDPI - failed)
- [ ] Richner-2019-Journal-of-Neural-Engineering -> ../MASTER/888B096E (In Chrome for Zotero)
- [ ] Rong-2020-Engineering -> ../MASTER/D5F8B73F (In Chrome for Zotero)
- [ ] Salimpour-2019-Frontiers-in-Neuroscience -> ../MASTER/D0532643
- [ ] Schelter-2007 -> ../MASTER/F45A8E5A (No journal info)
- [ ] Sebaei-2024-South-Eastern-European-Journal-of-Public-Health -> ../MASTER/CF93E994 
- [ ] Seo-2020-Mathematics -> ../MASTER/0AFEF557 (MDPI - failed)
- [ ] Shirzadi-2024-Diagnostics -> ../MASTER/98763EC9 (MDPI - failed)
- [ ] Sivathamboo-2020-IEEE-Reviews-in-Biomedical-Engineering -> ../MASTER/ABFB9D35 (IEEE - not subscribed)
- [ ] Song-2022-Sensors -> ../MASTER/CEB508B6 (MDPI - failed)
- [ ] Sun-2022-Acta-Epileptologica -> ../MASTER/E8601E3A 
- [ ] Tang-2015-Bio-Medical-Materials-and-Engineering -> ../MASTER/90E10266 (In Chrome for Zotero)
- [ ] Ujma-2022-Scientific-Reports -> ../MASTER/9D62A9C5 (DOI issue)
- [ ] Wang-2020-2020-42nd-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-amp-Biology-Society-EMBC -> ../MASTER/FFB1C06B (IEEE - not subscribed)
- [ ] Watson-2015-BMC-Neuroscience -> ../MASTER/AB782507
- [x] Winter-2020-Scientific-Reports -> ../MASTER/E8361A2E ✅ Downloaded
- [x] Xie-2017-Scientific-Reports -> ../MASTER/B9F0224C ✅ Downloaded
- [ ] Yanagisawa-2012-The-Journal-of-Neuroscience -> ../MASTER/54D73605
- [ ] Yekutieli-2018-Epilepsy-Journal -> ../MASTER/9C6D5B43 
- [ ] Yuan-2015-2015-IEEE-International-Conference-on-Digital-Signal-Processing-DSP -> ../MASTER/96980DBC (IEEE - not subscribed)
- [ ] Zhang-2024-International-Journal-of-Surgery -> ../MASTER/8F313217
- [ ] Zhou-2016-2016-38th-Annual-International-Conference-of-the-IEEE-Engineering-in-Medicine-and-Biology-Society-EMBC -> ../MASTER/7E53E268 (IEEE - not subscribed) 

<!-- EOF -->
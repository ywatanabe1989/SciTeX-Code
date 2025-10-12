<!-- ---
!-- Timestamp: 2025-08-06 15:14:51
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/from_user/renamed-async_functions.md
!-- --- -->

# This works
rename.sh run_all_checks_async run_all_checks_async ./src/scitex/scholar

# Let's apply rename.sh using shell script, loop through
for func_name in ...; do rename.sh "$func_name" "$func_name"_async ./src/scitex/scholar

File: validation/_PreflightChecker.py
  36   5     async def run_all_checks_async(
  77   5     async def _check_python_version_async(self):
  92   5     async def _check_required_packages_async(self):
 122   5     async def _check_optional_features_async(
 183   5     async def _check_download_directory_async(self, download_dir: Optional[Path]):
 217   5     async def _check_network_connectivity_async(self):
 248   5     async def _check_authentication_status_async(
 295   5     async def _check_system_resources_async(self):
 373   1 async def run_preflight_checks_async(**kwargs) -> Dict[str, Any]:

File: validation/_PDFValidator.py
 203   5     async def validate_batch_async(

File: enrichment/_CitationEnricher.py
  63   7     # async def _enrich_async(self, papers: List[Paper]) -> None:
  86   7     # async def _enrich_async(self, papers):
 106   5     async def _enrich_async(self, papers):
 126   5     async def _get_citations_async(
 140   9         async def fetch_crossref_async():

File: enrichment/_BibTeXEnricher.py
 137   5     async def _fetch_crossref_async_metadata(self, doi: str) -> Dict[str, Any]:
 161   5     async def _fetch_pubmed_metadata_async(
 184   5     async def _fetch_semantic_scholar_metadata_async(
 219   5     async def _enrich_single_entry_async(
 320   5     async def enrich_bibtex_async(
 388   9         async def enrich_with_limit_async(entry: Dict, index: int):
 466   1 async def main():

File: docs/from_agents/feature-requests/scholar-openathens-authentication.md
  44   5     async def authenticate_async(self, username: str, password: str) -> Session:
  47   5     async def download_with_auth_async(self, url: str, session: Session) -> bytes:
  55   1 async def download_pdf_async(self, doi: str) -> Optional[Path]:

File: docs/zenrows_official/with_playwright.md
  60   1 async def scrape_asyncr_async():
 111   1 async def scrape_asyncr_async(url):

File: docs/from_user/suggestions.md
  48   1 async def main():

File: search_engine/_BaseSearchEngine.py
  46   5     async def search_async(
  73   5     async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
  78   5     async def get_citation_count_async(self, doi: str) -> Optional[int]:
  83   5     async def resolve_doi_async(
  89   5     async def _rate_limit_async(self):

File: search_engine/_UnifiedSearcher.py
 141   5     async def search_async(
 289   1 async def search_async(

File: old/suggestions.md
1585   5     async def _run_translator_on_page_async(self, page: Page, translator_path: Path) -> Optional[str]:
1643   5     async def download(self, paper: Paper, session_data: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
1676   1 async def main():

File: examples/complete_workflow_example.py
  45   1 async def main():

File: examples/openathens/test_openathens_debug_download.py
  20   1 async def debug_pdf_download():

File: examples/openathens/download_nature_neuro_paper.py
  19   1 async def download_paper():

File: search_engine/web/_GoogleScholarSearchEngine.py
  47   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: examples/openathens/quick_test_async_openathens_dois.py
  34   1 async def quick_test_async():

File: search_engine/web/_PubMedSearchEngine.py
  57   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 131   5     async def _fetch_details_async(self, session: aiohttp.ClientSession, pmids: List[str]) -> List[Paper]:
 261   5     async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
 290   5     async def get_citation_count_async(self, doi: str) -> Optional[int]:
 297   5     async def resolve_doi_async(self, title: str, year: Optional[int] = None) -> Optional[str]:
 332   1 async def main():

File: examples/openathens/test_openathens_flow.py
  22   1 async def test_complete_flow_async():

File: search_engine/web/_SemanticScholarSearchEngine.py
  69   5     async def search_async(
 160   5     async def _fetch_paper_by_id_async(self, paper_id: str) -> Optional[Paper]:
 285   5     async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
 290   5     async def get_citation_count_async(self, doi: str) -> Optional[int]:
 301   5     async def resolve_doi_async(
 341   1 async def main():

File: search_engine/web/_CrossRefSearchEngine.py
  53   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 206   5     async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
 238   5     async def get_citation_count_async(self, doi: str) -> Optional[int]:
 249   5     async def resolve_doi_async(self, title: str, year: Optional[int] = None) -> Optional[str]:
 283   1 async def main():

File: examples/openathens/test_openathens_session_reuse.py
  22   1 async def test_session_reuse_async():

File: examples/openathens/test_openathens_reuse_session.py
  20   1 async def test_with_saved_cookies_async():

File: examples/openathens/test_openathens_debug.py
  20   1 async def monitor_auth_process_async():

File: examples/openathens/test_openathens_manual.py
  22   1 async def main():

File: examples/openathens/capture_cookies_and_test.py
  16   1 async def capture_and_test_async():

File: examples/openathens/test_openathens_interactive.py
  20   1 async def main():

File: old/search_engine_v01/local/_LocalSearchEngine.py
  35   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: examples/openathens/test_openathens_simple.py
  19   1 async def test_openathens_approach_async():

File: examples/openathens/test_openathens_paywalled.py
  92   1 async def test_openathens_authentication_async():

File: examples/openathens/test_direct_pdf_download.py
  21   1 async def download_with_cookies():

File: _Scholar.py
 445   9         async def download_batch_async():
1114   5     async def authenticate_async_openathens_async(self, force: bool = False) -> bool:
1147   5     async def is_openathens_authenticate_asyncd_async(self) -> bool:
1565   5     async def authenticate_async_ezproxy_async(self, force: bool = False) -> bool:
1600   5     async def is_ezproxy_authenticate_asyncd_async(self) -> bool:
1662   5     async def authenticate_async_shibboleth_async(self, force: bool = False) -> bool:
1701   5     async def is_shibboleth_authenticate_asyncd_async(self) -> bool:
1746   5     async def __aenter__(self):
1749   5     async def __aexit__(self, exc_type, exc_val, exc_tb):

File: old/search_engine_v01/_UnifiedSearcher.py
 140   5     async def search_async(
 288   1 async def search_async(

File: old/search_engine_v01/_BaseSearchEngine.py
  46   5     async def search_async(
  73   5     async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
  78   5     async def get_citation_count_async(self, doi: str) -> Optional[int]:
  83   5     async def resolve_doi_async(
  89   5     async def _rate_limit_async(self):

File: old/search_engine_v01/web/_GoogleScholarSearchEngine.py
  47   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: search_engine/web/_ArxivSearchEngine.py
  43   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 175   5     async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
 202   5     async def get_citation_count_async(self, doi: str) -> Optional[int]:
 209   5     async def resolve_doi_async(self, title: str, year: Optional[int] = None) -> Optional[str]:
 242   1 async def main():

File: examples/openathens/test_authenticate_asyncd_browser.py
  15   1 async def test_authenticate_asyncd_downloads():

File: old/search_engine_v01/web/_ArxivSearchEngine.py
  35   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: old/search_engine_v01/local/_VectorSearchEngine.py
  41   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: Scholar.py
  91   5     async def resolve_doi_async(self, paper_id: int) -> Optional[str]:

File: old/search_engine_v01/web/_CrossRefSearchEngine.py
  36   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: search_engine/local/_VectorSearchEngine.py
  41   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: search_engine/local/_LocalSearchEngine.py
  35   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:

File: examples/test_cookie_encryption.py
  22   1 async def test_encryption_async():

File: old/search_engine_v01/web/_SemanticScholarSearchEngine.py
  44   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 127   5     async def _fetch_paper_by_id_async(self, paper_id: str) -> Optional[Paper]:

File: doi/_BibTeXBatchDOIResolver.py
 238   5     async def resolve_all_async(self) -> Tuple[int, int, int]:
 579   5     async def main():

File: old/search_engine_v01/web/_PubMedSearchEngine.py
  43   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 117   5     async def _fetch_details_async(self, session: aiohttp.ClientSession, pmids: List[str]) -> List[Paper]:

File: utils/_retry_handler.py
 155   9         async def wrapper(*args, **kwargs) -> Any:
 258   5     async def download_with_retry(

File: utils/_email.py
  40   1 async def send_email_async(

File: utils/_CheckpointScreenshotter.py
  60   5     async def checkpoint(self, page, description: str, full_page: bool = False) -> str:
 100   5     async def error_checkpoint(self, page, error_description: str, full_page: bool = True) -> str:
 138   5     async def page_info_checkpoint(self, page, step_description: str) -> dict:
 257   1 async def take_checkpoint(screenshotter: CheckpointScreenshotter, page, description: str) -> str:
 262   1 async def take_error_checkpoint(screenshotter: CheckpointScreenshotter, page, error_desc: str) -> str:
 267   1 async def take_info_checkpoint(screenshotter: CheckpointScreenshotter, page, description: str) -> dict:

File: utils/_DirectScholarPDFDownloader.py
  39   5     async def _capture_download_screenshot(self, page, download_path: Path, stage: str) -> Optional[str]:
  73   5     async def download_pdf_async_direct(self, 
 104  13             async def handle_response(response):
 254   5     async def download_multiple_pdfs(self, 
 337   1 async def download_pdf_asyncs_direct(page, pdf_urls: List[str], download_dir: Path) -> List[Tuple[str, Path, bool, Optional[str]]]:

File: utils/_GeneralizedPDFDetector.py
 217   5     async def detect_pdf_candidates(self, page, doi: str = "", url: str = "") -> List[PDFCandidate]:
 386   5     async def download_best_pdf(self, page, candidates: List[PDFCandidate], 

File: doi/batch/_LibraryManager.py
 182   5     async def resolve_and_create_library_structure_async(

File: utils/_screenshot_capturer.py
  49   5     async def capture_on_failure(
  91   5     async def _save_page_info(
 125   5     async def capture_workflow(
 203   5     async def capture_comparison(

File: utils/_JavaScriptInjectionPDFDetector.py
 364   5     async def detect_pdfs_with_injection(
 645   5     async def download_detected_pdfs(
 694   5     async def _download_pdf_async_url(self, page, pdf_url: str, download_path: Path) -> bool:
 768  21                     async def handle_response(response):
 893   1 async def detect_pdfs_with_injection(page, url: str = "", doi: str = "") -> InjectedPDFResult:
 911   5     async def test_injection_detection():

File: doi/strategies/_ResolutionOrchestrator.py
 113   5     async def resolve_async(
 275   5     async def resolve_doi_async(self, *args, **kwargs) -> Optional[Dict]:
 346   5     async def test_resolution_orchestrator():

File: doi/_resolve_doi_asyncs.py
  23   1 async def resolve_single_doi(title: str):
  35   1 async def resolve_bibtex_dois(args):

File: doi/_SingleBatchDOIResolver.py
 171   5     async def resolve_async(
 371   5     async def main():

File: doi/_BatchDOIResolver.py
 147   5     async def _resolve_single_async(
 311   9         async def process_all():
 330  13             async def bounded_resolve(paper, index):
 479   5     async def resolve_and_create_library_structure_async(
 506   5     async def main():

File: doi/strategies/_SourceResolutionStrategy.py
 118   5     async def metadata2metadata_async(
 222   5     async def _try_corpus_id_resolution(
 276   5     async def _try_sources(
 360   5     async def _search_source_async(
 393   5     async def _get_comprehensive_metadata_async(
 459   5     async def test_source_resolution_strategy():

File: doi/utils/enhanced_doi_resolver.py
 181   5     async def resolve_async(

File: doi/_SourceRotationManager.py
 401   5     async def test_source_rotation_manager():

File: doi/utils/pubmed_converter.py
 105   5     async def _apply_rate_limiting_async(self):
 187   5     async def pmid2doi_async(self, pmid: Union[str, int]) -> Optional[str]:
 327   5     async def bibtex_entries2dois_async(self, entries: List[Dict]) -> Dict[str, str]:

File: doi/_RateLimitHandler.py
 422   5     async def wait_with_countdown_async(self, wait_time: float, source: str = "API"):
 569   5     async def test_rate_limit_handler_async():

File: doi/sources/_BaseDOISource.py
 236   5     async def _apply_rate_limiting_async(self):
 247   5     async def search_async(self,

File: project_management/feature-request-scholar-openathens-authentication.md
  44   5     async def authenticate_async(self, username: str, password: str) -> Session:
  47   5     async def download_with_auth_async(self, url: str, session: Session) -> bytes:
  55   1 async def download_pdf_async(self, doi: str) -> Optional[Path]:

File: auth/_OpenAthensAuthenticator.py
 132   5     async def _ensure_session_loaded_async(self) -> None:
 137   5     async def authenticate_async(self, force: bool = False, **kwargs) -> dict:
 178   5     async def _perform_browser_authentication_async(self) -> dict:
 213   5     async def _handle_successful_authentication_async(self, page) -> dict:
 232   5     async def is_authenticate_asyncd(self, verify_live: bool = True) -> bool:
 262   5     async def _verify_live_authentication_async(self) -> bool:
 278   5     async def get_auth_headers_async(self) -> Dict[str, str]:
 282   5     async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
 288   5     async def logout_async(self, clear_cache=False) -> None:
 298   5     async def get_session_async_info_async(self) -> Dict[str, Any]:
 310   5     async def _notify_user_intervention_needed_async(self) -> None:
 368   5     async def _notify_authentication_success_async(self) -> None:
 416   5     async def _notify_authentication_failed_async(self, error_details: str) -> None:
 471   1 async def main():

File: database/_ScholarDatabaseIntegration.py
  86   5     async def process_bibtex_workflow(
 210   5     async def _download_pdf_async_for_entry(

File: browser/remote/_CaptchaHandler.py
  40   5     async def handle_page_async(self, page: Page) -> bool:
  67   5     async def _detect_captcha_async(self, page: Page) -> bool:
  99   5     async def _is_cloudflare_challenge_async(self, page: Page) -> bool:
 124   5     async def _solve_cloudflare_challenge_async(self, page: Page) -> bool:
 188   5     async def _has_recaptcha_async(self, page: Page) -> bool:
 195   5     async def _solve_recaptcha_async(self, page: Page) -> bool:
 246   5     async def _has_hcaptcha_async(self, page: Page) -> bool:
 253   5     async def _solve_hcaptcha_async(self, page: Page) -> bool:
 295   5     async def _extract_turnstile_key_async(self, page: Page) -> Optional[str]:
 327   5     async def _submit_recaptcha_async(self, page_url: str, site_key: str) -> Optional[str]:
 337   5     async def _submit_hcaptcha_async(self, page_url: str, site_key: str) -> Optional[str]:
 347   5     async def _submit_turnstile_async(self, page_url: str, site_key: str) -> Optional[str]:
 357   5     async def _submit_captcha_async(self, params: Dict[str, Any]) -> Optional[str]:
 379   5     async def _get_captcha_result_async(self, task_id: str) -> Optional[str]:

File: auth/_AuthCacheManager.py
  64   5     async def save_session_async(self, session_manager: SessionManager) -> bool:
  88   5     async def load_session_async(self, session_manager: SessionManager) -> bool:

File: auth/_BrowserAuthenticator.py
  48   5     async def navigate_to_login_async(self, url: str) -> Page:
  85   5     async def wait_for_login_completion_async(
 143   5     async def verify_authentication_async(
 199   5     async def extract_session_cookies_async(
 214   5     async def reliable_click_async(self, page: Page, selector: str) -> bool:
 218   5     async def reliable_fill_async(self, page: Page, selector: str, value: str) -> bool:
 259   5     async def _verify_login_success_async(

File: browser/remote/_ZenRowsAPIBrowser.py
  68   5     async def navigate_and_screenshot_async(
 238   5     async def get_pdf_url_async(self, doi: str, use_openurl: bool = True) -> Optional[str]:
 289   5     async def batch_screenshot_async(
 307   9         async def process_url_async(url: str, index: int) -> Dict[str, Any]:
 319   9         async def process_with_limit_async(url: str, index: int):

File: auth/sso_automation/_UniversityOfMelbourneSSOAutomator.py
  65   5     async def perform_login_async(self, page: Page) -> bool:
 117   5     async def _handle_username_step_async(self, page: Page) -> bool:
 147   5     async def _handle_password_step_async(self, page: Page) -> bool:
 174   5     async def _handle_generic_login_async(self, page: Page) -> bool:
 214   5     async def _handle_duo_authentication_async(self, page: Page) -> bool:
 259   5     async def _wait_for_completion_async(self, page: Page) -> bool:
 293   5     async def _take_debug_screenshot_async(self, page: Page):

File: browser/remote/_ZenRowsRemoteScholarBrowserManager.py
  74   5     async def get_browser_async(self) -> Browser:
 110   5     async def get_authenticate_asyncd_context(
 149   5     async def new_page(self, context: Optional[BrowserContext] = None) -> Any:
 163   5     async def close(self):
 174   5     async def take_screenshot_reliable_async(
 240   5     async def navigate_and_extract_async(
 289   5     async def __aenter__(self):
 293   5     async def __aexit__(self, exc_type, exc_val, exc_tb):
 302   5     async def main():
 322   9         async def test_browser_async(browser_type, browser_manager, use_auth=False):
 501   7     # async def main():

File: auth/_EZProxyAuthenticator.py
 158   5     async def authenticate_async(self, force: bool = False, **kwargs) -> dict:
 296   5     async def is_authenticate_asyncd(self, verify_live: bool = False) -> bool:
 357   5     async def get_auth_headers_async(self) -> Dict[str, str]:
 362   5     async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
 368   5     async def logout_async(self) -> None:
 380   5     async def get_session_async_info_async(self) -> Dict[str, Any]:
 424   5     async def create_authenticate_asyncd_browser(self) -> tuple[Browser, Any]:

File: auth/BrowserUtils.py
  32   5     async def reliable_fill_async(page: Page, selector: str, value: str) -> bool:
  72   5     async def reliable_click_async(page: Page, selector: str) -> bool:
 109   5     async def wait_for_element_async(page: Page, selector: str, timeout: int = 5000) -> bool:

File: auth/_AuthLockManager.py
  53   5     async def acquire_lock_async(self) -> bool:
  80   5     async def release_lock_async(self) -> None:
 107   5     async def _try_acquire_lock_async(self) -> bool:
 132   5     async def __aenter__(self):
 138   5     async def __aexit__(self, exc_type, exc_val, exc_tb):

File: auth/ScholarAuthManager.py
 132   5     async def ensure_authenticate_asyncd(
 144   5     async def is_authenticate_asyncd(self, verify_live: bool = True) -> bool:
 162   5     async def authenticate_async(
 183   5     async def get_auth_headers_async(self) -> Dict[str, str]:
 194   5     async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
 205   5     async def logout_async(self) -> None:
 224   5     async def main():

File: browser/local/utils/_CookieAutoAcceptor.py
  47   5     async def inject_auto_acceptor_async(self, context):
 103   7     # async def accept_cookies_async(
 139   5     async def check_cookie_banner_exists_async(self, page: Page) -> bool:

File: browser/local/README.md
  37   1 async def run_main():

File: auth/_BaseAuthenticator.py
  54   5     async def is_authenticate_asyncd(self, verify_live: bool = False) -> bool:
  67   5     async def authenticate_async(self, **kwargs) -> dict:
  80   5     async def get_auth_headers_async(self) -> Dict[str, str]:
  90   5     async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
 100   5     async def logout_async(self) -> None:
 105   5     async def get_session_async_info_async(self) -> Dict[str, Any]:
 126   5     async def main():

File: auth/sso_automation/_BaseSSOAutomator.py
  77   5     async def perform_login_async(self, page: Page) -> bool:
  81   5     async def handle_sso_redirect_async(self, page: Page) -> bool:
 124   5     async def _save_session_async(self, context: BrowserContext):
 144   5     async def _restore_session_async(self, context: BrowserContext) -> bool:
 176   5     async def notify_user_async(self, event_type: str, **kwargs) -> None:

File: auth/sso_automation/README.md
 108   5     async def perform_login_async(self, page: Page) -> bool:

File: browser/README.md
  24   1 async def main():

File: search/_UnifiedSearcher.py
  49   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
  53   5     async def _rate_limit_async(self):
  73   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 144   5     async def _fetch_paper_by_id_async(self, paper_id: str) -> Optional[Paper]:
 241   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 302   5     async def _fetch_pubmed_details_async(self, session: aiohttp.ClientSession, pmids: List[str]) -> List[Paper]:
 418   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 528   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 699   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 877   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
 986   5     async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
1135   5     async def search_async(self,
1233   1 async def search_async(query: str,

File: auth/_ShibbolethAuthenticator.py
 201   5     async def authenticate_async(self, force: bool = False, **kwargs) -> dict:
 323   5     async def _find_institutional_login_async(self, page: Page) -> Optional[Any]:
 345   5     async def _handle_wayf_selection_async(self, page: Page) -> bool:
 394   5     async def _handle_idp_login_async(self, page: Page) -> None:
 439   5     async def _extract_saml_attributes_async(self, page: Page) -> Dict[str, Any]:
 468   5     async def is_authenticate_asyncd(self, verify_live: bool = False) -> bool:
 525   5     async def get_auth_headers_async(self) -> Dict[str, str]:
 545   5     async def get_auth_cookies_async(self) -> List[Dict[str, Any]]:
 551   5     async def logout_async(self) -> None:
 571   5     async def get_session_async_info_async(self) -> Dict[str, Any]:
 658   5     async def create_authenticate_asyncd_browser(self) -> tuple[Browser, Any]:

File: auth/_OpenAthensAutomation.py
  32   1 async def _debug_screenshot_async(page: Page, description: str) -> None:
  74   5     async def perform_openathens_authentication_async(self, page: Page) -> bool:
 142   5     async def _handle_cookie_banner_async(self, page: Page) -> bool:
 254   5     async def _analyze_page_content_async(self, page: Page, stage: str) -> Dict[str, Any]:
 321   5     async def _handle_institution_selection_async(self, page: Page) -> bool:
 361   5     async def _wait_for_navigation_async(self, page: Page, timeout: int = 15) -> bool:
 405   5     async def _ocr_click_institution_async(self, page: Page) -> bool:
 433   5     async def _pyautogui_click_institution_async(self, page: Page) -> bool:
 459   5     async def _tab_key_navigation_async(self, page: Page, search_field) -> bool:
 565   5     async def _simple_keyboard_navigation_async(self, page: Page, search_field) -> bool:
 628   5     async def _handle_unimelb_sso_login_async(self, page: Page) -> bool:
 685   5     async def _handle_duo_2fa_async(self, page: Page) -> bool:
 777   5     async def _select_institution_from_dropdown_async(self, page: Page) -> bool:
 936   5     async def _select_institution_keyboard_async(self, page: Page, search_field) -> bool:
 961   5     async def _handle_sso_login_async(self, page: Page) -> bool:
 995   5     async def _handle_username_step_async_async(self, page: Page) -> bool:
1032   5     async def _handle_password_step_async_async(self, page: Page) -> bool:
1069   5     async def _handle_2fa_async(self, page: Page) -> bool:
1125   5     async def _wait_for_completion_async_async(self, page: Page, timeout: int = 60) -> bool:
1158   5     async def _notify_user_intervention_async(self, event_type: str, **kwargs) -> None:

File: browser/local/utils/_CaptchaHandler.py
  44   5     async def inject_captcha_handler_async(self, context):
  93   5     async def handle_captcha_async(
 125   5     async def check_captcha_exists_async(self, page: Page) -> bool:

File: browser/local/utils/_ChromeProfileManager_v01-with-config.py
  84   5     def check_extensions_installed(self) -> Dict[str, bool]:
 128   5     async def install_extensions_interactive_async(self):
 172   5     async def check_lean_library_active_async(self, page, url: str) -> bool:

File: download/_ShibbolethDownloadStrategy.py
  74   5     async def can_download(self, url: str, paper: Optional[Any] = None) -> bool:
 100   5     async def download(
 186   5     async def _needs_institutional_login_async(self, page: Page) -> bool:
 199   5     async def _find_institutional_login_async(self, page: Page) -> Optional[Any]:
 216   5     async def _find_pdf_link_async(self, page: Page) -> Optional[str]:
 264   5     async def get_authenticate_asyncd_session(self) -> Dict[str, Any]:

File: browser/local/utils/_ChromeProfileManager.py
 125   5     def check_extensions_installed(self) -> bool:
 178   5     async def install_extensions_interactive_asyncly_if_not_installed(self):
 237   5     async def check_lean_library_active_async(

File: browser/local/utils/_StealthManager.py
 254   7     # async def inject_stealth_scripts(self, page: Page):
 373   5     async def add_human_behavior_async(self, page: Page):
 394   5     async def handle_cloudflare_challenge_async(
1007   5     async def human_delay_async(self, min_ms: int = 1000, max_ms: int = 3000):
1011   5     async def human_click_async(self, page: Page, element):
1016   5     async def human_mouse_move_async(self, page: Page):
1021   5     async def human_scroll_async(self, page: Page):
1026   5     async def human_type_async(self, page: Page, selector: str, text: str):
1039   5     async def main():

File: browser/local/utils/_ChromeProfileManager_v99.py
 108   5     async def install_extensions_fallback_async(self):
 135   5     def check_extensions_installed(self) -> Dict[str, bool]:
 179   5     async def install_extensions_interactive_async(self):
 368   5     async def check_lean_library_active_async(self, page, url: str) -> bool:

File: browser/local/utils/_ChromeProfileManager_v02-detected-by-cloudflare.py
 125   5     def check_extensions_installed(self) -> bool:
 178   5     async def install_extensions_interactive_asyncly_if_not_installed(self):
 237   5     async def check_lean_library_active_async(

File: browser/local/_BrowserMixin.py
  50   5     async def get_shared_browser_async(cls) -> Browser:
  65   5     async def cleanup_shared_browser_async(cls):
  74   5     async def get_browser_async(self) -> Browser:
 123   5     async def new_page(self, url=None):
 138   5     async def close_page(self, page_index):
 145   5     async def close_all_pages(self):
 152   5     async def create_browser_context_async(
 178   5     async def get_session_async(self, timeout: int = 30) -> aiohttp.ClientSession:
 192   5     async def close_session(self):
 202   5     async def accept_cookies_async(self, page_index=0, wait_seconds=2):
 226   5     async def show_async(self):
 234   5     async def hide_async(self):
 242   5     async def _restart_contexts_async(self):
 249   5     async def __aenter__(self):
 252   5     async def __aexit__(self, exc_type, exc_val, exc_tb):
 260   5     async def main():
 264  13             async def scrape_async(self, url):

File: download/_BaseDownloadStrategy.py
  30   5     async def can_download(self, url: str, metadata: Dict[str, Any]) -> bool:
  43   5     async def download(

File: download/_ZenRowsDownloadStrategy.py
  59   5     async def can_download(self, url: str, metadata: Dict[str, Any]) -> bool:
  73   5     async def download(
 197   5     async def _find_pdf_url_async(self, html_content: str, base_url: str) -> Optional[str]:
 239   5     async def _download_pdf_async_url(self, pdf_url: str, output_path: Path) -> Optional[Path]:

File: open_url/_OpenURLResolver.py
 115   5     async def _capture_checkpoint_screenshot_async(
 204   5     async def _follow_saml_redirect_async(self, page, saml_url, doi=""):
 256   5     async def _find_and_click_publisher_go_button_async(self, page, doi=""):
 429   5     async def _download_pdf_async_from_publisher_page(
 612   5     async def resolve_and_download_pdf_async(
 726   5     async def _resolve_single_async(
 972   5     async def _resolve_parallel_async(
 999   9         async def worker_async(doi):
1070   5     async def __aenter__(self):
1073   5     async def __aexit__(self, exc_type, exc_val, exc_tb):
1078   1 async def try_openurl_resolver_async(
1104   5     async def main():

File: browser/local/_ScholarBrowserManager.py
  99   5     async def get_authenticate_asyncd_context(
 145   5     async def _create_stealth_context_async(
 164   5     async def get_shared_browser_with_profile_async(self) -> Browser:
 175   5     async def _ensure_playwright_started_async(self):
 179   5     async def _ensure_extensions_installed_async(self):
 188   5     async def _launch_persistent_context_async(self):
 236   5     async def _apply_stealth_scripts_async(self):
 248   5     async def check_lean_library_active_async(self, page, url, timeout_sec=5):
 264  15     #         async def __aenter__(self):
 281  15     #         async def __aexit__(self, exc_type, exc_val, exc_tb):
 287   5     async def take_screenshot_async(
 298   5     async def __aexit__(self, exc_type, exc_val, exc_tb):
 304   5     async def main(browser_mode="interactive"):

File: download/_EZProxyDownloadStrategy.py
  71   5     async def can_download(self, url: str, paper: Optional[Any] = None) -> bool:
  92   5     async def download(
 172   5     async def _find_pdf_link_async(self, page: Page) -> Optional[str]:
 213   5     async def get_authenticate_asyncd_session(self) -> Dict[str, Any]:

File: download/_ScreenshotDownloadHelper.py
  57   5     async def download_with_screenshots(self, storage_key: str, urls: List[str],
  99  13             async def handle_download(download):
 205   5     async def _capture_screenshot_async(self, page: Page, storage_key: str, 
 238   5     async def _check_for_login_async(self, page: Page) -> bool:
 258   5     async def _check_for_captcha_async(self, page: Page) -> bool:
 277   5     async def _try_download_button(self, page: Page) -> bool:

File: download/_SmartScholarPDFDownloader.py
  46   5     async def can_handle_async(self, paper: Paper, url: str) -> bool:
  50   5     async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
  71   5     async def can_handle_async(self, paper: Paper, url: str) -> bool:
  75   5     async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
 106   5     async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
 214   5     async def can_handle_async(self, paper: Paper, url: str) -> bool:
 222   5     async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
 306   5     async def capture_systematic_screenshot_async(self, paper: Paper, url: str, description: str, page: Optional[Page] = None):
 367   5     async def download_single(self, paper: Paper) -> Tuple[bool, Optional[Path]]:
 497   5     async def _capture_failure_screenshot_async(self, paper: Paper, url: str, description: str):
 573   5     async def download_batch(
 596   9         async def download_with_limit(paper: Paper, index: int):
 676   1 async def main():

File: download/_ZoteroTranslatorRunner.py
 434   5     async def run_translator_async(
 551   5     async def _enhance_item_with_pdf_urls_async(self, page: Page, item: Dict):
 596   5     async def extract_pdf_urls_async(self, url: str) -> List[str]:
 617   5     async def batch_extract_async(
 634   9         async def extract_with_limit_async(url: str) -> Tuple[str, Dict]:
 657   1 async def extract_bibliography_from_url_async(url: str) -> List[Dict[str, Any]]:
 672   1 async def find_pdf_urls_async(url: str) -> List[str]:
 690   5     async def test_translator_async():

File: open_url/_ZenRowsOpenURLResolver.py
 123   5     async def _zenrows_request_async(self, url: str) -> Optional[Dict[str, Any]]:
 196   5     async def _resolve_single_async(self, **kwargs) -> Optional[Dict[str, Any]]:
 295   5     async def close(self):
 299   5     async def __aenter__(self):
 303   5     async def __aexit__(self, exc_type, exc_val, exc_tb):
 309   1 async def test_zenrows_openurl_resolver():

File: open_url/resolve_urls/__main__.py
 167   1 async def _async_main_async(args, dois):

File: open_url/_ResolverLinkFinder.py
 133   5     async def find_link_async(self, page, doi: str) -> dict:
 152   5     async def _find_by_domain_async(self, page: Page, doi: str) -> Optional[str]:
 192   5     async def _find_by_structure_async(self, page, doi: str):
 254   5     async def _find_by_text_async(self, page: Page) -> Optional[str]:
 272   5     async def click_and_wait_async(self, page: Page, link: ElementHandle) -> bool:
 317   1 async def find_and_click_resolver_link_async(page: Page, doi: str) -> Optional[str]:

File: download/_ScholarPDFDownloader.py
 278   5     async def download_pdf_async(
 370   5     async def _download_from_doi_async(
 484   5     async def _get_authenticate_asyncd_session_async(self) -> Optional[Dict[str, Any]]:
 585   5     async def _try_direct_patterns_async(
 603   5     async def _try_lean_library_async(
 634   5     async def _try_openathens_async(
 653   5     async def _try_ezproxy_async(
 685   5     async def _try_shibboleth_async(
 717   5     async def _try_zotero_translator_async(
 744   5     async def _try_openurl_async_resolver_async(
 834   5     async def _try_zenrows_async(
 871   5     async def _handle_cookie_consent_async(self, page) -> None:
 913   5     async def _try_playwright_async(
1319   5     async def _resolve_doi_async_async(self, doi: str) -> Optional[str]:
1345   5     async def _download_file_async(
1397   5     async def _try_direct_url_download_async(
1420   5     async def _is_valid_url_async(self, url: str) -> bool:
1463   5     async def batch_download(
1542   9         async def download_with_limit_async(
1604   5     async def _download_file_with_auth_async(
1675   5     async def _extract_pdf_urls_from_page_async(self, page, url: str) -> List[str]:
1728   5     async def _run_translator_with_auth_async(
1895   1 async def download_pdf_async(
1920   1 async def download_pdf_asyncs_async(
1956   5     async def test_unified_downloader_async():

File: open_url/README.md
 155   1 async def resolve_with_fallback_async(doi, metadata):

File: open_url/_UnimelbLibraryGoButtonSelector.py
 111   5     async def analyze_go_buttons_async(self, page) -> List[GoButtonCandidate]:
 405   5     async def intelligent_go_button_selection_async(self, page) -> Optional[Dict]:
 445   1 async def select_most_reliable_go_button_async(page) -> Optional[Dict]:

File: open_url/_DOIToURLResolver.py
  73   5     async def _capture_workflow_screenshot_async(self, doi: str, url: str, stage: str, page: Optional[Page] = None):
 246   5     async def resolve_single_async(
 308   5     async def _try_openurl_async(self, doi: str) -> Optional[Dict[str, any]]:
 368   5     async def _try_direct_urls_async(
 407   5     async def _verify_url_access_async(self, url: str) -> Optional[Dict[str, any]]:
 456   5     async def _check_pdf_access_async(self, page: Page) -> bool:
 488   5     async def resolve_batch_async(
 505   9         async def resolve_with_limit_async(doi: str, index: int):
 584   1 async def main():

File: open_url/_ResumableOpenURLResolver.py
 108   5     async def resolve_from_dois_async(self, dois: List[str]) -> Dict[str, Dict[str, Any]]:

File: open_url/_MultiInstitutionalResolver.py
 158  13             async def test():
 216   5     async def resolve_with_fallback_async(

File: open_url/_OpenURLResolverWithZenRows.py
 109   5     async def _zenrows_request_async(
 199   5     async def _get_all_browser_cookies_async(self) -> Dict[str, str]:
 236   5     async def _resolve_single_async_zenrows_async(
 459   5     async def _resolve_single_async(
 537   5     async def resolve_async(
 554   5     async def _resolve_parallel_async(
 581   9         async def worker_async(doi):
 650   5     async def __aenter__(self):
 654   5     async def __aexit__(self, exc_type, exc_val, exc_tb):
 662   1 async def test_zenrows_resolver_async():

rg finished (484 matches found) at Tue Aug  5 17:58:48, duration 0.70 s


func_names=(
    "run_all_checks_async"
    "_check_python_version_async"
    "_check_required_packages_async"
    "_check_optional_features_async"
    "_check_download_directory_async"
    "_check_network_connectivity_async"
    "_check_authentication_status_async"
    "_check_system_resources_async"
    "run_preflight_checks_async"
    "_get_citations_async"
    "fetch_crossref_async"
    "_fetch_crossref_async_metadata"
    "_fetch_pubmed_metadata_async"
    "_fetch_semantic_scholar_metadata_async"
    "_enrich_single_entry_async"
    "enrich_with_limit_async"
    "authenticate_async"
    "download_with_auth_async"
    "download_pdf_async"
    "scrape_asyncr_async"
    "fetch_by_id_async"
    "get_citation_count_async"
    "resolve_doi_async"
    "_run_translator_on_page_async"
    "download"
    "debug_pdf_download"
    "download_paper"
    "quick_test_async"
    "test_complete_flow_async"
    "monitor_auth_process_async"
    "capture_and_test_async"
    "test_openathens_approach_async"
    "test_openathens_authentication_async"
    "download_with_cookies"
    "test_session_reuse_async"
    "test_with_saved_cookies_async"
    "test_authenticate_asyncd_downloads"
    "test_encryption_async"
    "wait_with_countdown_async"
    "test_rate_limit_handler_async"
    "handle_page_async"
    "_detect_captcha_async"
    "_is_cloudflare_challenge_async"
    "_solve_cloudflare_challenge_async"
    "_has_recaptcha_async"
    "_solve_recaptcha_async"
    "_has_hcaptcha_async"
    "_solve_hcaptcha_async"
    "_extract_turnstile_key_async"
    "_submit_recaptcha_async"
    "_submit_hcaptcha_async"
    "_submit_turnstile_async"
    "_submit_captcha_async"
    "_get_captcha_result_async"
    "navigate_to_login_async"
    "wait_for_login_completion_async"
    "verify_authentication_async"
    "extract_session_cookies_async"
    "reliable_click_async"
    "reliable_fill_async"
    "_verify_login_success_async"
    "navigate_and_screenshot_async"
    "get_pdf_url_async"
    "batch_screenshot_async"
    "process_url_async"
    "process_with_limit_async"
    "perform_login_async"
    "_handle_username_step_async"
    "_handle_password_step_async"
    "_handle_generic_login_async"
    "_handle_duo_authentication_async"
    "_wait_for_completion_async"
    "_take_debug_screenshot_async"
    "get_browser_async"
    "get_authenticate_asyncd_context"
    "new_page"
    "close"
    "take_screenshot_reliable_async"
    "navigate_and_extract_async"
    "test_browser_async"
    "is_authenticate_asyncd"
    "get_auth_headers_async"
    "get_auth_cookies_async"
    "logout_async"
    "get_session_async_info_async"
    "create_authenticate_asyncd_browser"
    "wait_for_element_async"
    "acquire_lock_async"
    "release_lock_async"
    "_try_acquire_lock_async"
    "ensure_authenticate_asyncd"
    "inject_auto_acceptor_async"
    "check_cookie_banner_exists_async"
    "handle_sso_redirect_async"
    "_save_session_async"
    "_restore_session_async"
    "notify_user_async"
    "_find_institutional_login_async"
    "_handle_wayf_selection_async"
    "_handle_idp_login_async"
    "_extract_saml_attributes_async"
    "_debug_screenshot_async"
    "perform_openathens_authentication_async"
    "_handle_cookie_banner_async"
    "_analyze_page_content_async"
    "_handle_institution_selection_async"
    "_wait_for_navigation_async"
    "_ocr_click_institution_async"
    "_pyautogui_click_institution_async"
    "_tab_key_navigation_async"
    "_simple_keyboard_navigation_async"
    "_handle_unimelb_sso_login_async"
    "_handle_duo_2fa_async"
    "_select_institution_from_dropdown_async"
    "_select_institution_keyboard_async"
    "_handle_sso_login_async"
    "_handle_username_step_async_async"
    "_handle_password_step_async_async"
    "_handle_2fa_async"
    "_wait_for_completion_async_async"
    "_notify_user_intervention_async"
    "inject_captcha_handler_async"
    "handle_captcha_async"
    "check_captcha_exists_async"
    "check_extensions_installed"
    "install_extensions_interactive_async"
    "check_lean_library_active_async"
    "can_download"
    "_needs_institutional_login_async"
    "_find_pdf_link_async"
    "get_authenticate_asyncd_session"
    "install_extensions_interactive_asyncly_if_not_installed"
    "add_human_behavior_async"
    "handle_cloudflare_challenge_async"
    "human_delay_async"
    "human_click_async"
    "human_mouse_move_async"
    "human_scroll_async"
    "human_type_async"
    "install_extensions_fallback_async"
    "get_shared_browser_async"
    "cleanup_shared_browser_async"
    "close_page"
    "close_all_pages"
    "create_browser_context_async"
    "get_session_async"
    "close_session"
    "accept_cookies_async"
    "show_async"
    "hide_async"
    "_restart_contexts_async"
    "scrape_async"
    "_find_pdf_url_async"
    "_download_pdf_async_url"
    "_capture_checkpoint_screenshot_async"
    "_follow_saml_redirect_async"
    "_find_and_click_publisher_go_button_async"
    "_download_pdf_async_from_publisher_page"
    "resolve_and_download_pdf_async"
    "_create_stealth_context_async"
    "get_shared_browser_with_profile_async"
    "_ensure_playwright_started_async"
    "_ensure_extensions_installed_async"
    "_launch_persistent_context_async"
    "_apply_stealth_scripts_async"
    "take_screenshot_async"
    "download_with_screenshots"
    "handle_download"
    "_capture_screenshot_async"
    "_check_for_login_async"
    "_check_for_captcha_async"
    "_try_download_button"
    "can_handle_async"
    "capture_systematic_screenshot_async"
    "download_single"
    "_capture_failure_screenshot_async"
    "download_batch"
    "download_with_limit"
    "_enhance_item_with_pdf_urls_async"
    "extract_pdf_urls_async"
    "batch_extract_async"
    "extract_with_limit_async"
    "extract_bibliography_from_url_async"
    "find_pdf_urls_async"
    "test_translator_async"
    "_zenrows_request_async"
    "_async_main_async"
    "find_link_async"
    "_find_by_domain_async"
    "_find_by_structure_async"
    "_find_by_text_async"
    "click_and_wait_async"
    "find_and_click_resolver_link_async"
    "_download_from_doi_async"
    "_get_authenticate_asyncd_session_async"
    "_try_direct_patterns_async"
    "_try_lean_library_async"
    "_try_openathens_async"
    "_try_ezproxy_async"
    "_try_shibboleth_async"
    "_try_zotero_translator_async"
    "_try_openurl_async_resolver_async"
    "_try_zenrows_async"
    "_handle_cookie_consent_async"
    "_try_playwright_async"
    "_resolve_doi_async_async"
    "_download_file_async"
    "_try_direct_url_download_async"
    "_is_valid_url_async"
    "download_with_limit_async"
    "_download_file_with_auth_async"
    "_extract_pdf_urls_from_page_async"
    "_run_translator_with_auth_async"
    "download_pdf_asyncs_async"
    "test_unified_downloader_async"
    "resolve_with_fallback_async"
    "analyze_go_buttons_async"
    "intelligent_go_button_selection_async"
    "select_most_reliable_go_button_async"
    "_capture_workflow_screenshot_async"
    "_try_openurl_async"
    "_try_direct_urls_async"
    "_verify_url_access_async"
    "_check_pdf_access_async"
    "resolve_with_limit_async"
    "_get_all_browser_cookies_async"
    "_resolve_single_async_zenrows_async"
    "worker_async"
    "test_zenrows_resolver_async"
)

for func_name in "${func_names[@]}"; do
    rename.sh "$func_name" "${func_name}_async" ./src/scitex/scholar -n
done

rename.sh close close ./src/scitex/scholar -n
rename.sh _async _async ./src/scitex/scholar -n
rename.sh get_session_async_info_async get_session_info_async ./src/scitex/scholar -n



rename.sh BatchDOIResolver BatchBatchDOIResolver ./src/scitex/scholar -n
rename.sh BibTeXBatchDOIResolver BibTeXDOIResolver ./src/scitex/scholar -n
rename.sh UnifiedBatchDOIResolver DOIResolver ./src/scitex/scholar -n
rename.sh SingleBatchDOIResolver SingleDOIResolver ./src/scitex/scholar -n
SingleBatchDOIResolver

<!-- EOF -->
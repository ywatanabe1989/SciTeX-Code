#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 05:08:32 (ywatanabe)"
# File: ./src/scitex/scholar/url/helpers/finders/zotero_translators/experiments/extract_zotero_test_cases.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

# -----------------------------------------------------------------------------
# Extract Zotero Test Cases
# -----------------------------------------------------------------------------
# This script finds all Zotero translator .js files in a specified directory,
# extracts the embedded test case blocks (the content between
# /** BEGIN TEST CASES **/ and /** END TEST CASES **/), and concatenates them
# into a single output file for easy review and processing.
# -----------------------------------------------------------------------------

# --- Configuration ---

# Set the directory where your Zotero .js files are located.
# This path is relative to where you run the script. Adjust if necessary.
TRANSLATORS_DIR="./src/scitex/scholar/url/helpers/finders/zotero_translators"

# Set the name for the final output file.
OUTPUT_FILE="concatenated_zotero_tests.txt"


# --- Main Script Logic ---

# 1. Verify that the source directory exists.
if [ ! -d "$TRANSLATORS_DIR" ]; then
    echo "Error: Source directory not found at '$TRANSLATORS_DIR'"
    echo "Please make sure you are running this script from your project's root directory."
    exit 1
fi

# 2. Clear the output file to ensure a clean run every time.
echo "Initializing output file: $OUTPUT_FILE"
> "$OUTPUT_FILE"

# 3. Find all .js files and loop through them.
echo "Searching for translators in '$TRANSLATORS_DIR'..."
find "$TRANSLATORS_DIR" -name "*.js" | while read -r filepath; do
    # 4. Check if the file actually contains a test case block.
    if grep -q "/\*\* BEGIN TEST CASES \*\*/" "$filepath"; then
        # Get just the filename for cleaner logging.
        filename=$(basename "$filepath")
        echo "  -> Found and extracting test cases from: $filename"

        # 5. Add a header to the output file to identify the source of the tests.
        echo "================================================================================" >> "$OUTPUT_FILE"
        echo "## Test Cases from: $filename" >> "$OUTPUT_FILE"
        echo "================================================================================" >> "$OUTPUT_FILE"

        # 6. Use 'sed' to extract the content between the markers and append it.
        sed -n '/\/\*\* BEGIN TEST CASES \*\*\//,/\/\*\* END TEST CASES \*\*\//p' "$filepath" >> "$OUTPUT_FILE"

        # Add a couple of newlines for better readability between blocks.
        echo "" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo ""
echo "✅ Process complete."
echo "All embedded test cases have been extracted into: $OUTPUT_FILE"


# (.env-3.11) (wsl) SciTeX-Code $ /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/finders/zotero_translators/experiments/extract_zotero_test_cases.sh
# Initializing output file: concatenated_zotero_tests.txt
# Searching for translators in './src/scitex/scholar/url/helpers/finders/zotero_translators'...
#   -> Found and extracting test cases from: Dialnet.js
#   -> Found and extracting test cases from: Databrary.js
#   -> Found and extracting test cases from: Biblio.com.js
#   -> Found and extracting test cases from: LIBRIS ISBN.js
#   -> Found and extracting test cases from: Elsevier Health Journals.js
#   -> Found and extracting test cases from: OSF Preprints.js
#   -> Found and extracting test cases from: ResearchGate.js
#   -> Found and extracting test cases from: Deutsche Fotothek.js
#   -> Found and extracting test cases from: Bluesky.js
#   -> Found and extracting test cases from: IBISWorld.js
#   -> Found and extracting test cases from: Epicurious.js
#   -> Found and extracting test cases from: MODS.js
#   -> Found and extracting test cases from: National Transportation Library ROSA P.js
#   -> Found and extracting test cases from: Scopus.js
#   -> Found and extracting test cases from: IDEA ALM.js
#   -> Found and extracting test cases from: MEDLINEnbib.js
#   -> Found and extracting test cases from: Bundesgesetzblatt.js
#   -> Found and extracting test cases from: PEP Web.js
#   -> Found and extracting test cases from: DABI.js
#   -> Found and extracting test cases from: Bibliotheque nationale de France.js
#   -> Found and extracting test cases from: DAI-Zenon.js
#   -> Found and extracting test cases from: PRC History Review.js
#   -> Found and extracting test cases from: Fatcat.js
#   -> Found and extracting test cases from: Code4Lib Journal.js
#   -> Found and extracting test cases from: CNKI.js
#   -> Found and extracting test cases from: The Boston Globe.js
#   -> Found and extracting test cases from: Scholars Portal Journals.js
#   -> Found and extracting test cases from: National Gallery of Australia.js
#   -> Found and extracting test cases from: In These Times.js
#   -> Found and extracting test cases from: JSTOR.js
#   -> Found and extracting test cases from: National Agriculture Library.js
#   -> Found and extracting test cases from: Hindawi Publishers.js
#   -> Found and extracting test cases from: La Republica (Peru).js
#   -> Found and extracting test cases from: DOAJ.js
#   -> Found and extracting test cases from: National Library of Belarus.js
#   -> Found and extracting test cases from: AMS MathSciNet (Legacy).js
#   -> Found and extracting test cases from: CLACSO.js
#   -> Found and extracting test cases from: The Telegraph.js
#   -> Found and extracting test cases from: Canada.com.js
#   -> Found and extracting test cases from: OAPEN.js
#   -> Found and extracting test cases from: The New Yorker.js
#   -> Found and extracting test cases from: Copernicus.js
#   -> Found and extracting test cases from: Publications du Quebec.js
#   -> Found and extracting test cases from: Erudit.js
#   -> Found and extracting test cases from: Kanopy.js
#   -> Found and extracting test cases from: K10plus ISBN.js
#   -> Found and extracting test cases from: Bookshop.org.js
#   -> Found and extracting test cases from: Heise.js
#   -> Found and extracting test cases from: Yandex Books.js
#   -> Found and extracting test cases from: Web of Science Tagged.js
#   -> Found and extracting test cases from: Airiti.js
#   -> Found and extracting test cases from: Rechtspraak.nl.js
#   -> Found and extracting test cases from: Chicago Journal of Theoretical Computer Science.js
#   -> Found and extracting test cases from: Le Devoir.js
#   -> Found and extracting test cases from: Le Maitron.js
#   -> Found and extracting test cases from: Wikiwand.js
#   -> Found and extracting test cases from: Vice.js
#   -> Found and extracting test cases from: Tatknigafund.js
#   -> Found and extracting test cases from: The Intercept.js
#   -> Found and extracting test cases from: Google Scholar.js
#   -> Found and extracting test cases from: Retsinformation.js
#   -> Found and extracting test cases from: Archeion.js
#   -> Found and extracting test cases from: BOFiP-Impots.js
#   -> Found and extracting test cases from: LA Times.js
#   -> Found and extracting test cases from: Der Freitag.js
#   -> Found and extracting test cases from: RAND.js
#   -> Found and extracting test cases from: Envidat.js
#   -> Found and extracting test cases from: New Zealand Herald.js
#   -> Found and extracting test cases from: Cambridge Engage Preprints.js
#   -> Found and extracting test cases from: World History Connected.js
#   -> Found and extracting test cases from: HUDOC.js
#   -> Found and extracting test cases from: Informationssystem Medienpaedagogik.js
#   -> Found and extracting test cases from: wiso.js
#   -> Found and extracting test cases from: Library Catalog (BiblioCommons).js
#   -> Found and extracting test cases from: Library Catalog (Amicus).js
#   -> Found and extracting test cases from: RefWorks Tagged.js
#   -> Found and extracting test cases from: Springer Link.js
#   -> Found and extracting test cases from: DEPATISnet.js
#   -> Found and extracting test cases from: ACLWeb.js
#   -> Found and extracting test cases from: NYTimes.com.js
#   -> Found and extracting test cases from: COBISS.js
#   -> Found and extracting test cases from: HighBeam.js
#   -> Found and extracting test cases from: Wanfang Data.js
#   -> Found and extracting test cases from: jurion.js
#   -> Found and extracting test cases from: Business Standard.js
#   -> Found and extracting test cases from: Mikromarc.js
#   -> Found and extracting test cases from: LIVIVO.js
#   -> Found and extracting test cases from: Neural Information Processing Systems.js
#   -> Found and extracting test cases from: RSC Publishing.js
#   -> Found and extracting test cases from: SAE Papers.js
#   -> Found and extracting test cases from: Pastebin.js
#   -> Found and extracting test cases from: Lexis+.js
#   -> Found and extracting test cases from: HighWire.js
#   -> Found and extracting test cases from: CQ Press.js
#   -> Found and extracting test cases from: Protein Data Bank.js
#   -> Found and extracting test cases from: National Technical Reports Library.js
#   -> Found and extracting test cases from: Fachportal Padagogik.js
#   -> Found and extracting test cases from: Bloomberg.js
#   -> Found and extracting test cases from: Library Catalog (Voyager 7).js
#   -> Found and extracting test cases from: Library Catalog (SIRSI).js
#   -> Found and extracting test cases from: Library Catalog (Capita Prism).js
#   -> Found and extracting test cases from: Gale Databases.js
#   -> Found and extracting test cases from: RIS.js
#   -> Found and extracting test cases from: SAGE Knowledge.js
#   -> Found and extracting test cases from: Haaretz.js
#   -> Found and extracting test cases from: DPLA.js
#   -> Found and extracting test cases from: HighWire 2.0.js
#   -> Found and extracting test cases from: Nagoya University OPAC.js
#   -> Found and extracting test cases from: Wildlife Biology in Practice.js
#   -> Found and extracting test cases from: Herder.js
#   -> Found and extracting test cases from: MPG PuRe.js
#   -> Found and extracting test cases from: CAOD.js
#   -> Found and extracting test cases from: HAL Archives Ouvertes.js
#   -> Found and extracting test cases from: mEDRA.js
#   -> Found and extracting test cases from: UChicago VuFind.js
#   -> Found and extracting test cases from: Cornell University Press.js
#   -> Found and extracting test cases from: Microsoft Academic.js
#   -> Found and extracting test cases from: Europe PMC.js
#   -> Found and extracting test cases from: MARCXML.js
#   -> Found and extracting test cases from: Air University Journals.js
#   -> Found and extracting test cases from: ATS International Journal.js
#   -> Found and extracting test cases from: Optical Society of America.js
#   -> Found and extracting test cases from: EPA National Library Catalog.js
#   -> Found and extracting test cases from: Daum News.js
#   -> Found and extracting test cases from: The Economic Times - The Times of India.js
#   -> Found and extracting test cases from: IMDb.js
#   -> Found and extracting test cases from: EUR-Lex.js
#   -> Found and extracting test cases from: HCSP.js
#   -> Found and extracting test cases from: Mailman.js
#   -> Found and extracting test cases from: Max Planck Institute for the History of Science Virtual Laboratory Library.js
#   -> Found and extracting test cases from: CERN Document Server.js
#   -> Found and extracting test cases from: TalisPrism.js
#   -> Found and extracting test cases from: XML ContextObject.js
#   -> Found and extracting test cases from: Journal of Extension.js
#   -> Found and extracting test cases from: Ahval News.js
#   -> Found and extracting test cases from: SSOAR.js
#   -> Found and extracting test cases from: Library Catalog (RERO ILS).js
#   -> Found and extracting test cases from: EBSCOhost.js
#   -> Found and extracting test cases from: OZON.ru.js
#   -> Found and extracting test cases from: DSpace Intermediate Metadata.js
#   -> Found and extracting test cases from: The Met.js
#   -> Found and extracting test cases from: Google Books.js
#   -> Found and extracting test cases from: Engineering Village.js
#   -> Found and extracting test cases from: The New York Review of Books.js
#   -> Found and extracting test cases from: BibLaTeX.js
#   -> Found and extracting test cases from: Alsharekh.js
#   -> Found and extracting test cases from: Education Week.js
#   -> Found and extracting test cases from: Japan Times Online.js
#   -> Found and extracting test cases from: PubMed XML.js
#   -> Found and extracting test cases from: Dagens Nyheter.js
#   -> Found and extracting test cases from: CABI - CAB Abstracts.js
#   -> Found and extracting test cases from: Datacite JSON.js
#   -> Found and extracting test cases from: SlideShare.js
#   -> Found and extracting test cases from: Dimensions.js
#   -> Found and extracting test cases from: OECD.js
#   -> Found and extracting test cases from: Standard Ebooks.js
#   -> Found and extracting test cases from: PyPI.js
#   -> Found and extracting test cases from: Ancestry.com US Federal Census.js
#   -> Found and extracting test cases from: JISC Historical Texts.js
#   -> Found and extracting test cases from: ACM Digital Library.js
#   -> Found and extracting test cases from: Library Catalog (TIND ILS).js
#   -> Found and extracting test cases from: Oxford Music and Art Online.js
#   -> Found and extracting test cases from: Galegroup.js
#   -> Found and extracting test cases from: NRC.nl.js
#   -> Found and extracting test cases from: MIT Press Books.js
#   -> Found and extracting test cases from: NRC Research Press.js
#   -> Found and extracting test cases from: Le Figaro.js
#   -> Found and extracting test cases from: digibib.net.js
#   -> Found and extracting test cases from: Probing the Past.js
#   -> Found and extracting test cases from: El Pais.js
#   -> Found and extracting test cases from: TheMarker.js
#   -> Found and extracting test cases from: ASCE.js
#   -> Found and extracting test cases from: YPSF.js
#   -> Found and extracting test cases from: Ovid.js
#   -> Found and extracting test cases from: SORA.js
#   -> Found and extracting test cases from: MCV.js
#   -> Found and extracting test cases from: Verniana-Jules Verne Studies.js
#   -> Found and extracting test cases from: Primo 2018.js
#   -> Found and extracting test cases from: The Art Newspaper.js
#   -> Found and extracting test cases from: Goodreads.js
#   -> Found and extracting test cases from: ProQuest.js
#   -> Found and extracting test cases from: Cell Press.js
#   -> Found and extracting test cases from: The Daily Beast.js
#   -> Found and extracting test cases from: Camara Brasileira do Livro ISBN.js
#   -> Found and extracting test cases from: Ubiquity Journals.js
#   -> Found and extracting test cases from: F1000 Research.js
#   -> Found and extracting test cases from: IEEE Computer Society.js
#   -> Found and extracting test cases from: DOI.js
#   -> Found and extracting test cases from: Bibliontology RDF.js
#   -> Found and extracting test cases from: Lagen.nu.js
#   -> Found and extracting test cases from: Slate.js
#   -> Found and extracting test cases from: AIP.js
#   -> Found and extracting test cases from: Gallica.js
#   -> Found and extracting test cases from: Preprints.org.js
#   -> Found and extracting test cases from: ARTstor.js
#   -> Found and extracting test cases from: Institute of Physics.js
#   -> Found and extracting test cases from: Stanford Encyclopedia of Philosophy.js
#   -> Found and extracting test cases from: Bangkok Post.js
#   -> Found and extracting test cases from: CanLII.js
#   -> Found and extracting test cases from: Old Bailey Online.js
#   -> Found and extracting test cases from: Cornell LII.js
#   -> Found and extracting test cases from: Idref.js
#   -> Found and extracting test cases from: PhilPapers.js
#   -> Found and extracting test cases from: The Independent.js
#   -> Found and extracting test cases from: ASTIS.js
#   -> Found and extracting test cases from: AustLII and NZLII.js
#   -> Found and extracting test cases from: The New Republic.js
#   -> Found and extracting test cases from: SVT Nyheter.js
#   -> Found and extracting test cases from: BioOne.js
#   -> Found and extracting test cases from: Wiktionary.js
#   -> Found and extracting test cases from: BIBSYS.js
#   -> Found and extracting test cases from: Notre Dame Philosophical Reviews.js
#   -> Found and extracting test cases from: ScienceDirect.js
#   -> Found and extracting test cases from: Library Catalog (PICA2).js
#   -> Found and extracting test cases from: BibTeX.js
#   -> Found and extracting test cases from: Thieme.js
#   -> Found and extracting test cases from: Archiv fuer Sozialgeschichte.js
#   -> Found and extracting test cases from: Integrum.js
#   -> Found and extracting test cases from: Literary Hub.js
#   -> Found and extracting test cases from: L'Annee Philologique.js
#   -> Found and extracting test cases from: Queensland State Archives.js
#   -> Found and extracting test cases from: Toronto Star.js
#   -> Found and extracting test cases from: Microbiology Society Journals.js
#   -> Found and extracting test cases from: American Archive of Public Broadcasting.js
#   -> Found and extracting test cases from: Baidu Scholar.js
#   -> Found and extracting test cases from: DrugBank.ca.js
#   -> Found and extracting test cases from: ARTnews.js
#   -> Found and extracting test cases from: Internet Archive Wayback Machine.js
#   -> Found and extracting test cases from: University of Wisconsin-Madison Libraries Catalog.js
#   -> Found and extracting test cases from: Dreier Neuerscheinungsdienst.js
#   -> Found and extracting test cases from: Treesearch.js
#   -> Found and extracting test cases from: UNZ Print Archive.js
#   -> Found and extracting test cases from: Euclid.js
#   -> Found and extracting test cases from: BnF ISBN.js
#   -> Found and extracting test cases from: METS.js
#   -> Found and extracting test cases from: Data.gov.js
#   -> Found and extracting test cases from: MIDAS Journals.js
#   -> Found and extracting test cases from: Stanford University Press.js
#   -> Found and extracting test cases from: Library Catalog (Dynix).js
#   -> Found and extracting test cases from: UPCommons.js
#   -> Found and extracting test cases from: The Nation.js
#   -> Found and extracting test cases from: The Economist.js
#   -> Found and extracting test cases from: CFF.js
#   -> Found and extracting test cases from: CROSBI.js
#   -> Found and extracting test cases from: Lapham's Quarterly.js
#   -> Found and extracting test cases from: ISTC.js
#   -> Found and extracting test cases from: Foreign Policy.js
#   -> Found and extracting test cases from: zotero.org.js
#   -> Found and extracting test cases from: KStudy.js
#   -> Found and extracting test cases from: Gulag Many Days, Many Lives.js
#   -> Found and extracting test cases from: Insignia OPAC.js
#   -> Found and extracting test cases from: Peeters.js
#   -> Found and extracting test cases from: Art Institute of Chicago.js
#   -> Found and extracting test cases from: Litres.js
#   -> Found and extracting test cases from: VoxEU.js
#   -> Found and extracting test cases from: magazines.russ.ru.js
#   -> Found and extracting test cases from: eLife.js
#   -> Found and extracting test cases from: Elicit.js
#   -> Found and extracting test cases from: InvenioRDM.js
#   -> Found and extracting test cases from: Washington Monthly.js
#   -> Found and extracting test cases from: JRC Publications Repository.js
#   -> Found and extracting test cases from: LingBuzz.js
#   -> Found and extracting test cases from: Bosworth Toller's Anglo-Saxon Dictionary Online.js
#   -> Found and extracting test cases from: Time.com.js
#   -> Found and extracting test cases from: Library Catalog (Blacklight).js
#   -> Found and extracting test cases from: Bryn Mawr Classical Review.js
#   -> Found and extracting test cases from: Library Hub Discover.js
#   -> Found and extracting test cases from: Taylor and Francis+NEJM.js
#   -> Found and extracting test cases from: NYPL Menus.js
#   -> Found and extracting test cases from: AlterNet.js
#   -> Found and extracting test cases from: Access Science.js
#   -> Found and extracting test cases from: Fairfax Australia.js
#   -> Found and extracting test cases from: Citizen Lab.js
#   -> Found and extracting test cases from: Die Zeit.js
#   -> Found and extracting test cases from: Patents - USPTO.js
#   -> Found and extracting test cases from: SAILDART.js
#   -> Found and extracting test cases from: J-Stage.js
#   -> Found and extracting test cases from: Bioconductor.js
#   -> Found and extracting test cases from: The Chronicle of Higher Education.js
#   -> Found and extracting test cases from: Rock, Paper, Shotgun.js
#   -> Found and extracting test cases from: OSTI Energy Citations.js
#   -> Found and extracting test cases from: US National Archives Research Catalog.js
#   -> Found and extracting test cases from: Pajhwok Afghan News.js
#   -> Found and extracting test cases from: Libraries Tasmania.js
#   -> Found and extracting test cases from: Annual Reviews.js
#   -> Found and extracting test cases from: Gene Ontology.js
#   -> Found and extracting test cases from: IngentaConnect.js
#   -> Found and extracting test cases from: fishpond.co.nz.js
#   -> Found and extracting test cases from: ESpacenet.js
#   -> Found and extracting test cases from: GameSpot.js
#   -> Found and extracting test cases from: WikiLeaks PlusD.js
#   -> Found and extracting test cases from: scinapse.js
#   -> Found and extracting test cases from: REDALYC.js
#   -> Found and extracting test cases from: artnet.js
#   -> Found and extracting test cases from: eMJA.js
#   -> Found and extracting test cases from: Wikisource.js
#   -> Found and extracting test cases from: USENIX.js
#   -> Found and extracting test cases from: Le Monde.js
#   -> Found and extracting test cases from: ProQuest Ebook Central.js
#   -> Found and extracting test cases from: PubPub.js
#   -> Found and extracting test cases from: E-periodica Switzerland.js
#   -> Found and extracting test cases from: OpenEdition Journals.js
#   -> Found and extracting test cases from: Journal of Machine Learning Research.js
#   -> Found and extracting test cases from: DOI Content Negotiation.js
#   -> Found and extracting test cases from: FreeCite.js
#   -> Found and extracting test cases from: Chronicling America.js
#   -> Found and extracting test cases from: National Bureau of Economic Research.js
#   -> Found and extracting test cases from: reddit.js
#   -> Found and extracting test cases from: NewsBank.js
#   -> Found and extracting test cases from: NZZ.ch.js
#   -> Found and extracting test cases from: IGN.js
#   -> Found and extracting test cases from: Artforum.js
#   -> Found and extracting test cases from: Electronic Colloquium on Computational Complexity.js
#   -> Found and extracting test cases from: INSPIRE.js
#   -> Found and extracting test cases from: ThesesFR.js
#   -> Found and extracting test cases from: Newlines Magazine.js
#   -> Found and extracting test cases from: dejure.org.js
#   -> Found and extracting test cases from: Project Gutenberg.js
#   -> Found and extracting test cases from: BioMed Central.js
#   -> Found and extracting test cases from: Harvard University Press Books.js
#   -> Found and extracting test cases from: SSRN.js
#   -> Found and extracting test cases from: Theory of Computing.js
#   -> Found and extracting test cases from: Brukerhandboken.js
#   -> Found and extracting test cases from: Harvard Caselaw Access Project.js
#   -> Found and extracting test cases from: OpenEdition Books.js
#   -> Found and extracting test cases from: Library Catalog (PICA).js
#   -> Found and extracting test cases from: Internet Archive.js
#   -> Found and extracting test cases from: UpToDate References.js
#   -> Found and extracting test cases from: Finna.js
#   -> Found and extracting test cases from: Mastodon.js
#   -> Found and extracting test cases from: informIT database.js
#   -> Found and extracting test cases from: Boston Review.js
#   -> Found and extracting test cases from: Colorado State Legislature.js
#   -> Found and extracting test cases from: Dagstuhl Research Online Publication Server.js
#   -> Found and extracting test cases from: Hanrei Watch.js
#   -> Found and extracting test cases from: Defense Technical Information Center.js
#   -> Found and extracting test cases from: GMS German Medical Science.js
#   -> Found and extracting test cases from: ZIPonline.js
#   -> Found and extracting test cases from: Gasyrlar Awazy.js
#   -> Found and extracting test cases from: Sueddeutsche.de.js
#   -> Found and extracting test cases from: Vanity Fair.js
#   -> Found and extracting test cases from: Web of Science Nextgen.js
#   -> Found and extracting test cases from: CBC.js
#   -> Found and extracting test cases from: Biblioteca Nacional de Maestros.js
#   -> Found and extracting test cases from: Lulu.js
#   -> Found and extracting test cases from: newshub.co.nz.js
#   -> Found and extracting test cases from: Eastview.js
#   -> Found and extracting test cases from: State Records Office of Western Australia.js
#   -> Found and extracting test cases from: La Presse.js
#   -> Found and extracting test cases from: El Comercio (Peru).js
#   -> Found and extracting test cases from: The Open Library.js
#   -> Found and extracting test cases from: Hispanic-American Periodical Index.js
#   -> Found and extracting test cases from: PubMed.js
#   -> Found and extracting test cases from: Canadian Letters and Images.js
#   -> Found and extracting test cases from: Artefacts Canada.js
#   -> Found and extracting test cases from: WestLaw UK.js
#   -> Found and extracting test cases from: CourtListener.js
#   -> Found and extracting test cases from: Christian Science Monitor.js
#   -> Found and extracting test cases from: Human Rights Watch.js
#   -> Found and extracting test cases from: The Hindu.js
#   -> Found and extracting test cases from: dLibra.js
#   -> Found and extracting test cases from: Financial Times.js
#   -> Found and extracting test cases from: arXiv.org.js
#   -> Found and extracting test cases from: Civilization.ca.js
#   -> Found and extracting test cases from: eLibrary.ru.js
#   -> Found and extracting test cases from: Semantic Scholar.js
#   -> Found and extracting test cases from: Amazon.js
#   -> Found and extracting test cases from: Trove.js
#   -> Found and extracting test cases from: Atlanta Journal-Constitution.js
#   -> Found and extracting test cases from: Primo.js
#   -> Found and extracting test cases from: New Left Review.js
#   -> Found and extracting test cases from: Demographic Research.js
#   -> Found and extracting test cases from: PKP Catalog Systems.js
#   -> Found and extracting test cases from: Wikipedia.js
#   -> Found and extracting test cases from: Regeringskansliet.js
#   -> Found and extracting test cases from: Duke University Press Books.js
#   -> Found and extracting test cases from: PC Games.js
#   -> Found and extracting test cases from: EurogamerUSgamer.js
#   -> Found and extracting test cases from: Qatar Digital Library.js
#   -> Found and extracting test cases from: WHO.js
#   -> Found and extracting test cases from: SLUB Dresden.js
#   -> Found and extracting test cases from: Encyclopedia of Korean Culture.js
#   -> Found and extracting test cases from: Russian State Library.js
#   -> Found and extracting test cases from: ACS Publications.js
#   -> Found and extracting test cases from: ASCO Meeting Library.js
#   -> Found and extracting test cases from: Optimization Online.js
#   -> Found and extracting test cases from: RePEc - Econpapers.js
#   -> Found and extracting test cases from: Sacramento Bee.js
#   -> Found and extracting test cases from: Archive Ouverte en Sciences de l'Information et de la Communication  (AOSIC).js
#   -> Found and extracting test cases from: Inside Higher Ed.js
#   -> Found and extracting test cases from: AllAfrica.js
#   -> Found and extracting test cases from: LiveJournal.js
#   -> Found and extracting test cases from: The Microfinance Gateway.js
#   -> Found and extracting test cases from: Library Catalog (SLIMS).js
#   -> Found and extracting test cases from: Columbia University Press.js
#   -> Found and extracting test cases from: Library Catalog (Pika).js
#   -> Found and extracting test cases from: Delpher.js
#   -> Found and extracting test cases from: International Nuclear Information System.js
#   -> Found and extracting test cases from: Oxford Reference.js
#   -> Found and extracting test cases from: Tumblr.js
#   -> Found and extracting test cases from: Paris Review.js
#   -> Found and extracting test cases from: Google Patents.js
#   -> Found and extracting test cases from: Cascadilla Proceedings Project.js
#   -> Found and extracting test cases from: CIA World Factbook.js
#   -> Found and extracting test cases from: AEA Web.js
#   -> Found and extracting test cases from: Library Catalog (InnoPAC).js
#   -> Found and extracting test cases from: Research Square.js
#   -> Found and extracting test cases from: National Archives of South Africa.js
#   -> Found and extracting test cases from: ePrint IACR.js
#   -> Found and extracting test cases from: clinicaltrials.gov.js
#   -> Found and extracting test cases from: Failed Architecture.js
#   -> Found and extracting test cases from: Victoria & Albert Museum.js
#   -> Found and extracting test cases from: Scholia.js
#   -> Found and extracting test cases from: Mainichi Daily News.js
#   -> Found and extracting test cases from: Computer History Museum Archive.js
#   -> Found and extracting test cases from: Google Presentation.js
#   -> Found and extracting test cases from: PLoS Journals.js
#   -> Found and extracting test cases from: ACLS Humanities EBook.js
#   -> Found and extracting test cases from: NPR.js
#   -> Found and extracting test cases from: LexisNexis.js
#   -> Found and extracting test cases from: Svenska Dagbladet.js
#   -> Found and extracting test cases from: Library Catalog (VTLS).js
#   -> Found and extracting test cases from: The Atlantic.js
#   -> Found and extracting test cases from: AGRIS.js
#   -> Found and extracting test cases from: CSIRO Publishing.js
#   -> Found and extracting test cases from: Korean National Library.js
#   -> Found and extracting test cases from: Sud Ouest.js
#   -> Found and extracting test cases from: Transportation Research Board.js
#   -> Found and extracting test cases from: HathiTrust.js
#   -> Found and extracting test cases from: Tatpressa.ru.js
#   -> Found and extracting test cases from: Bezneng Gajit.js
#   -> Found and extracting test cases from: OpenAlex JSON.js
#   -> Found and extracting test cases from: ADS Bibcode.js
#   -> Found and extracting test cases from: FAZ.NET.js
#   -> Found and extracting test cases from: SFU IPinCH.js
#   -> Found and extracting test cases from: Brill.js
#   -> Found and extracting test cases from: Aluka.js
#   -> Found and extracting test cases from: APS-Physics.js
#   -> Found and extracting test cases from: ARTFL Encyclopedie.js
#   -> Found and extracting test cases from: Library Catalog (SIRSI eLibrary).js
#   -> Found and extracting test cases from: APS.js
#   -> Found and extracting test cases from: JETS.js
#   -> Found and extracting test cases from: CSL JSON.js
#   -> Found and extracting test cases from: Canadiana.ca.js
#   -> Found and extracting test cases from: Legifrance.js
#   -> Found and extracting test cases from: The National Archives (UK).js
#   -> Found and extracting test cases from: MARC.js
#   -> Found and extracting test cases from: EurasiaNet.js
#   -> Found and extracting test cases from: Le monde diplomatique.js
#   -> Found and extracting test cases from: Womennews.js
#   -> Found and extracting test cases from: Ynet.js
#   -> Found and extracting test cases from: Library Catalog (Encore).js
#   -> Found and extracting test cases from: NASA ADS.js
#   -> Found and extracting test cases from: Pleade.js
#   -> Found and extracting test cases from: SIPRI.js
#   -> Found and extracting test cases from: Oxford University Press.js
#   -> Found and extracting test cases from: sbn.it.js
#   -> Found and extracting test cases from: Habr.js
#   -> Found and extracting test cases from: dhistory.js
#   -> Found and extracting test cases from: Oxford Dictionaries Premium.js
#   -> Found and extracting test cases from: Champlain Society - Collection.js
#   -> Found and extracting test cases from: Australian Dictionary of Biography.js
#   -> Found and extracting test cases from: Access Engineering.js
#   -> Found and extracting test cases from: University Press Scholarship.js
#   -> Found and extracting test cases from: Library of Congress Digital Collections.js
#   -> Found and extracting test cases from: ProMED.js
#   -> Found and extracting test cases from: semantics Visual Library.js
#   -> Found and extracting test cases from: Huff Post.js
#   -> Found and extracting test cases from: Superlib.js
#   -> Found and extracting test cases from: Emerald Insight.js
#   -> Found and extracting test cases from: Douban.js
#   -> Found and extracting test cases from: Stuff.co.nz.js
#   -> Found and extracting test cases from: Dar Almandumah.js
#   -> Found and extracting test cases from: Jahrbuch.js
#   -> Found and extracting test cases from: TVNZ.js
#   -> Found and extracting test cases from: HeinOnline.js
#   -> Found and extracting test cases from: Frieze.js
#   -> Found and extracting test cases from: CLASE.js
#   -> Found and extracting test cases from: Denik CZ.js
#   -> Found and extracting test cases from: Reuters.js
#   -> Found and extracting test cases from: PubFactory Journals.js
#   -> Found and extracting test cases from: ZOBODAT.js
#   -> Found and extracting test cases from: Atypon Journals.js
#   -> Found and extracting test cases from: Store norske leksikon.js
#   -> Found and extracting test cases from: DBpia.js
#   -> Found and extracting test cases from: Digital Spy.js
#   -> Found and extracting test cases from: Matbugat.ru.js
#   -> Found and extracting test cases from: beck-online.js
#   -> Found and extracting test cases from: London Review of Books.js
#   -> Found and extracting test cases from: Nature Publishing Group.js
#   -> Found and extracting test cases from: LookUs.js
#   -> Found and extracting test cases from: Open WorldCat.js
#   -> Found and extracting test cases from: American Institute of Aeronautics and Astronautics.js
#   -> Found and extracting test cases from: Cairn.info.js
#   -> Found and extracting test cases from: Bookmarks.js
#   -> Found and extracting test cases from: Safari Books Online.js
#   -> Found and extracting test cases from: Dryad Digital Repository.js
#   -> Found and extracting test cases from: Primo Normalized XML.js
#   -> Found and extracting test cases from: ReferBibIX.js
#   -> Found and extracting test cases from: taz.de.js
#   -> Found and extracting test cases from: ProQuest PolicyFile.js
#   -> Found and extracting test cases from: The Guardian.js
#   -> Found and extracting test cases from: Flickr.js
#   -> Found and extracting test cases from: Perlego.js
#   -> Found and extracting test cases from: Institute of Contemporary Art.js
#   -> Found and extracting test cases from: Antikvarium.hu.js
#   -> Found and extracting test cases from: APA PsycNET.js
#   -> Found and extracting test cases from: The Straits Times.js
#   -> Found and extracting test cases from: CFF References.js
#   -> Found and extracting test cases from: Winnipeg Free Press.js
#   -> Found and extracting test cases from: Khaama Press.js
#   -> Found and extracting test cases from: openJur.js
#   -> Found and extracting test cases from: Game Studies.js
#   -> Found and extracting test cases from: Radio Free Europe  Radio Liberty.js
#   -> Found and extracting test cases from: Endnote XML.js
#   -> Found and extracting test cases from: Public Record Office Victoria.js
#   -> Found and extracting test cases from: medes.js
#   -> Found and extracting test cases from: JurPC.js
#   -> Found and extracting test cases from: National Academies Press.js
#   -> Found and extracting test cases from: Google Play.js
#   -> Found and extracting test cases from: Calisphere.js
#   -> Found and extracting test cases from: Open Conf.js
#   -> Found and extracting test cases from: Handelszeitung.js
#   -> Found and extracting test cases from: DigiZeitschriften.js
#   -> Found and extracting test cases from: News Corp Australia.js
#   -> Found and extracting test cases from: InfoTrac.js
#   -> Found and extracting test cases from: Tesis Doctorals en Xarxa.js
#   -> Found and extracting test cases from: EBSCO Discovery Layer.js
#   -> Found and extracting test cases from: Library Catalog (Visual Library 2021).js
#   -> Found and extracting test cases from: Alexander Street Press.js
#   -> Found and extracting test cases from: AMS MathSciNet.js
#   -> Found and extracting test cases from: Stack Exchange.js
#   -> Found and extracting test cases from: La Croix.js
#   -> Found and extracting test cases from: Washington Post.js
#   -> Found and extracting test cases from: Tony Blair Institute for Global Change.js
#   -> Found and extracting test cases from: Frontiers.js
#   -> Found and extracting test cases from: Digital Humanities Quarterly.js
#   -> Found and extracting test cases from: Google Research.js
#   -> Found and extracting test cases from: fr-online.de.js
#   -> Found and extracting test cases from: PubMed Central.js
#   -> Found and extracting test cases from: Kommersant.js
#   -> Found and extracting test cases from: Legislative Insight.js
#   -> Found and extracting test cases from: Isidore.js
#   -> Found and extracting test cases from: Tagesspiegel.js
#   -> Found and extracting test cases from: Edinburgh University Press Journals.js
#   -> Found and extracting test cases from: ABC News Australia.js
#   -> Found and extracting test cases from: APN.ru.js
#   -> Found and extracting test cases from: MDPI Journals.js
#   -> Found and extracting test cases from: Der Spiegel.js
#   -> Found and extracting test cases from: DBLP Computer Science Bibliography.js
#   -> Found and extracting test cases from: Library Catalog (TLCYouSeeMore).js
#   -> Found and extracting test cases from: Philosopher's Imprint.js
#   -> Found and extracting test cases from: Cambridge Core.js
#   -> Found and extracting test cases from: SciELO.js
#   -> Found and extracting test cases from: COinS.js
#   -> Found and extracting test cases from: Deutsche Nationalbibliothek.js
#   -> Found and extracting test cases from: Welt Online.js
#   -> Found and extracting test cases from: National Library of Norway.js
#   -> Found and extracting test cases from: FAO Publications.js
#   -> Found and extracting test cases from: Harper's Magazine.js
#   -> Found and extracting test cases from: The Globe and Mail.js
#   -> Found and extracting test cases from: LWN.net.js
#   -> Found and extracting test cases from: Elsevier Pure.js
#   -> Found and extracting test cases from: TimesMachine.js
#   -> Found and extracting test cases from: WIPO.js
#   -> Found and extracting test cases from: Medium.js
#   -> Found and extracting test cases from: Wall Street Journal.js
#   -> Found and extracting test cases from: Ariana News.js
#   -> Found and extracting test cases from: feb-web.ru.js
#   -> Found and extracting test cases from: CSV.js
#   -> Found and extracting test cases from: Current Affairs.js
#   -> Found and extracting test cases from: PC Gamer.js
#   -> Found and extracting test cases from: BBC.js
#   -> Found and extracting test cases from: NCBI Nucleotide.js
#   -> Found and extracting test cases from: Beobachter.js
#   -> Found and extracting test cases from: ORCID.js
#   -> Found and extracting test cases from: Baruch Foundation.js
#   -> Found and extracting test cases from: Noor Digital Library.js
#   -> Found and extracting test cases from: Lippincott Williams and Wilkins.js
#   -> Found and extracting test cases from: Library Catalog (Koha).js
#   -> Found and extracting test cases from: Desiring God.js
#   -> Found and extracting test cases from: Juris.js
#   -> Found and extracting test cases from: The Times of Israel.js
#   -> Found and extracting test cases from: Journal of Religion and Society.js
#   -> Found and extracting test cases from: University of California Press Books.js
#   -> Found and extracting test cases from: La Nacion (Argentina).js
#   -> Found and extracting test cases from: unAPI.js
#   -> Found and extracting test cases from: BOE.js
#   -> Found and extracting test cases from: Project MUSE.js
#   -> Found and extracting test cases from: Sveriges radio.js
#   -> Found and extracting test cases from: SALT Research Archives.js
#   -> Found and extracting test cases from: KitapYurdu.com.js
#   -> Found and extracting test cases from: Stitcher.js
#   -> Found and extracting test cases from: Juricaf.js
#   -> Found and extracting test cases from: Dataverse.js
#   -> Found and extracting test cases from: Library of Congress ISBN.js
#   -> Found and extracting test cases from: eMedicine.js
#   -> Found and extracting test cases from: NYPL Research Catalog.js
#   -> Found and extracting test cases from: AMS Journals.js
#   -> Found and extracting test cases from: Schweizer Radio und Fernsehen SRF.js
#   -> Found and extracting test cases from: Embedded Metadata.js
#   -> Found and extracting test cases from: Landesbibliographie Baden-Wurttemberg.js
#   -> Found and extracting test cases from: OVID Tagged.js
#   -> Found and extracting test cases from: Homeland Security Digital Library.js
#   -> Found and extracting test cases from: TV by the Numbers.js
#   -> Found and extracting test cases from: National Archives of Australia.js
#   -> Found and extracting test cases from: Central and Eastern European Online Library Journals.js
#   -> Found and extracting test cases from: NASA NTRS.js
#   -> Found and extracting test cases from: Adam Matthew Digital.js
#   -> Found and extracting test cases from: The Free Dictionary.js
#   -> Found and extracting test cases from: CEUR Workshop Proceedings.js
#   -> Found and extracting test cases from: WorldCat Discovery Service.js
#   -> Found and extracting test cases from: AquaDocs.js
#   -> Found and extracting test cases from: Blaetter.js
#   -> Found and extracting test cases from: BAILII.js
#   -> Found and extracting test cases from: OpenAlex.js
#   -> Found and extracting test cases from: Roll Call.js
#   -> Found and extracting test cases from: Polygon.js
#   -> Found and extracting test cases from: Library Catalog (Quolto).js
#   -> Found and extracting test cases from: BOCC.js
#   -> Found and extracting test cases from: Musee du Louvre.js
#   -> Found and extracting test cases from: Vimeo.js
#   -> Found and extracting test cases from: Perceiving Systems.js
#   -> Found and extracting test cases from: FreePatentsOnline.js
#   -> Found and extracting test cases from: Common-Place.js
#   -> Found and extracting test cases from: CalMatters.js
#   -> Found and extracting test cases from: newspapers.com.js
#   -> Found and extracting test cases from: World Digital Library.js
#   -> Found and extracting test cases from: Library Catalog (Aquabrowser).js
#   -> Found and extracting test cases from: Wikimedia Commons.js
#   -> Found and extracting test cases from: Bloomsbury Food Library.js
#   -> Found and extracting test cases from: Blogger.js
#   -> Found and extracting test cases from: Twitter.js
#   -> Found and extracting test cases from: EIDR.js
#   -> Found and extracting test cases from: NewsnetTamedia.js
#   -> Found and extracting test cases from: Library Catalog (Aleph).js
#   -> Found and extracting test cases from: Open Knowledge Repository.js
#   -> Found and extracting test cases from: Journal of Electronic Publishing.js
#   -> Found and extracting test cases from: De Gruyter Brill.js
#   -> Found and extracting test cases from: RePEc - IDEAS.js
#   -> Found and extracting test cases from: Crossref Unixref XML.js
#   -> Found and extracting test cases from: BBC Genome.js
#   -> Found and extracting test cases from: Library Genesis.js
#   -> Found and extracting test cases from: R-Packages.js
#   -> Found and extracting test cases from: RDF.js
#   -> Found and extracting test cases from: DART-Europe.js
#   -> Found and extracting test cases from: World Shakespeare Bibliography Online.js
#   -> Found and extracting test cases from: The Hamilton Spectator.js
#   -> Found and extracting test cases from: Library Catalog (TinREAD).js
#   -> Found and extracting test cases from: National Library of Poland ISBN.js
#   -> Found and extracting test cases from: SIRS Knowledge Source.js
#   -> Found and extracting test cases from: Library Catalog (Mango).js
#   -> Found and extracting test cases from: Summon 2.js
#   -> Found and extracting test cases from: etatar.ru.js
#   -> Found and extracting test cases from: govinfo.js
#   -> Found and extracting test cases from: SAGE Journals.js
#   -> Found and extracting test cases from: zbMATH.js
#   -> Found and extracting test cases from: Figshare.js
#   -> Found and extracting test cases from: GitHub.js
#   -> Found and extracting test cases from: National Diet Library Catalogue.js
#   -> Found and extracting test cases from: Oxford English Dictionary.js
#   -> Found and extracting test cases from: Library Catalog (DRA).js
#   -> Found and extracting test cases from: Crossref REST.js
#   -> Found and extracting test cases from: Access Medicine.js
#   -> Found and extracting test cases from: National Post.js
#   -> Found and extracting test cases from: ebrary.js
#   -> Found and extracting test cases from: Wired.js
#   -> Found and extracting test cases from: Inter-Research Science Center.js
#   -> Found and extracting test cases from: National Library of Australia (new catalog).js
#   -> Found and extracting test cases from: Papers Past.js
#   -> Found and extracting test cases from: Library Catalog (Voyager).js
#   -> Found and extracting test cases from: Milli Kutuphane.js
#   -> Found and extracting test cases from: Encyclopedia of Chicago.js
#   -> Found and extracting test cases from: Silverchair.js
#   -> Found and extracting test cases from: ERIC.js
#   -> Found and extracting test cases from: NTSB Accident Reports.js
#   -> Found and extracting test cases from: Publications Office of the European Union.js
#   -> Found and extracting test cases from: Internet Archive Scholar.js
#   -> Found and extracting test cases from: Globes.js
#   -> Found and extracting test cases from: YouTube.js
#   -> Found and extracting test cases from: University of Chicago Press Books.js
#   -> Found and extracting test cases from: Taylor & Francis eBooks.js
#   -> Found and extracting test cases from: GPO Access e-CFR.js
#   -> Found and extracting test cases from: IPCC.js
#   -> Found and extracting test cases from: IETF.js
#   -> Found and extracting test cases from: National Gallery of Art - USA.js
#   -> Found and extracting test cases from: Verso Books.js
#   -> Found and extracting test cases from: Library Catalog (OPALS).js
#   -> Found and extracting test cases from: Agencia del ISBN.js
#   -> Found and extracting test cases from: PEI Archival Information Network.js
#   -> Found and extracting test cases from: IEEE Xplore.js
#   -> Found and extracting test cases from: Bracero History Archive.js
#   -> Found and extracting test cases from: Foreign Affairs.js
#   -> Found and extracting test cases from: Talis Aspire.js
#   -> Found and extracting test cases from: CiteSeer.js
#   -> Found and extracting test cases from: Wikidata.js
#   -> Found and extracting test cases from: Climate Change and Human Health Literature Portal.js
#   -> Found and extracting test cases from: Wilson Center Digital Archive.js
#   -> Found and extracting test cases from: Potsdamer Neueste Nachrichten.js
#   -> Found and extracting test cases from: Wiley Online Library.js
#   -> Found and extracting test cases from: CiNii Research.js
#   -> Found and extracting test cases from: Harvard Business Review.js
#   -> Found and extracting test cases from: GameStar GamePro.js
#   -> Found and extracting test cases from: Substack.js
#   -> Found and extracting test cases from: The Times and Sunday Times.js

# ✅ Process complete.
# All embedded test cases have been extracted into: concatenated_zotero_tests.txt

# EOF
#!/bin/bash
# Download papers using Puppeteer MCP

# Create download directory
mkdir -p /home/ywatanabe/proj/SciTeX-Code/downloaded_papers

echo "Starting PDF downloads..."
echo "========================="

# Function to check if PDF was downloaded
check_download() {
    local filename="$1"
    local filepath="/home/ywatanabe/proj/SciTeX-Code/downloaded_papers/${filename}"
    
    if [ -f "$filepath" ]; then
        echo "✓ Successfully downloaded: $filename"
        return 0
    else
        echo "✗ Failed to download: $filename"
        return 1
    fi
}

# Example downloads (to be populated)

# Paper 1: Quantification of Phase-Amplitude Coupling in Neur...
echo "Downloading paper 1/5: Hulsemann-2019-FIN.pdf"

# Try URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/pdf/fnins-13-00573.pdf
echo "Trying URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/pdf/fnins-13-00573.pdf"
# Add puppeteer download command here

# Try URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/
echo "Trying URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/"
# Add puppeteer download command here

# Try URL: https://www.ncbi.nlm.nih.gov/pubmed/31275096
echo "Trying URL: https://www.ncbi.nlm.nih.gov/pubmed/31275096"
# Add puppeteer download command here

# Paper 2: The functional role of cross-frequency coupling...
echo "Downloading paper 2/5: Canolty-2010-TIC.pdf"

# Try URL: https://doi.org/10.1016/j.tics.2010.09.001
echo "Trying URL: https://doi.org/10.1016/j.tics.2010.09.001"
# Add puppeteer download command here

# Try URL: https://www.sciencedirect.com/science/article/pii/S1364661310002068
echo "Trying URL: https://www.sciencedirect.com/science/article/pii/S1364661310002068"
# Add puppeteer download command here

# Paper 3: Untangling cross-frequency coupling in neuroscienc...
echo "Downloading paper 3/5: Aru-2014-CON.pdf"

# Try URL: https://doi.org/10.1016/j.conb.2014.08.002
echo "Trying URL: https://doi.org/10.1016/j.conb.2014.08.002"
# Add puppeteer download command here

# Try URL: https://www.sciencedirect.com/science/article/pii/S0959438814001640
echo "Trying URL: https://www.sciencedirect.com/science/article/pii/S0959438814001640"
# Add puppeteer download command here

# Paper 4: Measuring phase-amplitude coupling between neurona...
echo "Downloading paper 4/5: Tort-2010-JON.pdf"

# Try URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC2944685/
echo "Trying URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC2944685/"
# Add puppeteer download command here

# Try URL: https://www.ncbi.nlm.nih.gov/pubmed/20463205
echo "Trying URL: https://www.ncbi.nlm.nih.gov/pubmed/20463205"
# Add puppeteer download command here

# Paper 5: Time-Frequency Based Phase-Amplitude Coupling Meas...
echo "Downloading paper 5/5: Munia-2019-SR.pdf"

# Try URL: https://doi.org/10.1038/s41598-019-48870-2
echo "Trying URL: https://doi.org/10.1038/s41598-019-48870-2"
# Add puppeteer download command here

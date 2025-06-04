#!/bin/bash
# Script to publish the gpt-researcher package to Azure DevOps Artifacts

# Function to display usage instructions
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -o, --organization <org>    Azure DevOps organization name"
    echo "  -p, --project <project>     Azure DevOps project name"
    echo "  -f, --feed <feed>           Azure Artifacts feed name (default: artifacts)"
    echo "  -h, --help                  Show this help message"
    echo ""
    echo "You can also set these environment variables instead of using command-line options:"
    echo "  AZURE_ORGANIZATION: Azure DevOps organization name"
    echo "  AZURE_PROJECT: Azure DevOps project name" 
    echo "  AZURE_FEED_NAME: Azure Artifacts feed name"
    echo "  AZURE_ARTIFACTS_PAT: Personal Access Token for Azure DevOps"
    echo ""
    echo "Example:"
    echo "  $0 -o myorg -p myproject -f myfeed"
    echo ""
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -o|--organization)
            ORG="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT="$2"
            shift 2
            ;;
        -f|--feed)
            FEED="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Use environment variables if command-line arguments not provided
ORG=${ORG:-${AZURE_ORGANIZATION}}
PROJECT=${PROJECT:-${AZURE_PROJECT}}
FEED=${FEED:-${AZURE_FEED_NAME:-artifacts}}

# Check if required values are set
if [ -z "$ORG" ] || [ -z "$PROJECT" ]; then
    echo "Error: Azure DevOps organization and project are required."
    echo ""
    show_usage
    exit 1
fi

# Check if PAT is set
if [ -z "$AZURE_ARTIFACTS_PAT" ]; then
    echo "Error: AZURE_ARTIFACTS_PAT environment variable is not set."
    echo "Please set it with an Azure DevOps Personal Access Token:"
    echo "export AZURE_ARTIFACTS_PAT=your_pat_here"
    exit 1
fi

# Set the Azure Feed URL
export AZURE_FEED_URL="https://pkgs.dev.azure.com/$ORG/$PROJECT/_packaging/$FEED/pypi/upload"

echo "Publishing gpt-researcher to Azure Artifacts..."
echo "Organization: $ORG"
echo "Project: $PROJECT"
echo "Feed: $FEED"
echo "Feed URL: $AZURE_FEED_URL"
echo ""

# Run the Python publishing script
python scripts/publish_to_azure.py

exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "Publication completed successfully!"
    echo ""
    echo "To install the package from your private feed, configure pip:"
    echo ""
    echo "1. Create or update your pip.conf/pip.ini:"
    echo "[global]"
    echo "extra-index-url=https://pkgs.dev.azure.com/$ORG/$PROJECT/_packaging/$FEED/pypi/simple/"
    echo ""
    echo "2. Install the necessary authentication packages:"
    echo "pip install keyring artifacts-keyring"
    echo ""
    echo "3. Install the package:"
    echo "pip install gpt-researcher"
else
    echo ""
    echo "Publication failed. Please check the error messages above."
fi

exit $exit_code

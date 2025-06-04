# Publishing to Azure DevOps Artifacts

This document explains how to publish the `gpt-researcher` package to your private Azure DevOps Artifacts feed.

## Prerequisites

1. An Azure DevOps organization with Artifacts enabled
2. A Personal Access Token (PAT) with the appropriate permissions:
   - Read & write package management scopes
   - You can generate a new PAT at `https://dev.azure.com/your-organization/_usersSettings/tokens`

## Setup

1. Make sure you have the required Python packages installed:
   ```bash
   pip install build twine
   ```

2. Clone the `gpt-researcher` repository:
   ```bash
   git clone https://github.com/assafelovic/gpt-researcher.git
   cd gpt-researcher
   ```

## Publishing Options

### Option 1: Using the Publishing Script (Recommended)

1. Run the publishing script:
   ```bash
   python scripts/publish_to_azure.py
   ```

2. When prompted, provide the following information:
   - Your Azure DevOps organization name
   - Your Azure DevOps project name
   - Your Azure Artifacts feed name

3. The script will build and publish the package to your Azure Artifacts feed.

### Option 2: Setting Environment Variables

You can set the following environment variables before running the script:

```bash
# Required - your Personal Access Token (do not commit this to version control)
export AZURE_ARTIFACTS_PAT=your_pat_here

# Optional - if not provided, you will be prompted for organization, project, and feed name
export AZURE_FEED_URL=https://pkgs.dev.azure.com/your-org/your-project/_packaging/your-feed/pypi/upload

# Optional - only used if AZURE_FEED_URL is not provided
export AZURE_FEED_NAME=your-feed-name
```

Then run the script:
```bash
python scripts/publish_to_azure.py
```

### Option 3: Manual Publishing

If you prefer to publish manually, follow these steps:

1. Create or update a `.pypirc` file in your home directory:
   ```ini
   [distutils]
   index-servers = azure

   [azure]
   repository = https://pkgs.dev.azure.com/your-org/your-project/_packaging/your-feed/pypi/upload
   username = azure
   password = your_pat_here
   ```

2. Build the package:
   ```bash
   python -m build
   ```

3. Publish using twine:
   ```bash
   python -m twine upload --repository azure dist/*
   ```

## Installing from Azure DevOps Artifacts

To install the package from your private feed, you need to configure pip to use your Azure DevOps feed:

1. Create a `pip.ini` (Windows) or `pip.conf` (Unix/macOS) file:

   **Unix/macOS**
   ```bash
   mkdir -p ~/.pip
   touch ~/.pip/pip.conf
   ```

   Add the following content:
   ```ini
   [global]
   extra-index-url=https://pkgs.dev.azure.com/your-org/your-project/_packaging/your-feed/pypi/simple/
   ```

2. Set up authentication:
   ```bash
   pip install keyring artifacts-keyring
   ```

3. Install the package:
   ```bash
   pip install gpt-researcher
   ```

## Troubleshooting

If you encounter issues with publishing or installing from Azure Artifacts:

1. **Authentication Issues**:
   - Ensure your PAT has the correct permissions
   - Verify that your PAT hasn't expired
   - Make sure your feed URL is correctly formatted

2. **Package Already Exists**:
   - Azure Artifacts doesn't allow overwriting existing versions
   - Update the version number in `setup.py` before publishing

3. **Feed Visibility**:
   - Ensure your feed is either public or you have the appropriate permissions

For additional help, consult the Azure DevOps documentation on Artifacts or contact your Azure DevOps administrator.

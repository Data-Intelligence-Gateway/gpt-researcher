#!/usr/bin/env python
"""
Script to build and publish the gpt-researcher package to Azure DevOps Artifacts.
This script handles building the package and publishing it to a private Azure DevOps Artifacts feed
without requiring direct access to the PAT.

Usage:
    python publish_to_azure.py

Environment Variables:
    AZURE_ARTIFACTS_PAT: Personal Access Token for Azure DevOps
    AZURE_FEED_URL: URL of the Azure DevOps Artifacts feed
    AZURE_FEED_NAME: Name of the Azure DevOps Artifacts feed (optional)
"""

import os
import subprocess
import sys
import configparser
import tempfile
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['build', 'twine']
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing required package: {package}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


def clean_build_directories():
    """Remove old build directories if they exist."""
    dirs_to_clean = ['dist', 'build', '*.egg-info']
    for dir_pattern in dirs_to_clean:
        for path in Path('.').glob(dir_pattern):
            if path.is_dir():
                shutil.rmtree(path)


def build_package():
    """Build the Python package using build."""
    print("Building package...")
    subprocess.check_call([sys.executable, '-m', 'build'])
    print("Package built successfully.")


def create_pypirc_file(azure_feed_url, pat):
    """Create a temporary .pypirc file with Azure Artifacts credentials."""
    pypirc_path = Path.home() / '.pypirc'
    config = configparser.ConfigParser()
    
    if pypirc_path.exists():
        # Read existing .pypirc file if it exists
        config.read(pypirc_path)
    
    # Add or update the [distutils] section
    if not config.has_section('distutils'):
        config.add_section('distutils')
    config.set('distutils', 'index-servers', 'azure')
    
    # Add or update the [azure] section for Azure Artifacts
    if not config.has_section('azure'):
        config.add_section('azure')
    config.set('azure', 'repository', azure_feed_url)
    config.set('azure', 'username', 'azure')
    config.set('azure', 'password', pat)
    
    # Write to a temporary file to avoid saving PAT to disk permanently
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        config.write(temp_file)
        temp_file_path = temp_file.name
    
    return temp_file_path


def publish_to_azure(temp_pypirc_path):
    """Publish the package to Azure Artifacts using the temporary .pypirc file."""
    print("Publishing package to Azure Artifacts...")
    env = os.environ.copy()
    env['PYPIRC'] = temp_pypirc_path
    
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'twine', 'upload', '--repository', 'azure', 'dist/*'],
            env=env
        )
        print("Package published successfully to Azure Artifacts.")
    except subprocess.CalledProcessError as e:
        print(f"Error publishing package: {e}")
        return False
    return True


def get_required_env_vars():
    """Get required environment variables or prompt for them."""
    pat = os.environ.get('AZURE_ARTIFACTS_PAT')
    feed_url = os.environ.get('AZURE_FEED_URL')
    feed_name = os.environ.get('AZURE_FEED_NAME', 'artifacts')
    
    if not pat:
        print("AZURE_ARTIFACTS_PAT environment variable is required.")
        print("Please set it with an Azure DevOps Personal Access Token.")
        print("You can create a PAT at https://dev.azure.com/your-org/_usersSettings/tokens")
        return None, None
    
    if not feed_url:
        org = input("Enter your Azure DevOps organization name: ")
        project = input("Enter your Azure DevOps project name: ")
        if not feed_name:
            feed_name = input("Enter your Azure Artifacts feed name (default: artifacts): ") or "artifacts"
        
        # Construct the feed URL
        feed_url = f"https://pkgs.dev.azure.com/{org}/{project}/_packaging/{feed_name}/pypi/upload"
    
    return feed_url, pat


def main():
    # Check for required dependencies
    check_dependencies()
    
    # Get required environment variables or prompt for them
    feed_url, pat = get_required_env_vars()
    if not feed_url or not pat:
        sys.exit(1)
    
    # Clean build directories
    clean_build_directories()
    
    # Build the package
    build_package()
    
    # Create temporary .pypirc file
    temp_pypirc_path = create_pypirc_file(feed_url, pat)
    
    try:
        # Publish to Azure Artifacts
        success = publish_to_azure(temp_pypirc_path)
        
        if success:
            print("\nPackage successfully published to Azure DevOps Artifacts!")
            print(f"Feed URL: {feed_url}")
        else:
            print("\nFailed to publish package. Check the error messages above.")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_pypirc_path):
            os.unlink(temp_pypirc_path)


if __name__ == "__main__":
    main()

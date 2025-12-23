# Homebrew Tap for aidocs

This directory contains the Homebrew formula for installing `aidocs` CLI.

## Setup Instructions

### 1. Create the Homebrew Tap Repository

Create a new GitHub repository named `homebrew-aidocs` under the `binarcode` organization:

```bash
# Create the repository on GitHub
gh repo create binarcode/homebrew-aidocs --public --description "Homebrew tap for aidocs CLI"
```

### 2. Copy Formula to the Tap

```bash
# Clone the new tap repository
git clone https://github.com/binarcode/homebrew-aidocs.git
cd homebrew-aidocs

# Create Formula directory and copy the formula
mkdir -p Formula
cp /path/to/aidocs-cli/homebrew/Formula/aidocs.rb Formula/

# Update SHA256 (see below)
# Commit and push
git add .
git commit -m "Add aidocs formula"
git push
```

### 3. Generate SHA256 for Release

Before publishing, you need to create a GitHub release tag and get its SHA256:

```bash
# Create a tag (in aidocs-cli repo)
git tag v0.13.1
git push origin v0.13.1

# Get SHA256 of the release tarball
curl -sL https://github.com/binarcode/aidocs-cli/archive/refs/tags/v0.13.1.tar.gz | shasum -a 256
```

Replace `REPLACE_WITH_TAG_SHA256` in the formula with the actual hash.

## Installation

Once the tap is set up, users can install with:

```bash
# Add the tap (one-time)
brew tap binarcode/aidocs

# Install aidocs
brew install aidocs
```

Or in one command:

```bash
brew install binarcode/aidocs/aidocs
```

## Updating the Formula

When releasing a new version:

1. Create a new git tag: `git tag v0.X.X && git push origin v0.X.X`
2. Get the SHA256: `curl -sL https://github.com/binarcode/aidocs-cli/archive/refs/tags/vX.X.X.tar.gz | shasum -a 256`
3. Update `Formula/aidocs.rb` in the homebrew-aidocs repo with new version and SHA256
4. Commit and push to homebrew-aidocs

## Automated Updates (Optional)

You can set up a GitHub Action in the aidocs-cli repo to automatically update the formula when a new release is created. See `.github/workflows/update-homebrew.yml` for an example.

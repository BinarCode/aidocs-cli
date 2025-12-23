class Aidocs < Formula
  desc "AI-powered documentation generator CLI for Claude Code"
  homepage "https://github.com/binarcode/aidocs-cli"
  url "https://github.com/binarcode/aidocs-cli/archive/refs/tags/v0.13.1.tar.gz"
  sha256 "REPLACE_WITH_TAG_SHA256"
  license "MIT"
  head "https://github.com/binarcode/aidocs-cli.git", branch: "main"

  depends_on "python@3.11"

  def install
    python3 = "python3.11"
    venv = virtualenv_create(libexec, python3)

    # Install the package and its dependencies
    system libexec/"bin/pip", "install", ".", "--no-deps"
    system libexec/"bin/pip", "install", "typer>=0.9.0", "rich>=13.0.0", "httpx>=0.27.0"

    # Link the binary
    bin.install_symlink libexec/"bin/aidocs"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/aidocs version")
  end
end

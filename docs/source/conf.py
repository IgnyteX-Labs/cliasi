import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "..", "src")))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "cliasi"
copyright = "2026, f.rader"
author = "f.rader"

# Determine version dynamically from installed package metadata; fall back during local builds.
# Important: avoid defining a callable named `version` in this module, because Sphinx expects
# `version` config value to be a string. We alias the import to `pkg_version` to prevent clashes.
try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as pkg_version
    try:
        release = pkg_version("cliasi")
    except PackageNotFoundError:
        # Fallback to import if available (e.g., when running without install)
        try:
            from cliasi import __version__ as release  # type: ignore
        except Exception:
            release = '0.0.0'
except Exception:
    release = '0.0.0'


# Sphinx expects both `version` and `release` strings; often `version` is the short X.Y.
# We'll derive a short version by trimming any local/dev suffixes after the third dot.
def _short_version(ver: str) -> str:
    # Take first three numeric components (e.g., 1.2.3) if present.
    parts = ver.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:3])
    return ver


version = _short_version(release)

autoclass_content = 'both'

rst_prolog = f"""
    .. |version| replace:: {version}
    .. |release| replace:: {release}
"""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx_substitution_extensions",
]

# Autosummary: generate stub pages for autosummary directives
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": False,
}

# Syntax highlighting styles (light/dark)
pygments_style = "sphinx"
pygments_dark_style = "native"

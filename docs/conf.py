# Sphinx configuration for the ATick documentation site.
# Build locally:   pip install -r docs/requirements.txt && sphinx-build -b html docs docs/_build
# Host:            push to GitHub + connect the repo on https://readthedocs.org (see PUBLISHING.md)

project = "ATick"
author = "Aniket Chaturvedi"
copyright = "2026, Aniket Chaturvedi"
release = "1.0.2"
version = "1.0.2"

extensions = [
    "myst_parser",            # write the docs in Markdown
    "sphinx_copybutton",      # copy button on code blocks
    "sphinx_design",          # cards / grids / badges
    "sphinxext.opengraph",    # Open Graph / Twitter cards for SEO + link previews
    "sphinx_sitemap",         # sitemap.xml for search engines
]

# ---- SEO ----
# Set this to your real published URL (Read the Docs / custom domain) before going live.
html_baseurl = "https://atick.readthedocs.io/en/latest/"
sitemap_url_scheme = "{link}"

_SEO_DESCRIPTION = (
    "ATick is a standalone Python library for PDF digital signatures — PAdES (B-B/B-T/B-LT/B-LTA) "
    "and CMS signing, USB tokens (PKCS#11), the Windows certificate store, and Indian eSign (CCA), "
    "with RFC-3161 timestamps, long-term validation, and a green-tick verified-signature appearance "
    "that Adobe shows as valid. Zero dependencies — pip install atick."
)
_SEO_KEYWORDS = (
    "PDF digital signature Python, sign PDF Python, PAdES, CAdES, CMS, PKCS#11, USB token signing, "
    "eSign, CCA eSign, LTV, RFC-3161 timestamp, Adobe valid signature, green tick signature, "
    "digital signature library, PDF signing"
)
html_meta = {"description": _SEO_DESCRIPTION, "keywords": _SEO_KEYWORDS}

# Open Graph / Twitter card
ogp_site_url = html_baseurl
ogp_site_name = "ATick — Python PDF digital-signature library"
ogp_description_length = 300
ogp_type = "website"
ogp_image = "https://atick.readthedocs.io/en/latest/_static/atick_logo.png"
ogp_enable_meta_description = True
ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image" />',
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = ["colon_fence", "deflist", "tasklist"]
myst_heading_anchors = 3

# ---- HTML: pydata-sphinx-theme, styled to look like the Claude Code docs ----
html_theme = "pydata_sphinx_theme"
html_title = "ATick Docs"
html_static_path = ["_static"]
html_extra_path = ["_extra"]                # robots.txt at the site root
html_css_files = ["custom.css"]
html_favicon = "_static/favicon.png"
html_show_sourcelink = False
pygments_style = "friendly"
pygments_dark_style = "monokai"

html_theme_options = {
    "logo": {"image_light": "_static/atick_logo.png", "image_dark": "_static/atick_logo.png", "text": "ATick Docs"},
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],                       # the top-level section tabs
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "secondary_sidebar_items": ["page-toc"],               # right-hand "On this page"
    "show_prev_next": True,
    "show_nav_level": 1,
    "navigation_depth": 3,
    "header_links_before_dropdown": 6,
    "pygments_light_style": "friendly",
    "pygments_dark_style": "github-dark",
    "icon_links": [
        {"name": "PyPI", "url": "https://pypi.org/project/atick/", "icon": "fa-solid fa-cube"},
    ],
    "footer_start": ["copyright"],
    "footer_end": [],
}

html_sidebars = {
    "index": [],                                           # clean landing (no left sidebar)
    "**": ["sidebar-nav-bs"],                              # left section nav on inner pages
}

html_context = {"default_mode": "light"}

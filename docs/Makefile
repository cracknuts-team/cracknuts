# Minimal makefile for Sphinx documentation
#

# Default target
.DEFAULT_GOAL := default

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
LOCALEDIR     = $(SOURCEDIR)/locale

# Get version from cracknuts
VERSION       := $(shell uv run cracknuts --version 2>/dev/null || echo "dev")

# Put it first so that "make" without argument is like "make help".
help:
	@echo "CrackNuts Documentation Makefile"
	@echo "================================="
	@echo ""
	@echo "i18n Targets:"
	@echo "  update-i18n    - Generate gettext templates and update zh_CN translations"
	@echo "  compile-mo     - Compile .po files to .mo format"
	@echo "  clean-i18n     - Remove compiled .mo files"
	@echo ""
	@echo "Build Targets:"
	@echo "  build-en       - Build English documentation"
	@echo "  build-zh_CN    - Build Chinese (Simplified) documentation"
	@echo "  build-all      - Build all documentation (English + Chinese)"
	@echo ""
	@echo "Sphinx Built-in Targets:"
	@echo "  html           - Build HTML documentation"
	@echo "  dirhtml        - Build HTML with directory index"
	@echo "  singlehtml     - Build single HTML file"
	@echo "  latex          - Build LaTeX documentation"
	@echo "  man            - Build manual page"
	@echo "  text           - Build plain text"
	@echo "  clean          - Remove build directory"
	@echo ""
	@echo "Variables:"
	@echo "  SPHINXOPTS     - Additional options for sphinx-build"
	@echo "  VERSION        - Current version: $(VERSION)"

.PHONY: help Makefile default update-i18n compile-mo build-en build-zh_CN build-all clean-i18n

# Default target: build all documentation when running `make` without arguments
default: build-all

# -----------------------------------------------------------------------------
# i18n targets
# -----------------------------------------------------------------------------

update-i18n:
	@echo "==> Generating gettext templates..."
	$(SPHINXBUILD) -b gettext $(SOURCEDIR) $(BUILDDIR)/gettext
	@echo "==> Updating zh_CN translations..."
	uv run sphinx-intl update -p $(BUILDDIR)/gettext -l zh_CN
	@echo ""
	@echo "==> Checking for untranslated messages..."
	@if grep -q 'msgstr ""' $(SOURCEDIR)/locale/zh_CN/LC_MESSAGES/*.po 2>/dev/null; then \
		echo ""; \
		echo "⚠️  WARNING: Untranslated messages detected!"; \
		echo "   Please translate the following files before building:"; \
		echo ""; \
		grep -l 'msgstr ""' $(SOURCEDIR)/locale/zh_CN/LC_MESSAGES/*.po 2>/dev/null | while read f; do \
			count=$$(grep -c 'msgstr ""' "$$f"); \
			echo "   - $$f ($$count untranslated)"; \
		done; \
		echo ""; \
		echo "   Edit the .po files to add translations, then run 'make compile-mo' and 'make build-zh_CN'."; \
		echo ""; \
	fi

compile-mo:
	@echo "==> Compiling .po files to .mo..."
	uv run sphinx-intl build -d $(LOCALEDIR)

clean-i18n:
	@echo "==> Cleaning .mo files..."
	find $(LOCALEDIR) -name "*.mo" -delete

# -----------------------------------------------------------------------------
# multilingual documentation targets
# -----------------------------------------------------------------------------

build-en:
	@echo "==> Building English documentation..."
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/$(VERSION) $(SPHINXOPTS)

build-zh_CN: compile-mo
	@echo "==> Building Chinese documentation..."
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/$(VERSION)/zh_CN -D language=zh_CN $(SPHINXOPTS)

build-all: build-en build-zh_CN
	@echo "==> Building all documentation..."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
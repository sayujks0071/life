MAIN ?= main
PDFLATEX ?= pdflatex
BIBTEX ?= bibtex
TEXFLAGS ?= -interaction=nonstopmode -halt-on-error
PYTHON ?= python3

.PHONY: all paper quick check-figures validation clean cleanall

all: paper

paper: check-figures $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib $(wildcard sections/*.tex)
	@if command -v latexmk >/dev/null 2>&1; then \
		latexmk -pdf $(TEXFLAGS) $(MAIN).tex; \
	elif command -v $(PDFLATEX) >/dev/null 2>&1; then \
		$(PDFLATEX) $(TEXFLAGS) $(MAIN).tex; \
		$(BIBTEX) $(MAIN); \
		$(PDFLATEX) $(TEXFLAGS) $(MAIN).tex; \
		$(PDFLATEX) $(TEXFLAGS) $(MAIN).tex; \
	else \
		echo "ERROR: neither latexmk nor pdflatex is installed."; \
		echo "Install TeX Live, or upload this directory to Overleaf (see README.md)."; \
		exit 1; \
	fi

quick:
	$(PDFLATEX) $(TEXFLAGS) $(MAIN).tex

check-figures:
	$(PYTHON) ../scripts/check_manuscript_figures.py

validation:
	$(PYTHON) ../scripts/run_submission_validation.py

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).fdb_latexmk $(MAIN).fls $(MAIN).log $(MAIN).out $(MAIN).toc $(MAIN).lof $(MAIN).lot

cleanall: clean
	rm -f $(MAIN).pdf

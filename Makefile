.PHONY: all data figs alphafold clean manuscript

PYTHON = .venv/bin/python3

all: data figs manuscript

data: results/sweep_results.csv results/alphafold_summary.csv

results/single_sim.csv: scripts/sim_single.py
	$(PYTHON) scripts/sim_single.py

results/sweep_results.csv: scripts/sweep_params.py scripts/sim_single.py
	$(PYTHON) scripts/sweep_params.py

results/alphafold_summary.csv: scripts/alphafold_reanalysis.py
	$(PYTHON) scripts/alphafold_reanalysis.py

figs: scripts/make_figures.py data
	$(PYTHON) scripts/make_figures.py

manuscript: data
	$(PYTHON) scripts/update_manuscript.py

alphafold: results/alphafold_summary.csv

clean:
	rm -rf results/*.csv figures/*.png

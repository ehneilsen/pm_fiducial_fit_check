###############################################################################
# Utility
###############################################################################

# .PHONY: clean
# clean:
# 	rm -f data/*.h5 figures/*.png figures/*.pdf

###############################################################################
# Data collection
###############################################################################

# This section contains all code the retrieves 
# data from outside sources; later sections depend
# only on files generated in this section.

.PHONY: collect

collect: data/everywhere_inventory.txt \
		fiducial_fits
	pass

data/everywhere_inventory.txt: sh/everywhere_inventory.sh
	sh/everywhere_inventory.sh

fiducial_fits: sh/fit_fiducials.sh data/everywhere_inventory.txt
	sh/fit_fiducials.sh < data/everywhere_inventory.txt

###############################################################################
# Data munging
###############################################################################

# This section contains code that manipulates input data files, putting them
# in a useful format. Processing and analysis should take place in later
# sections.

munge: data/fids.h5

data/fids.h5: python/munge.py data/everywhere_inventory.txt
	python $^ data $@ \
		--exp_params_fname data/exp_params.txt \
		--fids_fname data/fids.txt

###############################################################################
# Processing
###############################################################################

# process: data/processed/sample_summary.txt \
# 	data/processed/sample_mean.txt

# data/processed/sample_summary.txt: python/sample_summarize.py \
# 		data/collected/sample_collected.txt
# 	$^ $@

# data/processed/sample_mean.txt: R/sample_mean.R \
# 		data/munged/sample.RData
# 	$^ $@

###############################################################################
# Figure generation
###############################################################################

plot: figures/petal_vs_q_page1.png \
	figures/petal_vs_q_page2.png \
	figures/distortion_vs_q_page1.png \
	figures/distortion_vs_q_page2.png \
	figures/petal_vs_zd_page1.png \
	figures/petal_vs_zd_page2.png \
	figures/distortion_vs_zd_page1.png \
	figures/distortion_vs_zd_page2.png \
	figures/petal_vs_mjd_page1.png \
	figures/petal_vs_mjd_page2.png \
	figures/distortion_vs_mjd_page1.png \
	figures/distortion_vs_mjd_page2.png

figures/petal_vs_%_page1.png: python/plot_petals.py \
		data/fids.h5
	python $^ $* 1 $@

figures/petal_vs_%_page2.png: python/plot_petals.py \
		data/fids.h5
	python $^ $* 2 $@

figures/distortion_vs_%_page1.png: python/plot_distortions.py \
		data/fids.h5
	python $^ $* 1 $@

figures/distortion_vs_%_page2.png: python/plot_distortions.py \
		data/fids.h5
	python $^ $* 2 $@

###############################################################################
# Report generation
###############################################################################

# report: report/sample_index.html

# report/figures/%: figures/%
# 	mkdir -p report/figures
# 	cp $< $@

# report/data/collected/%: data/collected/%
# 	mkdir -p report/data/collected
# 	cp $< $@

# report/data/munged/%: data/munged/%
# 	mkdir -p report/data/munged
# 	cp $< $@

# report/data/processed/%: data/processed/%
# 	mkdir -p report/data/processed
# 	cp $< $@

# report/sample_index.html: report/sample_index.org \
# 		report/data/processed/sample_summary.txt \
# 		report/data/munged/sample.RData \
# 		report/figures/sample_plot.png
# 	emacs $< --batch -f org-html-export-to-html --kill


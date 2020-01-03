###############################################################################
# Utility
###############################################################################

.PHONY: clean

clean:
	rm -fr data/*.h5 figures/*.png figures/*.pdf data/????? data/*.txt

.PHONY: retrieve

retrieve:
	rsync -Lav -e ssh cori.nersc.gov:/global/project/projectdirs/desi/users/neilsen/pm_fiducial_fit_check/data/ data

###############################################################################
# Data collection
###############################################################################

.PHONY: collect

collect: data/everywhere_inventory.txt
	pass

data/everywhere_inventory.txt: sh/everywhere_inventory.sh
	sh/everywhere_inventory.sh

###############################################################################
# Data processing
###############################################################################

.PHONY: process

process: fiducial_fits
	pass

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

focus_plot: figures/distortion_vs_focus_xtrans_page1.png \
	figures/distortion_vs_focus_ytrans_page1.png \
	figures/distortion_vs_focus_ytrans_page1.png \
	figures/distortion_vs_focus_xtilt_page1.png \
	figures/distortion_vs_focus_ytilt_page1.png \
	figures/distortion_vs_focus_ztilt_page1.png

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


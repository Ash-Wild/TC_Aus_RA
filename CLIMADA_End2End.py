# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 20:48:32 2021
End to End hazard working
Modified from this tutorial:
https://climada-python.readthedocs.io/en/stable/tutorial/climada_engine_Impact.html

#TC ID numbers from here:
http://ibtracs.unca.edu/index.php?name=v04r00-2019077S13123

@author: Ashley
"""

# Exposure from the module Litpop
# Note that the file gpw_v4_population_count_rev11_2015_30_sec.tif must be downloaded (do not forget to unzip) if
# you want to execute this cell on your computer.

%matplotlib inline
import numpy as np
from climada.entity import LitPop

# Aus with resolution 10km and financial_mode = income group.
exp_lp = LitPop()
exp_lp.set_country(countries=['AUS'], res_arcsec=300, fin_mode='income_group')
exp_lp.check()
exp_lp.gdf.head()
# not needed for impact calculations
# visualize the define exposure
exp_lp.plot_raster(save_tiff='CLIMADA.tiff')
print('\n Raster properties exposures:', exp_lp.meta)

# save the raster
import fiona; fiona.supported_drivers
from climada import CONFIG
results = CONFIG.local_data.save_dir.dir()
# write as hdf5 file
exp_lp.gdf.to_file(results.joinpath('exp_templ'))
exp_lp.gdf.to_csv(results.joinpath('exp_templ.csv'), sep='\t')

from climada.hazard import TCTracks, TropCyclone, Centroids

# Load histrocial tropical cyclone tracks from ibtracs over the North Atlantic basin between 2010-2012
ibtracks_na = TCTracks()
# trevor, Savannah, Veronica
#ibtracks_na.read_ibtracs_netcdf(provider='usa', storm_id=['2019074S08151', '2019067S11115','2019077S13123']) # SIDR 2007 and ROANU 2016
ibtracks_na.read_ibtracs_netcdf(provider='usa', storm_id=['2019067S11115'])
print('num tracks hist:', ibtracks_na.size)

ibtracks_na.equal_timestep(0.5)  # Interpolation to make the track smooth and to allow applying calc_perturbed_trajectories
# Add randomly generated tracks using the calc_perturbed_trajectories method (1 per historical track)
ibtracks_na.calc_perturbed_trajectories(nb_synth_tracks=1)
print('num tracks hist+syn:', ibtracks_na.size)
# not needed for calculations
# visualize tracks
ax = ibtracks_na.plot()
ax.get_legend()._loc = 2

# Define the centroids from the exposures position
centrs = Centroids()
lat = exp_lp.gdf['latitude'].values
lon = exp_lp.gdf['longitude'].values
centrs.set_lat_lon(lat, lon)
centrs.check()

# Using the tracks, compute the windspeed at the location of the centroids
tc = TropCyclone()
tc.set_from_tracks(ibtracks_na, centrs)
tc.check()

from climada.entity import ImpactFuncSet, IFTropCyclone
# impact function TC
impf_tc= IFTropCyclone()
impf_tc.set_emanuel_usa()

# add the impact function to an Impact function set
impf_set = ImpactFuncSet()
impf_set.append(impf_tc)
impf_set.check()

# Get the hazard type and hazard id
[haz_type] = impf_set.get_hazard_types()
[haz_id] = impf_set.get_ids()[haz_type]
print(f"hazard type: {haz_type}, hazard id: {haz_id}")

# Exposures: rename column and assign id
exp_lp.gdf.rename(columns={"impf_": "impf_" + haz_type}, inplace=True)
exp_lp.gdf['impf_' + haz_type] = haz_id
exp_lp.check()
exp_lp.gdf.head()

# Compute impact
# Do not save the results geographically resolved (only aggregate values)
from climada.engine import Impact
imp = Impact()
imp.calc(exp_lp, impf_set, tc, save_mat=False)
exp_lp.gdf

print(f"Aggregated average annual impact: ${round(imp.aai_agg,0)}")

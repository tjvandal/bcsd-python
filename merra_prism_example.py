import os
import time

import xarray as xr
import numpy as np

from bias_correct import BiasCorrectDaily, convert_to_float32

f_observed = 'data/prism_example.nc'
f_modeled = 'data/merra_example.nc'

obs_data = xr.open_dataset(f_observed)

print "loading observations"
obs_data.load()
obs_data = obs_data.dropna('time', how='all')
obs_data = obs_data.resample("D", "time")
obs_data = convert_to_float32(obs_data)

print "loading modeled"
modeled_data = xr.open_dataset(f_modeled)
del modeled_data['time_bnds']
modeled_data.load()
modeled_data = modeled_data.resample("D", "time")
convert_to_float32(modeled_data)

print "starting bcsd"
t0 = time.time()
bc = BiasCorrectDaily(max_train_year=2001, pool=2)
corrected = bc.bias_correction(obs_data, modeled_data, 'ppt',
                               'PRECTOTLAND')
print "running time:", (time.time() - t0)
corrected.to_netcdf("data/merra_bc_example.nc")

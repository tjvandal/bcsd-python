import os
import time
import argparse

import xarray as xr
import numpy as np

from bias_correct import BiasCorrectDaily, convert_to_float32

parser = argparse.ArgumentParser()
parser.add_argument("fobserved", help="Netcdf file containing an upscaled " \
                    "version of the observed dataset", type=str)
parser.add_argument("fmodeled", help="Netcdf file of a GCM or Reanalysis dataset",
                    type=str)
parser.add_argument("var1", help="Variable name of the observed dataset")
parser.add_argument("var2", help="Variable name of the modeled dataset")
parser.add_argument("ofile", help="File to save bias corrected dataset")
parser.add_argument("--njobs", help="File to save bias corrected dataset",
                   default=1, type=int)
args = parser.parse_args()
args = vars(args)

f_observed = 'data/prism_upscaled.nc'
f_modeled = 'data/merra_filled.nc'
obs_var = 'ppt'
modeled_var = 'PRECTOTLAND'


obs_data = xr.open_dataset(args['fobserved'])

print "loading observations"
obs_data.load()
obs_data = obs_data.dropna('time', how='all')
obs_data = obs_data.resample("D", "time")
obs_data = convert_to_float32(obs_data)

print "loading modeled"
modeled_data = xr.open_dataset(args['fmodeled'])
del modeled_data['time_bnds']
modeled_data.load()
modeled_data = modeled_data.resample("D", "time")
convert_to_float32(modeled_data)

print "starting bcsd"
t0 = time.time()
bc = BiasCorrectDaily(max_train_year=2001, pool=2)
corrected = bc.bias_correction(obs_data, modeled_data, args['var1'],
                               args['var2'], njobs=args['njobs'])
print "running time:", (time.time() - t0)
corrected.to_netcdf(args['ofile'])

import pickle
import os, sys

import numpy as np
import xray
from joblib import Parallel, delayed

from pydownscale.qmap import QMap

np.seterr(invalid='ignore')

def mapper(x, y, train_num, step=0.01):
    qmap = QMap(step=step)
    qmap.fit(x[:train_num], y[:train_num], axis=0)
    return qmap.predict(y)

def nanarray(size):
    arr = np.empty(size)
    arr[:] = np.nan
    return arr

def convert_to_float32(ds):
    for var in ds.data_vars:
        if ds[var].dtype == 'float64':
            ds[var] = ds[var].astype('float32', copy=False)
    return ds

class BiasCorrectDaily():
    """ A class which can perform bias correction on daily data

    The process applied is based on the bias correction process applied by
    the NASA NEX team
    (https://nex.nasa.gov/nex/static/media/other/NEX-GDDP_Tech_Note_v1_08June2015.pdf)
    This process does NOT require temporal disaggregation from monthly to daily time steps.
    Instead pooling is used to capture a greater range of variablity
    """
    def __init__(self, pool=15, max_train_year=np.inf, step=0.1):
        self.pool = pool
        self.max_train_year = max_train_year
        self.step = step

    def bias_correction(self, obs, modeled, obs_var, modeled_var, njobs=1):
        """
        Parameters
        ---------------------------------------------------------------
        obs: :py:class:`~xarray.DataArray`, required
            A baseline gridded low resolution observed dataset. This should include
            high quality gridded observations. lat and lon are expected as dimensions.
        modeled: :py:class:`~xarray.DataArray`, required
            A gridded low resolution climate variable to be bias corrected. This may include
            reanalysis or GCM datasets. It is recommended that the lat and lon dimensions 
            match are very similar to obs.
        obs_var: str, required
            The variable name in dataset obs which to model
        modeled_var: str, required
            The variable name in Dataset modeled which to bias correct
        njobs: int, optional
            The number of processes to execute in parallel
        """
        # Select intersecting time perids
        d1 = obs.time.values
        d2 = modeled.time.values
        intersection = np.intersect1d(d1, d2)
        obs = obs.loc[dict(time=intersection)]
        modeled = modeled.loc[dict(time=intersection)]

        dayofyear = obs['time.dayofyear']
        lat_vals = modeled.lat.values
        lon_vals = modeled.lon.values

        # initialize the output data array
        mapped_data = np.zeros(shape=(intersection.shape[0], lat_vals.shape[0], 
                                      lon_vals.shape[0]))
        # loop through each day of the year, 1 to 366
        for day in np.unique(dayofyear.values):
            print "Day = %i" % day
            # select days +- pool
            dayrange = (np.arange(day-self.pool, day+self.pool+1) + 366) % 366 + 1
            days = np.in1d(dayofyear, dayrange)
            subobs = obs.loc[dict(time=days)]
            submodeled = modeled.loc[dict(time=days)]

            # which rows correspond to these days
            sub_curr_day_rows = np.where(day == subobs['time.dayofyear'].values)[0]
            curr_day_rows = np.where(day == obs['time.dayofyear'].values)[0]
            train_num = np.where(subobs['time.year'] <= self.max_train_year)[0][-1]
            mapped_times = subobs['time'].values[sub_curr_day_rows]

            jobs = [] # list to collect jobs
            for i, lat in enumerate(lat_vals):
                X_lat = subobs.sel(lat=lat, lon=lon_vals, method='nearest')[obs_var].values
                Y_lat = submodeled.sel(lat=lat, lon=lon_vals)[modeled_var].values
                jobs.append(delayed(mapper)(X_lat, Y_lat, train_num, self.step))

            print "Running jobs", len(jobs)
            # select only those days which correspond to the current day of the year
            day_mapped = np.asarray(Parallel(n_jobs=njobs)(jobs))[:, sub_curr_day_rows]
            day_mapped = np.swapaxes(day_mapped, 0, 1)
            mapped_data[curr_day_rows, :, :] = day_mapped

        # put data into a data array
        dr = xray.DataArray(mapped_data, coords=[obs['time'].values, lat_vals, lon_vals],
                       dims=['time', 'lat', 'lon'])
        dr.attrs['gridtype'] = 'latlon'
        ds = xray.Dataset({'bias_corrected': dr}) 
        ds = ds.reindex_like(modeled)
        modeled = modeled.merge(ds) # merging aids in preserving netcdf structure
        # delete modeled variable to save space
        del modeled[modeled_var]
        return modeled


# Bias Correction Spatial Disaggregation

## Prism Downscaling MERRA-2 - Precipitation

Requirements
----------------
- python2.7
- xarray (http://xarray.pydata.org/en/stable/index.html)
- climate data operators (cdo) (https://code.zmaw.de/projects/cdo)

### Data
Merra 2 - A reanalysis dataset provided by NASA's Global Modeling and Assimilation 
Office. We extract preciptation from the land product to downscale. Reanalysis datasets
are used to test a downscaling model's skill against an observed dataset.
https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/

Prism - The prism 4km precipitation dataset is aggregated to 16km, which will be our
observations. http://www.prism.oregonstate.edu/

### Preprocessing of data
- Interplate missing values
- Upscale Prism and remap to MERRA
- Merge all years into single files, 1 per data source

```bash
cd data
prism='prism_example.nc'
merra='merra_example.nc'
prism_upscaled='prism_upscaled.nc'
merra_filled='merra_filled.nc'

cdo griddes $merra > merra_grid
cdo fillmiss $prism tmp_filled.nc
cdo remapbil,merra_grid -gridboxmean,3,3 tmp_filled.nc $prism_upscaled
cdo fillmiss $merra $merra_filled
rm tmp_filled.nc
```

### Bias Correction
```python
python ../merra_prism_example.py $prism_upscaled $merra_filled ppt PRECTOTLAND merra_bc.nc
```

### Spatial Disaggregation - Scaling
#### Remap Bias Corrected Merra to the High Resolution Prism
```bash
cdo griddes $prism > prism_grid
cdo remapbil,prism_grid merra_bc.nc merra_bc_interp.nc 
```
#### Interpolate upscaled Prism to Original Resolution
```bash
cdo remapbil,prism_grid $prism_upscaled prism_reinterpolated.nc
```
#### Compute scaling Factors
```bash
cdo ydayavg prism_reinterpolated.nc prism_interpolated_ydayavg.nc
cdo ydayavg $prism prism_ydayavg.nc
cdo div prism_ydayavg.nc prism_interpolated_ydayavg.nc scale_factors.nc
```

#### Execute Spatial Scaling
```python
python ../spatial_scaling.py merra_bc_interp.nc scale_factors.nc merra_bcsd.nc
```

#### Masking (optional)
The dataset provided does not contain any bodies of water but 
when downscaling north america the ocean is filled with interpolated values.
After spatial scaling we'll want to replace filled values with NaN. Here, we 
build a dataset with 1's over land and NaN over bodies of water.
```bash
cdo seltimestep,1 -div -addc,1 $prism -addc,1 $prism mask.nc
cdo mul mask.nc merra_bcsd.nc merra_bcsd_masked.nc
```

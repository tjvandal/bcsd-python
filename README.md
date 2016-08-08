# Bias Correction Spatial Disaggregation

## Prism Downscaling MERRA-2 - Precipitation

### Preprocessing of data
- Interplate missing values
- Upscale Prism and remap to MERRA
- Merge all years into single files, 1 per data source

```bash
cd /raid/tvandal/bcsd-prism-merra/
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
python merra_prism_example.py data/$prism_upscaled data/$merra_filled ppt PRECTOTLAND data/merra_bc.nc
```

### Spatial Disaggregation - Scaling
#### Remap Bias Corrected Merra to the High Resolution Prism
```bash
cdo griddes data/$prism > data/prism_grid
cdo remapbil,data/prism_grid data/merra_bc.nc data/merra_bc_interp.nc 
```
#### Interpolate upscaled Prism to Original Resolution
```bash
cdo remapbil,data/prism_grid data/$prism_upscaled data/prism_reinterpolated.nc
```
#### Compute scaling Factors
```bash
cdo ydayavg data/prism_reinterpolated.nc data/prism_interpolated_ydayavg.nc
cdo ydayavg data/$prism data/prism_ydayavg.nc
cdo div data/prism_ydayavg.nc data/prism_interpolated_ydayavg.nc data/scale_factors.nc
```

#### Execute Spatial Scaling
```python
python spatial_scaling.py data/merra_bc_interp.nc data/scale_factors.nc data/merra_bcsd.nc
```

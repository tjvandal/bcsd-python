# Bias Correction Spatial Disaggregation

## Prism Downscaling MERRA-2 - Precipitation

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

# Bias Correction Spatial Disaggregation

## Prism Downscaling MERRA-2 - Precipitation

### Preprocessing of data
- Interplate missing values
- Upscale Prism and remap to MERRA
- Merge all years into single files, 1 per data source

```bash
cd /raid/tvandal/bcsd-prism-merra/
prism='prism_ppt_16km_1981_2014.nc'
merra='merra2_lnd_prcp_1980_2015.nc'
prism_upscaled='prism_ppt_upscaled_1981_2014.nc'
merra_filled='merra2_lnd_prcp_1980_2015_filled.nc'

cdo griddes $merra > merra_map
cdo fillmiss $prism tmp_filled.nc
cdo remapbil,merra_map -gridboxmean,3,3 tmp_filled.nc $prism_upscaled
cdo fillmiss $merra $merra_filled
rm tmp_filled.nc
```

### Bias Correction
```python

```


### Spatial Disaggregation - Scaling
```python

```

### Mask Ocean
```bash

```

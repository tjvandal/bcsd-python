cd ~/repos/bcsd-python/data/
prism='prism_example.nc'
merra='merra_example.nc'
prism_upscaled='prism_upscaled.nc'
merra_filled='merra_filled.nc'

cdo griddes $merra > merra_map
cdo fillmiss $prism tmp_filled.nc
cdo remapbil,merra_map -gridboxmean,3,3 tmp_filled.nc $prism_upscaled
cdo fillmiss $merra $merra_filled
rm tmp_filled.nc

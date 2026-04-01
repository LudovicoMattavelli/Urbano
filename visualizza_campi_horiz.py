"""

"""

import xarray as xr
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.colors as mcolors
from plot_utilis import plot_map_model,plot_map_model_with_wind, plot_map_model_gridpoints, plot_timeseries_diff_2points, create_video_from_imagesSeries

temp_min =-1
temp_max =1
n_bins = 21

# DEFINISCO CASE STUDY
dataini = "20240701" 
oraini = "18" 
step_ini= "00"
step_fin= "06" #compreso
var_shortName="twater" # es: sp/2t/10u/10v/2d

resolution="2km"
#DEFINISCO ESPERIMENTI
A_experiment_name="icon_2I_fcruc"#"fcastnest2way_500m_GLBC_TUOFF_configLitt2"
B_experiment_name="icbc2I_GLBCModif2_TUON_configOpe"
experiment_name=f"{A_experiment_name}"
with_wind=False
calcolo_diff=False
dir_Data=f"/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Data_supporto/Urbano"
dir_files=f"{dir_Data}/Data_g100/{dataini}/getVarTimeseriesGrib_{dataini}{oraini}+{step_ini}_{step_fin}"
def build_grib_path(experiment_name,var_tag):
    return (
        f"{dir_files}/"
        f"{experiment_name}_{var_tag}_{dataini}{oraini}+{step_ini}_{step_fin}.grib"
    )
ref_file  = build_grib_path(A_experiment_name,var_shortName)
con_file= build_grib_path(B_experiment_name,var_shortName)


# Varriabili restanti
var_name_file = var_shortName
extent = [8.6,13.2,43.43,45.43]  # dom_v1_DOM03

Comune_studied='Bologna'
if var_shortName == "twater":
    colors = ['#2f00a2', '#5100ff', '#5d00ff', '#7458ff', '#00ffff', '#f6ff00', '#ffe435', '#ff1800', '#7a1b11','#c3ff00']
    bars= [5,10,15,20,25,30,35,40,45,55,65]
elif var_shortName == "tp":
    colors = ['#d5d5d5', '#93ffff','#00ffff', '#7590ff', '#2958ff', '#5f00ff', '#007473',
             '#f5ff00', '#ff7400', '#ff0000', '#ff00fc', '#b300ef', '#93007f']
    bars= [0.5,1,2,5,10,20,30,50,70,100,150,200,300,500]
elif var_shortName == "cape":
    colors = ['#ff0000', '#d10400', '#ff9000', '#fee700', '#c3ff00', '#31ff21', '#00ff2c', '#00ff2d', '#00ff55',
               '#00ff9a', '#00ffe0', '#00ddff', '#007cff', '#4b00ff', '#5500ff']
    bars = [100,200,300,500,750,1000,1250,1500,1750,2000,2250,2500,2750,3000,3500,4000]

comuni = gpd.read_file('/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Com01012025_WGS84.shp')
comune = comuni[comuni['COMUNE'] == Comune_studied]
comune = comune.to_crs(epsg=4326)

regioni = gpd.read_file('/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Reg01012025_WGS84.shp')
regioni = regioni.to_crs(epsg=4326)

def read_first_var(path):
    """Apre un file GRIB con cfgrib e restituisce la prima variabile e var_name"""
    ds = xr.open_dataset(path, engine="cfgrib")
    return ds[list(ds.data_vars)[0]],list(ds.data_vars)[0],ds[list(ds.data_vars)[0]].units

ref_var,var_name,var_units = read_first_var(f'{ref_file}')
if with_wind == True:
    level_name = "850"
    u_file  = build_grib_path(A_experiment_name,f"u_{level_name}")
    v_file  = build_grib_path(A_experiment_name,f"v_{level_name}")
    z_file  = build_grib_path(A_experiment_name,f"z_{level_name}")
    u_var,u_var_name = read_first_var(f'{u_file}')
    v_var,v_var_name = read_first_var(f'{v_file}')
    z_var,z_var_name = read_first_var(f'{z_file}')

if calcolo_diff == True:
    con_var,var_name,var_units = read_first_var(f'{con_file}')
    diff = con_var - ref_var
    ref_var = diff
    experiment_name=f"{B_experiment_name}-{A_experiment_name}"
else:
    bias=0
    if var_name == 't' or var_name=='t2m':
        bias = 273.15
        ref_var = ref_var - bias  
        var_units = "°C"
    lat_min, lat_max = 44.45, 45.2
    lon_min, lon_max = 10.0, 11.7

    temp_min=ref_var.sel(latitude=slice(lat_min, lat_max),longitude=slice(lon_min, lon_max)).min().values 
    temp_max=ref_var.sel(latitude=slice(lat_min, lat_max),longitude=slice(lon_min, lon_max)).max().values 
# tp: 0,50,25
# cape_ml 0,2400,25
n_bins = 25
temp_min =25
temp_max =75 #
#n_bins = 15
# Crea i boundaries (21 valori per 20 intervalli)
boundaries = np.linspace(temp_min, temp_max, n_bins + 1)
# Crea la colormap discreta
cmap = plt.cm.viridis#coolwarm
norm = mcolors.BoundaryNorm(boundaries, cmap.N)

for time_step in range(0,6): #[3,6,9,12]
    extent= [8.6,13.2,43.43,45.43]
    #extent = [10.75, 11.89, 43.93, 44.99]
    #extent = [9,12.9,44.45,45.2]
   # extent = [10.7,11.8,44,45.1]
    #extent= [6,20,36,49] #38
    if var_shortName == "tp":
        var_units = 'mm'
        timestep_start=time_step-3
        alpha = ref_var[time_step]-ref_var[timestep_start]
        oraini_val=int(oraini)+int(step_ini)
        hour=f"{timestep_start+oraini_val}:{time_step+oraini_val}"
    else:
            alpha = ref_var[time_step]
            hour=time_step+int(oraini)+int(step_ini)
            
    if with_wind == False:
        
        fig, ax = plot_map_model(alpha,experiment_name,hour,var_name,var_units,extent,cmap,norm,regioni,comune,resolution,f"{dataini}{oraini}")
    else:
        fig, ax = plot_map_model_with_wind(alpha,u_var[time_step], v_var[time_step], z_var[time_step],experiment_name,time_step,var_name,var_units,extent,cmap,norm,regioni,comune,resolution,dataini)
   # plt.savefig(f'/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Immagini_supporto/Urbano/Immagini_caso_{dataini}/plot_map_model_DOM03_{var_shortName}_{experiment_name}_{time_step}_{dataini}{oraini}+{step_ini}_{step_fin}.png', dpi=300, bbox_inches='tight')
    plt.show()

#-------------------------------------------------------------------------------------------------------------------------------


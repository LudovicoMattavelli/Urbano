#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 14:08:27 2026

@author: lmattavelli
"""
# ---------------------------------------------------------------------
import numpy as np
import xarray as xr
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.colors as mcolors
import xarray as xr
from plot_utilis import plot_map_model


experiment_name="RADNAZANA_orario"
extent = [8.6,13.2,43.43,45.43]
resolution = "radar"
regioni = gpd.read_file('/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Reg01012025_WGS84.shp')
regioni = regioni.to_crs(epsg=4326)
dataini = "2024-07-01" 
oraini = "0" 
var_shortName="tp" # es: sp/2t/10u/10v/2d
# Crea la colormap discreta
val_min, val_max = 0, 50
n_bins = 25
boundaries = np.linspace(val_min, val_max, n_bins + 1)
cmap = plt.cm.coolwarm
norm = mcolors.BoundaryNorm(boundaries, cmap.N)
comuni = gpd.read_file('/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Com01012025_WGS84.shp')
comune = comuni[comuni['COMUNE'] == 'Bologna']
comune = comune.to_crs(epsg=4326)
DIR_DATA="../Data_supporto/Dati_estratti/Radar_2024"

from datetime import datetime, timedelta
# Data iniziale come stringa
giorno_base = f"{dataini}-{oraini}"
# Conversione della stringa in oggetto datetime
data_base = datetime.strptime(giorno_base, "%Y-%m-%d-%H")

# Ciclo sulle 48 ore
# === CONFIGURAZIONE ===
PLOT_MODE = 'cumulative'  # 'single' oppure 'cumulative'
CUMULATIVE_HOURS = 3      # usato solo se PLOT_MODE == 'cumulative'

# === FUNZIONE PER LEGGERE UN FILE GRIB ===
def load_grib(data_base, offset_hours, DIR_DATA):
    data_corrente = data_base + timedelta(hours=offset_hours)
    giorno = data_corrente.strftime("%Y-%m-%d-%H")
    ref_file = f"{DIR_DATA}/{giorno}_RADNAZANA_orario.grib"
    ref_ds = xr.open_dataset(ref_file, engine="cfgrib")
    var_name = list(ref_ds.data_vars)[0]
    return ref_ds[var_name], var_name, giorno

# === LOOP PRINCIPALE ===
for time_step in range(12, 24):
    if PLOT_MODE == 'single':
        # --- Singolo timestep ---
        ref_var, var_name, giorno = load_grib(data_base, time_step, DIR_DATA)
        var_units = 'mm'
        data_to_plot = ref_var
    elif PLOT_MODE == 'cumulative':
        # --- Cumulata su CUMULATIVE_HOURS ore ---
        cumulative_data = None
        for offset in range(CUMULATIVE_HOURS+1):
            var, var_name, giorno = load_grib(data_base, time_step + offset, DIR_DATA)
            cumulative_data = var if cumulative_data is None else cumulative_data + var
        var_units = 'mm'
        time_step=f"{time_step+1}:{time_step + offset+1}"
        data_to_plot = cumulative_data
    else:
        raise ValueError(f"PLOT_MODE non valido: '{PLOT_MODE}'. Scegli 'single' o 'cumulative'.")
    # === PLOT ===
    fig, ax = plot_map_model(
        data_to_plot, experiment_name, time_step,
        var_name, var_units, extent, cmap, norm,
        regioni, comune, resolution, f"2024070100"
    )
    plt.show()




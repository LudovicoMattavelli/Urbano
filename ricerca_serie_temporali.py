#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 11:02:45 2026

@author: lmattavelli
"""
# ---------------------------------------------------------------------
# Librerie
# ---------------------------------------------------------------------
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import os
import matplotlib.colors as mcolors

# ---------------------------------------------------------------------
# Parametri grafici
# ---------------------------------------------------------------------
f_base = 19
f_title = f_base + 2
f_assi = f_base - 2 +2
f_ticks = f_base - 4 +1
imm_a = 12
imm_b = 6
unità_di_misura  = '°C'

direzione_vento = ['Vd_id165','B11001','vd10']
velocita_vento = ['V_id166','B11002','v10']
precipitazione = ['tp_id160','B13011','tp'] #160 o 250
temperatura = ['t_id158','B12101','t2m']
variabili = [temperatura, precipitazione, velocita_vento, direzione_vento]

experiment_name,var_bcode_in_obs,var_name_in_obs = variabili[1]
start_date    = "2024-01-01"
end_date      = "2024-12-31"
obs_file = f"/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Data_supporto/Dati_estratti/Data_{start_date}_{end_date}/Staz_{experiment_name}_{start_date}_{end_date}.csv"  #Data_2023-07-31_2023-08-01/Staz_t_id158_2023-07-31_2023-08-01.csv"
citta         = 'Bologna'
Urbane_stazioni   = [ 'Bologna urbana', 'Bologna idrografico',
                     'Modena urbana', 'Ferrara urbana', 'Piacenza urbana', 
    'Parma urbana',"Reggio nell'Emilia urbana",'Dozza', "Forli' urbana", 'Rimini urbana',"Villa Ghigi","Bologna San Luca"]
stazioni = Urbane_stazioni
# --- Bounding box [lat_min, lat_max, lon_min, lon_max] ---
lat_min, lat_max = 44.1, 44.7
lon_min, lon_max = 11, 11.7
days_to_plot=10
def plot_timeserie_stations_from_sepcific_domain(obs_file,var_bcode_in_obs,var_name_in_obs,start_date,end_date,lat_min, lat_max, lon_min, lon_max):
    #-----------------------------------------------
    # PLot tutte le staz
    #-----------------------------------------------
    obs_ds = pd.read_csv(obs_file)
    obs_ds.rename(columns={
        'Latitude': 'Lat',
        'Longitude': 'Lon',
        var_bcode_in_obs: var_name_in_obs,
        'B01019': 'Stazione',
        'B07030': 'Quota'
    }, inplace=True)

    # Converto colonna Date in datetime e imposto come indice
    obs_ds.loc[:, 'datetime'] = pd.to_datetime(obs_ds['Date'])
    obs_ds.set_index('datetime', inplace=True)


    mask = (
        (obs_ds['Lat'] >= lat_min) & (obs_ds['Lat'] <= lat_max) &
        (obs_ds['Lon'] >= lon_min) & (obs_ds['Lon'] <= lon_max)
    )
    obs_bbox = obs_ds[mask]

    # Prendi tutte le stazioni nel bbox
    stazioni = obs_bbox['Stazione'].unique()

    risultati = {}
    for stazione in stazioni:
        obs_st = obs_bbox[obs_bbox['Stazione'] == stazione].copy()
        obs_var_sel = obs_st[var_name_in_obs][start_date:end_date]
        #obs_var_sel_hourly = obs_var_sel.resample('1h').mean()  # media oraria
        risultati[stazione] = obs_var_sel
        
    # Chiamate
    start = pd.Timestamp(start_date)
    end   = pd.Timestamp(end_date)

    current = start
    while current < end:
        next_step = min(current + pd.Timedelta(days=2), end)
        plot_stazioni(risultati, var_name_in_obs, current, next_step)
        current = next_step

"""  
# --- Aggiungi stazioni come cerchi colorati ---
projPC = ccrs.PlateCarree()
fig = plt.figure()
ax = plt.axes(projection=projPC)

for stazione, serie in risultati.items():
    # Valore medio (o istantaneo) della stazione per lo step temporale
    obs_st = obs_bbox[obs_bbox['Stazione'] == stazione]
    lat = obs_st['Lat'].iloc[0]
    lon = obs_st['Lon'].iloc[0]
    
    # Prendi il valore più vicino al time_step del modello
    val = serie.iloc[12]

    sc = ax.scatter(
        lon, lat,
        c=val,
        cmap='viridis',
        s=80,           # dimensione cerchio
        edgecolors='black',
        linewidths=0.8,
        transform=projPC,
        zorder=5        # sopra il modello
    )

plt.show()

"""


def plot_timeserie_stations_from_list(obs_file,var_bcode_in_obs,var_name_in_obs,start_date,end_date,stazioni,days):
    #-----------------------------------------------
    # plotto solo la lista delle stazioni
    #-----------------------------------------------
    obs_ds = pd.read_csv(obs_file)
    obs_ds.rename(columns={
        'Latitude': 'Lat',
        'Longitude': 'Lon',
        var_bcode_in_obs: var_name_in_obs,
        'B01019': 'Stazione',
        'B07030': 'Quota'
    }, inplace=True)

    # Converto colonna Date in datetime e imposto come indice
    obs_ds.loc[:, 'datetime'] = pd.to_datetime(obs_ds['Date'])
    obs_ds.set_index('datetime', inplace=True)

    risultati = {}
    # Assicurati che l'indice sia datetime
    for stazione in stazioni:
        obs_st = obs_ds[obs_ds['Stazione'] == stazione].copy()
        obs_var_sel = obs_st[var_name_in_obs][start_date:end_date]
        #obs_var_sel.index = pd.to_datetime(obs_var_sel.index)  # forza datetime
        risultati[stazione] = obs_var_sel
    
    # Chiamate
    start = pd.Timestamp(start_date)
    end   = pd.Timestamp(end_date)

    current = start
    while current < end:
        next_step = min(current + pd.Timedelta(days=days), end)
        plot_stazioni(risultati, var_name_in_obs, current, next_step)
        current = next_step


# --- Plot helper per non ripetere codice ---
def plot_stazioni(risultati, var_name, xlim_start, xlim_end):
    fig, ax = plt.subplots(figsize=(12, 5))
    for stazione, serie in risultati.items():
        ax.plot(serie.index, serie.values, label=stazione)
    ax.set_xlabel('Data')
    ax.set_ylabel(var_name)
    ax.set_title(f'Serie temporale - {var_name} - {xlim_start} - {xlim_end}')
    ax.legend()
    ax.set_xlim([pd.Timestamp(xlim_start), pd.Timestamp(xlim_end)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m%h'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    #plt.savefig(f'../ICCARUS26DataImages/Immagini_caso_20230731/plot_obs_serie_temporale_v0_{experiment_name}_tp_{xlim_start}_{xlim_end}.png', dpi=300, bbox_inches='tight')
    plt.show()

plot_timeserie_stations_from_list(obs_file,var_bcode_in_obs,var_name_in_obs,start_date,end_date,stazioni,days_to_plot)




















"""
for stazione in stazioni:
    obs_st = obs_ds[obs_ds['Stazione'] == stazione].copy()
    target_lat = obs_st['Lat'].iloc[0]
    target_lon = obs_st['Lon'].iloc[0]
    obs_var_sel = obs_st[var_name_in_obs][start_date:end_date]
    risultati[stazione] = obs_var_sel

# --- Plot ---
fig, ax = plt.subplots(figsize=(12, 5))

for stazione, serie in risultati.items():
    ax.plot(serie.index, serie.values, label=stazione)

ax.set_xlabel('Data')
ax.set_ylabel(var_name_in_obs)
ax.set_title(f'Serie temporale - {var_name_in_obs}')
ax.legend()
ax.set_xlim([datetime.datetime(2024, 6, 1,0), datetime.datetime(2024, 7, 10,0)])
plt.tight_layout()
plt.show()
"""
    
"""
# --- Stazione urbana ---
obs_urb = obs_ds[obs_ds['Stazione'] == stazione_urb].copy()
target_lat_urb = obs_urb['Lat'].iloc[0]
target_lon_urb = obs_urb['Lon'].iloc[0]
obs_urb_var_sel = obs_urb[var_name_in_obs][start_date:end_date]

# --- Stazione rurale ---
obs_rur= obs_ds[obs_ds['Stazione'] == stazione_rur].copy()
target_lat_rur = obs_rur['Lat'].iloc[0]
target_lon_rur = obs_rur['Lon'].iloc[0]
obs_rur_var_sel = obs_rur[var_name_in_obs][start_date:end_date]



# Media oraria
obs_urb_var_hourly = obs_urb_var_sel.resample("h").mean()
obs_rur_var_hourly = obs_rur_var_sel.resample("h").mean()
common_index_hourly = obs_urb_var_hourly.index.intersection(obs_rur_var_hourly.index)

# Intersezione comune e conversione a °C
obs_urb_hourly_celsius = obs_urb_var_hourly.loc[common_index_hourly] - 273.15
obs_rur_hourly_celsius = obs_rur_var_hourly.loc[common_index_hourly] - 273.15

# Calcolo UHI osservazioni 
obs_UHI_hourly = obs_urb_hourly_celsius - obs_rur_hourly_celsius

# ---------------------------------------------------------------------
# Plot 
# ---------------------------------------------------------------------
start = datetime(2025, 6, 28, 12, 0)
end   = datetime(2025, 6, 30, 12, 0)
plot_series(
    common_index, obs_rur_var_sel, obs_urb_var_sel,
    stazione_urb, stazione_rur,
    start, end, mode="absolute"
)
"""




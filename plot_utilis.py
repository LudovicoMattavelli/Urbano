#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 Urban Plotting Utilities
============================================================

Description
-----------
Raccolta di funzioni per visualizzare gli efetti urbani partendo da dati grib.  
#I dati vengono plottati come punti (centri dei triangoli).  
#Per la visualizzazione a triangoli si veda il codice di Zonda su GitHub.

Functions
---------
- mappa_dominant_call : Plotta la n-esima classe dominante sull'Emilia Romagna
History
-------
- Created     : 2026-02-11 09:07
- Last Mod.   : 
- Last Check  : -> Tutto funziona correttamente!

Author
------
- lmattavelli@arpae.it
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from PIL import Image
from mpl_toolkits.axes_grid1 import make_axes_locatable

# ===============================
# 
# ===============================
f_base = 19
f_title = f_base + 2
f_assi = f_base - 2
f_ticks = f_base - 2# was -4
imm_a = 12
imm_b = 6
    

def plot_map_model(model_var, experiment_name, time_step, var_name, var_units,
                   extent, cmap, norm, regioni, comune, 
                   resolution='2km', run_date=None,
                   figsize=(imm_a, imm_b), title_fontsize=f_title):
    """
    Grafica la distribuzione spaziale di una variabile da file GRIB.
    
    Parameters
    ----------
    model_var : xarray.DataArray
        Variabile del modello da plottare
    model_name : str
        Nome del modello (es. 'ICON', 'COSMO')
    time_step : int
        Step temporale della previsione
    var_name : str
        Nome della variabile per il plot
    var_units : str
        Unità di misura
    extent : list[float]
        Estensione [lon_min, lon_max, lat_min, lat_max]
    color_var : list
        Lista di colori per la colormap
    bars_var : list[float]
        Boundaries per la normalizzazione
    regioni : geopandas.GeoDataFrame
        Shapefile delle regioni
    comune_shape : geopandas.GeoDataFrame, optional
        Shapefile dei comuni
    figsize : tuple, optional
        Dimensioni figura (larghezza, altezza)
    title_fontsize : int, optional
        Dimensione font del titolo
    run_date : str, optional
        Data/ora di run del modello (formato YYYYMMDDHH)
    resolution : str, optional
        Risoluzione del modello
    
    Returns
    -------
    fig, ax : matplotlib figure e axes
        Oggetti matplotlib per ulteriori personalizzazioni
    """ 
    # Proiezione e figura
    projPC = ccrs.PlateCarree()
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=projPC)
    ax.set_extent(extent, crs=projPC)
    
    # Plot della variabile
    plot = model_var.plot(
        ax=ax,
        cmap=cmap,
        norm=norm,
        transform=projPC,
        alpha=0.9,
        add_colorbar=True,
        cbar_kwargs={
            "shrink": 0.5, # was 0.6
            "label": f"{var_name} [{var_units}]",
            "orientation": "vertical",
            "pad": 0.02,
            "aspect": 16 ,#15
            "format": "%.1f"
        }
    )
    # Increase label size
    plot.colorbar.set_label(f"{var_name} [{var_units}]", fontsize=f_ticks)

    # Increase tick size
    plot.colorbar.ax.tick_params(labelsize=f_ticks)
    # Aggiungi confini regionali
    # Aggiungi i confini delle regioni
    if regioni is not False:
        ax.add_geometries(
            regioni.geometry,
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=0.5
        )
    if comune is not False:
        ax.add_geometries(
            comune.geometry,
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=0.5
        )
    # Elementi geografici
    ax.coastlines(resolution="10m")
    # Aggiungi gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    # Dimensione font delle coordinate
    gl.xlabel_style = {'size': f_ticks }
    gl.ylabel_style = {'size': f_ticks}
   # gl.left_labels= False
    # Tolgo labels superiori e a sinistra
    gl.top_labels = False
    gl.right_labels = False
    
    # Titolo dinamico
    title = f"{experiment_name} \n Run {run_date} \n {var_name} - Hour {time_step}"
    #if run_date:
       # title += f" - Run {run_date}"
    if resolution:
        title += f" - {resolution}"
    ax.set_title(title, fontsize=f_title, fontweight="bold")
    
    fig.tight_layout()
    
    return fig, ax

def plot_map_model_with_wind(model_var, u_var, v_var, z_var, experiment_name, time_step, var_name, var_units,
                   extent, cmap, norm, regioni, comune, 
                   resolution='2km', run_date=None,
                   figsize=(imm_a, imm_b), title_fontsize=14):
    """
    Grafica la distribuzione spaziale di una variabile da file GRIB.
    
    Parameters
    ----------
    model_var : xarray.DataArray
        Variabile del modello da plottare
    model_name : str
        Nome del modello (es. 'ICON', 'COSMO')
    time_step : int
        Step temporale della previsione
    var_name : str
        Nome della variabile per il plot
    var_units : str
        Unità di misura
    extent : list[float]
        Estensione [lon_min, lon_max, lat_min, lat_max]
    color_var : list
        Lista di colori per la colormap
    bars_var : list[float]
        Boundaries per la normalizzazione
    regioni : geopandas.GeoDataFrame
        Shapefile delle regioni
    comune_shape : geopandas.GeoDataFrame, optional
        Shapefile dei comuni
    figsize : tuple, optional
        Dimensioni figura (larghezza, altezza)
    title_fontsize : int, optional
        Dimensione font del titolo
    run_date : str, optional
        Data/ora di run del modello (formato YYYYMMDDHH)
    resolution : str, optional
        Risoluzione del modello
    
    Returns
    -------
    fig, ax : matplotlib figure e axes
        Oggetti matplotlib per ulteriori personalizzazioni
    """ 
    # Proiezione e figura
    projPC = ccrs.PlateCarree()
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=projPC)
    ax.set_extent(extent, crs=projPC)
    
    # Plot della variabile
    plot = model_var.plot(
        ax=ax,
        cmap=cmap,
        norm=norm,
        transform=projPC,
        alpha=0.9,
        add_colorbar=True,
        cbar_kwargs={
            "shrink": 0.5, # was 0.6
            "label": f"{var_name} [{var_units}]",
            "orientation": "vertical",
            "pad": 0.02,
            "aspect": 16 ,#15
            "format": "%.2d"
        }
    )
    # Barbe del vento (u10m, v10m già definiti a monte)
    lons = u_var.longitude.values
    lats = u_var.latitude.values
    u_vals = u_var.values
    v_vals = v_var.values
    lons2d, lats2d = np.meshgrid(lons, lats)  # entrambi (785, 789)
    # Ogni quanto plotto il vento
    step_wind = 5
    ax.barbs(
        lons2d[::step_wind, ::step_wind],
        lats2d[::step_wind, ::step_wind],
        u_vals[::step_wind, ::step_wind],
        v_vals[::step_wind, ::step_wind],
        transform=projPC,
        length=5,
        linewidth=0.8,
        color="navy",
        alpha=0.85,
        zorder=4,
        sizes=dict(emptybarb=0.15, spacing=0.2, height=0.4),
        barb_increments=dict(half=2.5, full=5, flag=25),
    )
    z_step = 20  # ogni 4 dam (standard operativo)
    z_levels = np.arange(
        np.floor(z_var.min() / z_step) * z_step,
        np.ceil(z_var.max() / z_step) * z_step + z_step,
        z_step
    )
    cs = ax.contour(
        lons,lats, z_var,
        levels=z_levels,
        colors="black",
        linewidths=1.4,
        transform=ccrs.PlateCarree(),
        zorder=2
    )
    # Linee ogni 8 dam più spesse
    cs_thick = ax.contour(
        lons,lats, z_var,
        levels=z_levels[::8],  # ogni 8 dam
        colors="black",
        linewidths=2.2,
        transform=ccrs.PlateCarree(),
        zorder=2
    )
    ax.clabel(cs_thick, fmt="%d", fontsize=9, inline=True, inline_spacing=5)
    # Increase label size
    plot.colorbar.set_label(f"{var_name} [{var_units}]", fontsize=f_ticks)

    # Increase tick size
    plot.colorbar.ax.tick_params(labelsize=f_ticks)
    # Aggiungi confini regionali
    # Aggiungi i confini delle regioni
    if regioni is not False:
        ax.add_geometries(
            regioni.geometry,
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=0.5
        )
    if comune is not False:
        ax.add_geometries(
            comune.geometry,
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=0.5
        )
    # Elementi geografici
    ax.coastlines(resolution="10m")
    # Aggiungi gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    # Dimensione font delle coordinate
    gl.xlabel_style = {'size': f_ticks }
    gl.ylabel_style = {'size': f_ticks}
   # gl.left_labels= False
    # Tolgo labels superiori e a sinistra
    gl.top_labels = False
    gl.right_labels = False
    
    # Titolo dinamico
    title = f"{experiment_name} \n {var_name} - Run {run_date} - Step {time_step}"
    if run_date:
        title += f" - Run {run_date}"
    if resolution:
        title += f" - {resolution}"
    ax.set_title(title, fontsize=title_fontsize, fontweight="bold")
    
    fig.tight_layout()
    
    return fig, ax

def plot_map_model_gridpoints(model_var, experiment_name, time_step, var_name, var_units,
                   extent, cmap, norm, regioni, comune_shape=None, 
                   resolution='2km', run_date=None, also_plot_target_points=False, target_points_list=None,
                   figsize=(12, 8), title_fontsize=14):
    """
    Questa funzione permette di plottare i punti griglia del dataset. 
    La dimesnione dei pallini va adattata a seconda della dimensione del dominio.
    È possibile plottare anche dei punti target, evidenziandoli tramite cerchietti.

    Parameters
    ----------
    model_var : TYPE
        DESCRIPTION.
    experiment_name : TYPE
        DESCRIPTION.
    time_step : TYPE
        DESCRIPTION.
    var_name : TYPE
        DESCRIPTION.
    var_units : TYPE
        DESCRIPTION.
    extent : TYPE
        DESCRIPTION.
    color_var : TYPE
        DESCRIPTION.
    bars_var : TYPE
        DESCRIPTION.
    regioni : TYPE
        DESCRIPTION.
    comune_shape : TYPE, optional
        DESCRIPTION. The default is None.
    resolution : TYPE, optional
        DESCRIPTION. The default is '2km'.
    run_date : TYPE, optional
        DESCRIPTION. The default is None.
    also_plot_target_points : TYPE, optional
        DESCRIPTION. The default is False.
    target_points_list : TYPE, optional
        DESCRIPTION. The default is None.
    figsize : TYPE, optional
        DESCRIPTION. The default is (12, 8).
    title_fontsize : TYPE, optional
        DESCRIPTION. The default is 14.

    Returns
    -------
    None.

    """
# Seleziona un singolo timestep (ad esempio il primo)
#data_snapshot = ref_var.isel(step=11)  # o scegli lo step che preferisci
    # Estrai le coordinate
    lats = model_var.latitude.values
    lons = model_var.longitude.values

    # Crea una mesh grid per avere tutte le combinazioni lat-lon
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Flatten degli array per lo scatter plot
    lon_flat = lon_grid.flatten()
    lat_flat = lat_grid.flatten()
    temp_flat = model_var.values.flatten()

    # Rimuovi eventuali valori NaN o invalidi (come -273.15)
    valid_mask = (temp_flat > -100) & (~np.isnan(temp_flat))
    lon_flat = lon_flat[valid_mask]
    lat_flat = lat_flat[valid_mask]
    temp_flat = temp_flat[valid_mask]

    # Creazione figura con Cartopy
    # Proiezione e figura
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent, crs=ccrs.PlateCarree()) #..

    # Aggiungi features geografiche
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)

    # Scatter plot con colormap
    scatter = ax.scatter(lon_flat, lat_flat, c=temp_flat, 
                         s=230,#220, 40  # dimensione punti
                         cmap=cmap, #RdYlBu_r',  # colormap (rosso=caldo, blu=freddo)
                         norm=norm,
                         edgecolors='none',
                         alpha=0.8,
                         transform=ccrs.PlateCarree())
    # I tuoi punti target
    if also_plot_target_points == True:
        colors = plt.cm.tab20b.colors  
        # Ciclo su tutti i punti della lista
        for i in range(len(target_points_list)):
            [lon_target, lat_target] = target_points_list[i]
            ax.plot(lon_target, lat_target, 'o', markersize=10, #8,18
                    transform=ccrs.PlateCarree(), label=f'Point {i}', 
                    markeredgecolor=colors[i], markeredgewidth=1.5, fillstyle='none')
        ax.legend(loc='upper right', fontsize=10)

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', 
                        pad=0.05, shrink=0.8)
    cbar.set_label('Temperature [°C]', fontsize=12, fontweight='bold')

    # Aggiungi gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    # Tolgo labels superiori e a sinistra
    gl.top_labels = False
    gl.right_labels = False
    
    # Titolo
    #valid_time = model_var.valid_time.values
    #ax.set_title(f'Temperature Grid Points - {np.datetime_as_string(valid_time, unit="h")}', 
     #            fontsize=14, fontweight='bold', pad=20)

    fig.tight_layout()
    
    return fig, ax

    print(f"Numero totale di punti: {len(lon_flat)}")
    print(f"Range temperatura: {temp_flat.min():.2f}°C - {temp_flat.max():.2f}°C")

def plot_timeseries_diff_2points(model_var,var_name,var_units,target_points_list):
    """
    Questa funzione serve per plottare le serie temporali di due punti griglia
    del modello e la loro differenza rispetto al primo
    La prima parte consiste in uno script che fa lo stesso lavoro di .sel(.., method=nearest)
    ma è preciso ed accurato.
    Dopo di che fa il plot delle variabili e della loro differenza

    Parameters
    ----------
    model_var : TYPE
        DESCRIPTION.
    var_name : TYPE
        DESCRIPTION.
    var_units : TYPE
        DESCRIPTION.
    target_1 : TYPE
        DESCRIPTION.
    target_2 : TYPE
        DESCRIPTION.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.
    ax : TYPE
        DESCRIPTION.

    """
    # Trova le coordinate più vicine disponibili
    lat_values = model_var.latitude.values
    lon_values = model_var.longitude.values

    # Per target_1
    [lon_target, lat_target] = target_points_list[0]
    idx_lat = np.argmin(np.abs(lat_values - lat_target))
    idx_lon= np.argmin(np.abs(lon_values - lon_target))
    actual_lat = lat_values[idx_lat]
    actual_lon = lon_values[idx_lon]
    ref_point = model_var.sel(latitude=actual_lat, longitude=actual_lon)
    
    # Creazione figura con due assi y
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Asse y sinistro - Serie temporali
    colors = plt.cm.tab20.colors
    #ax1.plot(ref_point["valid_time"], ref_point, 
     #        color=colors[0], linewidth=2, label=f"Point ref: {lon_target}°N, {lat_target}°E")
    ax1.set_xlabel("Tempo", fontsize=12, fontweight='bold')
    ax1.set_ylabel(f"{var_name} [{var_units}]", fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)

    # Asse y destro - Differenza
    ax2 = ax1.twinx()
    ax2.set_ylabel(f"Δ{var_name} [{var_units}]", fontsize=12, fontweight='bold', color=colors[0])
    ax2.tick_params(axis='y', labelcolor=colors[0])

    # Aggiungi una linea orizzontale a y=0 sull'asse destro per riferimento
    ax2.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    # Titolo
    ax1.set_title(f"Differenza in {var_name} tra due punti griglia specifici", 
                  fontsize=14, fontweight="bold", pad=20)
    
    for i in range(1,len(target_points_list)):
        
        [lon_target, lat_target] = target_points_list[i]
    # Per target_2
        idx_lat = np.argmin(np.abs(lat_values - lat_target))
        idx_lon = np.argmin(np.abs(lon_values - lon_target))
        actual_lat = lat_values[idx_lat]
        actual_lon = lon_values[idx_lon]

        print(f"Target {i}: [{lon_target}, {lat_target}]  -> Grid point: [{actual_lon:.3f}, {actual_lat:.3f}]")

    # Seleziona i punti esatti
        con_point = model_var.sel(latitude=actual_lat, longitude=actual_lon)
        #Calcolo differenza
        diff = con_point - ref_point
        # Verifica che siano diversi
        print(f"\nDifferenza media: {diff.mean().values:.3f}°C")  
        #ax1.plot(con_point["valid_time"], con_point, 
         #        color=colors[i+1], linewidth=2, label=f"Point {i}: {lon_target}°N, {lat_target}°E")

        ax2.plot(con_point["valid_time"], diff, 
                 color=colors[i+1], linewidth=2, linestyle='--', 
                 label=f"Δ(Point {i} - Point ref)")

    # Formattazione asse x per le date
    #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Leggende combinate
   # lines1, labels1 = ax1.get_legend_handles_labels()
   # lines2, labels2 = ax2.get_legend_handles_labels()
   # ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', framealpha=0.9, fontsize=10)

    # Layout e visualizzazione
    fig.tight_layout()
    # plt.savefig(f"Immagini/UHI_effect/Temperatura_comparison_{start}.png", dpi=300, bbox_inches='tight')
    return fig, ax1, ax2

def create_video_from_imagesSeries(repository,nome_file_1_part,var_ini,var_fin,nome_file_2_part,fps=1.2):

    from matplotlib.animation import FFMpegWriter
    from PIL import Image

    fig, ax = plt.subplots(figsize=(10, 8))
    writer = FFMpegWriter(fps=fps)

    output_video = f"{repository}/{nome_file_1_part}_{var_ini}_{nome_file_2_part}_anim.mp4"
    with writer.saving(fig, output_video, dpi=100):
        for alpha in range(var_ini, var_fin + 1):
            img_path = f"{repository}/{nome_file_1_part}_{alpha}_{nome_file_2_part}.png"
            img = Image.open(img_path)
            ax.clear()
            ax.imshow(img)
            ax.axis('off')
            writer.grab_frame()
            print(f"{alpha}")


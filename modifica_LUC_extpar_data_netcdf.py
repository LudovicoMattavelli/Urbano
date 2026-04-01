#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 14:59:31 2026

@author: lmattavelli
"""

import xarray as xr
import numpy as np
import matplotlib as plt
import cartopy.crs as ccrs
# 
# ===============================
f_base = 19
f_title = f_base + 2
f_assi = f_base - 2
f_ticks = f_base - 2# was -4
imm_a = 12
imm_b=6

Data_dir='/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Data_supporto/Urbano'
Domain_name='Nest500_from_OPE2km_to_EM500m_GLBC_v1'
Domain_number='DOM01'
grib_file=f'{Data_dir}/{Domain_name}_{Domain_number}_external_parameter.nc'
extent_mask = [11.22, 11.44, 44.42, 44.56]  # [lon_min, lon_max, lat_min, lat_max]

ds = xr.open_dataset(grib_file, engine="netcdf4")
var = ds['LU_CLASS_FRACTION']  # [nclass_lu, lat, lon]


# Coordinate in gradi (da radianti)
lon_deg = np.degrees(ds['clon'].values)  # (cell,)
lat_deg = np.degrees(ds['clat'].values)  # (cell,)

# --- Maschera geografica ---
# True per le celle DENTRO il rettangolo intorno a Bologna
inside_bbox = (
    (lon_deg >= extent_mask[0]) & (lon_deg <= extent_mask[1]) &
    (lat_deg >= extent_mask[2]) & (lat_deg <= extent_mask[3])
)  # shape: (cell,) booleano
outside_bbox = ~inside_bbox  # celle FUORI dalla zona di Bologna

print(f"Celle dentro bbox:  {inside_bbox.sum()}")
print(f"Celle fuori bbox:   {outside_bbox.sum()}")

# --- Modifica LU_CLASS_FRACTION ---
# lu ha shape (nclass_lu=23, cell=267600)
# La classe 19 corrisponde all'indice 18 (0-based!) oppure 19 (1-based, dipende dalla convenzione)
# Verifica quale convenzione usa il file:
lu = ds['LU_CLASS_FRACTION'].values.copy()  # copia per non modificare l'originale in-place

# Controlliamo se l'indice è 0-based o 1-based guardando i valori
# Se nclass_lu va da 1 a 23 -> classe 19 è indice 18  # ASSUNZIONE DA VERIFICARE!
# Dal print del dataset, nclass_lu è una dimensione senza coordinate -> assumiamo 0-based
CLASS_OLD = 18  # indice 0-based per la classe 19 (ARTIFICIAL AREAS)
CLASS_NEW = 3  # indice 0-based per la classe 20 (BARE AREAS) classe 4 (mosaic vegetation (50-70%) - cropland (20-50%))

# Per ogni cella FUORI dalla bbox:
# - azzeriamo la frazione della classe 19
# - aggiungiamo quel valore alla classe 14 (conservazione della somma = 1)
fraction_OLD_outside = lu[CLASS_OLD, outside_bbox].copy()  # salviamo le frazioni da spostare

lu[CLASS_NEW, outside_bbox] += fraction_OLD_outside  # aggiungiamo alla classe 14
lu[CLASS_OLD, outside_bbox]  = 0.0                  # azzeriamo la classe 19

# Verifica: la somma delle frazioni per ogni cella dovrebbe rimanere ~1
# (o invariata rispetto a prima)
col_sum_before = ds['LU_CLASS_FRACTION'].values.sum(axis=0)  # somma originale per cella
col_sum_after  = lu.sum(axis=0)                               # somma dopo modifica
print(f"\nSomma frazioni (prima): min={col_sum_before.min():.4f}, max={col_sum_before.max():.4f}")
print(f"Somma frazioni (dopo):  min={col_sum_after.min():.4f},  max={col_sum_after.max():.4f}")

# --- Ricostruzione del dataset modificato ---
# Sostituiamo la variabile LU_CLASS_FRACTION con quella modificata,
# mantenendo tutti gli altri attributi e variabili intatti
lu_new = xr.DataArray(
    lu,
    dims=ds['LU_CLASS_FRACTION'].dims,
    attrs=ds['LU_CLASS_FRACTION'].attrs,
    name='LU_CLASS_FRACTION'
)

ds_modified = ds.assign(LU_CLASS_FRACTION=lu_new)

# --- Salvataggio ---
output_file = f'{Data_dir}/{Domain_name}_{Domain_number}_external_parameter_modified_2.nc'
ds_modified.to_netcdf(output_file)
print(f"\nFile salvato: {output_file}")
def plot_lu_class_fraction_scatter(ds, class_index, extent, title_prefix="", s=0.5, comune=False, cmap='YlOrRd',figsize=(imm_a, imm_b)):
    """
    Plotta la LU_CLASS_FRACTION come scatter plot (un punto per cella).
    Le celle con frazione = 0 non vengono plottate.

    Parametri
    ----------
    ds           : xarray.Dataset con LU_CLASS_FRACTION, clon, clat
    class_index  : int, indice 0-based della classe (es. 18 per classe 19)
    title_prefix : str, prefisso opzionale per il titolo
    s            : float, dimensione dei punti (default piccolo per griglie dense)
    cmap         : str, colormap matplotlib
    """
    lon_deg = np.degrees(ds['clon'].values)
    lat_deg = np.degrees(ds['clat'].values)
    lu      = ds['LU_CLASS_FRACTION'].values  # (nclass_lu, cell)

    frac = lu[class_index, :]   # (cell,)
    mask = frac > 0             # solo celle con questa tile attiva

    if mask.sum() == 0:
        print(f"Nessuna cella attiva per la classe {class_index+1}, skip.")
        return
    # Proiezione e figura
    projPC = ccrs.PlateCarree()
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=projPC)
    ax.set_extent(extent, crs=projPC)

    sc = ax.scatter(
        lon_deg[mask],
        lat_deg[mask],
        c=frac[mask],
        s=s,
        cmap=cmap,
        vmin=0, vmax=1,
        transform=ccrs.PlateCarree()
    )
    if comune is not False:
        ax.add_geometries(
            comune.geometry,
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=0.5
        )
    plt.colorbar(sc, ax=ax, label='Frazione [-]')

    ax.set_xlabel("Longitudine [°]")
    ax.set_ylabel("Latitudine [°]")

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
    title =f"{title_prefix} Classe LU {class_index+1} a 2km —  {mask.sum()} celle attive"
   # if run_date:
   #     title += f" - Run {run_date}"
    ax.set_title(title, fontsize=f_title, fontweight="bold")
    
    fig.tight_layout()
    
    return fig, ax
import matplotlib.pyplot as plt
extent=extent_mask
extent = [8.6,13.2,43.43,45.43]
import geopandas as gpd
comuni = gpd.read_file('/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Com01012025_WGS84.shp')
comune = comuni[comuni['COMUNE'] == 'Bologna']
comune = comune.to_crs(epsg=4326)
fig,ax = plot_lu_class_fraction_scatter(ds, class_index=CLASS_OLD, extent=extent, title_prefix="PRIMA —", s=8, comune=comune)
plt.savefig(f'../Immagini_supporto/Urbano/Immagini_caso_20230731/Experiment_GLBCModif1/LUC_pre_modif_2km.png', dpi=300, bbox_inches='tight')
fig,ax=plot_lu_class_fraction_scatter(ds_modified, class_index=CLASS_OLD, extent=extent, title_prefix="DOPO —", s=8, comune=comune)
plt.savefig(f'../Immagini_supporto/Urbano/Immagini_caso_20230731/Experiment_GLBCModif1/LUC_post_modif_2km.png', dpi=300, bbox_inches='tight')
#plot_lu_class_fraction_scatter(ds_modified, class_index=CLASS_OLD, extent=extent, title_prefix="DOPO  —", s=20)

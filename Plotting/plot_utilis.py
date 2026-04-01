# ─────────────────────────────────────────────────────────────
# plot_utilis.py
# Funzione di plotting per variabili meteorologiche su mappa.
# ─────────────────────────────────────────────────────────────
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
 
 
# ══════════════════════════════════════════════════════════════
# COSTANTI GRAFICHE
# Modifica questi valori per cambiare l'aspetto di tutti i plot
# ══════════════════════════════════════════════════════════════
 
FONT_BASE   = 19
FONT_TITLE  = FONT_BASE + 2   # 21 — titolo
FONT_LABEL  = FONT_BASE - 2   # 17 — etichette assi e colorbar
FONT_TICKS  = FONT_BASE - 2   # 17 — tick assi e colorbar
 
FIG_WIDTH   = 12
FIG_HEIGHT  = 6
 
COLORBAR_SHRINK      = 0.5
COLORBAR_ASPECT      = 16
COLORBAR_PAD         = 0.02
COLORBAR_ORIENTATION = "vertical"
COLORBAR_FORMAT      = "%.1f"
 
GRIDLINE_LINEWIDTH  = 0.5
GRIDLINE_COLOR      = "gray"
GRIDLINE_ALPHA      = 0.5
GRIDLINE_LINESTYLE  = "--"
 
REGION_EDGECOLOR  = "black"
REGION_LINEWIDTH  = 0.5
COMUNE_EDGECOLOR  = "black"
COMUNE_LINEWIDTH  = 0.5
 
COASTLINE_RESOLUTION = "10m"
PLOT_ALPHA           = 0.9
 
 
# ══════════════════════════════════════════════════════════════
# FUNZIONE PRINCIPALE
# ══════════════════════════════════════════════════════════════
 
def plot_map_model(
    model_var,
    experiment_name,
    time_step,
    var_name,
    var_units,
    extent,
    cmap,
    norm,
    regioni,
    comune,
    resolution = "2km",
    run_date   = None,
    figsize    = (FIG_WIDTH, FIG_HEIGHT),
):
    """
    Grafica la distribuzione spaziale di una variabile da file GRIB.
 
    Parameters
    ----------
    model_var       : xr.DataArray      variabile del modello da plottare
    experiment_name : str               nome dell'esperimento (es. 'icon_2I_fcruc18')
    time_step       : int | str         step temporale o intervallo (es. 3 oppure '3:6 (3h)')
    var_name        : str               nome della variabile
    var_units       : str               unità di misura
    extent          : list[float]       [lon_min, lon_max, lat_min, lat_max]
    cmap            : ListedColormap    colormap matplotlib
    norm            : BoundaryNorm      normalizzazione matplotlib
    regioni         : GeoDataFrame | False   shapefile regioni (False = non plottare)
    comune          : GeoDataFrame | False   shapefile comune  (False = non plottare)
    resolution      : str, optional     risoluzione del modello (default '2km')
    run_date        : str, optional     data/ora run formato YYYYMMDDHH
    figsize         : tuple, optional   dimensioni figura (larghezza, altezza)
 
    Returns
    -------
    fig, ax : Figure, Axes   oggetti matplotlib per ulteriori personalizzazioni
    """
 
    # ── proiezione e figura ───────────────────────────────────
    proj = ccrs.PlateCarree()
    fig  = plt.figure(figsize=figsize)
    ax   = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
 
    # ── plot variabile ────────────────────────────────────────
    plot = model_var.plot(
        ax        = ax,
        cmap      = cmap,
        norm      = norm,
        transform = proj,
        alpha     = PLOT_ALPHA,
        add_colorbar = True,
        cbar_kwargs  = {
            "shrink":      COLORBAR_SHRINK,
            "label":       f"{var_name} [{var_units}]",
            "orientation": COLORBAR_ORIENTATION,
            "pad":         COLORBAR_PAD,
            "aspect":      COLORBAR_ASPECT,
            "format":      COLORBAR_FORMAT,
        },
    )
 
    # ── colorbar: font etichetta e tick ───────────────────────
    plot.colorbar.set_label(f"{var_name} [{var_units}]", fontsize=FONT_LABEL)
    plot.colorbar.ax.tick_params(labelsize=FONT_TICKS)
 
    # ── shapefile regioni ─────────────────────────────────────
    if regioni is not False:
        ax.add_geometries(
            regioni.geometry,
            crs       = proj,
            facecolor = "none",
            edgecolor = REGION_EDGECOLOR,
            linewidth = REGION_LINEWIDTH,
        )
 
    # ── shapefile comune ──────────────────────────────────────
    if comune is not False:
        ax.add_geometries(
            comune.geometry,
            crs       = proj,
            facecolor = "none",
            edgecolor = COMUNE_EDGECOLOR,
            linewidth = COMUNE_LINEWIDTH,
        )
 
    # ── elementi geografici ───────────────────────────────────
    ax.coastlines(resolution=COASTLINE_RESOLUTION)
 
    # ── gridlines ────────────────────────────────────────────
    gl = ax.gridlines(
        draw_labels = True,
        linewidth   = GRIDLINE_LINEWIDTH,
        color       = GRIDLINE_COLOR,
        alpha       = GRIDLINE_ALPHA,
        linestyle   = GRIDLINE_LINESTYLE,
    )
    gl.xlabel_style  = {"size": FONT_TICKS}
    gl.ylabel_style  = {"size": FONT_TICKS}
    gl.top_labels    = False
    gl.right_labels  = False
 
    # ── titolo ────────────────────────────────────────────────
    title = f"{experiment_name}\nRun {run_date}\n{var_name} — Hour {time_step}"
    if resolution:
        title += f" — {resolution}"
    ax.set_title(title, fontsize=FONT_TITLE, fontweight="bold")
 
    fig.tight_layout()
 
    return fig, ax

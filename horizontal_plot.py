# ─────────────────────────────────────────────────────────────
# meteo_plot.py
# ─────────────────────────────────────────────────────────────
from __future__ import annotations
from dataclasses import dataclass, field
from matplotlib.colors import ListedColormap, BoundaryNorm
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt

from plot_utilis import plot_map_model


# ══════════════════════════════════════════════════════════════
# 1. CONFIGURAZIONE VARIABILI
# ══════════════════════════════════════════════════════════════

@dataclass
class VariableConfig:
    """
    Configurazione per una variabile meteorologica.

    Attributi
    ---------
    name         : identificatore breve (uguale alla chiave in CONFIGS)
    colors       : lista di colori esadecimali per la colormap
    bars         : livelli per BoundaryNorm
    mode         : 'instant' (default) oppure 'diff' (variabile cumulata)
    steps_cumul  : se mode='diff', lista dei passi di accumulo da plottare
                   es. [3, 12] → produce un plot per accumulo 3h e uno per 12h
    bias         : offset numerico applicato dopo la lettura (es. -273.15 per K→°C)
    units_override: sovrascrive l'unità letta dal GRIB
    """
    name          : str
    colors        : list
    bars          : list
    mode          : str  = 'instant'
    steps_cumul   : list = field(default_factory=list)
    bias          : float = 0.0
    units_override: str   = ""

    def make_cmap_norm(self):
        cmap = ListedColormap(self.colors)
        norm = BoundaryNorm(boundaries=self.bars, ncolors=cmap.N)
        return cmap, norm


class MeteoVariables:
    """Registro di tutte le configurazioni delle variabili meteorologiche."""

    CONFIGS: dict[str, VariableConfig] = {

        'tp': VariableConfig(
            name='tp',
            colors=['#d5d5d5', '#93ffff', '#00ffff', '#7590ff', '#2958ff',
                    '#5f00ff', '#007473', '#f5ff00', '#ff7400', '#ff0000',
                    '#ff00fc', '#b300ef', '#93007f'],
            bars=[0.5, 1, 2, 5, 10, 20, 30, 50, 70, 100, 150, 200, 300, 500],
            mode='diff',
            steps_cumul=[1,3, 12],   # produce diversi plot: accumulo 3h, accumulo 12h,...
        ),

        'twater': VariableConfig(
            name='twater',
            colors=['#2f00a2', '#5100ff', '#5d00ff', '#7458ff', '#00ffff',
                    '#f6ff00', '#ffe435', '#ff1800', '#7a1b11', '#c3ff00'],
            bars=[5, 10, 15, 20, 25, 30, 35, 40, 45, 55, 65],
        ),

        'cape_ml': VariableConfig(
            name='cape_ml',
            colors=['#ff0000', '#d10400', '#ff9000', '#fee700', '#c3ff00',
                    '#31ff21', '#00ff2c', '#00ff2d', '#00ff55', '#00ff9a',
                    '#00ffe0', '#00ddff', '#007cff', '#4b00ff', '#5500ff'],
            bars=[100, 200, 300, 500, 750, 1000, 1250, 1500, 1750,
                  2000, 2250, 2500, 2750, 3000, 3500, 4000],
        ),

        '2t': VariableConfig( #da sistemare
            name='t2m',
            colors=['#0000ff', '#0055ff', '#00aaff', '#00ffff', '#55ff00',
                    '#aaff00', '#ffff00', '#ffaa00', '#ff5500', '#ff0000'],
            bars=[-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40],
            bias=-273.15,
            units_override='°C',
        ),
    }

    @classmethod
    def get(cls, name: str) -> VariableConfig:
        if name not in cls.CONFIGS:
            raise KeyError(
                f"Variabile '{name}' non presente in MeteoVariables.CONFIGS.\n"
                f"Disponibili: {list(cls.CONFIGS.keys())}"
            )
        return cls.CONFIGS[name]


# ══════════════════════════════════════════════════════════════
# 2. PREPROCESSING
# ══════════════════════════════════════════════════════════════

def read_first_var(path: str):
    """Apre un file GRIB con cfgrib e restituisce (DataArray, var_name, units)."""
    ds = xr.open_dataset(path, engine="cfgrib")
    var_name = list(ds.data_vars)[0]
    da = ds[var_name]
    return da, var_name, str(da.units)


def preprocessing(grib_path: str, cfg: VariableConfig):
    """
    Legge il GRIB e applica bias e override unità dalla configurazione.

    Returns
    -------
    data      : xr.DataArray  (tutti i timestep)
    var_name  : str
    var_units : str
    """
    data, var_name, var_units = read_first_var(grib_path)

    if cfg.bias != 0.0:
        data = data + cfg.bias

    if cfg.units_override:
        var_units = cfg.units_override

    return data, var_name, var_units


# ══════════════════════════════════════════════════════════════
# 3. PLOTTING
# ══════════════════════════════════════════════════════════════

def plotting_timesteps(
    data          : xr.DataArray,
    cfg           : VariableConfig,
    var_name      : str,
    var_units     : str,
    experiment_name: str,
    step_ini      : int,
    step_fin      : int,
    oraini        : int,
    extent        : list,
    selected_domain: str,
    regioni,
    comune,
    resolution    : str,
    run_label     : str,
    out_dir_imm       : Path | None = None,
):
    """
    Itera sui timestep e produce un plot per ciascuno.

    Per variabili 'instant': un plot per timestep.
    Per variabili 'diff':    per ogni timestep, un plot per ogni passo
                             di accumulo definito in cfg.steps_cumul.
    """
    cmap, norm = cfg.make_cmap_norm()

    for time_step in range(step_ini, step_fin + 1):

        if cfg.mode == 'diff':
            # ── un plot per ogni passo di accumulo (es. 3h e 12h) ──────────
            for acc_step in cfg.steps_cumul:
                timestep_start = time_step - acc_step
                if timestep_start < 0:
                    print("Non hai dati sufficienti per questo accumulo, quindi lo salto")
                    continue

                alpha = data[time_step] - data[timestep_start]
                oraini_val = oraini + step_ini
                hour = f"{timestep_start + oraini_val}:{time_step + oraini_val} ({acc_step}h)"

                fig, ax = plot_map_model(
                    alpha, experiment_name, hour,
                    var_name, var_units,
                    extent, cmap, norm,
                    regioni, comune,
                    resolution, run_label,
                )

        else:
            # ── modalità instant: un plot per timestep ──────────────────────
            alpha = data[time_step]
            hour  = time_step + oraini + step_ini

            fig, ax = plot_map_model(
                alpha, experiment_name, hour,
                var_name, var_units,
                extent, cmap, norm,
                regioni, comune,
                resolution, run_label,
            )
         
        imm_path = (
           #f"{dir_imm}/"
            f"plot_map_model{var_shortName}_{experiment_name}_{time_step}_{selected_domain}"
            f"_{dataini}{oraini}+{step_ini}_{step_fin}.png"
        )
        plt.savefig(out_dir_imm/imm_path, dpi=300, bbox_inches='tight')
        plt.show()


# ══════════════════════════════════════════════════════════════
# 4. MAIN  –  definisci qui gli esperimenti da girare
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from pathlib import Path
    
    # ── DEFINISCO EXPERIMENTS ─────────────────────────────────
    VARIABLES = ["twater", "cape_ml"]   # <-- lista variabili, uguale per tutti gli esperimenti

    # Ogni dict rappresenta un esperimento. Aggiungi/rimuovi righe liberamente.
    EXPERIMENTS = [
        dict(dataini="20240701", oraini="18", step_ini= 0, step_fin= 6, experiment="icon_2I_fcruc", resolution="2km"),
       # dict(dataini="20240701", oraini="00", step_ini= 0, step_fin= 6, experiment="icon_2I_fcruc", resolution="2km"),
        #dict(dataini="20240702", oraini="06", step_ini= 0, step_fin= 6, experiment="icon_2I_fcruc2", resolution="2km"),
    ]


    dir_base = "/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti"
    name_progetto = "Urbano"

    # Shapefile (caricati una sola volta)
    comuni  = gpd.read_file(
        '/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Com01012025_WGS84.shp'
    )
    comune_studied = "BOLOGNA"
    comune  = comuni[comuni['COMUNE'] == comune_studied].to_crs(epsg=4326)
    regioni = gpd.read_file(
        '/home/lmattavelli@ARPA.EMR.NET/Documenti/Progetti/Old_projects/GO1/Mappe/Reg01012025_WGS84.shp'
    ).to_crs(epsg=4326)

    # Domini disponibili
    DOMAINS = {
        "DOM03": [8.6,  13.2,  43.43, 45.43],
        "DOM04": [10.75, 11.89, 43.93, 44.99],
    }
    selected_domain = "DOM03"
    extent = DOMAINS[selected_domain]

    # ── loop esperimenti ──────────────────────────────────────
    for exp in EXPERIMENTS:
        dataini       = exp["dataini"]
        oraini        = exp["oraini"]
        step_ini      = exp["step_ini"]
        step_fin      = exp["step_fin"]
        experiment    = exp["experiment"]
        resolution    = exp["resolution"]

        experiment_name = f"{experiment}{oraini}"
        run_label       = f"{dataini}{oraini}"

        dir_files = (
            f"{dir_base}/Data_supporto/{name_progetto}/Data_g100/{dataini}/"
            f"getVarTimeseriesGrib_{dataini}{oraini}"
            f"+{step_ini:02d}_{step_fin:02d}"
        )
        
        dir_imm =  (
            f"{dir_base}/Immagini_supporto/{name_progetto}/"
            f"Immagini_caso_{dataini}/"
            f"{experiment_name}"
        ) 
        # crea la cartella output (non fa nulla se esiste già)
        out_dir_imm = Path(dir_imm)
        out_dir_imm.mkdir(exist_ok=True)
        for var_shortName in VARIABLES:          # <-- loop interno sulle variabili
            grib_path = (
                f"{dir_files}/"
                f"{experiment}_{var_shortName}_{dataini}{oraini}"
                f"+{step_ini:02d}_{step_fin:02d}.grib"
            )

            cfg = MeteoVariables.get(var_shortName)
            data, var_name, var_units = preprocessing(grib_path, cfg)

            print(f"\n── {experiment_name}  var={var_shortName}  run={run_label} ──")

            plotting_timesteps(
                data=data, cfg=cfg,
                var_name=var_name, var_units=var_units,
                experiment_name=experiment_name,
                step_ini=step_ini, step_fin=step_fin,
                oraini=int(oraini),
                extent=extent,
                selected_domain=selected_domain,
                regioni=regioni, comune=comune,
                resolution=resolution, run_label=run_label, out_dir_imm=out_dir_imm,
            )
        
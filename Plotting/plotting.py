# ─────────────────────────────────────────────────────────────
# plotting.py
# Loop sui timestep e generazione/salvataggio delle figure.
#
# Gestisce automaticamente due modalità:
#   'instant' → un plot per timestep
#   'diff'    → per ogni timestep, un plot per ogni passo di
#               accumulo definito in cfg.steps_cumul
# ─────────────────────────────────────────────────────────────
from __future__ import annotations
from pathlib import Path

import xarray as xr
import matplotlib.pyplot as plt

from config import VariableConfig
from plot_utilis import plot_map_model


def plotting_timesteps(
    data           : xr.DataArray,
    cfg            : VariableConfig,
    var_name       : str,
    var_units      : str,
    experiment_name: str,
    step_ini       : int,
    step_fin       : int,
    oraini         : int,
    extent         : list,
    selected_domain: str,
    regioni,
    comune,
    resolution     : str,
    run_label      : str,
    out_dir        : Path | None = None,
) -> None:
    """
    Itera sui timestep [step_ini, step_fin] e produce un plot per ciascuno.

    Modalità 'instant'
        Un plot per timestep: alpha = data[time_step]

    Modalità 'diff'
        Per ogni timestep, un plot per ogni passo in cfg.steps_cumul.
        alpha = data[time_step] - data[time_step - acc_step]
        I timestep per cui (time_step - acc_step) < 0 vengono saltati.

    Parameters
    ----------
    out_dir : se specificato, le figure vengono salvate come .png
              nella cartella indicata (oltre ad essere mostrate).
    """
    cmap, norm = cfg.make_cmap_norm()

    for time_step in range(step_ini, step_fin + 1):

        if cfg.mode == 'diff':
            # ── variabile cumulata: un plot per ogni passo di accumulo ───────
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
            # ── modalità instant: un plot per timestep ───────────────────────
            alpha = data[time_step]
            hour  = time_step + oraini + step_ini

            fig, ax = plot_map_model(
                alpha, experiment_name, hour,
                var_name, var_units,
                extent, cmap, norm,
                regioni, comune,
                resolution, run_label,
            )
            
        if out_dir:
            fname = (
                f"plot_map_model_{var_name}_{experiment_name}_{time_step}_{selected_domain}_{cfg.mode}.png"
            )
            fig.savefig(out_dir/fname, dpi=300, bbox_inches='tight')
            print(f"  Salvato: {out_dir / fname}")

        plt.show()

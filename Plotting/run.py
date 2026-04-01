# ─────────────────────────────────────────────────────────────
# run.py
# Legge la configurazione da config.yaml ed esegue il plotting
# per tutti gli esperimenti e le variabili definiti.
#
# Uso:
#   python run.py                        # usa config.yaml nella stessa cartella
#   python run.py --config altro.yaml    # usa un file yaml personalizzato
# ─────────────────────────────────────────────────────────────
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import yaml
import geopandas as gpd

from config import MeteoVariables
from preprocessing import preprocessing
from plotting import plotting_timesteps


# ══════════════════════════════════════════════════════════════
# LETTURA CONFIG
# ══════════════════════════════════════════════════════════════

def load_config(config_path: Path) -> dict:
    """Carica e valida il file config.yaml."""

    # ── esistenza file ────────────────────────────────────────
    #if not config_path.exists():
    #    print(f"[ERRORE] File di configurazione non trovato: {config_path}")
    #    print( "         Assicurati che config.yaml sia nella stessa cartella di run.py,")
    #    print( "         oppure specifica il percorso con --config /percorso/config.yaml")
    #    sys.exit(1)

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    # ── campi obbligatori ─────────────────────────────────────
    required = ["variables", "experiments", "step_ini", "step_fin",
                "resolution", "comune_studied", "selected_domain",
                "dir_base", "shp_comuni", "shp_regioni", "domains"]
    #missing = [k for k in required if k not in cfg]
    #if missing:
    #    print(f"[ERRORE] Campi mancanti in {config_path}: {missing}")
    #    sys.exit(1)

    # ── dominio selezionato esiste in domains ─────────────────
    if cfg["selected_domain"] not in cfg["domains"]:
        available = list(cfg["domains"].keys())
        print(f"[ERRORE] Dominio '{cfg['selected_domain']}' non trovato in config.yaml.")
        print(f"         Domini disponibili: {available}")
        sys.exit(1)

    # ── shapefile esistono ────────────────────────────────────
    for key in ("shp_comuni", "shp_regioni"):
        p = Path(cfg[key])
        if not p.exists():
            print(f"[ERRORE] Shapefile non trovato: {p}")
            print(f"         Controlla il campo '{key}' in config.yaml")
            sys.exit(1)

    return cfg


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def build_grib_path(dir_files: str, experiment: str, var: str,
                    dataini: str, oraini: str,
                    step_ini: int, step_fin: int) -> Path:
    fname = (
        f"{experiment}_{var}_{dataini}{oraini}"
        f"+{step_ini:02d}_{step_fin:02d}.grib"
    )
    return Path(dir_files) / fname


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main(config_path: Path) -> None:
    cfg = load_config(config_path)

    # ── parametri condivisi ───────────────────────────────────
    variables      = cfg["variables"]
    experiments    = cfg["experiments"]
    comune_studied = cfg["comune_studied"]
    dir_base       = cfg["dir_base"]
    extent         = cfg["domains"][cfg["selected_domain"]]
    selected_domain = cfg["selected_domain"]

    # ── shapefile (caricati una sola volta) ───────────────────
    comuni  = gpd.read_file(cfg["shp_comuni"])
    comune  = comuni[comuni["COMUNE"] == comune_studied].to_crs(epsg=4326)
    regioni = gpd.read_file(cfg["shp_regioni"]).to_crs(epsg=4326)

    # ── contatori per il riepilogo finale ─────────────────────
    n_ok   = 0
    n_skip = 0
    skipped: list[str] = []

    # ── loop esperimenti × variabili ─────────────────────────
    for exp in experiments:
        dataini    = exp["dataini"]
        oraini     = exp["oraini"]
        experiment = exp["experiment"]
        step_ini       = int(exp["step_ini"])
        step_fin       = int(exp["step_fin"])
        resolution     = exp["resolution"]

        experiment_name = f"{experiment}_{oraini}"
        run_label       = f"{dataini}{oraini}"

        out_dir = Path(dir_base) / f"{dir_base}/Immagini_supporto/"
        f"Immagini_caso_{dataini}/"
        f"{experiment_name}"
        out_dir.mkdir(exist_ok=True)

        dir_files = (
            f"{dir_base}/Data_supporto/Data_g100/{dataini}/"
            f"getVarTimeseriesGrib_{dataini}{oraini}"
            f"+{step_ini:02d}_{step_fin:02d}"
        )

        print(f"\n{'═'*60}")
        print(f"Esperimento : {experiment_name}")
        print(f"Run         : {run_label}")
        print(f"Output      : {out_dir}")
        print(f"{'═'*60}")

        for var_shortName in variables:

            grib_path = build_grib_path(
                dir_files, experiment, var_shortName,
                dataini, oraini, step_ini, step_fin,
            )

            # ── gestione file GRIB mancante ───────────────────
            if not grib_path.exists():
                msg = f"{experiment_name} | {var_shortName} → {grib_path}"
                print(f"  [SKIP] File GRIB non trovato: {grib_path}")
                skipped.append(msg)
                n_skip += 1
                continue

            print(f"\n  Variabile: {var_shortName}")

            var_cfg = MeteoVariables.get(var_shortName)
            data, var_name, var_units = preprocessing(str(grib_path), var_cfg)

            plotting_timesteps(
                data            = data,
                cfg             = var_cfg,
                var_name        = var_name,
                var_units       = var_units,
                experiment_name = experiment_name,
                step_ini        = step_ini,
                step_fin        = step_fin,
                oraini          = int(oraini),
                extent          = extent,
                selected_domain = selected_domain,
                regioni         = regioni,
                comune          = comune,
                resolution      = resolution,
                run_label       = run_label,
                out_dir         = out_dir,
            )
            n_ok += 1

    # ── riepilogo finale ──────────────────────────────────────
    print(f"\n{'═'*60}")
    print(f"COMPLETATO  →  {n_ok} variabili processate, {n_skip} saltate")
    if skipped:
        print("File GRIB non trovati:")
        for s in skipped:
            print(f"  • {s}")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Meteo plotting — legge la configurazione da un file YAML."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "config.yaml",
        help="Percorso al file di configurazione YAML (default: config.yaml)",
    )
    args = parser.parse_args()
    main(args.config)
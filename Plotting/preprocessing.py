# ─────────────────────────────────────────────────────────────
# preprocessing.py
# Lettura dei file GRIB e applicazione di correzioni
# (bias numerico, override unità) definite in VariableConfig.
# ─────────────────────────────────────────────────────────────
from __future__ import annotations
import xarray as xr

from config import VariableConfig


def read_first_var(path: str) -> tuple:
    """
    Apre un file GRIB con cfgrib e restituisce la prima variabile.

    Returns
    -------
    data     : xr.DataArray
    var_name : str   (nome della variabile nel dataset)
    units    : str   (unità lette dal GRIB)
    """
    ds = xr.open_dataset(path, engine="cfgrib")
    var_name = list(ds.data_vars)[0]
    da = ds[var_name]
    return da, var_name, str(da.units)


def preprocessing(grib_path: str, cfg: VariableConfig) -> tuple:
    """
    Legge il GRIB e applica le correzioni definite in VariableConfig.

    Correzioni applicate:
    - cfg.bias          → offset numerico (es. -273.15 per K → °C)
    - cfg.units_override → sovrascrive l'unità letta dal GRIB

    Parameters
    ----------
    grib_path : percorso completo al file .grib
    cfg       : VariableConfig della variabile da leggere

    Returns
    -------
    data      : xr.DataArray  (tutti i timestep, con bias applicato)
    var_name  : str
    var_units : str
    """
    data, var_name, var_units = read_first_var(grib_path)

    if cfg.bias != 0.0:
        data = data + cfg.bias

    if cfg.units_override:
        var_units = cfg.units_override

    return data, var_name, var_units

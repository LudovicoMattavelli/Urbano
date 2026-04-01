# ─────────────────────────────────────────────────────────────
# config.py
# Definizione delle variabili meteorologiche e delle loro
# configurazioni grafiche (colormap, livelli, modalità).
#
# Per aggiungere una nuova variabile:
#   1. Aggiungi una entry in MeteoVariables.CONFIGS
#   2. Definisci colors, bars e mode ('instant' o 'diff')
#   3. Se mode='diff', specifica steps_cumul
# ─────────────────────────────────────────────────────────────
from __future__ import annotations
from dataclasses import dataclass, field
from matplotlib.colors import ListedColormap, BoundaryNorm


@dataclass
class VariableConfig:
    """
    Configurazione grafica per una variabile meteorologica.

    Parametri
    ---------
    name          : identificatore breve (uguale alla chiave in CONFIGS)
    colors        : lista di colori esadecimali per la colormap
    bars          : livelli per BoundaryNorm (contour levels)
    mode          : 'instant' → valore istantaneo (default)
                    'diff'    → differenza tra step (variabile cumulata)
    steps_cumul   : [solo se mode='diff'] lista dei passi di accumulo da plottare
                    es. [3, 12] → produce un plot per acc. 3h e uno per 12h
    bias          : offset numerico applicato dopo la lettura (es. -273.15 per K→°C)
    units_override: sovrascrive l'unità letta dal GRIB (es. '°C')
    """
    name          : str
    colors        : list
    bars          : list
    mode          : str  = 'instant'
    steps_cumul   : list = field(default_factory=list)
    bias          : float = 0.0
    units_override: str   = ""

    def make_cmap_norm(self):
        """Restituisce (ListedColormap, BoundaryNorm) pronti per matplotlib."""
        cmap = ListedColormap(self.colors)
        norm = BoundaryNorm(boundaries=self.bars, ncolors=cmap.N)
        return cmap, norm


class MeteoVariables:
    """
    Registro centrale di tutte le variabili meteorologiche supportate.

    Uso
    ---
    cfg = MeteoVariables.get('tp')
    cmap, norm = cfg.make_cmap_norm()
    """

    CONFIGS: dict[str, VariableConfig] = {

        # ── precipitazione totale ────────────────────────────────────────────
        'tp': VariableConfig(
            name='tp',
            colors=['#d5d5d5', '#93ffff', '#00ffff', '#7590ff', '#2958ff',
                    '#5f00ff', '#007473', '#f5ff00', '#ff7400', '#ff0000',
                    '#ff00fc', '#b300ef', '#93007f'],
            bars=[0.5, 1, 2, 5, 10, 20, 30, 50, 70, 100, 150, 200, 300, 500],
            mode='diff',
            steps_cumul=[3, 12],
        ),

        # ── temperatura acqua ────────────────────────────────────────────────
        'twater': VariableConfig(
            name='twater',
            colors=['#2f00a2', '#5100ff', '#5d00ff', '#7458ff', '#00ffff',
                    '#f6ff00', '#ffe435', '#ff1800', '#7a1b11', '#c3ff00'],
            bars=[5, 10, 15, 20, 25, 30, 35, 40, 45, 55, 65],
        ),

        # ── CAPE mixed-layer ─────────────────────────────────────────────────
        'cape_ml': VariableConfig(
            name='cape_ml',
            colors=['#ff0000', '#d10400', '#ff9000', '#fee700', '#c3ff00',
                    '#31ff21', '#00ff2c', '#00ff2d', '#00ff55', '#00ff9a',
                    '#00ffe0', '#00ddff', '#007cff', '#4b00ff', '#5500ff'],
            bars=[100, 200, 300, 500, 750, 1000, 1250, 1500, 1750,
                  2000, 2250, 2500, 2750, 3000, 3500, 4000],
        ),

        # ── temperatura 2m ───────────────────────────────────────────────────
        't2m': VariableConfig(
            name='t2m',
            colors=['#0000ff', '#0055ff', '#00aaff', '#00ffff', '#55ff00',
                    '#aaff00', '#ffff00', '#ffaa00', '#ff5500', '#ff0000'],
            bars=[-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40],
            bias=-273.15,
            units_override='°C',
        ),

        # ── aggiungi qui le tue variabili ────────────────────────────────────
    }

    @classmethod
    def get(cls, name: str) -> VariableConfig:
        """
        Restituisce la VariableConfig corrispondente a `name`.
        Lancia KeyError con messaggio leggibile se non trovata.
        """
        if name not in cls.CONFIGS:
            available = list(cls.CONFIGS.keys())
            raise KeyError(
                f"Variabile '{name}' non presente in MeteoVariables.CONFIGS.\n"
                f"Variabili disponibili: {available}"
            )
        return cls.CONFIGS[name]

# meteo-plot

Script Python per il plotting di variabili meteorologiche da file GRIB, con supporto a più esperimenti e variabili configurabili esternamente.

---

## Struttura del repository

```
meteo-plot/
├── README.md            ← sei qui
├── requirements.txt     ← dipendenze Python
├── config.yaml          ← ✏️  unico file da modificare per girare lo script
│
├── run.py               ← entry point, legge config.yaml e lancia il loop
├── config.py            ← definizione variabili meteorologiche (VariableConfig, MeteoVariables)
├── preprocessing.py     ← lettura file GRIB e correzioni (bias, unità)
├── plotting.py          ← loop sui timestep e salvataggio figure
└── plot_utilis.py       ← funzione plot_map_model (già esistente)
```

### Cosa toccare e cosa no

| File | Quando modificarlo |
|---|---|
| `config.yaml` | Ogni volta: esperimenti, variabili, percorsi, dominio |
| `config.py` | Solo per aggiungere una nuova variabile meteorologica |
| `run.py` | Mai |
| `preprocessing.py` | Mai |
| `plotting.py` | Mai |

---

## Installazione

```bash
git clone https://github.com/<tuo-utente>/meteo-plot.git
cd meteo-plot
pip install -r requirements.txt
```

---

## Utilizzo

1. Modifica `config.yaml` con i tuoi esperimenti e percorsi
2. Lancia lo script:

```bash
python run.py
```

Per usare un file di configurazione alternativo:

```bash
python run.py --config /percorso/altro.yaml
```

---

## Aggiungere una nuova variabile

Apri `config.py` e aggiungi una entry in `MeteoVariables.CONFIGS`:

```python
'nome_variabile': VariableConfig(
    name='nome_variabile',
    colors=['#hex1', '#hex2', ...],   # colori della colormap
    bars=[val1, val2, ...],           # livelli per BoundaryNorm
    mode='instant',                   # 'instant' oppure 'diff'
    steps_cumul=[],                   # solo se mode='diff', es. [3, 12]
    bias=0.0,                         # offset numerico (es. -273.15 per K→°C)
    units_override='',                # sovrascrive le unità lette dal GRIB
),
```

Poi aggiungi il nome in `config.yaml` sotto `variables`.

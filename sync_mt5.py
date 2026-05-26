#!/usr/bin/env python3
"""
Trading Journal — Auto-sync MT5
Vigila tu carpeta de MT5 y sube el historial a sync.json cada 2 horas.

Instalación:
  pip3 install watchdog schedule

Uso:
  python3 sync_mt5.py
"""

import os, json, csv, glob, time, datetime, re, shutil, pathlib, logging

# ── CONFIGURACIÓN ─────────────────────────────────────────────────
MT5_HISTORY_FOLDER = os.path.expanduser(
    "~/Library/Application Support/MetaQuotes/Terminal/*/MQL5/Files"
)
# También busca exportaciones manuales en tu carpeta de Descargas:
DOWNLOADS_FOLDER   = os.path.expanduser("~/Downloads")
CSV_FILENAME_GLOB  = "*.csv"          # patrón de nombre del CSV exportado
OUTPUT_FILE        = "sync.json"      # archivo que lee el journal
SYNC_INTERVAL_HRS  = 2                # cada cuántas horas sincronizar
LOG_FILE           = "sync_mt5.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger()

# ── LÓGICA ───────────────────────────────────────────────────────
def find_latest_csv():
    """Busca el CSV más reciente en las rutas de MT5 y Descargas."""
    patterns = [
        *glob.glob(MT5_HISTORY_FOLDER, recursive=False),
        DOWNLOADS_FOLDER
    ]
    candidates = []
    for folder in patterns:
        if not os.path.isdir(folder):
            continue
        for f in pathlib.Path(folder).glob(CSV_FILENAME_GLOB):
            candidates.append(f)
    if not candidates:
        return None
    # el más reciente por fecha de modificación
    return max(candidates, key=lambda f: f.stat().st_mtime)

def parse_csv(filepath):
    """Lee el CSV de MT5 y retorna lista de trades."""
    trades = []
    try:
        with open(filepath, newline='', encoding='utf-8-sig') as f:
            # Detecta delimitador
            sample = f.read(2048); f.seek(0)
            delimiter = ';' if sample.count(';') > sample.count(',') else ','
            reader = csv.DictReader(f, delimiter=delimiter)
            for i, row in enumerate(reader):
                k = {key.lower().strip(): (val or '').strip() for key, val in row.items()}
                def gv(*names):
                    for n in names:
                        for key in k:
                            if n in key and k[key]:
                                return k[key]
                    return ''
                symbol   = gv('symbol','instrument','pair')
                t_type   = gv('type','direction','side','action')
                t_lower  = t_type.lower()
                if not symbol or not any(x in t_lower for x in ['buy','sell','long','short']):
                    continue
                profit_raw = re.sub(r'[^0-9.\-]', '', gv('profit','pnl','p&l','net profit','gain'))
                profit = float(profit_raw) if profit_raw else 0.0
                close_time = gv('close time','exit time','time2','close date')
                trade = {
                    "id":         f"SYNC_{i}_{int(time.time())}",
                    "symbol":     symbol,
                    "type":       t_type,
                    "volume":     gv('volume','lots','size','qty','lot'),
                    "entry":      gv('price','open price','entry price','open'),
                    "sl":         gv('s/l','sl','stop loss','stoploss'),
                    "tp":         gv('t/p','tp','take profit','takeprofit'),
                    "profit":     profit,
                    "openTime":   gv('time','open time','open date','date','entry time'),
                    "closeTime":  close_time or None,
                    "closePrice": gv('close price','exit price','price2') or None,
                    "status":     "closed" if close_time and len(close_time) > 2 else "open",
                    "note":       gv('comment','comments','remark','label'),
                    "setup":      "",
                    "session":    "",
                    "emotion":    "",
                    "riskPct":    ""
                }
                trades.append(trade)
    except Exception as e:
        log.error(f"Error leyendo CSV: {e}")
    return trades

def write_sync(trades, source_file):
    """Escribe sync.json que el journal lee."""
    data = {
        "lastSync":   datetime.datetime.now().isoformat(),
        "sourceFile": str(source_file),
        "tradeCount": len(trades),
        "trades":     trades
    }
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"sync.json actualizado — {len(trades)} trades desde {source_file.name}")

def do_sync():
    csv_file = find_latest_csv()
    if not csv_file:
        log.warning("No se encontró ningún CSV de MT5. Exporta el historial manualmente.")
        return
    trades = parse_csv(csv_file)
    if trades:
        write_sync(trades, csv_file)
    else:
        log.warning(f"CSV encontrado pero sin trades válidos: {csv_file}")

# ── MAIN ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 50)
    log.info("Trading Journal — Auto-sync MT5 iniciado")
    log.info(f"Intervalo: cada {SYNC_INTERVAL_HRS} horas")
    log.info(f"Output: {os.path.abspath(OUTPUT_FILE)}")
    log.info("=" * 50)

    # Primera sync inmediata
    do_sync()

    # Loop cada 2 horas
    interval_secs = SYNC_INTERVAL_HRS * 3600
    while True:
        log.info(f"Próxima sync en {SYNC_INTERVAL_HRS}h...")
        time.sleep(interval_secs)
        do_sync()

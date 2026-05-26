# Trading Journal — MT5

Dashboard profesional para trackear tus trades de MT5.

## Deploy en GitHub Pages (5 minutos)

```bash
# 1. Crea el repo en GitHub llamado "Trading-Journal" (público)
# 2. En tu Mac, abre Terminal:

cd ~/Desktop
git clone https://github.com/TU_USUARIO/Trading-Journal.git
cd Trading-Journal

# Copia los archivos de este proyecto aquí
# Luego:
git add .
git commit -m "Initial commit"
git push origin main

# 3. En GitHub → Settings → Pages → Source: main branch → Save
# Tu journal estará en: https://TU_USUARIO.github.io/Trading-Journal/
```

## Auto-sync con MT5 en Mac

### Instalación (una sola vez)
```bash
pip3 install watchdog schedule
```

### Uso
```bash
# Corre este script en tu Mac cuando tengas MT5 abierto:
cd ~/Desktop/Trading-Journal
python3 sync_mt5.py

# El script corre en background y sincroniza cada 2 horas.
# Para correrlo automáticamente al encender el Mac, ver sección LaunchAgent.
```

### Exportar desde MT5 (Mac)
1. Abre MT5 → pestaña Historial
2. Clic derecho → "Guardar como informe detallado"
3. Formato: CSV
4. Guarda en `~/Downloads/` (el script lo detecta automáticamente)

### LaunchAgent (opcional) — auto-inicio al encender
```bash
# Crea el archivo:
cat > ~/Library/LaunchAgents/com.tradingjournal.sync.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.tradingjournal.sync</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/TU_USUARIO/Desktop/Trading-Journal/sync_mt5.py</string>
  </array>
  <key>WorkingDirectory</key><string>/Users/TU_USUARIO/Desktop/Trading-Journal</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/tradingjournal.log</string>
  <key>StandardErrorPath</key><string>/tmp/tradingjournal.err</string>
</dict>
</plist>
PLIST

# Actívalo:
launchctl load ~/Library/LaunchAgents/com.tradingjournal.sync.plist
```

## Estructura de archivos
```
Trading-Journal/
├── index.html       ← El journal completo
├── sync.json        ← Generado por el script Python (auto-sync)
├── sync_mt5.py      ← Script de auto-sync
└── README.md
```

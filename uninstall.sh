#!/bin/bash

# Controlla i privilegi di root
if [ "$EUID" -ne 0 ]; then
  echo "Esegui lo script con i privilegi di root (sudo ./uninstall.sh)"
  exit 1
fi

echo "Disinstallazione di Arch Toolbox in corso..."

# Rimuove la directory dei file del programma
if [ -d "/usr/share/arch-toolbox" ]; then
    rm -rf /usr/share/arch-toolbox
    echo "Directory /usr/share/arch-toolbox rimossa."
fi

# Rimuove il file di collegamento dal menu delle applicazioni
if [ -f "/usr/share/applications/arch-toolbox.desktop" ]; then
    rm -f /usr/share/applications/arch-toolbox.desktop
    echo "File di lancio rimosso dal menu delle applicazioni."
fi

# Aggiorna il database dei desktop file se disponibile
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database
fi

echo "Disinstallazione completata con successo! L'applicazione è stata rimossa dal sistema."

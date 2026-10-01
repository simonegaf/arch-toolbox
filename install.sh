#!/bin/bash

# Controlla i privilegi di root
if [ "$EUID" -ne 0 ]; then
  echo "Esegui lo script con i privilegi di root (sudo ./install.sh)"
  exit 1
fi

echo "Installazione di Arch Toolbox in corso..."

# Crea la directory di destinazione e copia lo script
mkdir -p /usr/share/arch-toolbox
cp arch_toolbox.py /usr/share/arch-toolbox/
chmod +x /usr/share/arch-toolbox/arch_toolbox.py

# Installa il file .desktop per il menu delle applicazioni
cp arch-toolbox.desktop /usr/share/applications/

# Aggiorna il database dei desktop file
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database
fi

echo "Installazione completata con successo! Trovi 'Arch Toolbox' nel menu delle applicazioni."

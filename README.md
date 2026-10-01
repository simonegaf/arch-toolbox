# Arch Toolbox

**Arch Toolbox** è un'applicazione grafica leggera sviluppata in Python (Tkinter) e progettata specificamente per sistemi basati su **Arch Linux** (EndeavourOS, Manjaro, ecc.). Unisce in un'unica interfaccia intuitiva gli strumenti essenziali per la pulizia del sistema e il controllo preventivo della sicurezza.

## Caratteristiche Principali

### 🧹 Manutenzione & Pulizia
* **Rimozione Orfani**: Pulizia automatica dei pacchetti orfani non più necessari (`yay -Yc`).
* **Pulizia Radicale della Cache**: Svuotamento completo e forzato della cache di Pacman (`pacman -Scc`).

### 🛡 Screening & Sicurezza
* **Stato Firewall (UFW)**: Verifica rapida dello stato e delle regole di protezione attive.
* **Porte di Rete Aperte**: Scansione in tempo reale dei servizi e delle porte in ascolto (`ss`), con riepilogo pulito dei servizi attivi.
* **Audit delle Vulnerabilità**: Integrazione con `arch-audit` per rilevare tempestivamente eventuali criticità di livello High.

## Requisiti di Sistema
* Arch Linux o derivate.
* Python 3 con libreria Tkinter (`python-tkinter`).
* Pacchetti di sistema: `ufw`, `arch-audit`, `yay`.

## Installazione rapida da sorgente
Clona la repository e lancia lo script di installazione con i permessi di root:

```bash
git clone [https://github.com/simonegaf/arch-toolbox.git](https://github.com/simonegaf/arch-toolbox.git)
cd arch-toolbox
sudo ./install.sh

#!/usr/bin/env python3
"""
=============================================================================
  WiFi Info Boosted - Outil d'analyse, de diagnostic et d'audit WiFi (Windows)
=============================================================================
  Fonctionnalités :
   - Informations détaillées sur la connexion WiFi actuelle
   - Révélation de TOUS les mots de passe WiFi enregistrés
   - Scanner de réseaux environnants (Signal, Canal, Bande 2.4GHz/5GHz/6GHz)
   - Diagnostics réseau (IPv4, IPv6, Passerelle, DNS, MAC, IP Publique)
   - Test de Latence & Stabilité (Ping & Perte de paquets)
   - Moniteur de Signal WiFi en temps réel (Barre visuelle)
   - Générateur de QR Code WiFi ASCII dans le terminal pour smartphones
   - Exportation des rapports en JSON, CSV et TXT
   - Mode CLI (arguments) & Mode Interactif (Menu)
=============================================================================
"""

import sys
import os
import re
import subprocess
import json
import csv
import time
import argparse
import socket
import urllib.request
import ctypes

# Force l'encodage UTF-8 pour la console Python
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Activation du support des couleurs ANSI sur la console Windows
def enable_ansi_support():
    if os.name == "nt":
        try:
            kernel32 = ctypes.windll.kernel32
            hStdOut = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(hStdOut, mode)
            return True
        except Exception:
            return False
    return True

USE_COLORS = enable_ansi_support()

class Colors:
    CYAN = "\033[96m" if USE_COLORS else ""
    GREEN = "\033[92m" if USE_COLORS else ""
    YELLOW = "\033[93m" if USE_COLORS else ""
    RED = "\033[91m" if USE_COLORS else ""
    MAGENTA = "\033[95m" if USE_COLORS else ""
    BLUE = "\033[94m" if USE_COLORS else ""
    BOLD = "\033[1m" if USE_COLORS else ""
    DIM = "\033[2m" if USE_COLORS else ""
    RESET = "\033[0m" if USE_COLORS else ""

def disable_colors():
    Colors.CYAN = ""
    Colors.GREEN = ""
    Colors.YELLOW = ""
    Colors.RED = ""
    Colors.MAGENTA = ""
    Colors.BLUE = ""
    Colors.BOLD = ""
    Colors.DIM = ""
    Colors.RESET = ""


def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}==================================================================================
   📡 WiFi Info Boosted v1.0 - Analyse & Diagnostic Réseau Windows by Goat Asta
=================================================================================={Colors.RESET}"""
    print(banner)


def run_command(command):
    """Exécute une commande shell ou liste d'arguments avec décodage multi-encodage."""
    try:
        if isinstance(command, list):
            res = subprocess.run(command, capture_output=True)
        else:
            res = subprocess.run(command, capture_output=True, shell=True)

        raw = res.stdout
        # Tester d'abord UTF-8, puis CP850, CP1252 pour préserver les émojis et caractères accentués
        for enc in ["utf-8", "cp850", "cp1252", "latin1"]:
            try:
                decoded = raw.decode(enc)
                if "\ufffd" not in decoded:
                    return decoded.strip()
            except Exception:
                continue
        return raw.decode("utf-8", errors="replace").strip()
    except Exception as e:
        return f"Erreur: {e}"


def format_signal_bar(percent_str):
    """Génère une barre visuelle de signal avec coloration dynamique."""
    try:
        val = int(re.sub(r"[^\d]", "", str(percent_str)))
    except ValueError:
        return f"{Colors.DIM}[──────────] ?%{Colors.RESET}"

    length = 10
    filled = int(round(length * val / 100))
    bar = "█" * filled + "░" * (length - filled)

    if val >= 75:
        color = Colors.GREEN
    elif val >= 45:
        color = Colors.YELLOW
    else:
        color = Colors.RED

    return f"{color}[{bar}] {val}%{Colors.RESET}"


def get_current_wifi_info():
    """Récupère les détails de l'interface WiFi actuellement connectée."""
    output = run_command("netsh wlan show interfaces")
    if not output or "Aucun" in output or "disconnected" in output.lower() or "dconnect" in output.lower():
        return None

    info = {}
    patterns = {
        "Nom de l'interface": r"Nom\s*:\s*(.+)",
        "Description": r"Description\s*:\s*(.+)",
        "Adresse physique (MAC)": r"Adresse physique\s*:\s*(.+)",
        "État": r"État\s*:\s*(.+)",
        "SSID": r"SSID\s*:\s*(.+)",
        "BSSID (Routeur)": r"(?:Point d'accès d’identificateur SSID|BSSID)\s*:\s*(.+)",
        "Bande": r"Bande\s*:\s*(.+)",
        "Canal": r"Canal\s*:\s*(.+)",
        "Type de réseau": r"Type de réseau\s*:\s*(.+)",
        "Type de radio": r"Type de radio\s*:\s*(.+)",
        "Authentification": r"Authentification\s*:\s*(.+)",
        "Chiffrement": r"Chiffrement\s*:\s*(.+)",
        "Réception (Mbps)": r"Réception\s*:\s*(.+)",
        "Transmission (Mbps)": r"Transmission\s*:\s*(.+)",
        "Signal (%)": r"Signal\s*:\s*(.+)",
        "RSSI": r"Rssi\s*:\s*(.+)",
        "Nom du profil": r"Profil\s*:\s*(.+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            val = match.group(1).strip()
            info[key] = val.strip('"')

    if "Nom du profil" in info and info["Nom du profil"]:
        profile_name = info["Nom du profil"]
        detail_output = run_command(["netsh", "wlan", "show", "profile", f"name={profile_name}", "key=clear"])
        key_match = re.search(r"(?:Contenu[^\:]*|Key Content)\s*:\s*(.+)", detail_output)
        if key_match:
            info["Mot de passe"] = key_match.group(1).strip()
        else:
            info["Mot de passe"] = "(Aucun ou non accessible)"

    return info


def get_all_wifi_passwords():
    """Récupère tous les profils WiFi enregistrés et leurs mots de passe."""
    output = run_command("netsh wlan show profiles")
    profiles = []

    for line in output.splitlines():
        if ("Profil" in line or "Profile" in line) and ":" in line:
            parts = line.split(":", 1)
            name = parts[1].strip()
            if name and not name.startswith("<") and "stratégies" not in name.lower() and "policy" not in name.lower() and not line.startswith("Profils"):
                profiles.append(name)

    result = []
    for profile in profiles:
        detail_output = run_command(["netsh", "wlan", "show", "profile", f"name={profile}", "key=clear"])
        
        auth_match = re.search(r"Authentification\s*:\s*(.+)", detail_output)
        key_match = re.search(r"(?:Contenu[^\:]*|Key Content)\s*:\s*(.+)", detail_output)
        
        auth = auth_match.group(1).strip() if auth_match else "Inconnu"
        password = key_match.group(1).strip() if key_match else "(Ouvert / Non stocké)"

        result.append({
            "SSID": profile,
            "Authentification": auth,
            "Mot de passe": password
        })

    return result


def scan_nearby_networks():
    """Scanne tous les réseaux WiFi environnants captés par la carte réseau."""
    output = run_command("netsh wlan show networks mode=bssid")
    networks = []

    current_ssid = None
    current_net = {}

    lines = output.splitlines()
    for line in lines:
        line_str = line.strip()

        match_ssid = re.match(r"^SSID\s+\d+\s*:\s*(.*)", line_str)
        if match_ssid:
            if current_net and current_ssid:
                networks.append(current_net)
            current_ssid = match_ssid.group(1).strip() or "(Réseau masqué)"
            current_net = {
                "SSID": current_ssid,
                "Type": "Infrastructure",
                "Authentification": "",
                "Chiffrement": "",
                "BSSID": "",
                "Signal": "0%",
                "Bande": "",
                "Canal": "",
                "Radio": ""
            }
            continue

        if not current_net:
            continue

        match_auth = re.match(r"^Authentification\s*:\s*(.+)", line_str)
        if match_auth:
            current_net["Authentification"] = match_auth.group(1).strip()
            continue

        match_ciph = re.match(r"^Chiffrement\s*:\s*(.+)", line_str)
        if match_ciph:
            current_net["Chiffrement"] = match_ciph.group(1).strip()
            continue

        match_bssid = re.match(r"^BSSID\s+\d+\s*:\s*(.+)", line_str)
        if match_bssid:
            current_net["BSSID"] = match_bssid.group(1).strip()
            continue

        match_sig = re.match(r"^Signal\s*:\s*(.+)", line_str)
        if match_sig:
            current_net["Signal"] = match_sig.group(1).strip()
            continue

        match_band = re.match(r"^Bande\s*:\s*(.+)", line_str)
        if match_band:
            current_net["Bande"] = match_band.group(1).strip()
            continue

        match_chan = re.match(r"^Canal\s*:\s*(.+)", line_str)
        if match_chan:
            current_net["Canal"] = match_chan.group(1).strip()
            continue

        match_rad = re.match(r"^Type de radio\s*:\s*(.+)", line_str)
        if match_rad:
            current_net["Radio"] = match_rad.group(1).strip()
            continue

    if current_net and current_ssid:
        networks.append(current_net)

    return networks


def get_ip_diagnostics():
    """Récupère la configuration IP locale, le routeur/passerelle et l'IP publique."""
    diag = {
        "Nom d'hôte": socket.gethostname(),
        "IPv4 locale": "Non disponible",
        "Masque de sous-réseau": "",
        "Passerelle par défaut": "",
        "Adresse MAC": "",
        "IP Publique": "En cours de vérification..."
    }

    ipconfig_out = run_command("ipconfig /all")
    
    wifi_section = False
    for line in ipconfig_out.splitlines():
        if "Wi-Fi" in line or "sans fil" in line:
            wifi_section = True
        elif wifi_section and line.startswith("Carte "):
            wifi_section = False

        if wifi_section or diag["IPv4 locale"] == "Non disponible":
            match_ipv4 = re.search(r"Adresse IPv4[^\:]*:\s*([\d\.]+)", line)
            if match_ipv4:
                diag["IPv4 locale"] = match_ipv4.group(1).strip()

            match_mask = re.search(r"Masque de sous-réseau[^\:]*:\s*([\d\.]+)", line)
            if match_mask and not diag["Masque de sous-réseau"]:
                diag["Masque de sous-réseau"] = match_mask.group(1).strip()

            match_gw = re.search(r"Passerelle par défaut[^\:]*:\s*([\d\.]+)", line)
            if match_gw and not diag["Passerelle par défaut"]:
                diag["Passerelle par défaut"] = match_gw.group(1).strip()

            match_mac = re.search(r"Adresse physique[^\:]*:\s*([A-FA-f0-9\-]{17})", line)
            if match_mac and not diag["Adresse MAC"]:
                diag["Adresse MAC"] = match_mac.group(1).strip()

    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={"User-Agent": "WiFiInfo/2.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            diag["IP Publique"] = data.get("ip", "Inconnue")
    except Exception:
        diag["IP Publique"] = "Impossible de récupérer l'IP publique (Hors-ligne ?)"

    return diag


def run_ping_test(target="8.8.8.8", count=3):
    """Effectue un test de latence et perte de paquets."""
    output = run_command(f"ping -n {count} {target}")
    
    result = {
        "Cible": target,
        "Paquets envoyés": count,
        "Paquets reçus": 0,
        "Perte (%)": "100%",
        "Latence min (ms)": "N/A",
        "Latence moy (ms)": "N/A",
        "Latence max (ms)": "N/A",
        "Statut": "Échec"
    }

    loss_match = re.search(r"perte\s*([\d]+%)", output, re.IGNORECASE) or re.search(r"loss\s*([\d]+%)", output, re.IGNORECASE)
    if loss_match:
        result["Perte (%)"] = loss_match.group(1)

    times_match = re.search(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Moyenne = (\d+)ms", output) or \
                  re.search(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms", output)
    if times_match:
        result["Latence min (ms)"] = times_match.group(1)
        result["Latence max (ms)"] = times_match.group(2)
        result["Latence moy (ms)"] = times_match.group(3)
        avg = int(times_match.group(3))
        result["Statut"] = "Excellent" if avg < 40 else ("Moyen" if avg < 100 else "Lent")
        result["Paquets reçus"] = count

    return result


def display_current_wifi():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}--- CONNEXION WIFI ACTUELLE ---{Colors.RESET}\n")
    info = get_current_wifi_info()
    if not info:
        print(f"  {Colors.RED}[!] Aucune connexion WiFi détectée.{Colors.RESET}")
        print("      Assurez-vous que la carte WiFi est activée et connectée à un réseau.\n")
        return None

    for key, value in info.items():
        if key == "Signal (%)":
            formatted_val = f"{value} {format_signal_bar(value)}"
            print(f"  {Colors.CYAN}{key:26s}{Colors.RESET} : {formatted_val}")
        elif key == "Mot de passe":
            print(f"  {Colors.GREEN}{Colors.BOLD}{key:26s}{Colors.RESET} : {Colors.GREEN}{Colors.BOLD}{value}{Colors.RESET}")
        else:
            print(f"  {Colors.CYAN}{key:26s}{Colors.RESET} : {value}")
    print()
    return info


def display_saved_passwords():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}--- PROFILS WIFI ET MOTS DE PASSE ENREGISTRÉS ---{Colors.RESET}\n")
    passwords = get_all_wifi_passwords()
    if not passwords:
        print(f"  {Colors.RED}[!] Aucun profil WiFi enregistré trouvé.{Colors.RESET}\n")
        return []

    header = f"  {'#':<4} {'SSID / Nom du réseau':<32} {'Authentification':<20} {'Mot de passe':<25}"
    print(f"{Colors.BOLD}{header}{Colors.RESET}")
    print("  " + "─" * 83)

    for idx, item in enumerate(passwords, 1):
        ssid = item['SSID']
        if len(ssid) > 30:
            ssid = ssid[:27] + "..."
        auth = item['Authentification']
        pwd = item['Mot de passe']
        
        pwd_colored = f"{Colors.GREEN}{pwd}{Colors.RESET}" if pwd and not pwd.startswith("(") else f"{Colors.DIM}{pwd}{Colors.RESET}"
        print(f"  {Colors.CYAN}{idx:<4}{Colors.RESET} {ssid:<32} {auth:<20} {pwd_colored:<25}")
    
    print(f"\n  {Colors.DIM}Total : {len(passwords)} réseaux enregistrés.{Colors.RESET}\n")
    return passwords


def display_nearby_networks():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}--- BALAYAGE DES RÉSEAUX WIFI ENVIRONNANTS ---{Colors.RESET}\n")
    networks = scan_nearby_networks()
    if not networks:
        print(f"  {Colors.RED}[!] Aucun réseau environnant capté.{Colors.RESET}\n")
        return []

    header = f"  {'SSID / Réseau':<28} {'Signal':<18} {'Bande':<10} {'Canal':<8} {'Sécurité':<20} {'BSSID (MAC)':<18}"
    print(f"{Colors.BOLD}{header}{Colors.RESET}")
    print("  " + "─" * 105)

    for net in networks:
        ssid = net["SSID"]
        if len(ssid) > 26:
            ssid = ssid[:23] + "..."
        sig_bar = format_signal_bar(net["Signal"])
        band = net["Bande"] or "2.4GHz"
        chan = net["Canal"] or "-"
        sec = net["Authentification"] or net["Chiffrement"] or "Ouvert"
        bssid = net["BSSID"] or "-"

        print(f"  {Colors.CYAN}{ssid:<28}{Colors.RESET} {sig_bar:<28} {band:<10} {chan:<8} {sec:<20} {bssid:<18}")

    print(f"\n  {Colors.DIM}Total : {len(networks)} réseaux détectés à proximité.{Colors.RESET}\n")
    return networks


def display_ip_diagnostics():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}--- DIAGNOSTICS RÉSEAU & IP ---{Colors.RESET}\n")
    diag = get_ip_diagnostics()
    for key, val in diag.items():
        print(f"  {Colors.CYAN}{key:26s}{Colors.RESET} : {Colors.BOLD}{val}{Colors.RESET}")
    
    print(f"\n  {Colors.BOLD}Test de Latence (Ping Google 8.8.8.8) :{Colors.RESET}")
    ping = run_ping_test("8.8.8.8", 3)
    status_color = Colors.GREEN if ping['Statut'] in ['Excellent', 'Moyen'] else Colors.RED
    print(f"    - Statut connexion : {status_color}{ping['Statut']}{Colors.RESET}")
    print(f"    - Latence moyenne  : {Colors.BOLD}{ping['Latence moy (ms)']} ms{Colors.RESET}")
    print(f"    - Perte de paquets : {ping['Perte (%)']}")
    print()
    return diag


def monitor_signal(interval=2):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}--- MONITEUR DE SIGNAL WIFI EN TEMPS RÉEL ---{Colors.RESET}")
    print(f"  Appuyez sur {Colors.BOLD}Ctrl+C{Colors.RESET} pour quitter le mode moniteur.\n")

    try:
        while True:
            info = get_current_wifi_info()
            timestamp = time.strftime("%H:%M:%S")
            if not info:
                print(f"\r[{timestamp}] {Colors.RED}[!] WiFi déconnecté...{Colors.RESET}              ", end="", flush=True)
            else:
                ssid = info.get("SSID", "Inconnu")
                sig = info.get("Signal (%)", "0%")
                rx = info.get("Réception (Mbps)", "-")
                tx = info.get("Transmission (Mbps)", "-")
                sig_bar = format_signal_bar(sig)
                
                print(f"\r[{timestamp}] SSID: {Colors.CYAN}{Colors.BOLD}{ssid}{Colors.RESET} | Signal: {sig_bar} | Rx: {rx} Mbps | Tx: {tx} Mbps  ", end="", flush=True)
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.GREEN}[✓] Surveillance arrêtée.{Colors.RESET}\n")


def generate_wifi_qr_code(ssid=None, password=None):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}--- GÉNÉRATEUR DE QR CODE WIFI ---{Colors.RESET}\n")
    
    if not ssid:
        current = get_current_wifi_info()
        if current:
            ssid = current.get("SSID")
            password = current.get("Mot de passe")

    if not ssid:
        ssid = input("  Entrez le nom du réseau WiFi (SSID) : ").strip()
        password = input("  Entrez le mot de passe (laissez vide si ouvert) : ").strip()

    if not password or password.startswith("("):
        auth_type = "nopass"
        pass_str = ""
    else:
        auth_type = "WPA"
        pass_str = password

    qr_payload = f"WIFI:T:{auth_type};S:{ssid};P:{pass_str};;"

    print(f"  Réseau : {Colors.CYAN}{Colors.BOLD}{ssid}{Colors.RESET}")
    print(f"  Clé    : {Colors.GREEN}{pass_str if pass_str else '(Aucun)'}{Colors.RESET}")
    print(f"  Chaîne : {qr_payload}\n")

    try:
        req = urllib.request.Request(f"https://qrenco.de/{qr_payload}", headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            qr_text = resp.read().decode("utf-8")
            print(qr_text)
            print(f"  {Colors.GREEN}{Colors.BOLD}[✓] Scannez ce QR code avec l'appareil photo de votre smartphone pour vous connecter !{Colors.RESET}\n")
            return
    except Exception:
        pass

    print(f"  {Colors.YELLOW}[i] Impossible d'afficher le rendu graphique du QR Code dans ce terminal (mode hors-ligne).{Colors.RESET}")
    print(f"      Chaîne de connexion directe : {Colors.BOLD}{qr_payload}{Colors.RESET}\n")


def export_report(export_format="json", filename=None):
    if not filename:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"wifi_report_{timestamp}.{export_format.lower()}"

    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "current_connection": get_current_wifi_info(),
        "saved_passwords": get_all_wifi_passwords(),
        "nearby_networks": scan_nearby_networks(),
        "ip_diagnostics": get_ip_diagnostics()
    }

    try:
        if export_format.lower() == "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        elif export_format.lower() == "csv":
            with open(filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Type", "SSID", "Sécurité / Auth", "Mot de passe / Signal", "Détails"])
                if data["current_connection"]:
                    c = data["current_connection"]
                    writer.writerow(["Connexion Actuelle", c.get("SSID"), c.get("Authentification"), c.get("Mot de passe"), c.get("Signal (%)")])
                for p in data["saved_passwords"]:
                    writer.writerow(["Profil Enregistré", p.get("SSID"), p.get("Authentification"), p.get("Mot de passe"), ""])
                for n in data["nearby_networks"]:
                    writer.writerow(["Réseau Environnant", n.get("SSID"), n.get("Authentification"), n.get("Signal"), n.get("BSSID")])
        else: # txt
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"=========================================\n")
                f.write(f" RAPPORT DIAGNOSTIC WIFI - {data['timestamp']}\n")
                f.write(f"=========================================\n\n")
                f.write(f"CONNEXION ACTUELLE:\n")
                f.write(json.dumps(data["current_connection"], indent=2, ensure_ascii=False) + "\n\n")
                f.write(f"MOTS DE PASSE ENREGISTRÉS:\n")
                for item in data["saved_passwords"]:
                    f.write(f" - {item['SSID']} | Auth: {item['Authentification']} | Pwd: {item['Mot de passe']}\n")
                f.write(f"\nRÉSEAUX ENVIRONNANTS:\n")
                for net in data["nearby_networks"]:
                    f.write(f" - {net['SSID']} | Signal: {net['Signal']} | Canal: {net['Canal']} | BSSID: {net['BSSID']}\n")

        print(f"  {Colors.GREEN}{Colors.BOLD}[✓] Rapport exporté avec succès vers : {filename}{Colors.RESET}\n")
    except Exception as e:
        print(f"  {Colors.RED}[!] Erreur lors de l'exportation : {e}{Colors.RESET}\n")


def interactive_menu():
    while True:
        print_banner()
        print(f"  {Colors.BOLD}Menu Principal :{Colors.RESET}\n")
        print(f"  {Colors.CYAN}1.{Colors.RESET} Connexion WiFi Actuelle (Détails & Mot de passe)")
        print(f"  {Colors.CYAN}2.{Colors.RESET} Afficher TOUS les Mots de Passe Enregistrés")
        print(f"  {Colors.CYAN}3.{Colors.RESET} Scanner les Réseaux WiFi Environnants")
        print(f"  {Colors.CYAN}4.{Colors.RESET} Diagnostics Réseau (IP, DNS, MAC, Latence Ping)")
        print(f"  {Colors.CYAN}5.{Colors.RESET} Moniteur de Signal en Temps Réel")
        print(f"  {Colors.CYAN}6.{Colors.RESET} Générer un QR Code WiFi (Pour Smartphone)")
        print(f"  {Colors.CYAN}7.{Colors.RESET} Rapport Complet & Exportation (JSON/CSV/TXT)")
        print(f"  {Colors.CYAN}0.{Colors.RESET} Quitter")
        print()

        choice = input(f"  {Colors.BOLD}Votre choix [0-7] : {Colors.RESET}").strip()

        if choice == "1":
            display_current_wifi()
        elif choice == "2":
            display_saved_passwords()
        elif choice == "3":
            display_nearby_networks()
        elif choice == "4":
            display_ip_diagnostics()
        elif choice == "5":
            monitor_signal()
        elif choice == "6":
            generate_wifi_qr_code()
        elif choice == "7":
            display_current_wifi()
            display_saved_passwords()
            display_nearby_networks()
            display_ip_diagnostics()
            fmt = input("  Format d'exportation (json/csv/txt) [defaut: json] : ").strip() or "json"
            export_report(fmt)
        elif choice == "0":
            print(f"\n  {Colors.GREEN}Merci d'avoir utilisé WiFi Info Boosted. À bientôt !{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"\n  {Colors.RED}[!] Choix invalide, veuillez réessayer.{Colors.RESET}\n")

        input(f"  {Colors.DIM}Appuyez sur Entrée pour continuer...{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(description="WiFi Info Boosted - Outil complet d'analyse WiFi Windows")
    parser.add_argument("-a", "--all", action="store_true", help="Afficher toutes les informations et diagnostics")
    parser.add_argument("-c", "--current", action="store_true", help="Afficher les détails de la connexion actuelle")
    parser.add_argument("-p", "--passwords", action="store_true", help="Lister tous les profils et leurs mots de passe")
    parser.add_argument("-s", "--scan", action="store_true", help="Scanner les réseaux WiFi à proximité")
    parser.add_argument("-i", "--ip", action="store_true", help="Afficher les diagnostics IP et latence")
    parser.add_argument("-m", "--monitor", action="store_true", help="Lancer le moniteur de signal en temps réel")
    parser.add_argument("-q", "--qr", action="store_true", help="Générer un QR Code pour la connexion WiFi")
    parser.add_argument("-e", "--export", choices=["json", "csv", "txt"], help="Exporter les résultats vers un fichier")
    parser.add_argument("-o", "--output", help="Nom du fichier de sortie pour l'exportation")
    parser.add_argument("--no-color", action="store_true", help="Désactiver les couleurs console")

    args = parser.parse_args()

    if args.no_color:
        disable_colors()

    if not any([args.all, args.current, args.passwords, args.scan, args.ip, args.monitor, args.qr, args.export]):
        interactive_menu()
        return

    print_banner()

    if args.all or args.current:
        display_current_wifi()

    if args.all or args.passwords:
        display_saved_passwords()

    if args.all or args.scan:
        display_nearby_networks()

    if args.all or args.ip:
        display_ip_diagnostics()

    if args.qr:
        generate_wifi_qr_code()

    if args.export:
        export_report(args.export, args.output)

    if args.monitor:
        monitor_signal()


if __name__ == "__main__":
    main()

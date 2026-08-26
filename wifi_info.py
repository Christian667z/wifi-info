#!/usr/bin/env python3
"""
Script Python pour afficher les informations du réseau WiFi connecté.
Fonctionne sur Windows uniquement.
"""

import subprocess
import sys
import re

# Forcer l'encodage UTF-8 pour la sortie console
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_command(command):
    """Exécute une commande shell et retourne la sortie."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            encoding="cp850",
            errors="replace"
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Erreur: {e}"


def get_current_wifi():
    """Récupère le nom du réseau WiFi actuellement connecté."""
    output = run_command("netsh wlan show interfaces")
    if "Aucun" in output or "disconnected" in output.lower():
        return None
    return output


def get_wifi_profiles():
    """Récupère la liste des profils WiFi enregistrés."""
    output = run_command("netsh wlan show profiles")
    profiles = re.findall(r":\s*(.+)", output)
    return [p.strip() for p in profiles]


def get_wifi_profile_detail(profile_name):
    """Récupère les détails d'un profil WiFi spécifique (clé incluse)."""
    output = run_command(f'netsh wlan show profile name="{profile_name}" key=clear')
    return output


def parse_interface_info(output):
    """Parse les informations de l'interface WiFi connectée."""
    info = {}
    patterns = {
        "Nom du profil": r"Nom du profil\s*:\s*(.+)",
        "SSID": r"SSID\s*:\s*(.+)",
        "État": r"État\s*:\s*(.+)",
        "Type de réseau": r"Type de réseau\s*:\s*(.+)",
        "Type d'authentification": r"Type d'authentification\s*:\s*(.+)",
        "Chiffrement": r"Chiffrement\s*:\s*(.+)",
        "BSSID": r"BSSID\s*:\s*(.+)",
        "Type de signal": r"Type de signal\s*:\s*(.+)",
        "Qualité du signal": r"Qualité du signal\s*:\s*(.+)",
        "Réception (Mbps)": r"Réception\s*:\s*(.+)",
        "Transmission (Mbps)": r"Transmission\s*:\s*(.+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            info[key] = match.group(1).strip()
    return info


def parse_profile_detail(output):
    """Parse les détails d'un profil WiFi."""
    info = {}
    patterns = {
        "Type d'authentification": r"Type d'authentification\s*:\s*(.+)",
        "Chiffrement": r"Chiffrement\s*:\s*(.+)",
        "Clé de sécurité": r"Contenu de la clé\s*:\s*(.+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            info[key] = match.group(1).strip()
    return info


def main():
    print("=" * 55)
    print("       INFORMATIONS WIFI - Script Python")
    print("=" * 55)

    # Vérifier la connexion WiFi actuelle
    interface_output = get_current_wifi()

    if interface_output is None:
        print("\n[!] Aucune connexion WiFi détectée.")
        print("    Vérifiez que le WiFi est activé et connecté.\n")
    else:
        print("\n--- Connexion WiFi actuelle ---\n")
        info = parse_interface_info(interface_output)
        if info:
            for key, value in info.items():
                print(f"  {key:30s} : {value}")
        else:
            print("  Impossible de parser les informations de l'interface.")
            print("  Sortie brute :")
            print(interface_output)

    # Lister les profils WiFi enregistrés
    print("\n--- Profils WiFi enregistrés ---\n")
    profiles = get_wifi_profiles()
    if profiles:
        for i, profile in enumerate(profiles, 1):
            print(f"  {i}. {profile}")
    else:
        print("  Aucun profil trouvé.")

    # Afficher les détails du profil connecté
    if interface_output:
        match = re.search(r"Nom du profil\s*:\s*(.+)", interface_output)
        if match:
            current_profile = match.group(1).strip()
            print(f"\n--- Détails du profil connecté : {current_profile} ---\n")
            detail_output = get_wifi_profile_detail(current_profile)
            detail = parse_profile_detail(detail_output)
            if detail:
                for key, value in detail.items():
                    print(f"  {key:30s} : {value}")
            else:
                print("  Impossible de récupérer les détails.")

    print("\n" + "=" * 55)
    print("  Script terminé.")
    print("=" * 55)


if __name__ == "__main__":
    main()

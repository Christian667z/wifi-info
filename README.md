# 📡 WiFi Info Boosted v2.0

Outil puissant et complet en **Python** et **Node.js** pour analyser, diagnostiquer, auditer les réseaux WiFi et révéler tous les mots de passe enregistrés sous Windows.

---

## 🌟 Nouvelles Fonctionnalités v2.0

- 🔑 **Révélation de TOUS les mots de passe** : Extraction automatique de tous les réseaux WiFi enregistrés avec leurs clés en clair.
- 📡 **Scanner de réseaux environnants** : Détection des points d'accès à proximité avec force du signal (`%` + barre visuelle), bande (`2.4GHz`, `5GHz`, `6GHz`), canal et adresse MAC (`BSSID`).
- 📶 **Moniteur de signal en temps réel** : Suivi dynamique de la force du signal WiFi et du débit (Mbps).
- 🌐 **Diagnostics Réseau & IP** : IP locale IPv4/IPv6, masque de sous-réseau, passerelle, DNS, MAC et vérification d'IP publique.
- ⚡ **Test de Latence & Stabilité** : Mesure de la qualité de connexion via ping (ms) et perte de paquets (%).
- 📱 **Générateur de QR Code WiFi** : Affiche un QR Code ASCII directement dans le terminal pour connecter un smartphone instantanément sans saisir le mot de passe.
- 📊 **Exportation de Rapports** : Sauvegarde des rapports au format **JSON**, **CSV** ou **TXT**.
- 🎨 **Interface Console Moderne** : Couleurs ANSI natives, icônes et menu interactif facile à prendre en main.

---

## 🚀 Utilisation

### 1. Script Python (`wifi_info.py`)

#### Mode Interactif (Menu)

Lancez simplement le script sans argument pour ouvrir le menu interactif :

```bash
python wifi_info.py
```

```
=============================================================================
   📡 WiFi Info Boosted v2.0 - Analyse & Diagnostic Réseau Windows
=============================================================================

  Menu Principal :

  1. Connexion WiFi Actuelle (Détails & Mot de passe)
  2. Afficher TOUS les Mots de Passe Enregistrés
  3. Scanner les Réseaux WiFi Environnants
  4. Diagnostics Réseau (IP, DNS, MAC, Latence Ping)
  5. Moniteur de Signal en Temps Réel
  6. Générer un QR Code WiFi (Pour Smartphone)
  7. Rapport Complet & Exportation (JSON/CSV/TXT)
  0. Quitter
```

#### Mode Ligne de Commande (CLI Flags)

| Option | Description |
|---|---|
| `python wifi_info.py -a`, `--all` | Rapport complet (Connexion, Mots de passe, Scan, IP) |
| `python wifi_info.py -c`, `--current` | Détails de la connexion WiFi actuelle + mot de passe |
| `python wifi_info.py -p`, `--passwords` | Lister tous les profils enregistrés et leurs mots de passe |
| `python wifi_info.py -s`, `--scan` | Scanner les réseaux WiFi à proximité |
| `python wifi_info.py -i`, `--ip` | Diagnostics IP locale, publique et test de latence Ping |
| `python wifi_info.py -m`, `--monitor` | Surveillance en temps réel de la force du signal |
| `python wifi_info.py -q`, `--qr` | Générer un QR Code WiFi pour mobile |
| `python wifi_info.py -e json|csv|txt` | Exporter le rapport au format spécifié |
| `python wifi_info.py --no-color` | Désactiver les couleurs de la console |

#### Exemples CLI Python

```bash
# Afficher tous les mots de passe enregistrés
python wifi_info.py -p

# Exporter un rapport complet en JSON
python wifi_info.py -a -e json -o rapport_wifi.json

# Générer un QR Code pour se connecter au WiFi
python wifi_info.py -q

# Lancer le moniteur de signal
python wifi_info.py -m
```

---

### 2. Script Node.js (`wifi_info.js`)

```bash
# Résumé par défaut
node wifi_info.js

# Rapport complet
node wifi_info.js --all

# Mots de passe uniquement
node wifi_info.js --passwords

# Scanner les réseaux proches
node wifi_info.js --scan

# Diagnostics IP & Réseau
node wifi_info.js --ip

# Exporter en JSON
node wifi_info.js --export
```

---

## 📱 App Mobile React Native / Expo (`wifi-info-mobile`)

Pour les appareils mobiles (Android & iOS), l'application React Native est disponible dans le dossier `wifi-info-mobile/`.

```bash
cd wifi-info-mobile
npm install
npx expo start
```

---

## 🔑 Résumé de Compatibilité

| Fonctionnalité | Windows (Python) | Windows (Node.js) | App Mobile (Android/iOS) |
|---|:---:|:---:|:---:|
| **Connexion Actuelle** | ✅ | ✅ | ✅ |
| **Mots de Passe Stockés** | ✅ | ✅ | ❌ (Limitation OS) |
| **Scan Réseaux Proches** | ✅ | ✅ | ⚠️ (Partiel) |
| **Diagnostics IP & Ping** | ✅ | ✅ | ✅ |
| **QR Code WiFi** | ✅ | ❌ | ❌ |
| **Exportation JSON/CSV** | ✅ | ✅ | ❌ |

---

## 🛠️ Prérequis & Installation

- **Windows 10 / 11**
- **Python 3.6+** (Aucune bibliothèque tierce requise, utilise les modules natifs)
- **Node.js 14+** (Pour le script JS)

Aucune installation `pip` n'est nécessaire. Tout fonctionne "out-of-the-box" !

---

## 📄 Licence

Projet sous licence MIT.

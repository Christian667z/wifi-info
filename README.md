# WiFi Info

Scripts et outils pour afficher les informations du réseau WiFi connecté.

## Contenu du projet

```
wifi-info/
├── wifi_info.py          # Script Python (Windows)
├── wifi_info.js          # Script Node.js (Windows)
├── wifi-info-mobile/     # App mobile React Native (Expo)
│   ├── App.js
│   ├── package.json
│   ├── app.json
│   └── assets/
└── README.md
```

---

## Scripts Desktop (Windows)

### Prérequis

- **Python** : Python 3.6+
- **Node.js** : Node.js 14+

### Utilisation

#### Python

```bash
python wifi_info.py
```

#### Node.js

```bash
node wifi_info.js
```

### Informations affichées

- SSID du réseau connecté
- BSSID (adresse MAC du routeur)
- Type d'authentification et chiffrement
- Qualité du signal
- Vitesse réception/émission (Mbps)
- Liste des profils WiFi enregistrés
- Clé de sécurité du profil connecté

---

## App Mobile (React Native / Expo)

### Prérequis

- [Node.js](https://nodejs.org/) 16+
- [Expo CLI](https://docs.expo.dev/get-started/installation/)
- Un téléphone Android ou iOS avec l'app **Expo Go** installée

### Installation

```bash
cd wifi-info-mobile
npm install
```

### Lancement

```bash
npx expo start
```

Scannez le QR code avec l'app Expo Go sur votre téléphone.

### Permissions requises

#### Android

Les permissions suivantes sont demandées automatiquement :

- `ACCESS_WIFI_STATE` — Accéder aux informations WiFi
- `CHANGE_WIFI_STATE` — Interagir avec le WiFi
- `ACCESS_FINE_LOCATION` — Requis par Android pour accéder au SSID
- `ACCESS_COARSE_LOCATION` — Localisation approximative

> **Important** : Sur Android, la **localisation doit être activée** pour accéder au SSID du réseau.

#### iOS

Sur iOS, les informations WiFi détaillées sont limitées par les restrictions du système. L'app affiche les données disponibles via l'API NetInfo.

### Fonctionnalités de l'app

- Affichage en temps réel du statut de connexion
- SSID et BSSID du réseau
- Adresse IP et sous-réseau
- Fréquence du réseau (2.4 GHz / 5 GHz)
- Vitesse de liaison, réception et émission
- Force du signal en pourcentage
- Interface sombre et moderne
- Actualisation manuelle des données

### Capture d'écran

```
┌─────────────────────────────┐
│       WiFi Info             │
│  Informations réseau        │
│                             │
│  ┌───────────────────────┐  │
│  │   ✓ Connecté au WiFi  │  │
│  │   Type: WiFi          │  │
│  └───────────────────────┘  │
│                             │
│  Détails de la connexion    │
│  ─────────────────────────  │
│  SSID (Réseau)    MonWiFi  │
│  BSSID (Routeur)  AA:BB:.. │
│  Adresse IP       192.168..│
│  Fréquence        5150 MHz │
│  Vitesse liaison  866 Mbps │
│  Signal           85%      │
│                             │
│  ┌───────────────────────┐  │
│  │     Actualiser        │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

---

## Limitations

| Plateforme | SSID | Mot de passe | Détails complets |
|------------|------|-------------|------------------|
| Windows (Python/Node) | ✓ | ✓ | ✓ |
| Android (Expo) | ✓ | ✗ | ✓ |
| iOS (Expo) | Limité | ✗ | Partiel |
| Web (navigateur) | ✗ | ✗ | Limité |

---

## Technologies utilisées

### Scripts Desktop
- **Python** : `subprocess`, `re`
- **Node.js** : `child_process`, `execSync`
- **Commandes** : `netsh wlan` (Windows)

### App Mobile
- **React Native** : Framework mobile
- **Expo** : Plateforme de développement
- **react-native-wifi-reborn** : Accès aux informations WiFi natives
- **@react-native-community/netinfo** : Détection du type de connexion

---

## Installation rapide

### Desktop uniquement

```bash
# Cloner le repo
git clone https://github.com/VOTRE_USERNAME/wifi-info.git
cd wifi-info

# Python
python wifi_info.py

# Node.js
node wifi_info.js
```

### App mobile

```bash
cd wifi-info-mobile
npm install
npx expo start
```

---

## Auteur

Créé avec ❤️

## Licence

MIT

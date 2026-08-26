/**
 * =============================================================================
 *  WiFi Info Boosted v2.0 - Script Node.js (Windows)
 * =============================================================================
 *  Utilisation :
 *    node wifi_info.js            -> Menu interactif ou résumé
 *    node wifi_info.js --all      -> Afficher toutes les informations
 *    node wifi_info.js --passwords -> Lister tous les mots de passe enregistrés
 *    node wifi_info.js --scan     -> Scanner les réseaux environnants
 *    node wifi_info.js --ip       -> Diagnostics réseau & IP
 *    node wifi_info.js --export   -> Exporter les résultats en JSON
 * =============================================================================
 */

const { execSync, exec } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

const Colors = {
  CYAN: "\x1b[96m",
  GREEN: "\x1b[92m",
  YELLOW: "\x1b[93m",
  RED: "\x1b[91m",
  MAGENTA: "\x1b[95m",
  BLUE: "\x1b[94m",
  BOLD: "\x1b[1m",
  DIM: "\x1b[2m",
  RESET: "\x1b[0m"
};

function printBanner() {
  console.log(`\n${Colors.CYAN}${Colors.BOLD}=============================================================================`);
  console.log(`   📡 WiFi Info Boosted v2.0 - Node.js Analyseur WiFi Windows`);
  console.log(`=============================================================================${Colors.RESET}\n`);
}

function runCommand(command) {
  try {
    return execSync(command, { encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }).trim();
  } catch (e) {
    if (e.stdout) return e.stdout.toString().trim();
    return `Erreur: ${e.message}`;
  }
}

function formatSignalBar(percentStr) {
  const val = parseInt(String(percentStr).replace(/[^\d]/g, ""), 10) || 0;
  const length = 10;
  const filled = Math.round((length * val) / 100);
  const bar = "█".repeat(filled) + "░".repeat(length - filled);
  let color = Colors.GREEN;
  if (val < 45) color = Colors.RED;
  else if (val < 75) color = Colors.YELLOW;
  return `${color}[${bar}] ${val}%${Colors.RESET}`;
}

function getCurrentWifiInfo() {
  const output = runCommand("netsh wlan show interfaces");
  if (!output || output.includes("Aucun") || output.toLowerCase().includes("disconnected") || output.toLowerCase().includes("dconnect")) {
    return null;
  }

  const info = {};
  const patterns = {
    "Nom de l'interface": /Nom\s*:\s*(.+)/,
    "Description": /Description\s*:\s*(.+)/,
    "Adresse MAC": /Adresse physique\s*:\s*(.+)/,
    "État": /État\s*:\s*(.+)/,
    "SSID": /SSID\s*:\s*(.+)/,
    "BSSID (Routeur)": /(?:Point d'accès d’identificateur SSID|BSSID)\s*:\s*(.+)/,
    "Bande": /Bande\s*:\s*(.+)/,
    "Canal": /Canal\s*:\s*(.+)/,
    "Authentification": /Authentification\s*:\s*(.+)/,
    "Chiffrement": /Chiffrement\s*:\s*(.+)/,
    "Réception (Mbps)": /Réception\s*:\s*(.+)/,
    "Transmission (Mbps)": /Transmission\s*:\s*(.+)/,
    "Signal (%)": /Signal\s*:\s*(.+)/,
    "Nom du profil": /Profil\s*:\s*(.+)/
  };

  for (const [key, regex] of Object.entries(patterns)) {
    const match = output.match(regex);
    if (match) {
      info[key] = match[1].trim().replace(/^"|"$/g, "");
    }
  }

  if (info["Nom du profil"]) {
    const profileName = info["Nom du profil"];
    const detailOutput = runCommand(`netsh wlan show profile name="${profileName}" key=clear`);
    const pwdMatch = detailOutput.match(/(?:Contenu[^\:]*|Key Content)\s*:\s*(.+)/);
    info["Mot de passe"] = pwdMatch ? pwdMatch[1].trim() : "(Aucun / Non stocké)";
  }

  return info;
}

function getAllWifiPasswords() {
  const output = runCommand("netsh wlan show profiles");
  const lines = output.split("\n");
  const profiles = [];

  for (const line of lines) {
    if ((line.includes("Profil") || line.includes("Profile")) && line.includes(":")) {
      const parts = line.split(":");
      const name = parts[1].trim();
      if (name && !name.startsWith("<") && !name.toLowerCase().includes("stratégies") && !line.startsWith("Profils")) {
        profiles.push(name);
      }
    }
  }

  const result = [];
  for (const profile of profiles) {
    const detailOutput = runCommand(`netsh wlan show profile name="${profile}" key=clear`);
    const authMatch = detailOutput.match(/Authentification\s*:\s*(.+)/);
    const pwdMatch = detailOutput.match(/(?:Contenu[^\:]*|Key Content)\s*:\s*(.+)/);

    result.push({
      SSID: profile,
      Authentification: authMatch ? authMatch[1].trim() : "Inconnu",
      "Mot de passe": pwdMatch ? pwdMatch[1].trim() : "(Ouvert / Non stocké)"
    });
  }

  return result;
}

function scanNearbyNetworks() {
  const output = runCommand("netsh wlan show networks mode=bssid");
  const networks = [];
  let currentNet = null;

  const lines = output.split("\n");
  for (const line of lines) {
    const l = line.trim();
    const ssidMatch = l.match(/^SSID\s+\d+\s*:\s*(.*)/);
    if (ssidMatch) {
      if (currentNet) networks.push(currentNet);
      currentNet = {
        SSID: ssidMatch[1].trim() || "(Réseau masqué)",
        Authentification: "",
        Signal: "0%",
        Bande: "",
        Canal: "",
        BSSID: ""
      };
      continue;
    }

    if (!currentNet) continue;

    const authMatch = l.match(/^Authentification\s*:\s*(.+)/);
    if (authMatch) currentNet.Authentification = authMatch[1].trim();

    const sigMatch = l.match(/^Signal\s*:\s*(.+)/);
    if (sigMatch) currentNet.Signal = sigMatch[1].trim();

    const bandMatch = l.match(/^Bande\s*:\s*(.+)/);
    if (bandMatch) currentNet.Bande = bandMatch[1].trim();

    const chanMatch = l.match(/^Canal\s*:\s*(.+)/);
    if (chanMatch) currentNet.Canal = chanMatch[1].trim();

    const bssidMatch = l.match(/^BSSID\s+\d+\s*:\s*(.+)/);
    if (bssidMatch) currentNet.BSSID = bssidMatch[1].trim();
  }

  if (currentNet) networks.push(currentNet);
  return networks;
}

function getIpDiagnostics() {
  const diag = {
    "Nom d'hôte": os.hostname(),
    "IPv4 locale": "Non disponible",
    "Masque de sous-réseau": "",
    "Passerelle par défaut": "",
    "Adresse MAC": ""
  };

  const ipconfigOut = runCommand("ipconfig /all");
  const lines = ipconfigOut.split("\n");
  let wifiSection = false;

  for (const line of lines) {
    if (line.includes("Wi-Fi") || line.includes("sans fil")) wifiSection = true;
    else if (wifiSection && line.startsWith("Carte ")) wifiSection = false;

    if (wifiSection || diag["IPv4 locale"] === "Non disponible") {
      const ipv4Match = line.match(/Adresse IPv4[^\:]*:\s*([\d\.]+)/);
      if (ipv4Match) diag["IPv4 locale"] = ipv4Match[1].trim();

      const maskMatch = line.match(/Masque de sous-réseau[^\:]*:\s*([\d\.]+)/);
      if (maskMatch && !diag["Masque de sous-réseau"]) diag["Masque de sous-réseau"] = maskMatch[1].trim();

      const gwMatch = line.match(/Passerelle par défaut[^\:]*:\s*([\d\.]+)/);
      if (gwMatch && !diag["Passerelle par défaut"]) diag["Passerelle par défaut"] = gwMatch[1].trim();

      const macMatch = line.match(/Adresse physique[^\:]*:\s*([A-FA-f0-9\-]{17})/);
      if (macMatch && !diag["Adresse MAC"]) diag["Adresse MAC"] = macMatch[1].trim();
    }
  }

  return diag;
}

function displayCurrentWifi() {
  console.log(`${Colors.YELLOW}${Colors.BOLD}--- CONNEXION WIFI ACTUELLE ---${Colors.RESET}\n`);
  const info = getCurrentWifiInfo();
  if (!info) {
    console.log(`  ${Colors.RED}[!] Aucune connexion WiFi détectée.${Colors.RESET}\n`);
    return;
  }
  for (const [key, val] of Object.entries(info)) {
    if (key === "Signal (%)") {
      console.log(`  ${Colors.CYAN}${key.padEnd(26)}${Colors.RESET} : ${val} ${formatSignalBar(val)}`);
    } else if (key === "Mot de passe") {
      console.log(`  ${Colors.GREEN}${Colors.BOLD}${key.padEnd(26)}${Colors.RESET} : ${Colors.GREEN}${Colors.BOLD}${val}${Colors.RESET}`);
    } else {
      console.log(`  ${Colors.CYAN}${key.padEnd(26)}${Colors.RESET} : ${val}`);
    }
  }
  console.log();
}

function displaySavedPasswords() {
  console.log(`${Colors.YELLOW}${Colors.BOLD}--- PROFILS WIFI ET MOTS DE PASSE ENREGISTRÉS ---${Colors.RESET}\n`);
  const passwords = getAllWifiPasswords();
  if (passwords.length === 0) {
    console.log(`  ${Colors.RED}[!] Aucun profil trouvé.${Colors.RESET}\n`);
    return;
  }

  console.log(`  ${Colors.BOLD}${"#".padEnd(4)} ${"SSID / Nom du réseau".padEnd(32)} ${"Authentification".padEnd(20)} ${"Mot de passe".padEnd(25)}${Colors.RESET}`);
  console.log("  " + "─".repeat(83));

  passwords.forEach((p, idx) => {
    let ssid = p.SSID;
    if (ssid.length > 30) ssid = ssid.substring(0, 27) + "...";
    const pwdColor = p["Mot de passe"].startsWith("(") ? Colors.DIM : Colors.GREEN;
    console.log(`  ${Colors.CYAN}${String(idx + 1).padEnd(4)}${Colors.RESET} ${ssid.padEnd(32)} ${p.Authentification.padEnd(20)} ${pwdColor}${p["Mot de passe"].padEnd(25)}${Colors.RESET}`);
  });

  console.log(`\n  ${Colors.DIM}Total : ${passwords.length} réseaux enregistrés.${Colors.RESET}\n`);
}

function displayNearbyNetworks() {
  console.log(`${Colors.YELLOW}${Colors.BOLD}--- BALAYAGE DES RÉSEAUX WIFI ENVIRONNANTS ---${Colors.RESET}\n`);
  const networks = scanNearbyNetworks();
  if (networks.length === 0) {
    console.log(`  ${Colors.RED}[!] Aucun réseau environnant capté.${Colors.RESET}\n`);
    return;
  }

  console.log(`  ${Colors.BOLD}${"SSID / Réseau".padEnd(28)} ${"Signal".padEnd(18)} ${"Bande".padEnd(10)} ${"Canal".padEnd(8)} ${"Sécurité".padEnd(20)} ${"BSSID".padEnd(18)}${Colors.RESET}`);
  console.log("  " + "─".repeat(105));

  networks.forEach((net) => {
    let ssid = net.SSID;
    if (ssid.length > 26) ssid = ssid.substring(0, 23) + "...";
    const sigBar = formatSignalBar(net.Signal);
    console.log(`  ${Colors.CYAN}${ssid.padEnd(28)}${Colors.RESET} ${sigBar.padEnd(28)} ${(net.Bande || "2.4GHz").padEnd(10)} ${(net.Canal || "-").padEnd(8)} ${(net.Authentification || "Ouvert").padEnd(20)} ${(net.BSSID || "-").padEnd(18)}`);
  });

  console.log(`\n  ${Colors.DIM}Total : ${networks.length} réseaux détectés.${Colors.RESET}\n`);
}

function displayIpDiagnostics() {
  console.log(`${Colors.YELLOW}${Colors.BOLD}--- DIAGNOSTICS RÉSEAU & IP ---${Colors.RESET}\n`);
  const diag = getIpDiagnostics();
  for (const [k, v] of Object.entries(diag)) {
    console.log(`  ${Colors.CYAN}${k.padEnd(26)}${Colors.RESET} : ${Colors.BOLD}${v}${Colors.RESET}`);
  }
  console.log();
}

function exportReport() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const filename = `wifi_report_${timestamp}.json`;
  const data = {
    timestamp: new Date().toLocaleString(),
    current_connection: getCurrentWifiInfo(),
    saved_passwords: getAllWifiPasswords(),
    nearby_networks: scanNearbyNetworks(),
    ip_diagnostics: getIpDiagnostics()
  };

  fs.writeFileSync(filename, JSON.stringify(data, null, 2), "utf-8");
  console.log(`  ${Colors.GREEN}${Colors.BOLD}[✓] Rapport exporté vers : ${filename}${Colors.RESET}\n`);
}

function main() {
  printBanner();
  const args = process.argv.slice(2);

  if (args.includes("--passwords") || args.includes("-p")) {
    displaySavedPasswords();
  } else if (args.includes("--scan") || args.includes("-s")) {
    displayNearbyNetworks();
  } else if (args.includes("--ip") || args.includes("-i")) {
    displayIpDiagnostics();
  } else if (args.includes("--export") || args.includes("-e")) {
    exportReport();
  } else if (args.includes("--all") || args.includes("-a")) {
    displayCurrentWifi();
    displaySavedPasswords();
    displayNearbyNetworks();
    displayIpDiagnostics();
  } else {
    displayCurrentWifi();
    displaySavedPasswords();
    console.log(`  ${Colors.DIM}Astuce : Utilisez node wifi_info.js --all | --passwords | --scan | --ip | --export${Colors.RESET}\n`);
  }
}

main();

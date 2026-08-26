/**
 * Script Node.js pour afficher les informations du réseau WiFi connecté.
 * Fonctionne sur Windows uniquement.
 *
 * Usage : node wifi_info.js
 */

const { execSync } = require("child_process");

function runCommand(command) {
  try {
    return execSync(command, { encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }).trim();
  } catch (e) {
    return e.stdout ? e.stdout.trim() : `Erreur: ${e.message}`;
  }
}

function getCurrentWifi() {
  const output = runCommand("netsh wlan show interfaces");
  if (output.includes("Aucun") || output.toLowerCase().includes("disconnected")) {
    return null;
  }
  return output;
}

function getWifiProfiles() {
  const output = runCommand("netsh wlan show profiles");
  const matches = output.match(/:\s*(.+)/g);
  if (!matches) return [];
  return matches.map((m) => m.replace(/:\s*/, "").trim());
}

function getWifiProfileDetail(profileName) {
  return runCommand(`netsh wlan show profile name="${profileName}" key=clear`);
}

function parseInfo(output, patterns) {
  const info = {};
  for (const [key, regex] of Object.entries(patterns)) {
    const match = output.match(regex);
    if (match) {
      info[key] = match[1].trim();
    }
  }
  return info;
}

function main() {
  console.log("=".repeat(55));
  console.log("       INFORMATIONS WIFI - Script Node.js");
  console.log("=".repeat(55));

  // Connexion WiFi actuelle
  const interfaceOutput = getCurrentWifi();

  if (!interfaceOutput) {
    console.log("\n[!] Aucune connexion WiFi détectée.");
    console.log("    Vérifiez que le WiFi est activé et connecté.\n");
  } else {
    console.log("\n--- Connexion WiFi actuelle ---\n");

    const interfacePatterns = {
      "Nom du profil": /Nom du profil\s*:\s*(.+)/,
      "SSID": /SSID\s*:\s*(.+)/,
      "État": /État\s*:\s*(.+)/,
      "Type de réseau": /Type de réseau\s*:\s*(.+)/,
      "Type d'authentification": /Type d'authentification\s*:\s*(.+)/,
      "Chiffrement": /Chiffrement\s*:\s*(.+)/,
      "BSSID": /BSSID\s*:\s*(.+)/,
      "Type de signal": /Type de signal\s*:\s*(.+)/,
      "Qualité du signal": /Qualité du signal\s*:\s*(.+)/,
      "Réception (Mbps)": /Réception\s*:\s*(.+)/,
      "Transmission (Mbps)": /Transmission\s*:\s*(.+)/,
    };

    const info = parseInfo(interfaceOutput, interfacePatterns);
    if (Object.keys(info).length > 0) {
      for (const [key, value] of Object.entries(info)) {
        console.log(`  ${key.padEnd(30)} : ${value}`);
      }
    } else {
      console.log("  Impossible de parser les informations.");
      console.log("  Sortie brute :");
      console.log(interfaceOutput);
    }
  }

  // Profils enregistrés
  console.log("\n--- Profils WiFi enregistrés ---\n");
  const profiles = getWifiProfiles();
  if (profiles.length > 0) {
    profiles.forEach((p, i) => console.log(`  ${i + 1}. ${p}`));
  } else {
    console.log("  Aucun profil trouvé.");
  }

  // Détails du profil connecté
  if (interfaceOutput) {
    const profileMatch = interfaceOutput.match(/Nom du profil\s*:\s*(.+)/);
    if (profileMatch) {
      const currentProfile = profileMatch[1].trim();
      console.log(`\n--- Détails du profil connecté : ${currentProfile} ---\n`);

      const detailOutput = getWifiProfileDetail(currentProfile);
      const detailPatterns = {
        "Type d'authentification": /Type d'authentification\s*:\s*(.+)/,
        "Chiffrement": /Chiffrement\s*:\s*(.+)/,
        "Clé de sécurité": /Contenu de la clé\s*:\s*(.+)/,
      };

      const detail = parseInfo(detailOutput, detailPatterns);
      if (Object.keys(detail).length > 0) {
        for (const [key, value] of Object.entries(detail)) {
          console.log(`  ${key.padEnd(30)} : ${value}`);
        }
      } else {
        console.log("  Impossible de récupérer les détails.");
      }
    }
  }

  console.log("\n" + "=".repeat(55));
  console.log("  Script terminé.");
  console.log("=".repeat(55));
}

main();

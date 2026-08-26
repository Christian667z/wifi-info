import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  Alert,
  Linking,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import NetInfo from "@react-native-community/netinfo";

let WifiManager = null;
try {
  WifiManager = require("react-native-wifi-reborn").default;
} catch (e) {
  console.log("WiFi module non disponible");
}

export default function App() {
  const [wifiInfo, setWifiInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connectionType, setConnectionType] = useState("unknown");

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setConnectionType(state.type);
      if (state.type === "wifi" && state.details) {
        setWifiInfo({
          ssid: state.details.ssid || "Non disponible",
          bssid: state.details.bssid || "Non disponible",
          strength: state.details.strength || "N/A",
          ipAddress: state.details.ipAddress || "Non disponible",
          subnet: state.details.subnet || "Non disponible",
          frequency: state.details.frequency
            ? `${state.details.frequency} MHz`
            : "N/A",
          linkSpeed: state.details.linkSpeed
            ? `${state.details.linkSpeed} Mbps`
            : "N/A",
          rxSpeed: state.details.rxLinkSpeed
            ? `${state.details.rxLinkSpeed} Mbps`
            : "N/A",
          txSpeed: state.details.txLinkSpeed
            ? `${state.details.txLinkSpeed} Mbps`
            : "N/A",
          isConnectionExpensive: state.isConnectionExpensive ? "Oui" : "Non",
        });
        setError(null);
      } else if (state.type !== "wifi") {
        setWifiInfo(null);
      }
    });

    return () => unsubscribe();
  }, []);

  const fetchDetailedInfo = async () => {
    setLoading(true);
    setError(null);

    try {
      if (Platform.OS === "android" && WifiManager) {
        const ssid = await WifiManager.getCurrentWifiSSID();
        const bssid = await WifiManager.getBSSID();
        const signal = await WifiManager.getCurrentSignalStrength();
        const ip = await WifiManager.getIP();

        setWifiInfo((prev) => ({
          ...prev,
          ssid: ssid || prev?.ssid || "Non disponible",
          bssid: bssid || prev?.bssid || "Non disponible",
          signalStrength: signal || "N/A",
          ipAddress: ip || prev?.ipAddress || "Non disponible",
        }));
      } else if (Platform.OS === "ios") {
        Alert.alert(
          "iOS",
          "Sur iOS, les informations WiFi détaillées sont limitées par le système. Les données affichées proviennent de NetInfo."
        );
      }
    } catch (err) {
      setError(`Erreur: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openLocationSettings = () => {
    Alert.alert(
      "Localisation requise",
      "Pour accéder au SSID WiFi, la localisation doit être activée. Voulez-vous ouvrir les paramètres ?",
      [
        { text: "Annuler", style: "cancel" },
        { text: "Ouvrir", onPress: () => Linking.openSettings() },
      ]
    );
  };

  const isConnectedToWifi = connectionType === "wifi";

  return (
    <View style={styles.container}>
      <StatusBar style="light" />

      <View style={styles.header}>
        <Text style={styles.title}>WiFi Info</Text>
        <Text style={styles.subtitle}>Informations réseau en temps réel</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Statut de connexion */}
        <View
          style={[
            styles.statusCard,
            isConnectedToWifi ? styles.statusConnected : styles.statusDisconnected,
          ]}
        >
          <Text style={styles.statusIcon}>{isConnectedToWifi ? "✓" : "✗"}</Text>
          <Text style={styles.statusText}>
            {isConnectedToWifi ? "Connecté au WiFi" : "Non connecté au WiFi"}
          </Text>
          <Text style={styles.statusDetail}>
            Type: {connectionType === "wifi" ? "WiFi" : connectionType === "cellular" ? "Données mobiles" : connectionType}
          </Text>
        </View>

        {/* Informations WiFi */}
        {isConnectedToWifi && wifiInfo ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Détails de la connexion</Text>

            <InfoRow label="SSID (Réseau)" value={wifiInfo.ssid} />
            <InfoRow label="BSSID (Routeur)" value={wifiInfo.bssid} />
            <InfoRow label="Adresse IP" value={wifiInfo.ipAddress} />
            <InfoRow label="Sous-réseau" value={wifiInfo.subnet} />
            <InfoRow label="Fréquence" value={wifiInfo.frequency} />
            <InfoRow label="Vitesse liaison" value={wifiInfo.linkSpeed} />
            <InfoRow label="Vitesse réception" value={wifiInfo.rxSpeed} />
            <InfoRow label="Vitesse émission" value={wifiInfo.txSpeed} />
            <InfoRow label="Signal" value={wifiInfo.strength !== "N/A" ? `${wifiInfo.strength}%` : "N/A"} />
            <InfoRow label="Connexion coûteuse" value={wifiInfo.isConnectionExpensive} />
          </View>
        ) : isConnectedToWifi ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Connexion WiFi détectée</Text>
            <Text style={styles.infoText}>
              Connecté au WiFi mais les détails ne sont pas encore chargés.
              Appuyez sur "Actualiser" pour récupérer les informations.
            </Text>
          </View>
        ) : (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Aucune connexion WiFi</Text>
            <Text style={styles.infoText}>
              Connectez-vous à un réseau WiFi pour voir les informations.
            </Text>
          </View>
        )}

        {/* Erreur */}
        {error && (
          <View style={styles.errorCard}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Boutons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.button}
            onPress={fetchDetailedInfo}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Actualiser</Text>
            )}
          </TouchableOpacity>

          {Platform.OS === "android" && (
            <TouchableOpacity
              style={[styles.button, styles.buttonSecondary]}
              onPress={openLocationSettings}
            >
              <Text style={styles.buttonText}>Paramètres localisation</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Note de sécurité */}
        <View style={styles.noteCard}>
          <Text style={styles.noteTitle}>Note</Text>
          <Text style={styles.noteText}>
            Sur Android, la localisation doit être activée pour accéder au SSID.
            Sur iOS, les informations sont limitées par les restrictions du système.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

function InfoRow({ label, value }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value || "N/A"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f0f23",
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    backgroundColor: "#1a1a2e",
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#00d4ff",
  },
  subtitle: {
    fontSize: 14,
    color: "#888",
    marginTop: 4,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  statusCard: {
    padding: 20,
    borderRadius: 16,
    alignItems: "center",
    marginBottom: 16,
  },
  statusConnected: {
    backgroundColor: "#0a3d0a",
    borderWidth: 1,
    borderColor: "#00ff88",
  },
  statusDisconnected: {
    backgroundColor: "#3d0a0a",
    borderWidth: 1,
    borderColor: "#ff4444",
  },
  statusIcon: {
    fontSize: 36,
    color: "#fff",
    marginBottom: 8,
  },
  statusText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#fff",
  },
  statusDetail: {
    fontSize: 13,
    color: "#aaa",
    marginTop: 4,
  },
  section: {
    backgroundColor: "#1a1a2e",
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#00d4ff",
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#2a2a4a",
  },
  infoLabel: {
    fontSize: 14,
    color: "#aaa",
    flex: 1,
  },
  infoValue: {
    fontSize: 14,
    color: "#fff",
    fontWeight: "600",
    flex: 1,
    textAlign: "right",
  },
  infoText: {
    fontSize: 14,
    color: "#888",
    lineHeight: 20,
  },
  buttonContainer: {
    gap: 12,
    marginBottom: 16,
  },
  button: {
    backgroundColor: "#00d4ff",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  buttonSecondary: {
    backgroundColor: "#2a2a4a",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "bold",
  },
  errorCard: {
    backgroundColor: "#3d0a0a",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#ff4444",
  },
  errorText: {
    color: "#ff6666",
    fontSize: 14,
  },
  noteCard: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 16,
    marginBottom: 40,
  },
  noteTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#ffaa00",
    marginBottom: 8,
  },
  noteText: {
    fontSize: 13,
    color: "#888",
    lineHeight: 20,
  },
});

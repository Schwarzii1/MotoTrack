Da wir einen Virtuellen Computer von Azure nutzen, ist es wichtig, diesen ausreichend abzusichern. Dieser ist durch eine öffentliche IP-Adresse identifizierbar. 
Unsere Firewall-Konfiguration setzt sich somit aus folgenden Regeln zusammen:

# Aktivieren von Logging
set loginterface pflog0

# Standardrichtlinien: Alles blockieren
block in all
block out all

# Erlaube eingehende Verbindungen auf bestimmten Ports (z. B. SSH und HTTPS)
pass in on egress proto tcp to any port 22  # SSH
pass in on egress proto tcp to any port 80  # HTTP

# Erlaube ausgehende Verbindungen für spezifische Protokolle
pass out on egress proto tcp to any port 80  # HTTP

# Rate-Limiting (z. B. für SSH, um Brute-Force-Angriffe zu erschweren)
pass in on egress proto tcp to any port 22 flags S/SA keep state (max-src-conn-rate 15/60)

# Blockiere ICMP-Pings (Ping-Anfragen blockieren)
block in proto icmp icmp-type 8 code 0

# Logging spezifischer Verbindungen
block log on egress from any to 192.168.1.0/24

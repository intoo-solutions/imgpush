# 📊 Stack locale pour travailler sur les métriques

Ce répertoire contient un certain nombre de fichiers de configuration et un fichier Docker Compose permettant de monter un stack avec les outils suivants :

## Services

### Grafana
- **Image Docker** : `grafana/grafana-enterprise`
- **Port** : 53000
- Utilisé pour visualiser les données de monitoring et les alertes.

### Prometheus
- **Image Docker** : `prom/prometheus`
- **Port** : 59090
- Collecte les métriques et évalue les règles d'alerte.

### Alertmanager
- **Image Docker** : `prom/alertmanager`
- **Port** : 59093
- Gère les alertes envoyées par Prometheus.

### imgpush
- **Instances** :
  - **Production Client 1** : Port 55000
  - **Staging Client 1** : Port 55001
  - **Staging Client 2** : Port 55002
  - **Production Client 2** : Port 55003
- Service de gestion d'images avec des configurations spécifiques pour chaque environnement.

### Metrics Rebuilder
- **Image Docker** : `intoo/imgpush:0.2.0`
- Utilisé pour reconstruire les métriques à partir des données existantes.

## Fichiers de Configuration

### alerts.yml
Contient les règles d'alerte pour Prometheus, incluant des alertes pour la détection de fichiers, le taux de téléversement inhabituel, et l'utilisation élevée du disque.

### alertmanager.yml
Configure Alertmanager, y compris les routes d'alerte, les récepteurs (comme Discord), et les templates pour les notifications.

### prometheus.yml
Définit la configuration de Prometheus, y compris l'intervalle de scrutation, les jobs de scrutation pour différents environnements, et les fichiers de règles d'alerte.

## Volumes

- **grafana-storage** : Stocke les données persistantes de Grafana.
- **prometheus-storage** : Stocke les données persistantes de Prometheus.
- **alertmanager-storage** : Stocke les données persistantes d'Alertmanager.

## Réseau

- **imgpush** : Un réseau Docker dédié pour faciliter la communication entre les services.
# 📊 Stack locale pour travailler sur les métriques

Ce répertoire contient un certain nombre de fichiers de configuration et un fichier Docker Compose permettant de monter un stack avec les outils suivants :

## ❓ Comment utiliser ce stack ?

1. Assurez-vous d'avoir Docker et Docker Compose installés sur votre machine.
2. Lancez le stack en utilisant la commande suivante :

```bash
docker-compose up
```

## 🤔 Et ensuite ?

1. Configurer Grafana pour utiliser Prometheus comme source de données.
   Adresse à utiliser: `http://prometheus:9090`
2. Importer les dashboards situés dans le répertoire [dashboards](./dashboards/) dans Grafana.
3. Visualisez les métriques et les alertes dans Grafana.

### 🚨 Pour déclencher des alertes

Rendez-vous dans le répertoire [load-testing](./load-testing/) et lisez le [README](./load-testing/README.md) associé :)

## 🍙 Services

### Grafana

- **Image Docker** : `grafana/grafana-enterprise`
- **Port** : 53000
- Utilisé pour visualiser les données de monitoring et les alertes.

### Prometheus

- **Image Docker** : `prom/prometheus`
- **Port** : 59090
- Collecte les métriques et évalue les règles d'alerte.

### Prometheus Alertmanager

- **Image Docker** : `prom/alertmanager`
- **Port** : 59093
- Gère les alertes envoyées par Prometheus.

### imgpush

- **Instances** :
  - **Production Client 1** : Port 55000
  - **Staging Client 1** : Port 55001
  - **Staging Client 2** : Port 55002
  - **Production Client 2** : Port 55003
- Instances d'imgpush, certains configurées pour utiliser S3, d'autres utilisant le système de fichiers

## 📁 Fichiers de configuration

### `alerts.yml`

Contient les règles d'alerte pour Prometheus, incluant des alertes pour la détection de fichiers, le taux de téléversement inhabituel, et l'utilisation élevée du disque.

### `alertmanager.example.yml`

Fichier d'exemple de configuration Alertmanager, y compris les routes d'alerte, les récepteurs (comme Discord), et les templates pour les notifications.

> **Note** : Pour utiliser ce fichier, copiez-le en `alertmanager.yml` et modifier l'adresse du webhook Discord.

### `prometheus.yml`

Définit la configuration de Prometheus, les configurations de scraping pour différents environnements, et les fichiers de règles d'alerte.

## Volumes

- **grafana-storage** : Stocke les données persistantes de Grafana.
- **prometheus-storage** : Stocke les données persistantes de Prometheus.
- **alertmanager-storage** : Stocke les données persistantes d'Alertmanager.

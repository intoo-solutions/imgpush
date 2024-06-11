---
title: "Prod - HowTo mettre en place imgpush en production"
draft: false
tags: ["imgpush", "howto", "setup"]
---

# 🚀 Mettre en place imgpush en production

Ce document décrit comment mettre en place imgpush en production.

## 📦 Prérequis

### Si vous comptez utiliser S3

- Un compte sur le provider S3 de votre choix
- Les credentials S3 (access key, secret key) pour ce compte
- Un bucket S3 prêt à l'emploi

### Si vous comptez utiliser le filesystem

- Un serveur avec un système de fichiers accessible en écriture
- Suffisamment d'espace disque pour stocker les fichiers

## 🛠 Installation

L'image Docker `intoo/imgpush` est disponible sur [Docker Hub](https://hub.docker.com/r/intoo/imgpush).

[Pour l'utiliser, voici un exemple de fichier Docker Compose](../docker-compose.yml)

Pour l'intégrer à un projet existant, vous pouvez ajouter un (ou des) service(s) dans votre fichier `docker-compose.yml`

Les services à ajouter dépendent de votre configuration (S3 ou filesystem).

### ☁️ Avec S3

```yaml
services:
  # Vos autres services

  imgpush:
    image: intoo/imgpush:0.2.0 # Remplacer par la dernière version
    environment:
      - S3_ENDPOINT=<votre URL S3>
      - S3_ACCESS_KEY_ID=<votre access key>
      - S3_SECRET_ACCESS_KEY=<votre secret key>
      - S3_BUCKET_NAME=<votre bucket>
      - S3_FOLDER_NAME=<votre dossier> # Optionnel
    ports:
      - "<votre port>:5000"
    volumes:
      - imgpush-metrics:/metrics

  # Ce service va démarrer, reconstruire les métriques à partir d'un bucket S3, les stocker dans un fichier dans le volume imgpush-metrics, puis s'arrêter
  imgpush-metrics-rebuilder:
    image: intoo/imgpush:0.2.0 # Remplacer par la dernière version
    environment:
      - REBUILD_METRICS=true
      - S3_METRICS_REBUILDER_THREAD_COUNT=<nombre de threads à utiliser pour la reconstruction des métriques> # 4 par défaut
      - S3_ENDPOINT=<votre URL S3>
      - S3_ACCESS_KEY_ID=<votre access key>
      - S3_SECRET_ACCESS_KEY=<votre secret key>
      - S3_BUCKET_NAME=<votre bucket>
      - S3_FOLDER_NAME=<votre dossier> # Optionnel
    volumes:
      - imgpush-metrics:/metrics

volumes:
  imgpush-metrics:
```

### 📁 Avec le filesystem

```yaml
services:
  # Vos autres services

  imgpush:
    image: intoo/imgpush:0.2.0 # Remplacer par la dernière version
    environment:
      - FILES_DIR=<votre dossier> # /files par défaut
    ports:
      - "<votre port>:5000"
    volumes:
      - <votre dossier>:<chemin donné à FILES_DIR> # Exemple: ./files:/files
```

### ❇️ Variables d'environnement

[Les variables d'environnement suivantes sont disponibles pour configurer imgpush](../README.md#configuration)

Parmi les plus importantes que l'on ne retrouve pas dans l'exemple de Docker Compose ci-dessus, on peut citer :

| Variable                | Description                                                           |
| ----------------------- | --------------------------------------------------------------------- |
| ALLOWED_MIME_FILE_TYPES | Types MIME autorisés à être uploadés                                  |
| MAX_SIZE_MB             | Taille maximale des fichiers uploadés en mégaoctets                   |
| NAME_STRATEGY           | Stratégie de nommage des fichiers uploadés (`randomstr`, ou `uuidv4`) |
| METRICS_FILE_PATH       | Chemin d'accès au fichier de métriques                                |
| OUTPUT_TYPE             | Format vers lequel convertir les images uploadées                     |

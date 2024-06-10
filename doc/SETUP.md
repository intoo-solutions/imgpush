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

### ☁️ Avec S3

L'image Docker `intoo/imgpush` est disponible sur [Docker Hub](https://hub.docker.com/r/intoo/imgpush).

[Pour l'utiliser, voici un exemple de fichier Docker Compose](../docker-compose.yml)

Pour l'intégrer à un projet existant, vous pouvez ajouter un service dans votre fichier `docker-compose.yml` :

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
      - "8080:8080"
    volumes:
      - imgpush-metrics:/metrics

  imgpush-metrics-rebuilder:
    image: intoo/imgpush:0.2.0 # Remplacer par la dernière version
    environment:
      - REBUILD_METRICS=true
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

[Les variables d'environnement suivantes sont disponibles pour configurer imgpush](../README.md#configuration)

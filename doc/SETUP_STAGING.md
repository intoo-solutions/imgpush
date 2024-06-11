---
title: "HowTo mettre en place imgpush en staging"
draft: false
tags: ["imgpush", "howto", "setup"]
---

# 🚀 Mettre en place imgpush dans les environnements de staging

Ce document décrit comment mettre en place imgpush dans un environnement de staging.

## ⚠️ Important

Avant de lire ce document, assurez-vous d'avoir lu le [guide de mise en place en production](SETUP_PROD.md).

Si vous comptez utiliser le filesystem en staging, ce guide de mise en production est suffisant.

En revanche, si vous comptez utiliser S3 pour l'environnement de staging, la différence majeure avec le guide de production est l'utilisation d'un unique bucket pour tout les projets, et donc l'utilisation de sous-dossiers pour séparer les données des différents projets.

## 🛠 Installation

### ☁️ Avec S3

Dans les environnements de staging, il est préférable d'utiliser le même bucket, et de séparer les données des différents projets via des sous-dossiers.

```yaml
services:
  # Vos autres services

  imgpush:
    image: intoo/imgpush:0.2.0 # Remplacer par la dernière version
    environment:
      - S3_ENDPOINT=<votre URL S3>
      - S3_ACCESS_KEY_ID=<votre access key>
      - S3_SECRET_ACCESS_KEY=<votre secret key>
      - S3_BUCKET_NAME=<votre bucket> # le bucket de staging intoo
      - S3_FOLDER_NAME=<nom du projet> # eg. nobi, seculib, etc
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
      - S3_BUCKET_NAME=<votre bucket> # le bucket de staging intoo
      - S3_FOLDER_NAME=<nom du projet> # eg. nobi, seculib, etc
    volumes:
      - imgpush-metrics:/metrics

volumes:
  imgpush-metrics:
```

### 📁 Avec le filesystem

Aucune configuration spécifique n'est requise pour utiliser le filesystem.

---
title: "HowTo - Guide pour développer sur imgpush"
draft: false
tags: ["imgpush", "howto", "dev"]
---

# 👨‍💻 Guide pour développeur

Lorsque vous travaillez sur imgpush, vous pouvez utiliser le fichier docker-compose.yml fourni. Ce fichier comporte deux services:

1. `imgpush`: le service principal qui expose l'API REST sur le port 5000.
2. `metrics-rebuilder`: un service qui permet de reconstruire les métriques de l'application à partir d'un bucket S3 existant.

Pour démarrer le service, vous devez avoir installé Docker et Docker Compose sur votre machine (ou Docker Desktop si vous êtes sur Windows, avec WSL). Vous pouvez suivre les instructions d'installation sur le site officiel de Docker.

Ensuite, pour configurer votre imgpush local, vous pouvez suivre les étapes suivantes:

1. Copier le fichier d'exemple `.env.example` en `.env`:

```bash
wsl -e cp .env.example .env
```

Ensuite, utilisez votre éditeur de texte préféré pour modifier les variables d'environnement dans le fichier `.env`:

Par exemple, avec Visual Studio Code:

```bash
code .env
```

Enfin, vous pouvez démarrer les services avec la commande suivante:

```bash
docker compose up
```

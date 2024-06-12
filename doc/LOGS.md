---
title: "HowTo - Comment lire les logs d'imgpush"
draft: false
tags: ["imgpush", "howto", "logs"]
---

# 📰 Comment lire les logs d'imgpush

## 🛳️ Si vous avez ajouté un service dans votre Docker Compose

Il vous suffit d'effectuer la commande suivante pour lire les logs de votre service :

```bash
docker compose logs <nom du service>
```

**➡️ Exemple**

`docker compose logs nobi-imgpush`

## 💻 Si vous êtes en développemennt local d'imgpush

Il vous suffit d'effectuer la commande suivante pour lire les logs de votre service :

```bash
docker compose logs
```

## ⏩ Si vous avez lancé imgpush avec `docker run`

Il vous suffit d'effectuer la commande suivante pour lire les logs de votre service :

```bash
docker logs <nom du container>
```

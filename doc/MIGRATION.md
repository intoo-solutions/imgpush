---
title: "HowTo - Migration des données"
draft: false
tags: ["imgpush", "howto", "s3", "migration"]
---

# 🚚 Migration des données

## Utilisation de du CLI AWS (fonctionne uniquement avec AWS S3)

Si vous souhaitez migrer de l'utilisation du système de fichiers vers S3, vous pouvez utiliser le CLI d'AWS pour copier les fichiers vers S3. La commande pour copier les fichiers est la suivante :

```bash
aws s3 cp SOURCE_DIR s3://DEST_BUCKET/ --recursive
```

## 🤖 Utilisation de rclone

Si vous utilisez un autre fournisseur que AWS, l'utilisation du CLI AWS n'est pas une option. Dans ce cas, vous pouvez utiliser `rclone` pour copier les fichiers vers votre fournisseur.

### ⚙️ Configuration de rclone

Tout d'abord, vous devrez configurer rclone pour utiliser votre fournisseur. Vous pouvez le faire en exécutant :

```bash
rclone config
```

Cela ouvrira un assistant qui vous guidera tout au long du processus de configuration.
Certains fournisseurs peuvent nécessiter une configuration supplémentaire ou des options spécifiques. Vous trouverez plus d'informations dans leur documentation. Par exemple, Cloudflare R2 a [cette page de documentation](https://developers.cloudflare.com/r2/examples/rclone/) qui explique comment configurer rclone pour Cloudflare R2.

### 🗃️ Copie des fichiers

Ensuite, vous pouvez copier les fichiers en utilisant la commande suivante :

```bash
rclone copy SOURCE_DIR PROVIDER_NAME:PATH
```

Par exemple, si vous utilisez R2 et avez ajouté une configuration nommée `r2`, vous pouvez copier les fichiers en utilisant :

```bash
rclone copy /chemin/vers/fichier r2:/nom-du-bucket/sous-dossier --recursive # pour Cloudflare R2
```

> [!WARNING]  
> N'ajoutez `/nom-du-bucket` que si l'endpoint que vous avez configuré dans rclone ne le contient pas déjà. Si c'est le cas, vous devez le supprimer du chemin, car cela créerait sinon un sous-dossier avec le nom du bucket à l'intérieur de votre bucket.

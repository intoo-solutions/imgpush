---
title: "User Stories"
draft: false
tags: ["imgpush", "stories"]
---

# 📖 Stories

Ce document comporte un ensemble de stories (aussi bien du point de vue de l'éditeur / hébergeur, que de l'utilisateur).

## 💻📦 Stories côté éditeur

### 1️⃣ US-1 - Je dois maîtriser mes coûts ✅

**En tant qu**'éditeur & hébergeur de la solution Follo

**Je veux** une solution pour stocker de nombreuses images & fichiers pas chère et qui scale bien avec le volume

**Afin de** maîtriser mes coûts quand le volume va augmenter

### 2️⃣ US-2 - Je dois m'intégrer à Seculib ✅

**En tant qu**'éditeur & hébergeur de la solution imgpush qui va être intégrée dans Seculib

**Je veux** une solution pour stocker de nombreuses images & fichiers résiliante, qui s'adapte à l'architecture choisie pour Séculib

**Afin de** pouvoir l'intégrer à Séculib, qui va devoir être scalé horizontalement, et pour laquelle on essaye d'utiliser des solutions SaaS cloud sans exploser le budget

> C'est un peu la même que l'US-1, mais là j'y rajoute les enjeux Seculib, qui sera pas déployé comme Follo. En gros ça veut dire qu'on doit utiliser un service cloud

### 3️⃣ US-3 - Refacturation ✅

**En tant qu**'utilisateur de la solution imgpush

**Je veux** un outil qui me permet de visualiser l'état des éléments pour lesquels je paie (ici, l'espace disque/le volume de données stockées)

**Afin de** pouvoir éventuellement refacturer à mon client

### 4️⃣ US-4 - Monitoring ✅

**En tant qu**'utilisateur de la solution imgpush

**Je veux** un outil qui me permet de visualiser l'évolution des éléments que je paye/consomme (ici, l'espace disque/le volume de données stockées), et qui m'alerte s'il dépasse un seuil ou accélère trop vite

**Afin d**'anticiper un problème (explosion des coûts, plus de stockage... )

> En tant qu'administrateur système, je veux stocker des milliers (voire des millions) de fichiers sans risquer d'atteindre une limite de stockage

> Vendredi 16h, je dois pouvoir vérifier que ça va pas atteindre un quota dans les prochaines 24 heures parce que dans 24h je serais à la plage

### 5️⃣ US-5 - Flexibilité ✅

**En tant qu**'éditeur de la solution imgpush

**Je veux** que le code me permette d'utiliser un autre hébergeur que S3 **sans changer le comportement**, et ne pas perdre la capacité de stockage disque actuelle

**Afin d**'être flexible et de répondre aux besoin de développement local et des clients (un client qui choisirait de ne pas utiliser AWS S3 car c'est américain)

### 6️⃣ US-6 - Fail fast ✅

**En tant qu**'utilisateur de la solution imgpush

**Je veux** que si je configure mal ça plante direct et pas à la première utilisation

**Afin de** ne être supris plus tard, ne pas avoir d'astreinte à gérer, ...

## 🧑‍🦱👩‍🦱 Stories côté utilisateur

### 7️⃣ US-7 - Proxy ✅

**En tant qu**'utilisateur parano,

**Je veux** que mes images soit servies par un domaine que j'ai whitelist

**Afin de** ne pas être bloqué par mon Adblock qui filtre les sites américains (US)

> Solution
>
> Proxifier la récupération des fichiers

### 8️⃣ US-8 - Redimensionnement ✅

**En tant qu**'utilisateur,

**Je veux** uploader n'importe quelle image à partir de mon téléphone et la recharger rapidement pour prévisualisation

**Afin de** ne pas perdre de temps

> Solution
>
> Proposer de redimensionner les images à la volée à l'aide de query params

### 9️⃣ US-9 - Je dois pouvoir migrer ✅

**En tant qu**'utilisateur de la solution imgpush actuelle

**Je veux** une procédure pour passer de imgpush-filesystem à imgpush-s3

**Afin de** migrer sans problèmes, ni pertes, ni doutes

### 1️⃣0️⃣ US-10 - Je dois configurer et documenter ⌛

**En tant qu**'utilisateur de la solution imgpush

**Je veux** pouvoir le mettre en place de façon maitrisée sur la prod, mais de façon simple pour mes env de qualif

**Afin de** simplifier la mise en place des env de qualif, car je vais en avoir beaucoup (au moins 15 chez Intoo)

> Ça, c'est les dossiers sur S3

> Et un manuel sur comment on fait ! Il faut une doc qui permette à Archi, Clément, les 2 Pierres de mettre en places imgpush s3 sur un projet, de l'env de dev du développeur jusqu'à la prod

> En tant qu'admin-sys, je veux configurer un bucket dédié à l'environement de staging

> En tant qu'admin-sys, je veux vider complètement un bucket pour réinitialiser les données (par ex en staging / recette)

> On ne commit pas les credentials du bucket prod

### 1️⃣1️⃣ US-11 - Je dois être paré légalement

**En tant que** plateforme de mise en relation

**Je veux** garantir aux agences partenaires et services de police que je leur fournit les images exactes stockées au moment de l'intervention

**Afin de** ne pas avoir de problème en cas de litige

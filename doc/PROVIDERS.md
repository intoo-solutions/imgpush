---
title: "Reference - Liste des providers S3"
draft: false
tags: ["imgpush", "reference", "s3"]
---

# 🗃️ Liste des providers S3

Les principaux providers compatibles S3 sont les suivants :

- AWS S3
- Cloudflare R2
- Backblaze B2
- Wasabi
- Google Cloud Storage

## 💲 Coûts

D'une manière générale, le provider le moins coûteux est Backblaze B2, qui peut d'ailleurs être combiné à un CDN partenaire comme Cloudflare pour réduire les coûts de transfert à 0.
Les autres options abordables sont Cloudflare R2 et Wasabi.

Les deux options les plus chères sont AWS S3 et Google Cloud Storage, avec le second étant le plus cher des deux.

Voici un tableau comparatif sommaire représentant les coûts de stockage de données et de transfert de données pour chaque provider :

| Fournisseur                     | Coût de stockage ($/Go/mois) | Frais de transfert de données                |
| ------------------------------- | ---------------------------- | -------------------------------------------- |
| Google Cloud Storage Standard   | 0,026                        | Frais pour les données transférées en sortie |
| AWS S3 Standard                 | 0,023                        | Frais pour les données transférées en sortie |
| Azure Blob Storage Chaud        | 0,0184                       | Frais pour les données transférées en sortie |
| Cloudflare R2                   | 0,015                        | Transfert de données gratuit                 |
| OVH Standard Object Storage     | 0,0084                       | Transfert de données gratuit                 |
| Wasabi                          | 0,0069                       | Transfert de données gratuit                 |
| Backblaze B2                    | 0,005                        | Frais pour les données transférées en sortie |
| Backblaze B2 (combiné avec CDN) | 0,005                        | Transfert de données gratuit                 |

[La liste complète comparant les coûts de chaque provider est disponible ici](https://simplebackups.com/blog/cloud-storage-price-feature-comparison-the-best-providers-in-2023/)

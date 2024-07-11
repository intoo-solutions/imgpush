# ⚖️ Load testing

Ce répertoire contient des fichiers de configuration pour l'outil Ddosify, permettant de réaliser des tests de charge sur imgpush.

## 📁 Fichiers de configurations disponibles

| Nom du fichier      | Description                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `manual_load.yml`   | Charge définie manuellement, simulant des comportement avec des périodes de forte activité et des périodes de faible activité. |
| `constant_load.yml` | Charge constante, simulant une activité continue.                                                                              |

## ▶️ Comment lancer un test de charge

### ⌨️ Via CLI

1. Installer l'outil Ddosify en CLI en suivant les instructions de la [documentation officielle](https://github.com/getanteon/anteon?tab=readme-ov-file#anteon-load-engine-ddosify)
2. Modifier l'URL de la cible dans le fichier de configuration à utiliser.
3. Lancer un test de charge en utilisant la commande suivante :

```bash
ddosify -config <chemin_vers_fichier_de_configuration>
```

**Exemple**

```bash
ddosify -config manual_load.yml
```

### 🌐 Via l'interface web

1. Installer l'outil Anteon (formerly known as Ddosify) en suivant les instructions de la [documentation officielle](https://github.com/getanteon/anteon?tab=readme-ov-file#anteon-self-hosted)
2. Accéder à l'interface web de l'outil en ouvrant un navigateur et en accédant à l'URL suivante : `http://localhost:8014`
3. Dans Performance Test > New Test, créer un nouveau test en renseignant les informations nécessaires et le scénario à utiliser.
4. Lancer le test

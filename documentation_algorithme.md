# Description de l'algorithme

## 1. Création d'un "fichier" de données DataPass

https://github.com/betagouv/suivi_dtnum_datapass/blob/main/datapass_row_maker.py/#L21-L22

Pour coller à la forme du fichier de suivi DTNUM (qui hérite sa forme de la précédente version de datapass), chaque demande génère une ou plusieurs lignes :

- Si la demande n'a pas d'habilitation, et n'est pas en brouillon -> une ligne de demande
- Si la demande a une ou plusieurs habilitations :
  - une ligne par habilitation
  - une ligne supplémentaire pour la demande si elle est dans l'état "submitted", "changes_requested" ou "refused"


### 1.1. Correspondance des données

https://github.com/betagouv/suivi_dtnum_datapass/blob/main/datapass_row_maker.py#L43-L96

Chaque ligne créée va transformer les données de DataPass pour que le nom des attributs corresponde à des colonnes du fichier de suivi DTNUM.

Par exemple l'`id` d'une demande deviendra `"N° Demande v2"`, et l'id d'une habilitation deviendra `"N° Habilitation v2"`.

A noter que l'habilitation reprend tous les champs de la demande, et en écrase certains pour qu'ils correspondent aux données de l'habilitation elle-même, et non aux données de la demande qui a pu être réouverte depuis.

### 1.2. Correspondance aux labels de suivi DTNUM

https://github.com/betagouv/suivi_dtnum_datapass/blob/main/datapass_data_correspondances.py

La création d'une ligne de demande ou d'habilitation utilise plusieurs méthodes de correspondances de données, pour coller aux labels utilisés par le fichier de suivi DTNUM.

Vous pouvez toutes les retrouver dans le fichier `datapass_data_correspondances.py`, c'est assez lisible normalement.

A noter que la correspondance des cas d'usage est faite à l'aide d'expression régulières. C'est à dire que si `demande.form_uid` _contient_ `"cantine-scolaire"`, alors la correspondance sortira `"CITP - cantine scolaire"`. Cela permet de faire correspondre tous les formulaires contenant `"cantine-scolaire"`, que ce soit sandbox, éditeur ou production.

## 2. Fusion des données de suivi avec les données datapass

https://github.com/betagouv/suivi_dtnum_datapass/blob/main/data_merger.py#L15-L58

La fusion se passe en plusieurs étapes.

### 2.1. Fusion des demandes et habilitations

#### 2.1.1. On fusionne les demandes en cours et les habilitations existantes

Pour ce faire, si on trouve dans les deux fichiers des lignes avec :
- Soit `N° de demande v2` égal et `N° d'habilitation v2` vide
- Soit `N° de demande v2` égal et `N° d'habilitation v2` égal

Alors on fusionne les lignes des deux fichiers, et on les retire du stock.

#### 2.1.2. Puis on fusionne les demandes qui ont "gagné" une habilitation

Dans le stock restant, on cherche les lignes de suivi avec `N° de demande v2` et `N° d'habilitation v2` vide, qui correspondent à une ligne datapass avec le même `N° de demande v2` et `N° d'habilitation v2` non vide.

On fusionn ces lignes qui ont "gagné" une habilitation car leur instruction s'est terminée depuis la dernière éxecution du programme. Et on les retire du stock.

#### 2.1.3. On rajoute les nouvelles lignes datapass

On rajoute le stock restant de lignes datapass : Ce sont les nouvelles demandes qui ont été créées depuis la dernière exécution du programme.

#### 2.1.4. On rajoute les lignes de suivi qui restent

On rajoute le stock restant de lignes de suivi DTNUM : Ce sont des ID que l'on n'a pas trouvés dans datapass, on remplit donc la colonne `Erreurs` avec un message indiquant l'erreur.

#### 2.1.5 On renseigne les régions et départements manquants

Une fois qu'on a fini de créer les lignes du nouveau fichier de suivi, on en profite pour faire une repasse et remplir les données de régions et départements qui manquent.

On utilise l'API Adresse de data.gouv.fr pour renseigner ces colonnes, dont voici [la documentation](https://adresse.data.gouv.fr/outils/api-doc/adresse)

#### 2.1.6 On marque les lignes en doublons

On refait une passe sur le résultat pour identifier de potentiels doublons, et on inscrit l'erreur dans la colonne `Erreurs`.


## 2.2 Méthode de fusion

Lorsque l'on fusionne une ligne de suivi DTNUM avec une ligne de DataPass, on va privilégier les données de suivi ou les données datapass selon les colonnes.

[Voir la liste des données privilégiées de DataPass](https://github.com/betagouv/suivi_dtnum_datapass/blob/main/data_merger.py/#L6-L7). Pour toutes les colonnes qui ne sont pas dans cette liste, on privilégie les données du fichier de suivi DTNUM.

Pour la plupart des données provenant de DataPass, on va les privilégier pour écraser les informations du fichier de suivi. Mais il y a quelques cas particuliers pour lesquels on préfère utiliser la "mémoire" du fichier de suivi pour retenir certains informations :

**Modèle pré-rempli / cas d'usage** : Par ce que certains types de DataPass v1 n'existent pas dans datapass v2, nous n'écrasons pas cette colonne pour conserver l'information.

**Date de réception** : Cette date est remplie avec soit la date de réouverture de la demande, soit la date de soumission initiale. Lorsqu'une demande est réouverte, son habilitation précédente doit conserver sa date de réception. Nous n'écrasons donc pas cette information du fichier de suivi pour éviter de mettre à jour toutes les dates de réception des habilitations précédent une réouverture.

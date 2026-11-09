# Journal des publications

Le plus récent en tête.

## 2026-11-09 — Installateur fabriqué par ce dépôt (branche `claude/fabrication-publique`, non publiée)

- **Demande :** quota de minutes GitHub du dépôt privé épuisé ; Franck : « Mets l'option 2 en route » (fabrication
  dans les dépôts publics, sur des branches d'essai). **`main` inchangé**, rien n'est publié sans sa phrase explicite.
- **Réalisation :** `outils/fabriquer-appli.py` et action « Publier les mises à jour » : un travail Windows par canal
  fabrique l'installateur à partir de `coquille/<canal>/` et de la page du canal (empreinte contrôlée, repère d'essai
  ajouté comme dans `build/construire-appli.py`), le garde en cache ; la publication le range dans `appli/`, complète
  sa taille et son empreinte dans `entrees/<canal>.json`, puis assemble, signe et publie comme avant. `.gitattributes`
  (aucune conversion de fins de ligne sur Windows), `.gitignore`, `README.md`. Essai 4.1.0 repassé par le nouveau
  chemin depuis la branche source `claude/fabrication-publique` (= `claude/essai-4.1` + ce changement de procédure) : page
  identique à l'octet, installateur retiré du dépôt, coquille et fiches écrites.
- **Livraison :** branche `claude/fabrication-publique` seulement ; résultat de la fabrication : voir l'action de la
  branche.

## 2026-11-08 — Essai 4.1.0 (premier dépôt)

- Site créé : page de téléchargement, `outils/assembler.py`, `outils/signer-appli.py`, action « Publier les mises à jour ».
- Canal **essai** : application Windows 4.1.0 (`appli/essai/`) et `Vocabulaire.html` ; fichiers fabriqués par l'action
  « Application Windows » du dépôt Vocabulaire (commit source `3d522ac`, branche `claude/essai-4.1`).
- Installateur signé avant l'envoi (le secret `TAURI_SIGNING_PRIVATE_KEY` n'est pas encore en place) ; signature
  vérifiée avec la clé publique de l'application (`5A6B8F7FEFB192FF`). Aucun canal stable : rien n'est publié sans
  l'accord de Franck.
- Mis en place par Franck le même soir : GitHub Pages (source GitHub Actions) et secret `TAURI_SIGNING_PRIVATE_KEY`.
  Site en ligne vérifié à 23 h 20 : page de téléchargement, essai 4.1.0, `appli/essai/latest.json` signé (signature
  valide pour la clé de l'application).

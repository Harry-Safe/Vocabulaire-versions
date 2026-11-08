# Journal des publications

Le plus récent en tête.

## 2026-11-08 — Essai 4.1.0 (premier dépôt)

- Site créé : page de téléchargement, `outils/assembler.py`, `outils/signer-appli.py`, action « Publier les mises à jour ».
- Canal **essai** : application Windows 4.1.0 (`appli/essai/`) et `Vocabulaire.html` ; fichiers fabriqués par l'action
  « Application Windows » du dépôt Vocabulaire (commit source `3d522ac`, branche `claude/essai-4.1`).
- Installateur signé avant l'envoi (le secret `TAURI_SIGNING_PRIVATE_KEY` n'est pas encore en place) ; signature
  vérifiée avec la clé publique de l'application (`5A6B8F7FEFB192FF`). Aucun canal stable : rien n'est publié sans
  l'accord de Franck.
- À faire par Franck : GitHub Pages (source GitHub Actions) et secret `TAURI_SIGNING_PRIVATE_KEY`.

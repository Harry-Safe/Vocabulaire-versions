"""Signe l'installateur de l'application Windows (action « Publier les mises à jour », après outils/assembler.py).

La clé privée vient seulement du secret TAURI_SIGNING_PRIVATE_KEY (sans mot de passe) : jamais dans un fichier.
La signature est écrite dans _site/appli/latest.json et _site/appli/essai/latest.json ; l'application refuse un
installateur dont la signature ne correspond pas à sa clé publique (tauri/src-tauri/src/lib.rs du dépôt Vocabulaire).
Sans le secret, une fiche déjà signée dans le dépôt (signature non vide) est gardée telle quelle ; une fiche non
signée fait échouer la publication (le site en ligne ne change pas).
"""
import json, os, subprocess, sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "_site" / "appli"
CLI = "@tauri-apps/cli@2.12.4"


def signer(fiche, cle):
    f = json.loads(fiche.read_text(encoding="utf-8"))
    for nom, p in f["platforms"].items():
        exe = fiche.parent / p["url"].rsplit("/", 1)[-1]
        if not exe.exists(): sys.exit(f"{exe.name} manquant dans {fiche.parent.relative_to(SITE.parent)}/")
        if not cle:
            if p.get("signature"): print(f"{fiche.parent.name} · {nom} : signature déjà présente gardée"); continue
            sys.exit("secret TAURI_SIGNING_PRIVATE_KEY absent et fiche non signée : l'application ne peut pas être publiée")
        subprocess.run(["npx", "--yes", CLI, "signer", "sign", str(exe)], check=True, env={**os.environ, "TAURI_SIGNING_PRIVATE_KEY_PASSWORD": ""})
        p["signature"] = (exe.parent / (exe.name + ".sig")).read_text(encoding="utf-8").strip()
        (exe.parent / (exe.name + ".sig")).unlink()
        print(f"{fiche.parent.name} · {nom} : {exe.name} signé")
    fiche.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    fiches = [x for x in (SITE / "latest.json", SITE / "essai" / "latest.json") if x.exists()]
    if not fiches: return print("pas d'application à signer")
    cle = os.environ.get("TAURI_SIGNING_PRIVATE_KEY", "").strip()
    for fiche in fiches: signer(fiche, cle)


if __name__ == "__main__":
    main()

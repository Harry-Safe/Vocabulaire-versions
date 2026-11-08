"""Prépare le site des mises à jour de Vocabulaire (dossier _site), lancé par l'action « Publier les mises à jour ».

- copie appli/, html/ et index.html ;
- écrit versions.json à partir de entrees/*.json (versions stable et essai, nouveautés, fichiers) après avoir
  vérifié que chaque fichier annoncé existe avec la taille et l'empreinte SHA-256 annoncées.
La signature de l'installateur (appli/…/latest.json) est ajoutée ensuite par outils/signer-appli.py.
"""
import hashlib, json, shutil, sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SITE = ICI / "_site"


def main():
    canaux = {}
    for f in sorted((ICI / "entrees").glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        for nom, x in e["fichiers"].items():
            p = ICI / x["url"]
            if not p.exists(): sys.exit(f"{f.name} : fichier absent {x['url']}")
            b = p.read_bytes()
            if hashlib.sha256(b).hexdigest() != x["sha256"] or len(b) != x["taille"]: sys.exit(f"{f.name} : {x['url']} ne correspond pas à son empreinte")
        canaux[f.stem] = e
    shutil.rmtree(SITE, ignore_errors=True); SITE.mkdir()
    for d in ("appli", "html"):
        if (ICI / d).is_dir(): shutil.copytree(ICI / d, SITE / d)
    shutil.copyfile(ICI / "index.html", SITE / "index.html")
    (SITE / "versions.json").write_text(json.dumps({"format": "vocabulaire-versions", "canaux": canaux}, ensure_ascii=False, indent=1), encoding="utf-8")
    (SITE / ".nojekyll").write_text("")
    print("versions.json :", ", ".join(f"{c} {e['version']}" for c, e in canaux.items()) or "aucune version")


if __name__ == "__main__":
    main()

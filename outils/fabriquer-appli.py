"""Fabrique l'installateur Windows d'un canal à partir de ce que ce dépôt publie déjà (action « Publier les mises à jour »).

L'installateur contient la page publiée sur le canal (html/[essai/]Vocabulaire.html, vérifiée par son empreinte dans
entrees/<canal>.json ; l'installateur d'essai y ajoute <meta name="vocabulaire-canal" content="essai">, comme
build/construire-appli.py du dépôt source) dans la coquille Tauri copiée du dépôt source (coquille/<canal>/, avec les
chemins de ce dépôt-là : tauri/…), écrite par build/publier-appli.py. La fabrication se fait ici, sur un dépôt public,
pour ne pas consommer les minutes GitHub du dépôt privé.

    python outils/fabriquer-appli.py <stable|essai> --plan       # faut-il fabriquer ? (sorties GitHub : fabriquer, cle, nom)
    python outils/fabriquer-appli.py <stable|essai> --preparer   # construction/ : coquille, page, numéro de version
    python outils/fabriquer-appli.py <stable|essai> --compiler   # Tauri : paquet/<nom de l'installateur annoncé>
    python outils/fabriquer-appli.py --placer <dossier>          # avant outils/assembler.py : installateurs fabriqués
                                                                 # rangés dans appli/, taille et empreinte dans entrees/

Ancien fonctionnement conservé : si l'installateur annoncé par appli/<…>/latest.json est déjà dans le dépôt, rien n'est
fabriqué. La signature reste faite par outils/signer-appli.py, sur _site/.
"""
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
PRODUIT, META = "Vocabulaire", "vocabulaire-canal"
SOUS = {"stable": "", "essai": "essai/"}
CONSTRUCTION = ICI / "construction"          # copie de travail de la coquille (ignorée par Git)
TAURI = CONSTRUCTION / "tauri"
PAQUET = ICI / "paquet"


def sortie(**valeurs):
    """Sorties d'étape GitHub (et affichage pour le journal de l'action)."""
    for k, v in valeurs.items(): print(f"{k} = {v}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            for k, v in valeurs.items(): f.write(f"{k}={v}\n")


def fiche(canal):
    p = ICI / "appli" / SOUS[canal] / "latest.json"
    if not p.exists(): return None, None
    f = json.loads(p.read_text(encoding="utf-8"))
    return f, f["platforms"]["windows-x86_64"]["url"].rsplit("/", 1)[-1]


def entree(canal):
    return json.loads((ICI / "entrees" / f"{canal}.json").read_text(encoding="utf-8"))


def controler(canal, f):
    """La coquille existe ; la page du canal est celle de la fiche, à la version annoncée pour l'application."""
    coquille = ICI / "coquille" / canal
    if not (coquille / "tauri" / "src-tauri" / "tauri.conf.json").exists():
        sys.exit(f"{canal} : ni installateur dans appli/{SOUS[canal]} ni coquille dans coquille/{canal}/ (build/publier-appli.py)")
    e = entree(canal)
    if e["version"] != f["version"]:
        sys.exit(f"{canal} : fiche en {e['version']}, application annoncée en {f['version']} : publier les deux ensemble")
    page = ICI / e["fichiers"]["html"]["url"]
    b = page.read_bytes()
    if hashlib.sha256(b).hexdigest() != e["fichiers"]["html"]["sha256"]:
        sys.exit(f"{canal} : {page.name} ne correspond pas à son empreinte")
    if canal == "essai":
        t = b.decode("utf-8")
        if "<title>" not in t: sys.exit(f"{page.name} : pas de <title> où annoncer le canal d'essai")
        b = t.replace("<title>", f'<meta name="{META}" content="essai">\n<title>', 1).encode("utf-8")
    return coquille, b


def cle(f, coquille, page):
    h = hashlib.sha256(f["version"].encode())
    for p in sorted(x for x in coquille.rglob("*") if x.is_file()):
        h.update(p.relative_to(coquille).as_posix().encode()); h.update(p.read_bytes())
    h.update(page)
    return h.hexdigest()[:32]


def plan(canal):
    f, nom = fiche(canal)
    if f is None: return sortie(fabriquer="non", raison=f"pas d'application sur le canal {canal}")
    if (ICI / "appli" / SOUS[canal] / nom).exists():
        return sortie(fabriquer="non", raison=f"{nom} déjà dans le dépôt (ancien fonctionnement)")
    coquille, page = controler(canal, f)
    sortie(fabriquer="oui", cle=cle(f, coquille, page), nom=nom)


def lancer(commande, dossier):
    print(f"> {commande}", flush=True)
    subprocess.run(commande, cwd=dossier, shell=True, check=True)        # npm et npx sont des .cmd sous Windows


def preparer(canal):
    """construction/ = la coquille du canal, sa page en tauri/www/index.html, la version annoncée dans Tauri et Cargo."""
    f, nom = fiche(canal)
    if f is None: sys.exit(f"pas d'application sur le canal {canal}")
    coquille, page = controler(canal, f)
    v = f["version"]
    shutil.rmtree(CONSTRUCTION, ignore_errors=True)
    shutil.copytree(coquille, CONSTRUCTION)
    (TAURI / "www").mkdir(exist_ok=True)
    (TAURI / "www" / "index.html").write_bytes(page)
    conf = TAURI / "src-tauri" / "tauri.conf.json"
    c = json.loads(conf.read_text(encoding="utf-8")); c["version"] = v
    conf.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cargo = TAURI / "src-tauri" / "Cargo.toml"
    cargo.write_text(re.sub(r'(?m)^version = "[^"]*"', f'version = "{v}"', cargo.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    print(f"{canal} : construction/ prête pour {nom} (page {len(page) // 1024} Ko)")


def compiler(canal):
    f, nom = fiche(canal)
    v = f["version"]
    lancer("npm install --no-audit --no-fund", TAURI)
    lancer("npx tauri build --bundles nsis", TAURI)
    faits = list((TAURI / "src-tauri" / "target" / "release" / "bundle" / "nsis").glob(f"*_{v}_x64-setup.exe"))
    if len(faits) != 1: sys.exit(f"installateur {v} introuvable après la fabrication : {faits}")
    shutil.rmtree(PAQUET, ignore_errors=True); PAQUET.mkdir()
    shutil.copyfile(faits[0], PAQUET / nom)
    print(f"{canal} : {nom} fabriqué ({(PAQUET / nom).stat().st_size // 1024} Ko)")


def placer(dossier):
    """Avant outils/assembler.py : chaque installateur fabriqué rejoint sa fiche dans appli/ (copie de travail de
    l'action, rien n'est commité) et sa taille et son empreinte complètent entrees/<canal>.json."""
    for canal in SOUS:
        f, nom = fiche(canal)
        source = Path(dossier) / f"appli-{canal}" / (nom or "")
        if f is None or not source.is_file(): continue
        dest = ICI / "appli" / SOUS[canal] / nom
        if dest.exists(): sys.exit(f"{dest} existe déjà : installateur à la fois dans le dépôt et fabriqué")
        shutil.copyfile(source, dest)
        p = ICI / "entrees" / f"{canal}.json"; e = json.loads(p.read_text(encoding="utf-8"))
        a = e["fichiers"]["appli"]
        if a["url"] != f"appli/{SOUS[canal]}{nom}": sys.exit(f"{p.name} annonce {a['url']}, l'application est {nom}")
        b = dest.read_bytes(); a["taille"], a["sha256"] = len(b), hashlib.sha256(b).hexdigest()
        p.write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{canal} : {nom} placé dans appli/{SOUS[canal]} ({len(b)} octets, empreinte écrite dans {p.name})")


def main():
    a = sys.argv[1:]
    if a[:1] == ["--placer"] and len(a) == 2: return placer(a[1])
    if len(a) != 2 or a[0] not in SOUS or a[1] not in ("--plan", "--preparer", "--compiler"): sys.exit(__doc__)
    {"--plan": plan, "--preparer": preparer, "--compiler": compiler}[a[1]](a[0])


if __name__ == "__main__":
    main()

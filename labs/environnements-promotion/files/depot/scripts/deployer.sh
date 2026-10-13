#!/usr/bin/env bash
# Déploie une version PUBLIÉE dans un environnement, sans rien reconstruire :
# l'artefact vient du registre, son empreinte est vérifiée avant installation,
# la configuration reste celle de l'environnement (/etc/inventaire/<env>.env).
set -euo pipefail

ENV_CIBLE="${1:?usage : deployer.sh <recette|production> <version> [empreinte]}"
VERSION="${2:?usage : deployer.sh <recette|production> <version> [empreinte]}"
# Facultative : l'empreinte relevée en recette. Fournie, elle impose que la
# production reçoive EXACTEMENT ce fichier, et non ce que le registre sert
# aujourd'hui sous ce numéro de version.
EMPREINTE="${3:-}"
REGISTRE="http://localhost:3000/api/packages/apprenant/generic/inventaire"

# Les entrées viennent d'un formulaire : on n'accepte que des valeurs connues,
# avant de s'en servir dans une URL ou un chemin.
case "$ENV_CIBLE" in
  recette|production) ;;
  *) echo "Environnement inconnu : $ENV_CIBLE" >&2; exit 2 ;;
esac
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version invalide : $VERSION (attendu : X.Y.Z)" >&2
  exit 2
fi
if [ -n "$EMPREINTE" ] && ! [[ "$EMPREINTE" =~ ^[0-9a-f]{64}$ ]]; then
  echo "Empreinte invalide : $EMPREINTE (attendu : 64 caractères hexadécimaux)" >&2
  exit 2
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

curl -fsS -o "$tmp/inventaire.pyz" "$REGISTRE/$VERSION/inventaire-$VERSION.pyz"
attendu=$(curl -fsS "$REGISTRE/$VERSION/inventaire-$VERSION.pyz.sha256" | cut -d' ' -f1)
obtenu=$(sha256sum "$tmp/inventaire.pyz" | cut -d' ' -f1)
if [ "$attendu" != "$obtenu" ]; then
  echo "Empreinte inattendue : $obtenu au lieu de $attendu" >&2
  exit 1
fi
if [ -n "$EMPREINTE" ] && [ "$EMPREINTE" != "$obtenu" ]; then
  echo "Ce n'est pas l'artefact attendu : $obtenu au lieu de $EMPREINTE" >&2
  exit 1
fi

install -m 0644 "$tmp/inventaire.pyz" "/opt/inventaire/$ENV_CIBLE/inventaire.pyz"
sudo /usr/bin/systemctl restart "inventaire@$ENV_CIBLE.service"

# Test de fumée : l'environnement sert-il la version demandée ?
port=$(sed -n 's/^INVENTAIRE_PORT=//p' "/etc/inventaire/$ENV_CIBLE.env")
for _ in $(seq 1 10); do
  if curl -fsS "http://127.0.0.1:$port/version" 2>/dev/null | grep -q "\"$VERSION\""; then
    curl -fsS "http://127.0.0.1:$port/version"; echo
    # Cinquième champ : la promotion a-t-elle imposé l'empreinte de la recette ?
    echo "$(date -u +%FT%TZ) $ENV_CIBLE $VERSION $obtenu ${EMPREINTE:+empreinte-imposee}" >> /var/log/inventaire/deploiements.log
    exit 0
  fi
  sleep 1
done
echo "L'environnement $ENV_CIBLE ne sert pas la version $VERSION" >&2
exit 1

#!/usr/bin/env bash
# Chiffre solution-en-clair/<lab>/solution.yaml vers solution/<lab>/solution.yaml
# avec ansible-vault et le mot de passe de .vault-pass (jamais versionné).
#
# Une solution dont le clair n'a pas changé n'est PAS rechiffrée : le chiffré
# change à chaque passage (sel aléatoire), ce qui périmerait sans raison
# l'attestation du lab (validation-labs.json).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -s .vault-pass ] || { echo ".vault-pass absent" >&2; exit 1; }
find solution-en-clair -name solution.yaml | while read -r clair; do
  cible="solution/${clair#solution-en-clair/}"
  mkdir -p "$(dirname "$cible")"
  if [ -s "$cible" ] && ansible-vault view --vault-password-file .vault-pass "$cible" </dev/null 2>/dev/null | cmp -s - "$clair"; then
    echo "inchangé : $cible"
    continue
  fi
  ansible-vault encrypt --vault-password-file .vault-pass --output "$cible" "$clair" </dev/null >/dev/null 2>&1
  echo "chiffré : $cible"
done

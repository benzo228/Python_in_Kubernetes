#!/usr/bin/env bash
# Включает policy gates в проекте Harbor. Запуск:
#   HARBOR_URL=http://192.168.49.2:30002 HARBOR_ADMIN_PASSWORD=... ./configure-policies.sh
# Флаги безопасности: -e (падать при любой ошибке), -u (падение при некорректных переменных), -o pipefail (считать ошибкой падение внутри pipeline).
set -euo pipefail
: "${HARBOR_ADMIN_PASSWORD:?set HARBOR_ADMIN_PASSWORD}"
HARBOR_URL="${HARBOR_URL:-http://192.168.49.2:30002}"
PROJECT="${PROJECT:-pet-project}"
API="$HARBOR_URL/api/v2.0"
AUTH=(-u "admin:$HARBOR_ADMIN_PASSWORD" -H "Content-Type: application/json")

# Автоскан при push + блокировка pull образов с Critical CVE (403)
curl -fsS -X PUT "${AUTH[@]}" "$API/projects/$PROJECT" -d '{
  "metadata": {"auto_scan": "true", "prevent_vul": "true", "severity": "critical"}
}'

# Tag immutability: тег нельзя перезаписать (теги = commit SHA)
if ! curl -fsS "${AUTH[@]}" "$API/projects/$PROJECT/immutabletagrules" | grep -q '"\*\*"'; then
  curl -fsS -X POST "${AUTH[@]}" "$API/projects/$PROJECT/immutabletagrules" -d '{
    "disabled": false,
    "scope_selectors": {"repository": [{"kind": "doublestar", "decoration": "repoMatches", "pattern": "**"}]},
    "tag_selectors": [{"kind": "doublestar", "decoration": "matches", "pattern": "**"}]
  }'
fi
echo "Policies applied to $PROJECT"

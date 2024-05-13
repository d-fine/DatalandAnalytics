#!/usr/bin/env bash
set -euxo pipefail

cd "$(dirname "$0")"

declare -A urls
declare -A files

urls[datasets]="https://dataland.com/api/v3/api-docs/public"
files[datasets]="./api_clients/datasets_api/datasets_open_api.yaml"
urls[documents]="https://dataland.com/documents/v3/api-docs/public"
files[documents]="./api_clients/documents_api/documents_open_api.yaml"
urls[qa]="https://dataland.com/qa/v3/api-docs/public"
files[qa]="./api_clients/qa_api/qa_open_api.yaml"
urls[requests]="https://dataland.com/community/v3/api-docs/public"
files[requests]="./api_clients/requests_api/requests_open_api.yaml"

for api in datasets documents qa requests
do
  echo "Updating OpenAPI specification file for $api."
  curl ${urls[$api]} | python -m json.tool | python -c 'import sys, yaml, json; print(yaml.dump(json.loads(sys.stdin.read()), sort_keys=False))' > ${files[$api]}
done

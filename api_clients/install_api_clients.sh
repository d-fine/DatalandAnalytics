#!/bin/bash
set -euxo pipefail

declare -a apis=("datasets" "documents" "requests" "qa")

for api in "${apis[@]}"
do
	echo ""
        echo "Creating openApiClients for ${api}"
        cd "${api}_api"
        openapi-generator-cli generate -g python -i "./${api}_open_api.yaml" --additional-properties=packageName=dataland_"$api"
        echo "Installing openApiClients for $api"
        pip install .
        cd ..
done

echo "Installation of openApiClients successful."

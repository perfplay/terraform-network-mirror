#!/usr/bin/env bash

set -e -u -o pipefail

usage() {
    echo "Usage: $0 [-p platform] [-m mirror_dir] settings_file"
    exit 1
}

platform="linux_amd64"
mirror_dir="./mirror"
error_occurred=0

while getopts ":p:m:" opt; do
    case ${opt} in
        p )
            platform=$OPTARG
            ;;
        m )
            mirror_dir=$OPTARG
            ;;
        \? )
            usage
            ;;
    esac
done
shift $((OPTIND -1))

[[ $# -eq 0 ]] && echo "Please pass a settings file path" && exit 1

settings_file=$1

echo "Settings file: $settings_file"
echo "Platform: $platform"
echo "Mirror directory: $mirror_dir"

mkdir -p "${mirror_dir}"

download_provider(){
  local provider_namespace=$1
  local provider_name=$2
  local provider_version=$3

  echo "Downloading Terraform Provider ${provider_namespace}/${provider_name}:${provider_version}"
  cat > main.tf << EOF
terraform {
  required_providers {
    ${provider_name} = {
      source  = "${provider_namespace}/${provider_name}"
      version = "${provider_version}"
    }
  }
}
EOF
  if terraform providers mirror -platform="${platform}" ./; then
    echo "Provider ${provider_namespace}/${provider_name}:${provider_version} downloaded successfully."
  else
    echo "Failed to download provider ${provider_namespace}/${provider_name}:${provider_version}, continuing..."
    error_occurred=1
  fi
  rm main.tf
}

settings_json=$(cat "${settings_file}")
providers=$(echo "${settings_json}" | jq '[ .providers[] ]')
provider_names=$(echo "${settings_json}" | jq '[ .providers[].name ]')

echo
echo "Mirror Settings:"
echo "  Providers:         ${provider_names}"
echo

echo "Downloading Providers Locally"
cd "${mirror_dir}"
for row in $(echo "${providers}" | jq -r '.[] | [.namespace, .name, .versions] | @base64'); do
  _namespace() {
    echo "${row}" | base64 --decode | jq -r .[0]
  }
  _name() {
    echo "${row}" | base64 --decode | jq -r .[1]
  }
  _versions() {
    echo "${row}" | base64 --decode | jq -r .[2]
  }

  # echo $(_name) $(_versions)
  for version in $(_versions | jq -r .[]); do
    ns=$(_namespace)
    n=$(_name)
    v=${version}

    download_provider "$ns" "$n" "$v"
  done
done

if [[ $error_occurred -ne 0 ]]; then
  echo "Errors occurred during provider downloads."
  exit 1
fi

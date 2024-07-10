#!/usr/bin/env python3

import json
import argparse
import requests

from packaging import version, specifiers
from Provider import Provider
from CustomLogger import CustomLogger

logger = CustomLogger()


def parse_args():
    parser = argparse.ArgumentParser(description='Update repositories.')
    parser.add_argument('--config', default="provider_versions.json", help='Provider versions file')
    parser.add_argument('--registry-url',
                        default="https://registry.terraform.io",
                        help='Terraform registry URL')
    return parser.parse_args()


def load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_file}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration file: {e}")
        return None


def fetch_versions(namespace, provider, registry_url, minimal_version=None, valid_versions=None):
    registry_url_with_path = f"{registry_url}/v1/providers/{namespace}/{provider}/versions"
    try:
        response = requests.get(registry_url_with_path)
        response.raise_for_status()
        versions = response.json().get('versions', [])

        filtered_versions = []
        for ver in versions:
            try:
                parsed_version = version.parse(ver['version'])
                if valid_versions and parsed_version in valid_versions:
                    filtered_versions.append(parsed_version)
                elif minimal_version is None or parsed_version >= minimal_version:
                    filtered_versions.append(parsed_version)
            except version.InvalidVersion as e:
                logger.warning(f"Invalid version: {ver['version']} - {e}")

        filtered_versions.sort()
        logger.info(f"Fetched versions for {namespace}/{provider}: {filtered_versions}")
        return filtered_versions
    except requests.RequestException as e:
        logger.error(f"Failed to fetch versions for {namespace}/{provider}: {e}")
        return []


def generate_json(namespace, provider, registry_url, minimal_version=None, valid_versions=None):
    parsed_versions = fetch_versions(namespace, provider, registry_url, minimal_version, valid_versions)
    versions = [str(ver) for ver in parsed_versions]
    if not versions:
        return

    provider_data = {
        "providers": [
            {
                "namespace": namespace,
                "name": provider,
                "versions": versions
            }
        ]
    }

    filename = f"{namespace}-{provider}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(provider_data, f, indent=4)
        logger.info(f"Generated JSON file: {filename}")
    except IOError as e:
        logger.error(f"Failed to write JSON file: {e}")


def main():
    args = parse_args()
    config_file = args.config

    config = load_config(config_file)
    if config is None:
        return

    providers = []
    for provider_data in config.get("providers", []):
        provider = Provider(
            namespace=provider_data.get("namespace"),
            name=provider_data.get("name"),
            minimal_version=provider_data.get("minimal_version"),
            versions=provider_data.get("versions", [])
        )
        providers.append(provider)

    for provider in providers:
        logger.info(f"Processing provider: {provider.namespace}/{provider.name}")
        logger.info(f"Minimal version for {provider.namespace}/{provider.name}: {[str(provider.parsed_minimal_version)]}")
        logger.info(f"Also valid versions for {provider.namespace}/{provider.name}: {[str(ver) for ver in provider.valid_parsed_versions]}")

        generate_json(provider.namespace, provider.name, args.registry_url,
                      provider.parsed_minimal_version, provider.valid_parsed_versions)


if __name__ == "__main__":
    main()
import json
import argparse
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


def main():
    args = parse_args()
    config_file = args.config
    registry_url = args.registry_url + "/v1/providers/"

    config = load_config(config_file)
    if config is None:
        return

    providers = []
    for provider_data in config.get("providers", []):
        provider = Provider(
            namespace=provider_data.get("namespace"),
            name=provider_data.get("name"),
            versions=provider_data.get("versions", [])
        )
        providers.append(provider)

    for provider in providers:
        logger.info(f"Processing provider: {provider.namespace}/{provider.name}")
        valid_versions = provider.validate_versions()
        logger.info(f"Valid versions for {provider.namespace}/{provider.name}: {valid_versions}")


if __name__ == "__main__":
    main()
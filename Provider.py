from packaging import version, specifiers
from CustomLogger import CustomLogger

logger = CustomLogger()


class Provider:
    def __init__(self, namespace, name, versions):
        self.namespace = namespace
        self.name = name
        self.versions = versions

    def validate_versions(self):
        valid_versions = []
        for ver in self.versions:
            if "+" in ver:
                base_version = ver.replace("+", "")
                try:
                    spec = specifiers.SpecifierSet(f">={base_version}")
                    valid_versions.append(f"{base_version}+")
                    logger.info(f"Valid version range: {base_version}+")
                except specifiers.InvalidSpecifier as e:
                    logger.warning(f"Invalid version specifier: {ver} - {e}")
            else:
                try:
                    parsed_version = version.parse(ver)
                    valid_versions.append(ver)
                    logger.info(f"Valid version: {ver}")
                except version.InvalidVersion as e:
                    logger.warning(f"Invalid version: {ver} - {e}")
        return valid_versions
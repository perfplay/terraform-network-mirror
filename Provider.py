from packaging import version
from CustomLogger import CustomLogger

logger = CustomLogger()


class Provider:
    def __init__(self, namespace, name, versions, minimal_version=None):
        self.namespace = namespace
        self.name = name
        self.minimal_version = minimal_version
        self.versions = versions
        self._valid_parsed_versions = []
        self._parsed_minimal_version = None
        self.validate_versions()

    @property
    def valid_parsed_versions(self):
        return self._valid_parsed_versions

    @property
    def parsed_minimal_version(self):
        return self._parsed_minimal_version

    def validate_versions(self):
        if self.minimal_version:
            try:
                self._parsed_minimal_version = version.parse(self.minimal_version)
                logger.debug(f"Valid minimal version: {self.minimal_version}")
            except version.InvalidVersion as e:
                logger.warning(f"Invalid minimal version: {self.minimal_version} - {e}")
        else:
            self._parsed_minimal_version = None

        for ver in self.versions:
            try:
                parsed_version = version.parse(ver)
                if not self._parsed_minimal_version or parsed_version <= self._parsed_minimal_version:
                    self._valid_parsed_versions.append(parsed_version)
                    logger.debug(f"Valid version: {ver}")
                else:
                    logger.warning(f"Version {ver} is higher than minimal version {self.minimal_version}")
            except version.InvalidVersion as e:
                logger.warning(f"Invalid version: {ver} - {e}")

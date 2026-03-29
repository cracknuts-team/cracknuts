from cracknuts.cracker.cracker_s1 import ConfigS1, CrackerS1


class CrackerF1(CrackerS1):
    def _parse_config_bytes(self, res):
        return ConfigS1()

    def write_config_to_cracker(self, res): ...

    def get_current_config(self) -> ConfigS1:
        return ConfigS1()

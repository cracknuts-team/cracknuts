from cracknuts.cracker.cracker_s1 import ConfigS1, CrackerS1


class CrackerF1(CrackerS1):
    def _parse_config_bytes(self, res):
        return ConfigS1()

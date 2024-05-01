class HookEntryErr(Exception):
    pass


class HookEntryTypeErr(HookEntryErr):
    pass


class YamlParserErr(Exception):
    pass


class YamlParserLoadErr(YamlParserErr):
    pass


class BadConfiguration(Exception):
    pass

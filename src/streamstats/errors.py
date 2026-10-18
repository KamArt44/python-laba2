class StreamStatsError(Exception):
    pass
class InvalidEventError(StreamStatsError):
    pass
class UnsupportedFormatError(StreamStatsError):
    pass
class InvalidTimestampError(InvalidEventError):
    pass
class CLIConfigError(StreamStatsError):
    pass

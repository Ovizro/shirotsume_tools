class ArchiveError(Exception):
    """归档读取错误"""


class InvalidSignatureError(ArchiveError):
    """文件签名无效"""


class UnsupportedVersionError(ArchiveError):
    """不支持的归档版本"""

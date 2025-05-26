import logging

def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    標準出力にフォーマット付きでログを出力するロガーを返す
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "[%(asctime)s] %(levelname)s:%(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
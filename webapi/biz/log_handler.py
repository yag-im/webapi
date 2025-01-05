import logging

from flask import Flask


def init_app(app: Flask) -> None:
    # log setup
    # TODO: use app.config["DEBUG"] flag for log_level
    log_level = logging.DEBUG

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"))

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    jbs_logger = logging.getLogger("webapi")
    jbs_logger.handlers.clear()
    jbs_logger.addHandler(handler)
    jbs_logger.setLevel(log_level)
    jbs_logger.propagate = False

    root_log = logging.getLogger()
    root_log.handlers.clear()
    root_log.addHandler(handler)
    root_log.setLevel(log_level)
    root_log.propagate = False

    # talkative modules:
    logging.getLogger("oauth2").setLevel(logging.INFO)
    # logging.getLogger("sqlalchemy").setLevel(logging.DEBUG)

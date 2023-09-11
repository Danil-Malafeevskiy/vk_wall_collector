import logging

class Logging(object):

    def __init__(self) -> None:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                                    "%Y-%m-%d %H:%M:%S")

        ch.setFormatter(formatter)
        logger.addHandler(ch)

    def log_to_console(self, message: str, type: str) -> None:
        if type == 'info':
            logging.info(message)
        else:
            logging.error(message)

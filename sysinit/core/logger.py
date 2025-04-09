import logging
from pathlib import Path


class Logger:
    def __init__(self, name="AppLogger", level=logging.INFO, log_to_file=False, log_file="logs/app.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # avoid duplicate logs in some environments

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

        # Console handler
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # File handler (optional)
        if log_to_file and not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def get(self):
        return self.logger
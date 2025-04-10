import subprocess
import logging
from pathlib import Path

from sysinit.core.logger import Logger


class CommandEngine:
    def __init__(self, verbose=True, dry_run=False, log_file=None, title: str = None, log_level: str = logging.DEBUG):
        self.title = title or "GenericCommandEngine"
        self.verbose = verbose
        self.dry_run = dry_run
        self.log_level = log_level

        self.logger = Logger(name=self.__class__.__name__, level=log_level).get()

    def run(self, cmd, sudo=False):
        if sudo:
            cmd = f"sudo {cmd}"

        self.logger.info(f"Running command: {cmd}")
        if self.dry_run:
            self.logger.warning("[SKIP]: Dry run: skipped execution.")
            return None

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0 and result.stderr:
            self.logger.error(f"🔴 Command failed")
            cmd_op = result.stderr.strip()
            self.logger.info(f"Command OP: \n{cmd_op}" if cmd_op else "... : [NO OUTPUT]")
        else:
            cmd_op = result.stdout.strip()
            self.logger.info(f"Command OP: \n{cmd_op}" if cmd_op else "... : [NO OUTPUT]")
            self.logger.info("🟢 Command execution successful ...OK")

        return result

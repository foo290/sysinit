from sysinit.core.command_manager import CommandEngine


class Command:
    def __init__(self, command_str, sudo=False, description=None, verbose=True, dry_run=False, log_file=None):
        self.command_str = command_str
        self.sudo = sudo
        self.description = description or command_str
        self.verbose = verbose
        self.dry_run = dry_run

        self.engine = CommandEngine(
            verbose=self.verbose,
            dry_run=self.dry_run,
        )

    def attach_engine(self, engine: CommandEngine):
        self.engine = engine

    def execute(self):
        if not self.engine:
            raise RuntimeError("CommandEngine not attached.")
        
        return self.engine.run(self.command_str, sudo=self.sudo)

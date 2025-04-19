# sysinit/term.py

import typer
import logging
import sys
from pathlib import Path

# Try to import IPython, needed for the interactive command
try:
    import IPython
except ImportError:
    IPython = None # Flag that IPython is not available

# Import UnitManager, Unit class, Command class, and potential custom exceptions
try:
    from sysinit.core.unit_manager import UnitManager
    from sysinit.core.unit import Unit
    from sysinit.core.command import Command # <-- Import Command
    # Import your custom exceptions if you have them
    # from sysinit.exceptions import UnitNotFoundError, ConfigError, CommandError
except ImportError:
    print("Error: Could not import sysinit components. Ensure it's installed correctly.", file=sys.stderr)
    sys.exit(1)

# Define placeholder exceptions if you haven't created custom ones yet
class UnitNotFoundError(KeyError): pass
class ConfigError(ValueError): pass
class CommandError(RuntimeError): pass
class YAMLError(Exception): pass # Assuming yaml.YAMLError might be used

# --- Typer App Initialization ---
app = typer.Typer(help="SysInit Terminal: Interactive shell for managing systemd services.")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# --- Interactive Shell Command ---
@app.command(name="shell", help="Launch an interactive IPython shell with the UnitManager loaded.")
def interactive_shell(
    config: Path = typer.Option(
        "config.yaml", # Default value
        "--config", "-c",
        # exists=True, # REMOVED: Allow non-existent default
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True, # Still check readability if it exists
        resolve_path=True,
        help="Path to the YAML configuration file (optional).",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        is_flag=True,
        help="Enable verbose logging output (DEBUG level)."
    )
):
    """
    Loads the specified config (if it exists) or starts with an empty manager,
    then launches an interactive IPython shell.
    The UnitManager instance is available as 'manager', the Unit class as 'Unit',
    and the Command class as 'Command'.
    """
    if IPython is None:
        typer.secho("IPython is required for the interactive shell.", fg=typer.colors.YELLOW, err=True)
        typer.secho("Please install it: pip install ipython", fg=typer.colors.YELLOW, err=True)
        typer.secho("Or install sysinit with the appropriate extra: pip install \"sysinit[dev]\" or \"sysinit[shell]\"", fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(code=1)

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug("Verbose logging enabled.")

    manager = None
    config_loaded = False
    config_error = None

    try:
        # Assume yaml might be needed for errors
        import yaml
        if config.exists():
            log.debug(f"Attempting to load configuration from: {config}")
            manager = UnitManager(config_path=str(config))
            config_loaded = True
            log.debug("UnitManager initialized successfully from config.")
        else:
            default_config_path = Path("config.yaml").resolve()
            if config.resolve() != default_config_path:
                 config_error = FileNotFoundError(f"Error: Specified configuration file not found at '{config}'.")
            else:
                 log.debug("Default config file 'config.yaml' not found. Initializing empty UnitManager.")
                 manager = UnitManager()
                 log.debug("Empty UnitManager initialized.")

    except ConfigError as e:
        config_error = ConfigError(f"Error loading or validating configuration '{config}': {e}")
    except YAMLError as e:
        config_error = YAMLError(f"Error parsing YAML file '{config}': {e}")
    except Exception as e:
        config_error = Exception(f"An unexpected error occurred initializing UnitManager: {e}")

    if config_error:
        typer.secho(str(config_error), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    elif manager is None:
        typer.secho("Failed to initialize UnitManager.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


    # --- Define helper functions ---
    # (Keep start, stop, status, services helpers as before)
    def start(service_name):
        """Helper to start a service."""
        try:
            typer.echo(f"Starting '{service_name}'...")
            manager.start_service(service_name)
            typer.secho(f"Service '{service_name}' started.", fg=typer.colors.GREEN)
        except UnitNotFoundError:
             typer.secho(f"Error: Service '{service_name}' not found in manager.", fg=typer.colors.RED)
        except Exception as e:
            typer.secho(f"Error starting '{service_name}': {e}", fg=typer.colors.RED)

    def stop(service_name):
        """Helper to stop a service."""
        try:
            typer.echo(f"Stopping '{service_name}'...")
            manager.stop_service(service_name)
            typer.secho(f"Service '{service_name}' stopped.", fg=typer.colors.GREEN)
        except UnitNotFoundError:
             typer.secho(f"Error: Service '{service_name}' not found in manager.", fg=typer.colors.RED)
        except Exception as e:
            typer.secho(f"Error stopping '{service_name}': {e}", fg=typer.colors.RED)

    def status(service_name=None):
        """Helper to get status (all or one)."""
        if service_name:
             try:
                unit = manager.get(service_name)
                if not unit:
                     typer.secho(f"Service '{service_name}' not found.", fg=typer.colors.RED)
                     return
                typer.echo(unit.status())
             except Exception as e:
                 typer.secho(f"Error getting status for '{service_name}': {e}", fg=typer.colors.RED)
        else:
             typer.echo("Status for all services:")
             manager.status_all()

    def services():
        """List available service names currently managed."""
        names = list(manager.units.keys())
        if not names:
            typer.echo("No services currently managed.")
            return
        typer.echo("Managed services:")
        for name in names:
            typer.echo(f"- {name}")

    def add_unit(unit_instance: Unit):
        """Adds a Unit instance to the manager."""
        if not isinstance(unit_instance, Unit):
             typer.secho("Error: Provided object is not a Unit instance.", fg=typer.colors.RED)
             return
        try:
            manager.add_unit(unit_instance)
            typer.secho(f"Unit '{unit_instance.name}' added to manager.", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Error adding unit '{unit_instance.name}': {e}", fg=typer.colors.RED)
    # --- End Helper Functions ---


    # Prepare namespace for IPython embedding
    user_ns = {
        'manager': manager,       # The core object (loaded or empty)
        'Unit': Unit,             # The Unit class itself
        'Command': Command,       # <-- Add the Command class
        'add_unit': add_unit,     # Helper to add units
        'start': start,           # Helper function
        'stop': stop,             # Helper function
        'status': status,         # Helper function
        'services': services,     # Helper function
        'config_path': config,    # Info: Path object for the attempted/loaded config
        'log': log                # Access to the logger
    }

    # Define the banner message based on whether config was loaded
    if config_loaded:
        loaded_msg = f"Config loaded from: {config}"
    else:
        loaded_msg = "No config file loaded. Manager is empty."

    banner = f"""--- SysInit Interactive Terminal ---
{loaded_msg}
Available objects:
  'manager':     The UnitManager instance. Access units via manager.units dict.
                 Call methods like manager.start_all(), manager.get('name'), etc.
  'Unit':        The Unit class. Create new units:
                 u = Unit(name='my-svc', exec_start='echo hello', manage_as_user=True)
                 u = Unit(name='cmd-svc', exec_start=Command('ls -l'), ...)
  'Command':     The Command class. Create command objects:
                 cmd = Command('hostname', verbose=True)
                 cmd.execute()
  'add_unit(u)': Helper function to add a created Unit instance 'u' to the manager.
  'start(name)': Helper function to start a managed service.
  'stop(name)':  Helper function to stop a managed service.
  'status(name=None)': Helper for status (one or all managed services).
  'services()':  List currently managed service names.
  'config_path': Path object for the attempted/loaded config file.
  'log':         Logger instance.

Use standard Python syntax. Press Ctrl+D or type exit() to quit.
System service operations may require sudo password if run as non-root.
"""

    typer.echo("Starting interactive session...")
    # Embed IPython shell
    IPython.embed(
        header="⚙️ Welcome to the SysInit Interactive Terminal!",
        banner1=banner,
        user_ns=user_ns,
        colors="neutral"
    )

# --- Entry point for running the Typer app ---
if __name__ == "__main__":
    app()
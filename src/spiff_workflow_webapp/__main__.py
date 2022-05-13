"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Spiff Workflow Webapp."""
    print("This does nothing")


if __name__ == "__main__":
    main(prog_name="spiff-workflow-webapp")  # pragma: no cover

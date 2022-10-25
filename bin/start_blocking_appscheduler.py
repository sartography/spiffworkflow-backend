from apscheduler.schedulers.background import BlockingScheduler
from spiffworkflow_backend import create_app, start_scheduler


def main() -> None:
    """Main."""
    app = create_app()
    start_scheduler(app, BlockingScheduler)


if __name__ == "__main__":
    main()

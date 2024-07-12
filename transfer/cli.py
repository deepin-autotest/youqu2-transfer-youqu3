import sys


def cli():
    from transfer.main import Transfer
    Transfer(
        project_path=sys.argv[1],
    ).transfer()

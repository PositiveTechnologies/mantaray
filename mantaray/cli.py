import click
import sys
import logging

import mantaray.core
from mantaray.__metadata__ import __version__, __author__, __author_email__, __description__, __title__


@click.command()
@click.option("--deepness", default=1, help="number of iterations for undecidable loops")
@click.argument("filename", type=click.Path(exists=True))
def main(filename, deepness):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="[%(levelname)s] %(name)s: %(message)s")
    mantaray.core.run(filename, deepness)


if __name__ == "__main__":
    click.echo("{0} v{1}".format(__title__, __version__))
    click.echo(__description__)
    click.echo("{0} ({1})\n".format(__author__, __author_email__))

    if sys.version_info < (3, 5):
        sys.exit("Python < 3.5 is not supported")

    main()

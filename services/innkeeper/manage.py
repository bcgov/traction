import click
from flask.cli import with_appcontext
from config import Config
from api.utils import check_password, hash_password


@click.group()
def cli():
    """Main entry point"""


@cli.command("init")
@with_appcontext
def init():
    """Create a new admin access key"""
    from extensions import db
    from api.models import AccessKey

    access_key = AccessKey.get_by_is_admin(True)
    if not access_key:
        click.echo("admin access key not found, creating.")
        password = hash_password(Config.INNKEEPER_ADMIN_KEY)
        access_key = AccessKey(password=password, is_active=True, is_admin=True)
        db.session.add(access_key)
        db.session.commit()
        click.echo("created admin access key")

    ok = check_password(Config.INNKEEPER_ADMIN_KEY, access_key.password)
    click.echo(f"admin access key configured: {ok}")


if __name__ == "__main__":
    cli()

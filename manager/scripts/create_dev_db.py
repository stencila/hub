import scripts.create_dev_accounts
import scripts.create_dev_users


def run(*args):
    """Create development database."""
    scripts.create_dev_users.run()
    scripts.create_dev_accounts.run()

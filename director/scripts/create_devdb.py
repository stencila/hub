"""Create development database."""

import scripts.create_dev_users
import scripts.create_dev_accounts
import scripts.create_dev_account_roles
import scripts.create_dev_projects
import scripts.create_dev_project_roles
import scripts.create_dev_project_nodes
import scripts.create_dev_project_sources
import scripts.create_dev_jobs


def run(*args):
    scripts.create_dev_users.run()
    scripts.create_dev_accounts.run()
    scripts.create_dev_account_roles.run()
    scripts.create_dev_projects.run()
    scripts.create_dev_project_roles.run()
    scripts.create_dev_project_nodes.run()
    scripts.create_dev_project_sources.run()
    scripts.create_dev_jobs.run()

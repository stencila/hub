from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.loader import MigrationLoader


def migrations_pending() -> bool:
    """
    Check if there are any migrations that haven't been applied yet.

    Inspired by https://tech.octopus.energy/news/2016/05/05/django-elb-health-checks.html
    """
    connection = connections[DEFAULT_DB_ALIAS]
    loader = MigrationLoader(connection)
    graph = loader.graph

    # Count unapplied migrations
    for app_name in loader.migrated_apps:
        for node in graph.leaf_nodes(app_name):
            for plan_node in graph.forwards_plan(node):
                if plan_node not in loader.applied_migrations:
                    return True

    return False

from lib import data_size
from lib.resource_allowance import QUOTA_DEFAULTS, QuotaName

FREE_PLAN_DESCRIPTION = """
<ul>
    <li>Up to {max_projects} Projects</li>
    <li>Public Projects Only</li>
    <li>No Teams</li>
    <li>{storage_limit} Disk Space</li>
    <li>{cpu_limit}% Shared CPU</li>
    <li>{memory_limit} Memory Limit</li>
</ul>
""".format(
    max_projects=QUOTA_DEFAULTS[QuotaName.MAX_PROJECTS],
    storage_limit=data_size.to_human(QUOTA_DEFAULTS[QuotaName.STORAGE_LIMIT]),
    cpu_limit=QUOTA_DEFAULTS[QuotaName.SESSION_CPU_LIMIT],
    memory_limit=data_size.to_human(QUOTA_DEFAULTS[QuotaName.SESSION_MEMORY_LIMIT])
)

FREE_PRODUCT = {
    'name': 'Stencila Basic',
    'extension': {
        'tag_line': 'Great for Starting Out'
    },
    'description': FREE_PLAN_DESCRIPTION,
}

FREE_PLAN = {
    'pk': 0,
    'price_description': 'Free',
    'product': FREE_PRODUCT
}

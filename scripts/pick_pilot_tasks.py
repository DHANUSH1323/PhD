"""Seeded choice of the 5 pilot tasks from the retail base split."""
import random

from tau2.domains.retail.environment import get_tasks

ids = sorted((t.id for t in get_tasks("base")), key=lambda x: int(x))
print(sorted(random.Random(17).sample(ids, 5), key=int))

import random
from sqlalchemy.orm import Session
from db.db_app import db
from db.user import User



USERS = 100
PROJECTS = 100_000
RPG_TOTAL = 500_000
MAX_DEPTH = 7
BATCH_SIZE = 5_000


def seed_users(session: Session):
    users = [
        User(name=f"user_{i}", is_group=False)
        for i in range(USERS)
    ]
    db.session.add_all(users)
    db.session.commit()
    return users


def seed_projects(session: Session, users):
    from db.project import Project

    projects = []
    for i in range(PROJECTS):
        owner = random.choice(users)
        # print("pr--", owner.id)
        projects.append(
            Project(
                name=f"project_{i}",
                owners=[owner.id],
            )
        )

        if len(projects) >= BATCH_SIZE:
            db.session.add_all(projects)
            db.session.commit()
            projects.clear()

    if projects:
        db.session.add_all(projects)
        db.session.commit()


def seed_resource_pool_groups(session: Session):
    from db.resource_pool_group import ResourcePoolGroup

    from db.project import Project

    groups = []

    # level -> ids
    levels: dict[int, list[int]] = {0: []}
    default_root = ResourcePoolGroup(
            name=f"rpg_root_0",
            project_id=None,
            parent_resource_pool_group_id=None,
        )

    db.session.add(default_root)
    db.session.commit()

    # create roots
    root_count = 100
    for i in range(1, root_count):
        g = ResourcePoolGroup(
            name=f"rpg_root_{i}",
            project_id=None,
            parent_resource_pool_group_id=default_root.id,
        )
        groups.append(g)

    db.session.add_all(groups)
    db.session.commit()

    levels[0] = db.session.query(ResourcePoolGroup.id).filter(
        ResourcePoolGroup._parent_resource_pool_group_id.is_not(None)
    ).all()
    levels[0] = [x[0] for x in levels[0]]

    created = root_count
    depth = 1

    # build internal tree
    while created < RPG_TOTAL - PROJECTS and depth < MAX_DEPTH:
        levels[depth] = []

        for parent_id in levels[depth - 1]:
            for _ in range(random.randint(2, 4)):
                if created >= RPG_TOTAL - PROJECTS:
                    break

                groups.append(
                    ResourcePoolGroup(
                        name=f"rpg_d{depth}_{created}",
                        project_id=None,
                        parent_resource_pool_group_id=parent_id,
                    )
                )
                created += 1

                if len(groups) >= BATCH_SIZE:
                    db.session.add_all(groups)
                    db.session.commit()
                    groups.clear()

        depth += 1

    if groups:
        db.session.add_all(groups)
        db.session.commit()

    # fetch all leaves
    leaf_ids = db.session.query(ResourcePoolGroup.id).filter(
        ~ResourcePoolGroup.id.in_(
            db.session.query(ResourcePoolGroup._parent_resource_pool_group_id)
            .filter(ResourcePoolGroup._parent_resource_pool_group_id.is_not(None))
        )
    ).all()

    leaf_ids = [x[0] for x in leaf_ids]

    # assign projects ONLY to leaves
    project_ids = db.session.query(Project.id).all()
    project_ids = [x[0] for x in project_ids]

    updates = []
    for leaf_id, project_id in zip(leaf_ids, project_ids):
        updates.append(
            {
                "id": leaf_id,
                "project_id": project_id,
            }
        )

        if len(updates) >= BATCH_SIZE:
            db.session.bulk_update_mappings(ResourcePoolGroup, updates)
            db.session.commit()
            updates.clear()

    if updates:
        db.session.bulk_update_mappings(ResourcePoolGroup, updates)
        db.session.commit()


def main_generate():
    users = seed_users(db.session)
    seed_projects(db.session, users)
    seed_resource_pool_groups(db.session)
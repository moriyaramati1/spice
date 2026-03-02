import random
from sqlalchemy.orm import Session
from db.db_app import db
from db.user import User
from db.project import Project
from db.resource_pool_group import ResourcePoolGroup

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
    db.session.bulk_save_objects(users)
    db.session.commit()
    return users


def seed_projects(session: Session, users):
    projects = []
    for i in range(PROJECTS):
        owner = random.choice(users)
        projects.append(
            Project(
                name=f"project_{i}",
                responsible_team=owner.id,
            )
        )

        if len(projects) >= BATCH_SIZE:
            db.session.bulk_save_objects(projects)
            db.session.commit()
            projects.clear()

    if projects:
        db.session.bulk_save_objects(projects)
        db.session.commit()


def seed_resource_pool_groups(session: Session):
    groups = []

    # level -> ids
    levels: dict[int, list[int]] = {0: []}

    # create roots
    root_count = 100
    for i in range(root_count):
        g = ResourcePoolGroup(
            name=f"rpg_root_{i}",
            project_id=None,
            parent_resource_pool_group_id=None,
        )
        groups.append(g)

    db.session.bulk_save_objects(groups)
    db.session.commit()

    levels[0] = db.session.query(ResourcePoolGroup.id).filter(
        ResourcePoolGroup.parent_resource_pool_group_id.is_(None)
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
                    db.session.bulk_save_objects(groups)
                    db.session.commit()
                    groups.clear()

        depth += 1

    if groups:
        db.session.bulk_save_objects(groups)
        db.session.commit()

    # fetch all leaves
    leaf_ids = db.session.query(ResourcePoolGroup.id).filter(
        ~ResourcePoolGroup.id.in_(
            db.session.query(ResourcePoolGroup.parent_resource_pool_group_id)
            .filter(ResourcePoolGroup.parent_resource_pool_group_id.isnot(None))
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
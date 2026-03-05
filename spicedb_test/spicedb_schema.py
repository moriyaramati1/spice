schema = """
    definition user {}
    definition usergroup {
        relation direct_member: user

        permission member = direct_member
    }

    definition resource_pool_group {
      relation parent: resource_pool_group
      relation owner: user | usergroup#member

      permission edit = parent->edit + owner      
    }


    definition project {
      relation resource_pool_group: resource_pool_group
      relation responsible_team: usergroup
      relation owner: user | usergroup#member

      permission edit = owner + responsible_team->member + resource_pool_group->edit
      permission create_deployment = owner + responsible_team->member
      permission resources_editor = resource_pool_group->member 
    }

"""
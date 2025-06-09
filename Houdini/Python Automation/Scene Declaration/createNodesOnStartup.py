import hou

def create_geo_node():
    # Get the /obj context
    obj = hou.node('/obj')
    if obj is None:
        raise RuntimeError("The /obj context does not exist.")

    # Check if a geo node already exists
    geo_node = obj.createNode('geo', 'my_geo_node', run_init_scripts=False)
    
    # Optional: Set parameters or customize the geo node
    geo_node.setPosition(hou.Vector2(0, 0))  # Set the position in the network editor

    # Layout the network
    obj.layoutChildren()

# Run the function
create_geo_node()

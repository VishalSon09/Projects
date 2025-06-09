"""FXPHD HOU301 - Jeronimo Maggi

Object oriented version for the Extract Transformation script. To use
set the Extract button callback to:

import oop_extract;reload(oop_extract);oop_extract.ExtractXform().extract(hou.node(hou.parm('alembic').eval()).path())

And the Create Collisions callback to:

import oop_extract;oop_extract.ExtractXform().create_collisions(hou.node(hou.parm('dop_node').eval()).path())
"""
import hou


def create_node(parent, node_type, input_node=None, name=''):
        """Create a Houdini node.

        Args:
            parent (hou.Node): Parent node where the node will be created in.
            node_type (str): Type of the node to create.
            input_node (hou.Node): Input node to connect.
            name (str): Optional name for the node.

        Returns:
            hou.Node: Newly created Houdini node.
        """
        if name:
            node = parent.createNode(node_type, name)
        else:
            node = parent.createNode(node_type)
        if input_node:
            node.setInput(0, input_node)
        node.moveToGoodPosition(move_inputs=False)
        return node


class ExtractXform(object):
    CONTEXT = hou.node('/obj')
    static_parts = {}

    def __init__(self):
        """Create the ExtractXform object."""

    def extract(self, alembic_path):
        """Extract the transforms of an Alembic object to the object context.

        Args:
            alembic_path (str): Absolute path to the Alembic geometry to extract.
        """
        self.subnet = create_node(self.CONTEXT, 'subnet', name='extract_animation')
        self.divide_geo_node = create_node(self.subnet, 'geo', name='divide_into_parts')
        self.divide_geo_node.setDisplayFlag(0)
        self.divide_parts_outputs = self._divide_into_parts(alembic_path)
        ExtractXform.static_parts = self._extract_object_transform()

    def create_collisions(self, dopnet):
        """Import the extracted animation as collisions in DOPs.

        Args:
            dopnet (hou.Node): DOP network where the collisions will be created.
        """
        dop_subnet = create_node(hou.node(dopnet), 'subnet', name='collisions')
        packed_nodes = self._create_packed_geo(dop_subnet)
        merge = create_node(dop_subnet, 'merge')
        for node in packed_nodes:
            merge.setNextInput(node)
        merge.moveToGoodPosition(move_inputs=False)
        output = create_node(dop_subnet, 'output', input_node=merge)
        output.setDisplayFlag(True)

    def _divide_into_parts(self, alembic_path):
        """Divide the animation into different parts based on their transforms.

        Object merge the provided alembic inside the divide_geo_node and
        divide it using the Divide By Xform HDA.

        Args:
            alembic_path (str): Absolute path to the Alembic geometry to extract.

        Returns:
            dict: {int: [hou.SopNode, hou.SopNode]}
                  Contains every part as a key with the value being a list made
                  of the static and animated output node respectively. Both objects
                  are hou.SopNodes. 
        """
        obj_merge_alembic = create_node(self.divide_geo_node, 'object_merge')
        obj_merge_alembic.parm('objpath1').set(alembic_path)

        divide_by_xform = create_node(self.divide_geo_node, 'divide_by_xform',
                                      input_node=obj_merge_alembic)
        attrib_name = divide_by_xform.evalParm('moving_parts_attrib')
        total_parts = divide_by_xform.geometry().attribValue(attrib_name)
        parts = {}
        for part in range(1, total_parts + 1):
            blast = self._blast_all_except_current_part(divide_by_xform, attrib_name, part)
            static_output = self._create_static_output(blast, part)
            anim_output = self._create_anim_output(blast, part)
            parts[part] = [static_output, anim_output]
        return parts

    def _blast_all_except_current_part(self, input_node, attrib, part):
        """Blast geometry depending on the value of the part attribute.

        Args:
            input_node (hou.SopNode): The input of the blast node to be created.
            attrib (str): The name of the attribute containing the parts.
            part (int): The value of the part that will be kept.

        Returns:
            hou.SopNode: Newly created Blast SOP.
        """
        blast = create_node(self.divide_geo_node, 'blast', input_node=input_node)
        blast.parm('group').set('@{0}={1}'.format(attrib, part))
        blast.setParms({'grouptype':3, 'negate':1})
        return blast

    def _create_static_output(self, input_node, part):
        """Create the static output for a single part.

        Args:
            input_node (hou.SopNode): The input from where the static output will
                                      be created.
            part (int): The current part for which to create the output.

        Returns:
            hou.SopNode: Null node representing the static output for the current part.
        """
        timeshift = create_node(self.divide_geo_node, 'timeshift', input_node=input_node)
        frame_parm = timeshift.parm('frame')
        frame_parm.deleteAllKeyframes()
        frame_parm.set(1)
        null_output = create_node(parent=self.divide_geo_node, node_type='null',
                                  input_node=timeshift, name='STATIC_PART_{0}'.format(part))
        return null_output

    def _create_anim_output(self, input_node, part):
        """Create the animated output for a single part.

        Args:
            input_node (hou.SopNode): The input from where the animated output will
                                      be created.
            part (int): The current part for which to create the output.

        Returns:
            hou.SopNode: Null node representing the animated output for the current part.
        """
        null_output = create_node(parent=self.divide_geo_node, node_type='null',
                                  input_node=input_node, name='ANIM_PART_{0}'.format(part))
        return null_output

    def _extract_object_transform(self):
        """Extract the transforms of every part individually.

        Use the Extract Geo node and set the source and destination parameters to
        be the static and animated outputs of every part respectively. Connect a
        geometry node as a child containing the static part so it gets the transform
        applied at object level.
        
        Returns:
            dict: [int: hou.SopNode] Contains every part as a key and the output null
                  node inside the static geometry of each part.
        """
        static_outputs = {}
        for part in self.divide_parts_outputs.keys():
            extract_geo = create_node(parent=self.subnet, node_type='extractgeo',
                                      name='extract_part{0}'.format(part))
            extract_geo.parm('srcpath').set(self.divide_parts_outputs[part][0].path())
            extract_geo.parm('dstpath').set(self.divide_parts_outputs[part][1].path())
            static_geo = create_node(parent=self.subnet, node_type='geo',
                                     name='part_{0}'.format(part), input_node=extract_geo)
            obj_merge = create_node(static_geo, 'object_merge')
            obj_merge.parm('objpath1').set(self.divide_parts_outputs[part][0].path())
            static_null = create_node(static_geo, 'null', name='OUT', input_node=obj_merge)
            static_outputs[part] = static_null
        return static_outputs

    def _create_packed_geo(self, parent):
        """Create an RBD Packed Object DOP for every part.

        Args:
            parent (hou.DopNode): Parent node where the RBD Packed Objects will
                                  be created.
        Returns:
            list: RBD Packed Object DOPs created.
        """
        packed_nodes = []
        for part in ExtractXform.static_parts.keys():
            packed_node = create_node(parent, 'rbdpackedobject', name='part_{0}'.format(part))
            packed_node.parm('soppath').set(ExtractXform.static_parts[part].path())
            packed_node.setParms({'initialstate':2, 'usetransform':1})
            packed_nodes.append(packed_node)
        return packed_nodes

from ..wce.worldtree import worldtree

def encode_worldtree(parser, collection, nodes) -> str:

    wt = worldtree()

    # Use collection name as tag
    wt.tag = collection.name

    wt.worldnodes = []

    # sort by WorldNode_#
    def get_index(o):
        try:
            return int(o.name.split("_")[-1])
        except:
            return 0

    nodes = sorted(nodes, key=get_index)

    for obj in nodes:

        props = obj.quail_worldnode

        wn = worldtree.worldnode()

        wn.normalabcd = (
            float(props.normal_x),
            float(props.normal_y),
            float(props.normal_z),
            float(props.normal_w),
        )

        wn.worldregiontag = props.region_tag
        wn.fronttree = int(props.front_tree)
        wn.backtree = int(props.back_tree)

        wt.worldnodes.append(wn)

    parser.worldtrees[wt.tag] = wt

    return ""
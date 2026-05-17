import bpy, bmesh, re, time
from mathutils import Vector
from mathutils.kdtree import KDTree
from ...common.mesh import cleanup_mesh_geometry, mesh_boundary_cleanup
from ...common.mesh import bmesh_from_mesh, mesh_from_bmesh, merge_verts_by_attrs
from ...common.math_helpers import aabb_intersects, aabb_mesh_world

def collapse_vertices_across_objects(objs, threshold=0.05):
    eps = 1e-6

    # 1) Build BMesh per object, collect coords+mapping
    coords = []
    mapping = []        # [(obj, bmvert, fpscale_factor), ...]
    bm_by_obj = {}      # {obj: bm, ...}

    for ob in objs:
        if ob.type != 'MESH':
            continue

        bm = bmesh_from_mesh(ob)
        bm.verts.ensure_lookup_table()
        bm_by_obj[ob] = bm
        wm = ob.matrix_world

        # ----------------------------------------
        # FPSCALE snapping factor
        # ----------------------------------------

        factor = None
        if ob.get("quaildef") == "dmspritedef2":
            props = getattr(ob, "quail_dmspritedef2", None)
            if props:
                fpscale = int(props.fpscale)
                factor = 2 ** fpscale

        for v in bm.verts:
            coords.append(wm @ v.co)
            mapping.append((ob, v, factor))

    if not coords:
        return

    # 2) Build KD-tree once
    kd = KDTree(len(coords))
    for i, co in enumerate(coords):
        kd.insert(co, i)

    kd.balance()
    visited = set()

    # 3) For each point, cluster & snap/merge
    for i, co in enumerate(coords):
        ob_i, v_i, _ = mapping[i]

        # skip deleted verts or already clustered
        if not v_i.is_valid or i in visited:
            continue

        # find all nearby indices
        raw = kd.find_range(co, threshold)
        nbrs = [
            j for (_, j, _) in raw
            if mapping[j][1].is_valid
        ]

        visited.update(nbrs)
        if len(nbrs) < 2:
            continue

        # new cluster centroid in world‐space
        centroid = (
            sum((coords[j] for j in nbrs), Vector())
            / len(nbrs)
        )

        # snap/merge each member back in its local BM
        for j in nbrs:
            ob, v, factor = mapping[j]

            # if this vertex was deleted during the loop, skip it
            if not v.is_valid:
                continue

            bm = bm_by_obj[ob]
            lt = ob.matrix_world.inverted() @ centroid

            # ----------------------------------------
            # FPSCALE quantization
            # ----------------------------------------

            if factor is not None:
                lt.x = round(lt.x * factor) / factor
                lt.y = round(lt.y * factor) / factor
                lt.z = round(lt.z * factor) / factor

            # try merging into an existing neighbor
            merged = False
            for e in v.link_edges:
                ov = e.other_vert(v)
                if (ov.co - lt).length < eps:
                    bmesh.ops.pointmerge(
                        bm,
                        verts=[v, ov],
                        merge_co=ov.co
                    )

                    merged = True

                    break

            if not merged:
                v.co = lt

            # update just this one entry in coords
            coords[j] = ob.matrix_world @ v.co

    # 4) Collapse any zero‐length edges in each BM
    for ob, bm in bm_by_obj.items():

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        to_merge = []
        for e in bm.edges:
            v1, v2 = e.verts
            if (v1.co - v2.co).length < eps:
                to_merge.append((v1, v2))

        for v1, v2 in to_merge:
            if v1.is_valid and v2.is_valid:
                bmesh.ops.pointmerge(
                    bm,
                    verts=[v1, v2],
                    merge_co=v1.co
                )

    # 5) Write back
    for ob, bm in bm_by_obj.items():
        mesh_from_bmesh(bm, ob)

def region_mesh_cleanup(objs):
    for ob in objs:
        bm = bmesh_from_mesh(ob)
        mesh_boundary_cleanup(bm)
        cleanup_mesh_geometry(bm)
        mesh_boundary_cleanup(bm)
        mesh_from_bmesh(bm, ob)

def split_edges_to_snap_verts(objs, threshold=1e-4):
    world_verts = {
        ob: [ob.matrix_world @ v.co for v in ob.data.vertices]
        for ob in objs
    }

    # Build KD-tree per object once
    kd_by_obj = {}
    for ob, verts in world_verts.items():
        kd = KDTree(len(verts))
        for i, co in enumerate(verts):
            kd.insert(co, i)
        kd.balance()
        kd_by_obj[ob] = kd

    # Cache AABBs once
    aabbs = {ob: aabb_mesh_world(ob) for ob in objs}

    for ob_B in objs:
        bm = bmesh_from_mesh(ob_B)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        minB, maxB = aabbs[ob_B]
        wm_B = ob_B.matrix_world
        edge_hits = {}

        for ob_A in objs:
            if ob_A is ob_B:
                continue
            minA, maxA = aabbs[ob_A]
            if not aabb_intersects(minA, maxA, minB, maxB, epsilon=0.001):
                continue

            kd_A = kd_by_obj[ob_A]
            wverts_A = world_verts[ob_A]

            for edge in bm.edges:
                v1, v2 = edge.verts
                w1 = wm_B @ v1.co
                w2 = wm_B @ v2.co
                seg = w2 - w1
                seg_len2 = seg.length_squared
                if seg_len2 == 0.0:
                    continue

                mid = (w1 + w2) * 0.5
                radius = seg.length * 0.5 + threshold
                candidates = kd_A.find_range(mid, radius)

                for (_, idx, _) in candidates:
                    p = wverts_A[idx]
                    t = (p - w1).dot(seg) / seg_len2
                    if 0.0 < t < 1.0:
                        proj = w1 + seg * t
                        if (proj - p).length <= threshold:
                            edge_hits.setdefault(edge, []).append(t)

        if not edge_hits:
            bm.free()
            continue

        # splitting logic unchanged
        for edge, hits in edge_hits.items():
            if not edge.is_valid:
                continue
            hits.sort(key=float)
            v1, v2 = edge.verts
            orig_v2 = v2
            current_edge = edge
            offset = 0.0
            for t in hits:
                local_t = (t - offset) / (1.0 - offset)
                result = bmesh.ops.subdivide_edges(
                    bm, edges=[current_edge], cuts=1,
                    edge_percents={current_edge: local_t},
                )
                new_vert = next(
                    (g for g in result["geom_split"] if isinstance(g, bmesh.types.BMVert)),
                    None
                )
                if new_vert:
                    for e_next in new_vert.link_edges:
                        if orig_v2 in e_next.verts:
                            current_edge = e_next
                            break
                offset = t

        merge_verts_by_attrs(bm)
        mesh_from_bmesh(bm, ob_B)

def triangulate_meshes(objs):
    """Triangulate faces and very quickly."""
    for ob in objs:
        bm = bmesh_from_mesh(ob)

        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='EAR_CLIP')
        cleanup_mesh_geometry(bm)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='EAR_CLIP')

        mesh_from_bmesh(bm, ob)

def delete_empty_region_meshes_and_clear_sprite(region_objs):
    """
    Remove region mesh objects that have no vertices, delete any *_BR empties
    parented to them, and clear the SPRITE property on the corresponding region empty.
    """
    for obj in list(region_objs):
        if obj.type != 'MESH':
            continue
        # if no verts, we want to nuke it
        if len(obj.data.vertices) == 0:
            # 1) clear the SPRITE field on R###### empty
            m = re.match(r"R(\d+)_DMSPRITEDEF", obj.name)
            if m:
                idx = int(m.group(1))
                region_empty_name = f"R{idx:06d}"
                region_empty = bpy.data.objects.get(region_empty_name)
                if region_empty and "SPRITE" in region_empty:
                    region_empty["SPRITE"] = ""

            # 3) delete the mesh itself
            bpy.data.objects.remove(obj, do_unlink=True)
            region_objs.remove(obj)

def finalize_region_meshes(region_objs, edge_snap_threshold=0.03, collapse_thresh=0.05):
    start = time.perf_counter()

    collapse_vertices_across_objects(region_objs, threshold=collapse_thresh)
    region_mesh_cleanup(region_objs)
    split_edges_to_snap_verts(region_objs, threshold=edge_snap_threshold)
    collapse_vertices_across_objects(region_objs, threshold=collapse_thresh)
    triangulate_meshes(region_objs)
    delete_empty_region_meshes_and_clear_sprite(region_objs)

    elapsed = time.perf_counter() - start

    print(f"🎉 All region meshes finalized in {elapsed:.2f} seconds.")

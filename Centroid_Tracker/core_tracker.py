from scipy.spatial import KDTree
import numpy as np
import sys
import pandas as pd

def track_centriods(mat, radius, max_gap):
    """
    Core centroid tracker for `centroid_tracker.py`.
    The main purpose is to assign CONSISTENT IDs to centroids in the image stack
    using KD-Tree as the nearest-neighbor tracking algorithm.

    Parameters:
        mat: datastructure from `load_mat.py`.
        radius: nearest-neighbor search radius.
        max_gap: Maximum frame gap – a new ID is assigned to the centroid if it reappears.
    """

    # Get the metadata / data
    frames = mat['frames']
    # [frame #, key]
    n_frames = mat['n_frames']
    rows = []

    # Dictionary of active centroid tracks to be appended to in each frame.
    # (previous_x, previous_y, last_seen_frame)
    active = {}

    # Create an initial frame seed. Needed to instantiate KDTree.
    # this also defines the format for the full loop.
    f0 = frames[0]
    seed_ids = [] # list of seed IDs from the first frame
    id = 0
    for i in range(f0['n']):
        active[id] = (f0['x'][i], f0['y'][i], 0)
        rows.append(dict(frame=0, centroid_idx=i, track_id=id,
                         x=f0['x'][i], y=f0['y'][i], dn=f0['dn'][i],
                         area=f0['a'][i], match_dist=0.0))
        seed_ids.append(id)
        id += 1

    # Cycle through the frames
    for i in range(1, n_frames):
        f = frames[i]
        
        # Check for empty data
        if f['n'] == 0:
            continue

        # Create a ndarray of current [x, y]s.
        pts = np.column_stack([f['x'], f['y']])

        # get Active Tracks 
        active_ids = []
        active_xys = []
        # Append the Previous Active Tracks:
        for tid, (lx, ly, last_seen) in active.items():
            # Check to see if the ID has disapeared for too long:
            # if its "active" then add to the active lists
            if i - last_seen <= max_gap:
                active_ids.append(tid)
                active_xys.append([lx, ly])

        assigned_new = {} # New centroid Track IDs
        assigned_dist = {} # New centroid ID frame-frame distance

        if active_xys:
            # instantiate the KDTree with the active [x,y]s
            active_xys = np.array(active_xys)
            tree_old = KDTree(active_xys)
            
            # we can now query against the KDTree!
            # Input the NEW [x,y], returns k-nn distances and their IDs!
            dists, idxs = tree_old.query(pts, k=1, distance_upper_bound=radius)

            # build a "candidate list" based on distance separation:
            # (distance, new x-loc, previous x-loc) - x-loc=prox for ID...?
            candidates = sorted(
                [(dists[j], j, idxs[j]) for j in range(f['n']) if dists[j] <= radius],
                key=lambda t: t[0]
            )

            # Create a set (unique items) of used and new x-locs.
            # This will (hopefully) prevent errors where the centroid doesn't move...
            used_old = set()
            used_new = set()

            for dist, new_j, old_j in candidates:
                if (new_j in used_new) or (old_j in used_old):
                    continue
                # Get the track ID from the old KDTree
                tid = active_ids[old_j]
                assigned_new[new_j] = tid
                assigned_dist[new_j] = dist
                
                used_new.add(new_j)
                used_old.add(old_j)

            # Emit rows and update the active list!
            for j in range(f['n']):
                if j in assigned_new:
                    tid = assigned_new[j]
                    dist = assigned_dist[j]
                else:
                    # skip and go to the next id
                    tid = id 
                    dist = np.nan
                    id += 1

                active[tid] = (f['x'][j], f['y'][j], i)
                rows.append(dict(frame=i, centroid_idx=j, track_id=tid, x=f['x'][j],
                                 y=f['y'][j], dn=f['dn'][j], area=f['a'][j], match_dist=dist))
                
        # Prune dead tracks to keep active dict lean
        active = {tid: v for tid, v in active.items() if i - v[2] <= max_gap}

    return pd.DataFrame(rows)
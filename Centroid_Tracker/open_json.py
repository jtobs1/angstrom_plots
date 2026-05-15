import json
from pathlib import Path

def open_json(fdir):
    with open(fdir, 'r') as f:
        data = json.load(f)
    bands = ['450','470','490','520']
    centroid_files = []
    for i, j in zip(bands, data['camera_SN']):
        centroid_files.append(Path(data['data_dir']+f"Band_{i}nm_BFS-PGE-16S7M_SN"+j+"/"+f"Band_{i}nm_BFS-PGE-16S7M_SN"+j+"_centroids.mat"))
    return centroid_files
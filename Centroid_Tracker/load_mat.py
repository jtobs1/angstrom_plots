import posixpath, sys
import scipy.io as sio

def load_mat(fname):
    mat = sio.loadmat(fname)

    n_frames = mat['data_files'].shape[0]
    c = mat['centroid']

    frames = []
    for i in range(n_frames):
        # The SHAPE of each entry in frames doesn't have to be constitent...
        # ie, the # centroids is no constant.

        # [x, y] for frame (i) in this camera
        # reshaping... wonky matlab stuff
        x = c['x'][0,i].flatten()
        y = c['y'][0,i].flatten()
        dn= c['total_DN'][0,i].flatten()
        a = c['area'][0,i].flatten()

        frames.append(dict(x=x, y=y, dn=dn, a=a, n=len(x)))

    return dict(frames=frames, n_frames=n_frames, raw=mat)


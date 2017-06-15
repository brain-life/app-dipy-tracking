import time
from dipy.tracking.local import LocalTracking
import csd_peaks, create_classifier, create_seeds, load_file, prob_dg
from nibabel.streamlines import Tractogram, save
from dipy.viz import fvtk
from dipy.viz.colormap import line_colors


def compute_streamlines(peaks, classifier, seeds, affine):
    # Initialization of LocalTracking. The computation happens in the next step.
    start = time.time()
    streamlines = LocalTracking(peaks, classifier, seeds, affine, step_size=.5)

    # Compute streamlines and store as a list.
    streamlines = list(streamlines)
    print("Number of streamlines " + str(len(streamlines)))
    end = time.time()
    print("Computed streamlines " + str((end - start)))
    return streamlines

def create_trk(streamlines, affine, name):
    start = time.time()
    tractogram = Tractogram(streamlines, affine_to_rasmm=affine)
    save(tractogram, name + '.trk')
    end = time.time()
    print("Created the trk file: " + str((end - start)))

def make_picture(name, streamlines):
    # Prepare the display objects.
    start = time.time()
    print("Making pretty pictures")
    if fvtk.have_vtk:
        streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))

        # Create the 3d display.
        r = fvtk.ren()
        fvtk.add(r, streamlines_actor)

        # Save still images for this static example.
        fvtk.record(r, n_frames=1, out_path=name + '.png',
                    size=(800, 800))
    end = time.time()
    print ('Made pretty pictures: ' + str((end - start)))


def streamlines():
    probdg = prob_dg.make_probdg
    classifier = create_classifier.classifier()
    seeds = create_seeds.seeds()
    d = load_file.load_files()
    affine = load_file.load_affine(d.data_file)
    streamlines = compute_streamlines(probdg, classifier, seeds, affine)
    create_trk(streamlines=streamlines, affine=affine, name='prob')
    make_picture('prob', streamlines=streamlines)

streamlines()
print('Hooray')




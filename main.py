import time
import numpy as np
import nibabel as nib
import json
import os, sys
from dipy.core.gradients import gradient_table
from dipy.viz import fvtk, actor, window
from dipy.viz.colormap import line_colors
from dipy.tracking import utils
from dipy.io.gradients import read_bvals_bvecs
from dipy.reconst.shm import CsaOdfModel
from dipy.data import default_sphere
from dipy.direction import peaks_from_model
from dipy.tracking.local import ThresholdTissueClassifier
from dipy.tracking.local import LocalTracking
from nibabel.streamlines import Tractogram, save
from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                   auto_response)
from dipy.direction import ProbabilisticDirectionGetter
"""
env = os.environ['ENV']
if env == 'IUHPC':
    sys.path.append("/N/dc2/projects/lifebid/code/aarya/dipy")
if env == 'VM':
    sys.path.append("/usr/local/dipy") #add this on jetstream
"""
def main():
    start = time.time()

    with open('config.json') as config_json:
        config = json.load(config_json)
    
    # Load the data
    dmri_image = nib.load(config['data_file'])
    dmri = dmri_image.get_data()
    affine = dmri_image.affine
    #aparc_im = nib.load(config['freesurfer'])
    aparc_im = nib.load('volume.nii.gz')
    aparc = aparc_im.get_data()
    end = time.time()
    print('Loaded Files: ' + str((end - start)))

    # Create the white matter and callosal masks
    start = time.time()
    wm_regions = [2, 41, 16, 17, 28, 60, 51, 53, 12, 52, 12, 52, 13, 18,
                  54, 50, 11, 251, 252, 253, 254, 255, 10, 49, 46, 7]

    wm_mask = np.zeros(aparc.shape)
    for l in wm_regions:
        wm_mask[aparc == l] = 1

    # Create the gradient table from the bvals and bvecs

    bvals, bvecs = read_bvals_bvecs(config['data_bval'], config['data_bvec'])

    gtab = gradient_table(bvals, bvecs, b0_threshold=100)
    end = time.time()
    print('Created Gradient Table: ' + str((end - start)))

    ##The probabilistic model##

    # Use the Constant Solid Angle (CSA) to find the Orientation Dist. Function
    # Helps orient the wm tracts
    start = time.time()
    csa_model = CsaOdfModel(gtab, sh_order=6)
    csa_peaks = peaks_from_model(csa_model, dmri, default_sphere,
                                 relative_peak_threshold=.8,
                                 min_separation_angle=45,
                                 mask=wm_mask)
    print('Creating CSA Model: ' + str(time.time() - start))

    # Begins the seed in the wm tracts
    seeds = utils.seeds_from_mask(wm_mask, density=[1, 1, 1], affine=affine)
    print('Created White Matter seeds: ' + str(time.time() - start))

    # Create a CSD model to measure Fiber Orientation Dist
    print('Begin the probabilistic model')

    response, ratio = auto_response(gtab, dmri, roi_radius=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
    csd_fit = csd_model.fit(dmri, mask=wm_mask)
    print ('Created the CSD model: ' + str(time.time() - start))

    # Set the Direction Getter to randomly choose directions

    prob_dg = ProbabilisticDirectionGetter.from_shcoeff(csd_fit.shm_coeff,
                                                        max_angle=30.,
                                                        sphere=default_sphere)
    print('Created the Direction Getter: ' + str(time.time() - start))

    # Restrict the white matter tracking
    classifier = ThresholdTissueClassifier(csa_peaks.gfa, .25)

    print('Created the Tissue Classifier: ' + str(time.time() - start))

    # Create the probabilistic model
    streamlines = LocalTracking(prob_dg, tissue_classifier=classifier, seeds=seeds, step_size=.5, max_cross=1,affine=affine)
    print('Created the probabilistic model: ' + str(time.time() - start))

    # Compute streamlines and store as a list.
    streamlines = list(streamlines)
    print('Computed streamlines: ' + str(time.time() - start))
    
    #from dipy.tracking.streamline import transform_streamlines
    #streamlines = transform_streamlines(streamlines, np.linalg.inv(affine))
    
    # Create a tractogram from the streamlines and save it 
    tractogram = Tractogram(streamlines, affine_to_rasmm=affine)
    #tractogram.apply_affine(np.linalg.inv(affine))
    save(tractogram, 'track.tck')
    end = time.time()
    print("Created the tck file: " + str((end - start)))

main()

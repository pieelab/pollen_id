import glob
import os
import logging
import shutil
import tempfile
import numpy as np
import unittest
from sticky_pi_ml.universal_insect_detector.ml_bundle import MLBundle, ClientMLBundle
from sticky_pi_ml.universal_insect_detector.trainer import Trainer
from sticky_pi_ml.universal_insect_detector.predictor import Predictor
from sticky_pi_ml.annotations import Annotation
from sticky_pi_api.client import LocalClient



class MockPredictor(Predictor):
    _detect_client_chunk_size = 3
    def _detect_instances(self, image, score_threshold=.2):
        out = []
        for i in range(5):
            contour = np.array([[[1, 1],[3, 1],[3, 3], [1, 3]]]).transpose((1, 0, 2))
            a = Annotation(contour, '#ff0000')
            out.append(a)
        return out


logging.getLogger().setLevel(logging.INFO)
test_dir = os.path.dirname(__file__)


class TestUID(unittest.TestCase):
    _bundle_dir = os.path.join(test_dir, 'ml_bundles/universal-insect-detector')
    _test_image = os.path.join(test_dir, "raw_images/5c173ff2/5c173ff2.2020-06-20_21-33-24.jpg")
    _raw_images_dir = os.path.join(test_dir, "raw_images")

    def test_ml_bundle(self):
        bndl = MLBundle(self._bundle_dir)
    #
    def test_client_ml_bundle(self):
        client_temp_dir = tempfile.mkdtemp(prefix='sticky_pi_client_')

        # the di dirname is used to identify the ML bundle
        temp_dst_bundle = os.path.join(tempfile.mkdtemp(prefix='sticky_pi_test_'), 'universal-insect-detector')
        os.makedirs(temp_dst_bundle)
        try:
            cli = LocalClient(client_temp_dir)

            bndl = ClientMLBundle(self._bundle_dir, cli)
            bndl.sync_local_to_remote()

            # should warn the ML bundle is empty at this stage
            bndl2 = ClientMLBundle(temp_dst_bundle, cli)

            # should reinit the bundle after dl the data to the local dir
            bndl2.sync_remote_to_local()
            # bndl2 = ClientMLBundle(bndl2._root_dir, cli)

            cf1 = bndl._config
            cf2 = bndl2._config
            cf1.MODEL.WEIGHTS = None
            cf2.MODEL.WEIGHTS = None
            cf1.OUTPUT_DIR = None
            cf2.OUTPUT_DIR = None

            self.assertDictEqual(cf1, cf2)
            self.assertEqual([os.path.basename(p) for p in sorted(glob.glob(os.path.join(bndl.dataset._data_dir)))],
                             [os.path.basename(p) for p in sorted(glob.glob(os.path.join(bndl2.dataset._data_dir)))])

        finally:
            shutil.rmtree(client_temp_dir)
            shutil.rmtree(temp_dst_bundle)
            pass
    #
    def test_client_predict(self):
        client_temp_dir = tempfile.mkdtemp(prefix='sticky_pi_client_')
        # the di dirname is used to identify the ML bundle
        temp_dst_bundle = os.path.join(tempfile.mkdtemp(prefix='sticky_pi_test_'), 'universal-insect-detector')
        os.makedirs(temp_dst_bundle)
        try:
            cli = LocalClient(client_temp_dir)

            bndl = ClientMLBundle(self._bundle_dir, cli)
            bndl.sync_local_to_remote()
            ims_to_pred = [im for im in sorted(glob.glob(os.path.join(self._raw_images_dir,'**', '*.jpg')))]
            cli.put_images(ims_to_pred)
            pred = MockPredictor(bndl)
            pred.detect_client()

            # second time should do nothing
            # pred.detect_client()

        finally:
            shutil.rmtree(client_temp_dir)
            shutil.rmtree(temp_dst_bundle)
            pass

    def test_validate(self):
        bndl = MLBundle(self._bundle_dir)
    #     # bndl.dataset.visualise(augment=True)
        pred = MockPredictor(bndl)
        t = Trainer(bndl)
        temp_dir = tempfile.mkdtemp(prefix='sticky_pi_test_')
        try:
            t.validate(pred, out_dir=temp_dir)
        finally:
            shutil.rmtree(temp_dir)
            # print(temp_dir)

    # #     t.resume_or_load(resume=True)
    #     # t.train()
    # def test_Predictor(self):
    #     bndl = MLBundle(self._bundle_dir)
    #     pred = Predictor(bndl)
    # #     im = Image(self._test_image)
    # #     pred.detect(im)



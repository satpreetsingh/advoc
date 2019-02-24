import os
import pickle
import unittest

import numpy as np

import advoc.audioio as audioio
import advoc.spectral as spectral


AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
WAV_MONO = os.path.join(AUDIO_DIR, 'mono.wav')
WAV_MONO_R9Y9 = os.path.join(AUDIO_DIR, 'mono_22k_r9y9.pkl')


class TestSpectralModule(unittest.TestCase):

  def setUp(self):
    _, self.wav_mono_44 = audioio.decode_audio(WAV_MONO, fastwav=True)
    _, self.wav_mono_22 = audioio.decode_audio(WAV_MONO, fs=22050)
    _, self.wav_mono_24 = audioio.decode_audio(WAV_MONO, fs=24000)


  def test_stft(self):
    X = spectral.stft(self.wav_mono_44, 1024, 256)
    self.assertEqual(X.dtype, np.complex128)
    self.assertEqual(X.shape, (647, 513, 1), 'invalid shape')

    X_mag = np.abs(X)
    self.assertEqual(X_mag.dtype, np.float64)
    self.assertAlmostEqual(np.sum(X_mag), 32820.952, 3, 'invalid spec')
    self.assertAlmostEqual(np.sum(X_mag[200]), 115.632, 3, 'invalid spec')
    self.assertAlmostEqual(np.sum(X_mag[40]), 6.049, 3, 'invalid spec')


  def test_tacotron2(self):
    melspec = spectral.waveform_to_tacotron2_feats(self.wav_mono_24)
    self.assertEqual(melspec.dtype, np.float64)
    self.assertEqual(melspec.shape, (303, 80, 1), 'invalid shape')

    self.assertAlmostEqual(np.sum(melspec), 5122.213, 3, 'invalid spec')
    self.assertAlmostEqual(np.sum(melspec[200]), 31.119, 3, 'invalid spec')
    self.assertAlmostEqual(np.sum(melspec[40]), 5.132, 3, 'invalid spec')


  def test_r9y9(self):
    with open('/home/cdonahue/advoc/advoc/tests/audio/mono_22k.pkl', 'rb') as f:
      wav_ref = pickle.load(f)
    melspec = spectral.waveform_to_r9y9_feats(self.wav_mono_22)
    self.assertEqual(melspec.dtype, np.float64)
    self.assertEqual(melspec.shape, (325, 80, 1), 'invalid shape')

    with open(WAV_MONO_R9Y9, 'rb') as f:
      r9y9_melspec = pickle.load(f)
    r9y9_melspec = np.swapaxes(r9y9_melspec, 0, 1)[:, :, np.newaxis]
    self.assertTrue(np.array_equal(melspec, r9y9_melspec), 'not equal r9y9')


if __name__ == '__main__':
  unittest.main()

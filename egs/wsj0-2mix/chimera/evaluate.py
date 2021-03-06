import sys
sys.path.append('../../../../../onssen/')

from onssen import utils
from sklearn.cluster import KMeans
import librosa
import numpy as np
import torch


class tester_chimera(utils.tester):
    def get_est_sig(self, input, label, output):
        """
        args:
            feature_mix: batch x frame x frequency
            embedding: batch x frame x frequency x embedding_dim
            stft_r_mix: batch x frame x frequency
            stft_i_mix: batch x frame x frequency
            sig_ref: batch x num_spk x nsample
        return:
            sig_est: batch x num_spk x nsample
        """
        feature_mix, = input
        embedding, mask_A, mask_B = output
        stft_r_mix, stft_i_mix, sig_ref = label

        stft_r_mix = stft_r_mix.detach().cpu().numpy()
        stft_i_mix = stft_i_mix.detach().cpu().numpy()
        embedding = embedding.detach().cpu().numpy()
        feature_mix = feature_mix.detach().cpu().numpy()
        mask_A = mask_A.detach().cpu().numpy()
        mask_B = mask_B.detach().cpu().numpy()
        
        stft_mix = stft_r_mix + 1j * stft_i_mix
        batch, frame, frequency = feature_mix.shape
        batch, num_spk, nsample = sig_ref.shape
        mask = np.zeros((num_spk, frame, frequency))
        mask[0, :, :] = mask_A[0]
        mask[1, :, :] = mask_B[0]
        stft_est = stft_mix * mask
        sig_est = np.zeros((batch, num_spk, nsample))
        for i in range(num_spk):
            sig_est[0, i] = librosa.core.istft(stft_est[i].T, hop_length=64, length=nsample)
        sig_est = torch.tensor(sig_est).to(self.device)
        return sig_est, sig_ref


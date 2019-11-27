import os
import re
import pandas as pd
import numpy as np

import mne
import autoreject
import TruScanEEGpy
import neurokit2 as nk


def _check_events(raw):
    event_channel = raw.copy().pick_channels(["Foto"]).to_data_frame()["Foto"]
    events = nk.events_find(event_channel, inter_min=200, discard_last=1)
    if len(events["Duration"]) != 60:
        print("Warning: " + str(len(events["Duration"])) + " events")
    return(events)


def _add_events(raw, participant="S1"):
    events_conditions = pd.read_csv("../data/" + participant + "/" + participant + ".csv")
    events_conditions = events_conditions["Category_Arousal"]
    events = _check_events(raw)
    events, event_id = nk.events_to_mne(events["Onset"], conditions=events_conditions)
    raw.add_events(events, "Foto")
    return(raw, events, event_id)


def _create_eog(raw):
    eog = raw.copy().pick_channels(["124", "125"]).to_data_frame()
    eog = eog["124"] - eog["125"]
    raw = nk.eeg_add_channel(raw, eog, channel_type="eog", channel_name="EOG")
    raw = raw.drop_channels(["124", "125"])
    return(raw)

def _set_montage(raw):
    mne.rename_channels(raw.info, dict(zip(raw.info["ch_names"], TruScanEEGpy.convert_to_tenfive(raw.info["ch_names"]))))
    montage = TruScanEEGpy.montage_mne_128(TruScanEEGpy.layout_128(names="10-5"))
    extra_channels = np.array(raw.info["ch_names"])[np.array([i not in montage.ch_names for i in raw.info["ch_names"]])]
    raw = raw.drop_channels(extra_channels[np.array([i not in ["EOG"] for i in extra_channels])])
    raw = raw.set_montage(montage)
    return(raw)




list_participants = os.listdir("../data/")
x = np.array(["." not in x for x in list_participants])
list_participants = list(np.array(list_participants)[x])

for participant in list_participants:
    print(participant)
    raw = mne.io.read_raw_edf("../data/" + participant + "/" + participant + ".edf", preload = True)
    raw, events, event_id = _add_events(raw)
#    raw = raw.resample(300, npad='auto')

    # Create EOGs
    raw = _create_eog(raw)

    # Set montage
    raw = _set_montage(raw)

    eeg_channels = mne.pick_types(raw.info, eeg=True)

    # =============================================================================
    # Preprocessing
    # =============================================================================

    # Bad channels - manual
    raw.plot(n_channels = 64, duration = 60, scalings = {"eeg": 20e-5})
#    raw.plot(butterfly = True)
    if participant == "S1":
        raw.info['bads'] = ["PO7"]
    raw = raw.interpolate_bads(reset_bads = True)


    # Rereference
#    raw.set_eeg_reference('average', projection=True)
#    raw.apply_proj()
    raw = raw.set_eeg_reference(['TP9', 'TP10'])

    # Filter
    raw = raw.notch_filter(np.arange(50, 251, 50), picks = eeg_channels, fir_design='firwin')
    raw = raw.filter(1, 30)

    # =============================================================================
    # Epoching
    # =============================================================================
    epochs = mne.Epochs(raw, events=events, event_id=event_id, tmin=-0.2, tmax=0.8, detrend=1, preload=True)
    epochs.resample(200, npad="auto")

    # Autoreject
    ransac = autoreject.Ransac(verbose='progressbar', picks=eeg_channels, n_jobs=1)
    epochs = ransac.fit_transform(epochs)
    reject = autoreject.get_rejection_threshold(epochs)


    # =============================================================================
    # ICA
    # =============================================================================
    ica = mne.preprocessing.ICA(n_components=30, method='fastica', max_iter=1000, noise_cov=None).fit(epochs, reject=reject)

    # Based on EOG
    ica.exclude = []
    eog_indices, eog_scores = ica.find_bads_eog(epochs)
    ica.exclude = eog_indices
    ica.plot_scores(eog_scores)

    ica.plot_properties(raw, picks=eog_indices)

    # ica.plot_components()
    # #ica.plot_properties(epochs, picks=[1, 2, 9])
    # #ica.exclude += [1, 2, 9]
    # epochs = ica.apply(epochs)
    #
    # # Autoreject 2
    # epochs = ransac.fit_transform(epochs)
    # reject = autoreject.get_rejection_threshold(epochs)
    # epochs.drop_bad(reject=reject)
    #
    #
    # evoked = epochs.average()
    #
    # #epochs.average().plot()
    # #epochs.average().plot_topomap()
    # epochs.average().plot_joint()
    # #mne.viz.plot_epochs(epochs.average(), butterfly = True)
    #
    #
    # #mne.viz.plot_evoked_topo(evoked)
    #
    #
    # #raw.plot()
    #
    # #epochs = mne.Epochs(raw, events=events, tmin=-0.2, tmax=0.5, detrend = 0, preload=True)
    # #reject = autoreject.get_rejection_threshold(epochs)
    # #raw.drop_channels(reject=reject)
    # #
    # #raw.drop_channels()
Affective Task Analysis
================

  - [Utilities](#utilities)
      - [Packages](#packages)
      - [Functions](#functions)
  - [Preprocessing](#preprocessing)
      - [Data](#data)

# Utilities

## Packages

``` python
import os
import re
import pandas as pd
import numpy as np

import mne
import autoreject
import neurokit as nk
```

## Functions

``` python
def check_events(raw):
    events = raw.to_data_frame()["Foto"]
    events = nk.find_events(events, cut = "higher")
    if len(events["durations"]) != 62:
        print("Warning!")
        raw.to_data_frame()["Foto"].plot()
    else:
        return(events)
```

``` python
def add_events(raw):
    events = check_events(raw)
    events, events_id = nk.eeg_create_mne_events(events["onsets"])
    raw.add_events(events, "Foto")
    return(raw)
```

# Preprocessing

## Data

``` python
list_participants = os.listdir("../data/")
x = np.array(["." not in x for x in list_participants])
list_participants = list(np.array(list_participants)[x])
list_participants
## ['S1']
```

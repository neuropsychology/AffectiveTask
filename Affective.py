import neuropsydia as n
import numpy as np
import pandas as pd
import random, os

# Define the path where the images stimuli are stored
path = "./stimuli/"


# =============================================================================
# Function definition
# =============================================================================
def fixation_cross(time = 3000):
    n.newpage("grey", auto_refresh = False)
    n.write("+", size = 2)
    trigger.stop()
    n.refresh()
    n.time.wait(time)

# =============================================================================
# Initialization
# =============================================================================
# Read stimuli
data_stimuli = pd.read_csv("stimuli_list.csv", index_col = 0).rename(columns = {"ID" : "Stimulus"})

# Create a list of filename of the images and randomly shuffle it
list_stimuli = list(data_stimuli["Stimulus"].values)
random.shuffle(list_stimuli)


# Initialize trigger
trigger = n.Trigger(TTL=False, photosensor="black", photosensor_size = 2.5)

#Create empty lists to store the stimuli displayed and the rating of the ppts
stimuli = []
rating_arousal = []
rating_valence = []
fixation = []


# =============================================================================
# Start
# =============================================================================
n.start()

participant = n.ask("ID: ")


n.instructions("In this task, you will be presented with different images and your task is to rate how intense your feeling is when you see the images.")

fixation_cross(3000)

for i in range(60): # Number of trials
    n.newpage("grey", auto_refresh=False)
    random_image = random.choice([
            x for x in list_stimuli
            if os.path.isfile(os.path.join(path, x))
            ])
    n.image("images/" + random_image, size = 20, y=0)
    trigger.start()
    n.refresh()
    n.time.wait(3000)
    list_stimuli.remove(random_image)
    random_image = random_image.split(".")[0]
    stimuli.append(random_image)

    fixation_cross(5000)

    n.newpage("grey", auto_refresh=False)
    trigger.stop()
    response_arousal = n.scale(title="Your emotion was:",
        y=3,
        line_length=10,
        edges=[1,9],
        background='grey',
        anchors=["Not intense", "Intense"],
        point_center=False,
        style="orange",
        show_result=False,
        show_result_shape_line_color="orange"
        )
    rating_arousal.append(response_arousal)
    response_valence = n.scale(
        y=-3,
        line_length=10,
        edges=[1,9],
        background='grey',
        anchors=["Very positive", "Very negative"],
        point_center=True,
        style="red",
        show_result=False,
        show_result_shape_line_color="red"
        )
    rating_valence.append(response_valence)

    ISI = int(np.random.uniform(3000, 5000))
    fixation_cross(ISI)
    n.newpage("grey", auto_refresh=False)

    fixation.append(ISI)
    n.time.wait(ISI)


# =============================================================================
# Save data
# =============================================================================
df = pd.DataFrame({"Stimulus": stimuli,
                   "Arousal" : rating_arousal,
                   "Valence" : rating_valence,
                   "ISI" : fixation,
                   "Trial": list(range(60))})
df["Participant"] = participant

merged_df = df.merge(data_stimuli, how = 'left', on = ["Stimulus"])
merged_df.to_csv("data/S" +  participant + ".csv")


n.close()
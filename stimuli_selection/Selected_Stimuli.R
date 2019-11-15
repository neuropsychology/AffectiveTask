library(tidyverse)
library(tools)
library(ggplot2)
library(see)

## Create a list of images that have been selected

images <- list.files(path = "./images/") %>%
  file_path_sans_ext()

## Create a dataframe that only has the ratings of selected stimuli (images)
df_filter <-read.csv("Original_Ratings.csv", stringsAsFactors = FALSE) %>%
  filter(ID %in% images) %>%
  rename(Tendency_Approach = AvAp)

## Plot the ratings (Valence, Arousal and AvAp) of the selected stimuli
df_filter %>%
  ggplot(aes(x = Valence, y = Arousal)) +
  geom_point(aes(color = Tendency_Approach, size = Category_Valence)) +
  geom_hline(yintercept=5, linetype = "dotted") +
  geom_vline(xintercept = 5, linetype = "dotted") +
  theme_modern()#+
  #geom_text(aes(label=ID),hjust=0, vjust=0)

write.csv(df_filter, "../stimuli_list.csv")

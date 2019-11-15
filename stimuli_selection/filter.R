library(tidyverse)
library(tools)
library(ggplot2)
library(see)

df_filter <-read.csv("Original_Ratings.csv", stringsAsFactors = FALSE) %>%
  select(ID, Valence, Arousal, AvAp, V.H, Description, Category_Valence, Category_Arousal) %>%
  rename(Tendency_Approach = AvAp)

df_filter %>%
  ggplot(aes(x = Valence, y = Arousal)) +
  geom_point(aes(color = Tendency_Approach, size = Category_Valence)) +
  geom_hline(yintercept=5, linetype = "dotted") +
  geom_vline(xintercept = 5, linetype = "dotted") +
  theme_modern()#+
  #geom_text(aes(label=ID),hjust=0, vjust=0)

write.csv(df_filter, "../stimuli_list.csv")

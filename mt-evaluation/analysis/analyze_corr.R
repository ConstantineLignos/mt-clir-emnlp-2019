library(tidyr)
library(dplyr)
library(ggplot2)
library(scales)
library(xtable)

theme_set(theme_bw())

corrs <- as.tbl(read.csv('mt_ir_scores_corr.tsv', sep='\t'))
corrs <- unite(corrs, dataset.model, dataset, model, remove = FALSE)
corrs <- corrs %>% group_by(dataset.model, measure1, measure2) %>% summarise_if(is.numeric, mean, na.rm = TRUE)
corrs.rbo <- filter(corrs, measure2 == 'rbo')

bleu.precs <- c("prec1.lower", "prec2.lower", "prec3.lower", "prec4.lower")
bleu.all <- c("bleu.lower", bleu.precs)
bleu.variations <- c("bleu.lower", "bleu.lower.depunc", "bleu.lower.stem", "bleu.lower.stem.depunc")

ggplot(filter(corrs.rbo, measure1 %in% bleu.precs), aes(measure1, corr, color = dataset.model)) + geom_point() + geom_hline(aes(yintercept = corr, color = dataset.model), filter(corrs.rbo, measure1 == 'bleu.lower'), linetype = 2) + scale_y_continuous(breaks = seq(0.65, 1.0, 0.05), minor_breaks = seq(0.65, 1.0, 0.01)) + ylab("Kendall's Tau") + xlab("N-gram Precision Measure") + labs(color = "Dataset & Model") + scale_color_discrete(breaks = c("europarl_bm25", "wiki_bm25", "wiki_neural"), labels = c("Europarl BM25", "Wikipedia BM25", "Wikipedia neural")) + scale_x_discrete(breaks = c('prec1.lower', 'prec2.lower', 'prec3.lower', 'prec4.lower'), labels = c('Unigram', 'Bigram', 'Trigram', '4-gram'))
ggsave('tau.bleu.rbo.png', width = 4.5, height = 2.25, units = 'in')

# Table: dataset.model and RBO correlations with BLEU and precision1-4
corrs.rbo.means <- select(corrs.rbo, -measure2) %>% droplevels() %>% group_by(dataset.model, measure1) %>% summarize(mean = mean(corr))

corrs.rbo.bleu.precs <- filter(corrs.rbo.means, measure1 %in% bleu.all) %>% spread(measure1, mean)
print(xtable(corrs.rbo.bleu.precs, digits = 3), include.rownames = FALSE)

corrs.rbo.bleu.variations <- filter(corrs.rbo.means, measure1 %in% bleu.variations) %>% spread(measure1, mean)
print(xtable(corrs.rbo.bleu.variations, digits = 3), include.rownames = FALSE)


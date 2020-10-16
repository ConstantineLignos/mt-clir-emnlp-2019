library(MASS)
library(tidyr)
library(dplyr)
library(ggplot2)
library(scales)
theme_set(theme_bw())

mt <- as.tbl(read.csv('output/mt_scores.csv', sep='\t'))
mt$bpe.tokens <- factor(mt$bpe.tokens)
summary(mt)

ir <- as.tbl(read.csv('output/ir_scores.tsv', sep='\t'))
ir$bpe.tokens <- factor(ir$bpe.tokens)
summary(ir)
ir.all <- filter(ir, query == 'all')
ir.queries <- filter(ir, query != 'all')
write.table(ir.queries, 'output/ir_scores_queries_only.tsv', sep = '\t', quote = FALSE, row.names = FALSE)

all <- left_join(ir.all, mt, by = c('lang', 'size', 'bpe.tokens'))
summary(all)
write.table(all, 'output/mt_ir_scores_all.tsv', sep = '\t', quote = FALSE, row.names = FALSE)

facet_labels <- c(
  "cs" = "Czech",
  "de" = "German",
  "wiki" = "Wikipedia",
  "europarl" = "Europarl",
  "bm25" = "BM25",
  "neural" = "Neural"
)
facet_labeller <- as_labeller(facet_labels)

# Test set BLEU
ggplot(mt, aes(size / 1000, bleu.lower, group=interaction(lang, bpe.tokens), color = bpe.tokens, shape = bpe.tokens)) + geom_point() + geom_line() + facet_grid(cols = vars(lang), labeller = facet_labeller) + theme(legend.justification = c(1, 0), legend.position = c(.99, 0.02)) + xlab('MT Training Size (thousands of sentences)') + ylab('BLEU') + scale_y_continuous(breaks = seq(10, 36, 2)) + labs(color = 'BPE Size', shape = 'BPE Size') + scale_colour_grey(start = 0.0, end = 0.6)
ggsave('size.bleu.bpe.png', width = 4.5, height = 3.0, units = 'in')

# MAP across sizes
ggplot(ir.all, aes(size, map, group=interaction(lang, bpe.tokens), color = bpe.tokens)) + geom_point() + geom_line() + facet_grid(cols = vars(lang), rows = vars(dataset, model), scales = 'free', labeller = facet_labeller) + theme(legend.justification = c(1, 0), legend.position = c(.99, 0.02)) + xlab('MT Training Size (sentences)') + ylab('MAP') + labs(color = 'BPE Size') + scale_y_continuous(labels = number_format(accuracy = 0.01))
ggsave('size.map.bpe.png', width = 4.5, height = 5, units = 'in')

ggplot(ir.all, aes(size / 1000, rbo, group=interaction(lang, bpe.tokens), color = bpe.tokens, shape = bpe.tokens)) + geom_point() + geom_line() + facet_grid(cols = vars(lang), rows = vars(dataset, model), scales = 'free', labeller = facet_labeller) + theme(legend.justification = c(1, 0), legend.position = c(.99, 0.02)) + xlab('MT Training Size (thousands of sentences)') + ylab('RBO') + labs(color = 'BPE Size', shape = 'BPE Size') + scale_y_continuous(labels = number_format(accuracy = 0.01)) + scale_colour_grey(start = 0.0, end = 0.6)
ggsave('size.rbo.bpe.png', width = 4.5, height = 5, units = 'in')

# Regression
# All data, trying different metrics
summary(lm(map ~ I(bleu.lower / 100) + dataset + lang + model + bpe.tokens, all))
summary(lm(map ~ I(prec1.lower / 100) + dataset + lang + model + bpe.tokens, all))
summary(lm(map ~ I(prec1.lower.depunc / 100) + dataset + lang + model + bpe.tokens, all))

# Lowercase BLEU, by model/collection
summary(lm(map ~ I(bleu.lower / 100) + lang + bpe.tokens, filter(all, dataset == 'europarl')))
summary(lm(map ~ I(bleu.lower / 100) + lang + bpe.tokens, filter(all, dataset == 'wiki', model == 'bm25')))
summary(lm(map ~ I(bleu.lower / 100) + lang + bpe.tokens, filter(all, dataset == 'wiki', model == 'neural')))

ggplot(all, aes(bleu.lower, map, color = dataset:model:lang)) + geom_smooth(method = "gam", formula = y ~ s(x, bs = "cs"), se = FALSE) + geom_point(aes(shape = bpe.tokens)) + theme(legend.position = "bottom", legend.box = "vertical") + guides(color = guide_legend(ncol = 3)) + labs(x = 'BLEU', y = 'MAP', color = 'Collection', shape = 'BPE Size') + scale_color_discrete(labels = c("Wiki BM25 CS", "Wiki BM25 DE", "Europarl BM25 CS", "Europarl BM25 DE", "Wiki Neural CS", "Wiki Neural DE"), breaks = c("wiki:bm25:cs", "wiki:bm25:de", "europarl:bm25:cs", "europarl:bm25:de", "wiki:neural:cs", "wiki:neural:de"))
ggsave('bleu.map.all.png', width = 5, height = 5.5, units = 'in')

# Appendix tables
(bleu.tab <- mt %>% select(lang, size, bpe.tokens, bleu.lower) %>% spread(size, bleu.lower))
print(xtable(bleu.tab), include.rownames = FALSE)

ir.all.rbo.map <- ir.all %>% select(lang, dataset, model, size, bpe.tokens, map, rbo)
ir.all.rbo.tab <- ir.all.rbo.map %>% select(-map) %>% spread(size, rbo)
print(xtable(ir.all.rbo.tab, digits = 3), include.rownames = FALSE)
ir.all.map.tab <- ir.all.rbo.map %>% select(-rbo) %>% spread(size, map)
print(xtable(ir.all.map.tab, digits = 3), include.rownames = FALSE)

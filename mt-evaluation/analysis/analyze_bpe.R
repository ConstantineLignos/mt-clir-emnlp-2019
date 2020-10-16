library(ggplot2)

theme_set(theme_bw())

bpe <- as.tbl(read.csv('output/mt_ir_bpe_delta.tsv', sep='\t'))
bpe$size <- factor(bpe$size)
bpe$match <- sign(bpe$bleu.lower.delta) == sign(bpe$rbo.delta)
summary(bpe)
bpe.wiki.bm25 <- filter(bpe, dataset == 'wiki', model == 'bm25')
bpe.wiki.neural <- filter(bpe, dataset == 'wiki', model == 'neural')
bpe.europarl.bm25 <- filter(bpe, dataset == 'europarl')

xtable(table(paste(bpe$dataset, bpe$model, sep = ":"), bpe$match))
cor.test(bpe.wiki$bleu.lower.delta, bpe.wiki$rbo.delta, method = "spearman", exact = FALSE)
cor.test(bpe.europarl$bleu.lower.delta, bpe.europarl$rbo.delta, method = "spearman", exact = FALSE)
xtable()
ggplot(bpe, aes(bleu.lower.delta, rbo.delta)) + geom_point() + geom_hline(yintercept = 0) + geom_vline(xintercept = 0) + facet_wrap(vars(dataset))

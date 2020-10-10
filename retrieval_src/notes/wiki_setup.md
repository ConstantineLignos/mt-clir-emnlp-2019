# Loading the data

Ideally, the abstract dump would be useful for our purposes. However, it's garbage.
```
<title>Wikipedia: Alabama</title>
<url>https://en.wikipedia.org/wiki/Alabama</url>
<abstract>We dare defend our rights</abstract>
...
<title>Wikipedia: Academy Awards</title>
<url>https://en.wikipedia.org/wiki/Academy_Awards</url>
<abstract>| website        =</abstract>
```

The abstracts that are present are often too-truncated versions of the introductory paragraph. So unfortunately, we need to dive in to use the 

1. Download a wikipedia dump, for example enwiki-20180920-pages-articles.xml.bz2
2. Follow instructions at https://github.com/spencermountain/dumpster-dive#readme
3. Command for ingest:
   ```
   npm install -g dumpster-divedumpster enwiki-20180920-pages-articles.xml --citations=false --infoboxes=false --images=false
   ```
# Dumping the data

1. Dump all of the article IDs to a file:
   ```
   python retrieval/wiki/dump_article_ids.py > data/wiki_ids.txt
   ```
2. Dump all of the articles for those IDs:
   ```
   python retrieval/wiki/dump_articles.py data/wiki_ids.txt data/articles_dump/ 3
   ```


Getting matched articles:
```
2.0 length ratio limit:
Wrote 3355 entries, discarded 194329 entries
ERROR: Did not return requested number of entries

3.0 length ratio limit:
Wrote 5000 entries, discarded 138830 entries
```

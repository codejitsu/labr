## Stanford Core NLP
wget http://nlp.stanford.edu/software/stanford-ner-2015-04-20.zip
wget http://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip
wget http://nlp.stanford.edu/software/stanford-postagger-full-2015-04-20.zip

unzip to tools/stanford/

Add to virtualenv/bin/activate:

```
STANFORDTOOLSDIR=":/projects/labr/tools/stanford/"
export STANFORDTOOLSDIR
export CLASSPATH=$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/stanford-postagger.jar:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar

export STANFORD_MODELS=$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/models:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/classifiers
```

```
cd stanford-parser-full-2015-04-20
cp stanford-parser-3.5.2-models.jar models.jar
unzip models.jar
```

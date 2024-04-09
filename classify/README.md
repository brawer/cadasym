# Classify

Experimental image classifier for cadastral symbols


## Evaluation

```sh
$ venv/bin/python3 -m classify cadasym-0.1.3.zip
Symbol Class          Precision Recall
--------------------------------------
black_dot                  87.9  100.0
double_white_circle         0.0    0.0
other                      77.9   93.1
white_circle               93.9   96.7
```

Reading example: When the classifier reports `black_dot`, the result is correct
in 87.9% of cases (whereas for 12.1% of `black_dot` results, the classifier
was wrong and should have returned something else). A recall of 100%
means that the classifier was always correct for every black dot image
in the corpus.

For categories with less than 50 test images in the corpus, stats are omitted.

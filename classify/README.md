# Classify

Experimental image classifier for cadastral symbols


## Evaluation

```sh
$ venv/bin/python3 -m classify cadasym-0.1.3.zip
Symbol Class          Precision Recall
--------------------------------------
black_dot                  71.8   86.4
double_white_circle         0.0    0.0
other                      76.8   91.3
white_circle               93.9   96.7
```

Reading example: When the classifier reports `black_dot`, the result is correct
in 71.8% of cases (whereas for 28.2% of `black_dot` results, the classifier
should have returned something else). For 86.4% of the black dot images in the
corpus, the classifier correctly assigned the `black_dot` label (whereas
for 13.6% of black dots, the classifier has wrongly returned something else).

For categories with less than 50 test images in the corpus, stats are omitted.

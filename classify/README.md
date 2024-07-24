# Classify

Experimental image classifier for cadastral symbols


## Evaluation

```sh
$ venv/bin/python3 -m classify cadasym-0.1.4.zip
Symbol Class          Precision Recall
--------------------------------------
black_dot                  69.4  100.0
double_white_circle       100.0   54.3
other                      85.9   89.4
white_circle               91.9   96.4
```

See [Wikipedia](https://en.wikipedia.org/wiki/Precision_and_recall)
for an explanation of “Precision” and “Recall”.

For categories with less than 50 test images in the corpus, stats are omitted.

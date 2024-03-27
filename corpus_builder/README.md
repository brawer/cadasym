# Corpus Builder

![Screenshot](./screenshot.png)

Corpus Builder is an ad-hoc desktop application that was written to
help building the Cadasym image corpus. When the application starts
up, it asks for PDFs with scanned cadastral mutation plans.  After
converting them to pixmaps, basic Computer Vision algorithms (from the
OpenCV library) are used to find potential cadastral symbols.  The
symbol candidates are presented to the user, who manually classifies
each symbol to build up the image corpus. After a candidate has been
classificed, the corpus builder app stores a cropped 256×256 pixel image
into the `corpus` folder.


## Setup

```sh
git clone https://github.com/brawer/cadasym.git
cd cadasym
python3 -m venv venv
venv/bin/pip3 install -r requirements.txt
venv/bin/python3 -m corpus_builder
```

## License

The source code to this app is eleased under the
[../LICENSES/MIT.txt](MIT license).



# Mergia
Mergia is a scipt-based program that can copy media files without duplicated.
Note! In iOS, file number will count even though a new incoming file name is not containing any numbers. For example,
* Last file on iOS is IMG_0051.HEIC, then air drop file "TEST_COUNT.JPG". The next file (live photo) that come from its camera will be IMG_0053.HEIC
* If change the air drop file to "IMG_0053.JPG", the next file will be IMG_0053 2.HEIC

## Supported Media
* Image: JPG, PNG
* Video: MOV, MP4
* Live: HEIC

## Unsupported Media
* Burst Image

## Requirements
* Python 3.6.5+ (Tested on Python 3.6.12_1, macOS 11.0.1) 
[See more](#rollback-python)
* Package Manager i.e. Homebrew

## Install Dependencies
```sh
$ brew install libffi libheif
$ pip3 install -r requirements.txt
```

## Usage
```sh
$ ./mergia.py --help
```
or
```sh
$ python3 mergia.py --help
```

## Sample
```sh
$ ./mergia.py --src="/src" --des="/des" --prefix="IMG_0000" --start_num=0 --sort_media=True --show_same=True --show_unsupport=True
```
or (suggest)
```sh
$ ./mergia.py --src="/src" --des="/des" --prefix="IMG_0000" --start_num=54
```

<h2 id="rollback-python">[Optional] Rollback Python</h2>

Downgrade to python and pin (force homebrew not to upgrade)
```sh
$ brew unlink python
$ brew install sashkab/python/python@3.6
$ brew link python@3.6
$ brew pin python
```
Want to upgrade python?
```sh
$ brew unpin python
$ brew update
$ brew upgrade
```

## Special Thanks
* [Sample media files](https://filesamples.com/)

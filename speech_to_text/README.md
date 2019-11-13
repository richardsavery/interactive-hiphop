Contains Instructions for Running Speech-to-Text

Takes in an audio file and creates phonetic transcription for Shimon

- Installing SpeechRecognition
    - `pip install SpeechRecognition`
    - `pip install pydub`
- Installing PocketSphinx
    - NOTE:
        - There will be an error if you try `pip3 install pocketsphinx`, so try the following steps instead

    - git clone --recursive https://github.com/bambocher/pocketsphinx-python
    - `cd pocketsphinx-python`
    - Edit file:
        - `vim deps/sphinxbase/src/libsphinxad/ad_openal.c`
    - Change
        #include <al.h>
        #include <alc.h>

        to

        #include <OpenAL/al.h>
        #include <OpenAL/alc.h>

    - python setup.py install


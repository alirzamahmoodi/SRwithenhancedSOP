Build Instructions:

1-      ! conda env create -f environment.yml
2-      ! conda activate google-ai
3-      ! pip install pyinstaller
4-      ! pyinstaller audio_transcriber.spec

Run Instructions:

1- Move the config.yaml file from "dist/audio_transcriber/_internal" to dist/audio_transcriber/"
2- Edit config.yaml file according to your use case.
3- Setup DICOM Receiver and DICOM Register services for dictation and structured report.
4- Open CMD in "dist/audio_transcriber/" path and run the command "audio_transcriber.exe".
5- The service will be up and running, listening for dictation *.dcm files in the spool folder.
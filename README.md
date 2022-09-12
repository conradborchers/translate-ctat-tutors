# CTAT Example-Tracing Tutor Translator

Status: Working Prototype + WIP

Code to translate existing `.html` and `.brd` files into another language using a Google API and the Python `translators` package.

Folder `files/` with subfolders `HTML/` and `FinalBRDs` is mirrored into the `translated_files/` folder while filenames receive a distinct suffix in order not to override files in Tutorshop. 

Note: You have to set the languages and the task instruction texts manually before running the code. Inline comments provide further guidance on this.

TODO: Find a better way to identify and change task instruction fields.

Feel free to report edgecases that corrupt files during translation.

Learn more about CTAT Intelligent Tutoring Authoring Tools [here](https://github.com/CMUCTAT/CTAT).

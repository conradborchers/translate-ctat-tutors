# CTAT Example-Tracing Tutor Translator

Status: Working Prototype + WIP

Code to translate existing `.html` and `.brd` files into another language using a Google API and the Python `translators` package.

Folder `files/` with subfolders `HTML/` and `FinalBRDs/` is mirrored into the `translated_files/` folder while filenames receive a distinct suffix in order not to override files in Tutorshop. Translations are ststored in `.txt` files for mass production where translations represents fields in `.brd.` files that are replaced with translated text. This has the advantage of being able to hand-code translations in `.txt` files that are not satisfactory based on a translation API. Translations are also stored in `.json` files such that translations of repeating entries must not be translated via a language API twice.

**Note**: You must manually set the languages and task instruction texts before running the code. Inline comments provide further guidance on this.

Feel free to report edge cases that corrupt files during translation.

Learn more about CTAT Intelligent Tutoring Authoring Tools [here](https://github.com/CMUCTAT/CTAT).

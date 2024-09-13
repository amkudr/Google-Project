****AutoComplete System****\
Description\
This is an autocomplete system that provides suggestions based on partial user input. The program works with text files packed in a ZIP archive and uses Levenshtein distance to find similar words in sentences. The system returns the best matches based on scores that take into account word positions and the number of replacement, deletion, or insertion operations.

How It Works
* Data Loading: The program loads text files from a ZIP archive. Each sentence is stored with metadata that includes the original sentence, the file name, and the line number (offset).
* Text Cleaning: All text is cleaned from punctuation, extra spaces, and converted to lowercase.
* Indexing: The program builds an inverted index that allows sentences to be searched by words and their positions within the text.
* Suggestion Matching: The user inputs text, and the system searches for matches in the inverted index. It uses Levenshtein distance to find similarly spelled words and also takes word positions into account. The final results are sorted based on the accumulated scores.

Technologies Used:
* Python — main programming language.
* zipfile — for working with ZIP archives.
* dataclasses — to structure sentence data.
* Levenshtein — library to calculate the Levenshtein distance between words.
* collections.defaultdict — for creating the inverted index and storing matches.
import zipfile
from dataclasses import dataclass
from typing import List, Dict, Tuple
import string
from collections import defaultdict
import Levenshtein
import re


@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int


# def clean_sentence1(sentence: str) -> str:
#     """
#     Cleans a sentence: removes punctuation, extra spaces, and converts to lowercase.
#     """
#     translator = str.maketrans('', '', string.punctuation)
#     return re.sub(r'\s+', ' ', sentence.strip().lower().translate(translator))

# def clean_sentence2(sentence: str) -> str:
#     """
#     Cleans a sentence: removes punctuation, extra spaces, and converts to lowercase using basic string operations.
#     """
#     translator = str.maketrans('', '', string.punctuation)
#     # Use str.split() and ' '.join() to remove excess spaces instead of re.sub
#     return ' '.join(sentence.strip().lower().translate(translator).split())

def clean_sentence(sentence: str) -> List[str]:
    """
    Cleans a sentence: removes punctuation, extra spaces, and converts to lowercase, returning a list of words.
    """
    translator = str.maketrans('', '', string.punctuation)
    return sentence.strip().lower().translate(translator).split()

def add_to_inverted_index(inverted_index: Dict[str, List[Tuple[int, int]]], sentence: str, sentence_id: int) -> None:
    """
    Adds sentence ID and word position to the inverted index.
    Now each word is associated with a list of tuples (sentence_id, word_position).
    """
    # words = clean_sentence(sentence).split()
    words = clean_sentence(sentence)

    for index, word in enumerate(words):
        inverted_index[word].append((sentence_id, index))  # Store both the sentence ID and word position


def build_inverted_index(data_store: List[Dict]) -> Dict[str, List[Tuple[int, int]]]:
    """
    Builds an inverted index from the data store using sentence IDs and word positions.
    The inverted index maps words to lists of tuples (sentence_id, word_position).
    """
    inverted_index = defaultdict(list)

    for sentence_id, entry in enumerate(data_store):
        sentence = entry['sentence']
        add_to_inverted_index(inverted_index, sentence, sentence_id)

    return inverted_index


def load_data_from_zip(zip_path: str) -> List[Dict]:
    """
    Reads text files from a zip archive and stores the original sentences along with their metadata.
    Returns:
        List of dictionaries where each dictionary has:
        - 'sentence': the original sentence
        - 'source_text': the name of the file the sentence came from
        - 'offset': the line number within the file
    """
    data_store = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.txt') and not file_info.is_dir():
                with zip_ref.open(file_info.filename) as file:
                    for offset, line in enumerate(file):
                        original_sentence = line.decode('utf-8').strip()
                        data_store.append({
                            'sentence': original_sentence,
                            'source_text': file_info.filename,
                            'offset': offset
                        })
    return data_store


def filter_by_levenshtein(user_word: str, word_from_index: str, max_distance: int = 1) -> bool:
    """
    Filters words by comparing their Levenshtein distance. Returns True if distance <= max_distance.
    """
    return Levenshtein.distance(user_word, word_from_index) <= max_distance


def get_score(user_word: str, word_from_index: str, first_ind: int) -> int:
    """
    Filters words by comparing their Levenshtein distance. Returns True if distance <= max_distance.
    """
    operations = Levenshtein.editops(user_word, word_from_index)
    cnt = len(word_from_index) * 2

    if len(operations) == 0: return cnt

    if operations[0][0] == 'replace':
        if operations[0][1] + first_ind == 0:
            cnt -= 5
        elif operations[0][1] + first_ind == 1:
            cnt -= 4
        elif operations[0][1] + first_ind == 2:
            cnt -= 3
        elif operations[0][1] + first_ind == 3:
            cnt -= 2
        else:
            cnt -= 1
    elif operations[0][0] == 'insert' or operations[0][0] == 'delete':
        if operations[0][1] + first_ind == 0:
            cnt -= 10
        elif operations[0][1] + first_ind == 1:
            cnt -= 8
        elif operations[0][1] + first_ind == 2:
            cnt -= 6
        elif operations[0][1] + first_ind == 3:
            cnt -= 4
        else:
            cnt -= 2

    return cnt


def match_sentences(user_words: List[str], inverted_index: Dict[str, List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
    """
    Matches user input against the inverted index, filtering sentences by word matches and Levenshtein distance.
    Now matches also by word positions in the sentence using the data in the inverted index.
    Returns a list of tuples (sentence ID, score).
    """

    # Dictionary to store matched sentences and their details:
    # {sentence_id: (word_position, levenshtein_error, score)}
    matched_sentence_map = defaultdict(list)
    first_ind = 0

    for user_word_index, user_word in enumerate(user_words):
        current_word_matches = defaultdict(list)

        # Iterate through inverted index to find words that match based on Levenshtein distance
        for index_word, entries in inverted_index.items():
            levenshtein_error = Levenshtein.distance(user_word, index_word)
            if levenshtein_error <= 1:  # Apply Levenshtein filter
                # Iterate through sentences and word positions from the inverted index
                for sentence_id, word_position in entries:
                    if user_word_index == 0:  # For the first word, directly append the match
                        matched_sentence_map[sentence_id].append(
                            (word_position, levenshtein_error, get_score(user_word, index_word, first_ind))
                        )
                    else:
                        # For subsequent words, check if they follow the previous match in sequence
                        if sentence_id in matched_sentence_map:
                            # Get the last match for this sentence
                            for matched_position, matched_levenshtein_error, matched_score in matched_sentence_map[
                                sentence_id]:
                                if word_position == matched_position + 1 and matched_levenshtein_error + levenshtein_error <= 1:
                                    # Add the match to the current matches
                                    current_word_matches[sentence_id].append(
                                        (word_position,
                                         matched_levenshtein_error + levenshtein_error,
                                         matched_score + get_score(user_word, index_word, first_ind) + 2)
                                    )

        # If it's not the first word, update matched_sentence_map with the new matches
        if user_word_index > 0:
            matched_sentence_map = current_word_matches
        first_ind += len(user_word) + 1

    # Return a list of tuples (sentence_id, score) for each sentence
    return [(sentence_id, max(score for _, _, score in matches))
            for sentence_id, matches in matched_sentence_map.items()]


def get_top_k_completions(user_input: str, data_store: List[Dict], inverted_index: Dict[str, List[Tuple[int, int]]],
                          k: int = 5) -> List[AutoCompleteData]:
    """
    Returns the top-k auto-complete suggestions based on user input.
    Now it considers the score for ranking.
    """
    cleaned_input = clean_sentence(user_input)  # Clean the user input
    # user_words = cleaned_input.split()  # Split the input into individual words
    user_words = cleaned_input  # Split the input into individual words
    matched_sentences = match_sentences(user_words, inverted_index)  # Get matching sentences and their scores

    # Convert matched sentence IDs and their scores into AutoCompleteData objects
    results = [
        AutoCompleteData(
            completed_sentence=data_store[sentence_id]['sentence'],
            source_text=data_store[sentence_id]['source_text'],
            offset=data_store[sentence_id]['offset'],
            score=score  # Set the score based on the matching result
        )
        for sentence_id, score in matched_sentences
    ]

    # Sort results by score (if needed) and return top-k completions
    results.sort(key=lambda x: (-x.score, x.completed_sentence))

    return results[:k]


if __name__ == "__main__":
    print("Loading the files...")
    zip_path = 'Archive2.zip'  # Update with your zip file name
    data_store = load_data_from_zip(zip_path)
    print("Preparing the data base...")
    inverted_index = build_inverted_index(data_store)

    restart = True
    user_input = ""
    print("The system is ready. Enter your text:")

    while True:
        if restart:
            user_input = input()
        else:
            user_input = f"{user_input}{input()}"

        if user_input.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        if user_input[-1] == "#":  # restart the next input if the user input ends with #
            restart = True
            user_input = user_input[:-1]
        else:
            restart = False

        suggestions = get_top_k_completions(user_input, data_store, inverted_index)
        print(f"Here are {len(suggestions)} suggestions")

        for i, suggestion in enumerate(suggestions, 1):
            print(
                f"{i}. {suggestion.completed_sentence.strip()} (Source: {suggestion.source_text}, Offset: {suggestion.offset}, Score: {suggestion.score})")
        if not restart:
            print(user_input, end="")

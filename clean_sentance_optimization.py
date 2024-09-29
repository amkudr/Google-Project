import re
import string
import timeit


def clean_sentence_regex(sentence: str) -> str:
    """
    Cleans a sentence: removes punctuation, extra spaces, and converts to lowercase using regular expressions.
    """
    translator = str.maketrans('', '', string.punctuation)
    return re.sub(r'\s+', ' ', sentence.strip().lower().translate(translator))


def clean_sentence_optimized(sentence: str) -> str:
    """
    Cleans a sentence: removes punctuation, extra spaces, and converts to lowercase using basic string operations.
    """
    translator = str.maketrans('', '', string.punctuation)
    # Use str.split() and ' '.join() to remove excess spaces instead of re.sub
    return ' '.join(sentence.strip().lower().translate(translator).split())


if __name__ == "__main__":

    # Example sentence for testing
    sentence = "  This, is! an example; sentence    with lots, of punctuation...  "

    # Time the original function using regex
    time_regex = timeit.timeit(lambda: clean_sentence_regex(sentence), number=100000)
    print(f"Regex version: {time_regex:.4f} seconds")
    print(clean_sentence_regex(sentence))

    # Time the optimized function without regex
    time_optimized = timeit.timeit(lambda: clean_sentence_optimized(sentence), number=100000)
    print(f"Optimized version: {time_optimized:.4f} seconds")
    print(clean_sentence_optimized(sentence))



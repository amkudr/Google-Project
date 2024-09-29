import cProfile
import pstats
from io import StringIO

# Import the function or the module you want to profile
from main import get_top_k_completions, load_data_from_zip, build_inverted_index


def main():
    # Your actual code for running the program
    print("Loading the files...")
    zip_path = 'Archive2.zip'  # Update with your zip file name
    data_store = load_data_from_zip(zip_path)
    print("Preparing the data base...")
    inverted_index = build_inverted_index(data_store)

    user_input = "apple day"
    # user_input = "This is a good"
    suggestions = get_top_k_completions(user_input, data_store, inverted_index)

    print(f"Here are {len(suggestions)} suggestions")
    for i, suggestion in enumerate(suggestions, 1):
        print(
            f"{i}. {suggestion.completed_sentence.strip()} (Source: {suggestion.source_text}, Offset: {suggestion.offset}, Score: {suggestion.score})"
        )


if __name__ == "__main__":
    # Start cProfile and profile the 'main' function
    pr = cProfile.Profile()
    pr.enable()

    # Call the main function that runs the code
    main()

    pr.disable()

    # Create a stream to store profiling results
    s = StringIO()
    # Create statistics object and sort by cumulative time (or other metric)
    ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats()
    ps.dump_stats("results3.prof")

    # Print profiling results
    print(s.getvalue())

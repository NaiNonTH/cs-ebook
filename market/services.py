# services.py

def check_marketshare_criteria(read_pages, total_pages):
    """
    Check if a user passes both marketshare criteria:
    1. Read at least 50% of the total pages.
    2. Read a STRICTLY continuous sequence of pages (no skips allowed) 
       that covers at least 40% of the total pages.
    """
    if not read_pages or total_pages == 0:
        return False

    # Remove duplicates and sort pages in ascending order
    sorted_unique_pages = sorted(list(set(read_pages)))
    total_read_count = len(sorted_unique_pages)

    # Condition 1: Must read at least 50% of the book
    if total_read_count < (total_pages * 0.5):
        return False

    # Condition 2: Find the longest strictly continuous reading sequence
    max_sequence_length = 1
    current_sequence_length = 1

    for i in range(1, len(sorted_unique_pages)):
        # Calculate the difference between the current page and the previous page
        diff = sorted_unique_pages[i] - sorted_unique_pages[i-1]

        if diff == 1:
            # Pages are exactly next to each other, continue the sequence
            current_sequence_length += 1
        else:
            # Sequence is broken. Save the max length and reset the counter.
            if current_sequence_length > max_sequence_length:
                max_sequence_length = current_sequence_length
            current_sequence_length = 1

    # Final check for the last sequence when the loop finishes
    if current_sequence_length > max_sequence_length:
        max_sequence_length = current_sequence_length

    # The longest strictly continuous sequence must be >= 40% of total pages
    return max_sequence_length >= (total_pages * 0.4)


# --- Quick Tests (You can remove these in production) ---
if __name__ == "__main__":
    # Example 1: Strictly continuous
    # Sequence [1, 2, 3, 4] is exactly 4 pages long. 4 >= 40% of 10. (PASS)
    print(check_marketshare_criteria([1, 2, 3, 4, 7, 9], 10))  # Expected: True

    # Example 2: Interrupted sequence (the one we discussed)
    # [1, 2] -> breaks -> [4, 5] -> breaks -> [7, 8] etc. Max sequence is only 2. (FAIL)
    print(check_marketshare_criteria([1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 26], 30))  # Expected: False
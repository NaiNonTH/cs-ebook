import math

def calculate_uread_criteria(read_pages: list[int], total_pages: int) -> bool:
    """
    Checks if a user's read pages meet both criteria:
    A (50% rule): Read at least 50% of total pages.
    B (40% continuous sequence rule): A sequence of pages (ascending order) that covers at least 40% of total pages.
    """
    if not total_pages or total_pages <= 0:
        return False

    unique_read_pages = sorted(list(set(read_pages)))

    # Condition A: 50% Rule (Rounded up)
    min_required_total_read = math.ceil(total_pages * 0.5)
    if len(unique_read_pages) < min_required_total_read:
        return False

    # Condition B: 40% strict continuous sequence rule (Rounded up)
    # The requirement says "ascending order that covers at least 40% of the total pages"
    # No gaps are allowed.
    min_required_sequence_length = math.ceil(total_pages * 0.4)

    if len(unique_read_pages) == 0:
        return False

    longest_seq_len = 1
    current_seq_len = 1
    max_allowed_gap = 1 # strict continuous sequence, no gaps allowed

    for i in range(1, len(unique_read_pages)):
        gap = unique_read_pages[i] - unique_read_pages[i - 1]
        if gap == max_allowed_gap: # exactly 1 page diff
            current_seq_len += 1
        else:
            longest_seq_len = max(longest_seq_len, current_seq_len)
            current_seq_len = 1
            
    longest_seq_len = max(longest_seq_len, current_seq_len)

    if longest_seq_len < min_required_sequence_length:
        return False

    return True

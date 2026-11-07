from datetime import date

from portfolio_chatbot.profile import Experience


def calculate_duration_months(
    experience: Experience, *, as_of: date | None = None
) -> int | None:
    if experience.start_year is None or experience.start_month is None:
        return None

    if experience.is_current is True:
        end_date = as_of or date.today()
        end_year = end_date.year
        end_month = end_date.month

    else:
        if experience.end_year is None or experience.end_month is None:
            return None

        end_year = experience.end_year
        end_month = experience.end_month

    # Resume dates have month-level precision, so count both the start and end months.
    months = (
        (end_year - experience.start_year) * 12
        + end_month
        - experience.start_month
        + 1
    )

    if months <= 0:
        return None

    return months


def calculate_total_experience_months(
    experiences: list[Experience], *, as_of: date | None = None
) -> int | None:
    date_ranges = []

    for experience in experiences:
        if experience.start_year is None or experience.start_month is None:
            continue

        if experience.is_current is True:
            end_date = as_of or date.today()
            end_year = end_date.year
            end_month = end_date.month

        else:
            if experience.end_year is None or experience.end_month is None:
                continue

            end_year = experience.end_year
            end_month = experience.end_month

        start_index = experience.start_year * 12 + experience.start_month - 1
        # Use the month after the listed end month as the exclusive boundary.
        end_exclusive_index = end_year * 12 + end_month

        if end_exclusive_index <= start_index:
            continue

        date_ranges.append((start_index, end_exclusive_index))

    if not date_ranges:
        return None

    date_ranges.sort()

    current_start, current_end = date_ranges[0]
    total_months = 0

    for start, end in date_ranges[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total_months += current_end - current_start
            current_start, current_end = start, end

    total_months += current_end - current_start
    return total_months


def format_experience_months(months: int | None) -> str | None:
    if months is None:
        return None

    years, remaining_months = divmod(months, 12)
    parts = []

    if years:
        parts.append(f"{years} {'year' if years == 1 else 'years'}")
    if remaining_months:
        parts.append(
            f"{remaining_months} {'month' if remaining_months == 1 else 'months'}"
        )

    return " ".join(parts) if parts else "0 months"

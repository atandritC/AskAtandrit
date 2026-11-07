from datetime import date

from portfolio_chatbot.profile import Experience


def calculate_duration_years(
    experience: Experience, *, as_of: date | None = None
) -> float | None:
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

    months = (
        (end_year - experience.start_year) * 12 + end_month - experience.start_month
    )

    if months < 0:
        return None

    return round(months / 12, 1)


def calculate_total_experience_years(
    experiences: list[Experience], *, as_of: date | None = None
) -> float | None:
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
        end_index = end_year * 12 + end_month - 1

        if end_index < start_index:
            continue

        date_ranges.append((start_index, end_index))

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
    return round(total_months / 12, 1)

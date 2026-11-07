from datetime import date

from portfolio_chatbot.experience_calculator import (
    calculate_duration_months,
    calculate_total_experience_months,
    format_experience_months,
)
from portfolio_chatbot.profile import Experience


def test_calculate_duration_counts_both_start_and_end_months():
    role = Experience(
        start_year=2024,
        start_month=11,
        end_year=2026,
        end_month=7,
        is_current=False,
    )

    assert calculate_duration_months(role) == 21
    assert format_experience_months(21) == "1 year 9 months"


def test_total_experience_does_not_double_count_overlapping_roles():
    first_role = Experience(
        start_year=2024,
        start_month=11,
        end_year=2026,
        end_month=7,
        is_current=False,
    )
    overlapping_role = Experience(
        start_year=2025,
        start_month=1,
        end_year=2026,
        end_month=1,
        is_current=False,
    )

    assert calculate_total_experience_months([first_role, overlapping_role]) == 21


def test_total_experience_skips_roles_without_dates():
    dated_role = Experience(
        start_year=2024,
        start_month=11,
        end_year=2026,
        end_month=7,
        is_current=False,
    )
    role_without_dates = Experience(is_current=False)

    assert calculate_total_experience_months([dated_role, role_without_dates]) == 21


def test_total_experience_uses_as_of_for_current_role():
    current_role = Experience(
        start_year=2024,
        start_month=11,
        is_current=True,
    )

    assert (
        calculate_total_experience_months(
            [current_role],
            as_of=date(2026, 11, 7),
        )
        == 25
    )


def test_format_experience_months_handles_singular_units():
    assert format_experience_months(1) == "1 month"
    assert format_experience_months(12) == "1 year"
    assert format_experience_months(None) is None

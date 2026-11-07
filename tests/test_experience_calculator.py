from datetime import date

from portfolio_chatbot.experience_calculator import (
    calculate_duration_years,
    calculate_total_experience_years,
)
from portfolio_chatbot.profile import Experience


def test_calculate_duration_years_for_completed_role():
    role = Experience(
        start_year=2024,
        start_month=11,
        end_year=2026,
        end_month=7,
        is_current=False,
    )

    assert calculate_duration_years(role) == 1.7


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

    assert calculate_total_experience_years([first_role, overlapping_role]) == 1.7


def test_total_experience_skips_roles_without_dates():
    dated_role = Experience(
        start_year=2024,
        start_month=11,
        end_year=2026,
        end_month=7,
        is_current=False,
    )
    role_without_dates = Experience(is_current=False)

    assert calculate_total_experience_years([dated_role, role_without_dates]) == 1.7


def test_total_experience_uses_as_of_for_current_role():
    current_role = Experience(
        start_year=2024,
        start_month=11,
        is_current=True,
    )

    assert (
        calculate_total_experience_years(
            [current_role],
            as_of=date(2026, 11, 7),
        )
        == 2.0
    )

"""Comprehensive tests for core/plans.py module."""

from typing import Dict, List

import pytest

from claude_monitor.core.plans import (
    COMMON_TOKEN_LIMITS,
    COST_LIMITS,
    DEFAULT_COST_LIMIT,
    DEFAULT_TOKEN_LIMIT,
    LIMIT_DETECTION_THRESHOLD,
    PLAN_LIMITS,
    TOKEN_LIMITS,
    PlanConfig,
    PlanType,
    Plans,
    get_cost_limit,
    get_token_limit,
)


class TestPlanType:
    """Test suite for PlanType enum."""

    def test_plan_type_values(self) -> None:
        """Test all plan type enum values."""
        assert PlanType.PRO.value == "pro"
        assert PlanType.MAX5.value == "max5"
        assert PlanType.MAX20.value == "max20"
        assert PlanType.TEAM_STANDARD.value == "team_standard"
        assert PlanType.TEAM_PREMIUM.value == "team_premium"
        assert PlanType.CUSTOM.value == "custom"

    def test_from_string_valid_plans(self) -> None:
        """Test from_string method with valid plan names."""
        assert PlanType.from_string("pro") == PlanType.PRO
        assert PlanType.from_string("max5") == PlanType.MAX5
        assert PlanType.from_string("max20") == PlanType.MAX20
        assert PlanType.from_string("team_standard") == PlanType.TEAM_STANDARD
        assert PlanType.from_string("team_premium") == PlanType.TEAM_PREMIUM
        assert PlanType.from_string("custom") == PlanType.CUSTOM

    def test_from_string_case_insensitive(self) -> None:
        """Test from_string method is case insensitive."""
        assert PlanType.from_string("PRO") == PlanType.PRO
        assert PlanType.from_string("Max5") == PlanType.MAX5
        assert PlanType.from_string("TEAM_STANDARD") == PlanType.TEAM_STANDARD
        assert PlanType.from_string("Team_Premium") == PlanType.TEAM_PREMIUM

    def test_from_string_invalid_plan(self) -> None:
        """Test from_string method with invalid plan name."""
        with pytest.raises(ValueError, match="Unknown plan type: invalid"):
            PlanType.from_string("invalid")


class TestPlanConfig:
    """Test suite for PlanConfig dataclass."""

    def test_plan_config_creation(self) -> None:
        """Test PlanConfig creation with all fields."""
        config = PlanConfig(
            name="pro",
            token_limit=19_000,
            cost_limit=18.0,
            message_limit=250,
            display_name="Pro",
        )

        assert config.name == "pro"
        assert config.token_limit == 19_000
        assert config.cost_limit == 18.0
        assert config.message_limit == 250
        assert config.display_name == "Pro"

    def test_formatted_token_limit_thousands(self) -> None:
        """Test formatted_token_limit property for values in thousands."""
        config = PlanConfig(
            name="pro",
            token_limit=19_000,
            cost_limit=18.0,
            message_limit=250,
            display_name="Pro",
        )
        assert config.formatted_token_limit == "19k"

        config = PlanConfig(
            name="max5",
            token_limit=88_000,
            cost_limit=35.0,
            message_limit=1_000,
            display_name="Max5",
        )
        assert config.formatted_token_limit == "88k"

    def test_formatted_token_limit_below_thousand(self) -> None:
        """Test formatted_token_limit property for values below 1000."""
        config = PlanConfig(
            name="test",
            token_limit=500,
            cost_limit=5.0,
            message_limit=50,
            display_name="Test",
        )
        assert config.formatted_token_limit == "500"

    def test_plan_config_immutable(self) -> None:
        """Test that PlanConfig is immutable (frozen=True)."""
        config = PlanConfig(
            name="pro",
            token_limit=19_000,
            cost_limit=18.0,
            message_limit=250,
            display_name="Pro",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            config.token_limit = 20_000  # type: ignore


class TestPlanLimits:
    """Test suite for PLAN_LIMITS configuration."""

    def test_plan_limits_structure(self) -> None:
        """Test PLAN_LIMITS has correct structure."""
        assert isinstance(PLAN_LIMITS, dict)
        assert len(PLAN_LIMITS) == 6  # PRO, MAX5, MAX20, TEAM_STANDARD, TEAM_PREMIUM, CUSTOM

    def test_pro_plan_limits(self) -> None:
        """Test Pro plan limits."""
        pro = PLAN_LIMITS[PlanType.PRO]
        assert pro["token_limit"] == 19_000
        assert pro["cost_limit"] == 18.0
        assert pro["message_limit"] == 250
        assert pro["display_name"] == "Pro"

    def test_max5_plan_limits(self) -> None:
        """Test Max5 plan limits."""
        max5 = PLAN_LIMITS[PlanType.MAX5]
        assert max5["token_limit"] == 88_000
        assert max5["cost_limit"] == 35.0
        assert max5["message_limit"] == 1_000
        assert max5["display_name"] == "Max5"

    def test_max20_plan_limits(self) -> None:
        """Test Max20 plan limits."""
        max20 = PLAN_LIMITS[PlanType.MAX20]
        assert max20["token_limit"] == 220_000
        assert max20["cost_limit"] == 140.0
        assert max20["message_limit"] == 2_000
        assert max20["display_name"] == "Max20"

    def test_team_standard_plan_limits(self) -> None:
        """Test Team Standard plan limits."""
        team_std = PLAN_LIMITS[PlanType.TEAM_STANDARD]
        assert team_std["token_limit"] == 23_750
        assert team_std["cost_limit"] == 25.0
        assert team_std["message_limit"] == 312
        assert team_std["display_name"] == "Team Standard"

    def test_team_premium_plan_limits(self) -> None:
        """Test Team Premium plan limits."""
        team_prem = PLAN_LIMITS[PlanType.TEAM_PREMIUM]
        assert team_prem["token_limit"] == 118_750
        assert team_prem["cost_limit"] == 125.0
        assert team_prem["message_limit"] == 1_563
        assert team_prem["display_name"] == "Team Premium"

    def test_custom_plan_limits(self) -> None:
        """Test Custom plan limits."""
        custom = PLAN_LIMITS[PlanType.CUSTOM]
        assert custom["token_limit"] == 44_000
        assert custom["cost_limit"] == 50.0
        assert custom["message_limit"] == 250
        assert custom["display_name"] == "Custom"


class TestPlansClass:
    """Test suite for Plans class."""

    def test_default_constants(self) -> None:
        """Test default constant values."""
        assert Plans.DEFAULT_TOKEN_LIMIT == 19_000
        assert Plans.DEFAULT_COST_LIMIT == 50.0
        assert Plans.DEFAULT_MESSAGE_LIMIT == 250
        assert Plans.LIMIT_DETECTION_THRESHOLD == 0.95

    def test_common_token_limits(self) -> None:
        """Test COMMON_TOKEN_LIMITS includes all plan limits."""
        expected_limits = [19_000, 23_750, 88_000, 118_750, 220_000, 880_000]
        assert Plans.COMMON_TOKEN_LIMITS == expected_limits

    def test_get_plan_pro(self) -> None:
        """Test get_plan method for Pro plan."""
        config = Plans.get_plan(PlanType.PRO)
        assert config.name == "pro"
        assert config.token_limit == 19_000
        assert config.cost_limit == 18.0
        assert config.message_limit == 250
        assert config.display_name == "Pro"

    def test_get_plan_team_standard(self) -> None:
        """Test get_plan method for Team Standard plan."""
        config = Plans.get_plan(PlanType.TEAM_STANDARD)
        assert config.name == "team_standard"
        assert config.token_limit == 23_750
        assert config.cost_limit == 25.0
        assert config.message_limit == 312
        assert config.display_name == "Team Standard"

    def test_get_plan_team_premium(self) -> None:
        """Test get_plan method for Team Premium plan."""
        config = Plans.get_plan(PlanType.TEAM_PREMIUM)
        assert config.name == "team_premium"
        assert config.token_limit == 118_750
        assert config.cost_limit == 125.0
        assert config.message_limit == 1_563
        assert config.display_name == "Team Premium"

    def test_get_plan_by_name_valid(self) -> None:
        """Test get_plan_by_name with valid plan names."""
        config = Plans.get_plan_by_name("pro")
        assert config is not None
        assert config.name == "pro"

        config = Plans.get_plan_by_name("team_standard")
        assert config is not None
        assert config.name == "team_standard"

        config = Plans.get_plan_by_name("team_premium")
        assert config is not None
        assert config.name == "team_premium"

    def test_get_plan_by_name_case_insensitive(self) -> None:
        """Test get_plan_by_name is case insensitive."""
        config = Plans.get_plan_by_name("PRO")
        assert config is not None
        assert config.name == "pro"

        config = Plans.get_plan_by_name("Team_Standard")
        assert config is not None
        assert config.name == "team_standard"

    def test_get_plan_by_name_invalid(self) -> None:
        """Test get_plan_by_name with invalid plan name."""
        config = Plans.get_plan_by_name("invalid")
        assert config is None

    def test_get_token_limit_pro(self) -> None:
        """Test get_token_limit for Pro plan."""
        limit = Plans.get_token_limit("pro")
        assert limit == 19_000

    def test_get_token_limit_team_standard(self) -> None:
        """Test get_token_limit for Team Standard plan."""
        limit = Plans.get_token_limit("team_standard")
        assert limit == 23_750

    def test_get_token_limit_team_premium(self) -> None:
        """Test get_token_limit for Team Premium plan."""
        limit = Plans.get_token_limit("team_premium")
        assert limit == 118_750

    def test_get_token_limit_invalid_plan(self) -> None:
        """Test get_token_limit with invalid plan returns default."""
        limit = Plans.get_token_limit("invalid")
        assert limit == Plans.DEFAULT_TOKEN_LIMIT

    def test_get_cost_limit_pro(self) -> None:
        """Test get_cost_limit for Pro plan."""
        limit = Plans.get_cost_limit("pro")
        assert limit == 18.0

    def test_get_cost_limit_team_standard(self) -> None:
        """Test get_cost_limit for Team Standard plan."""
        limit = Plans.get_cost_limit("team_standard")
        assert limit == 25.0

    def test_get_cost_limit_team_premium(self) -> None:
        """Test get_cost_limit for Team Premium plan."""
        limit = Plans.get_cost_limit("team_premium")
        assert limit == 125.0

    def test_get_cost_limit_invalid_plan(self) -> None:
        """Test get_cost_limit with invalid plan returns default."""
        limit = Plans.get_cost_limit("invalid")
        assert limit == Plans.DEFAULT_COST_LIMIT

    def test_get_message_limit_pro(self) -> None:
        """Test get_message_limit for Pro plan."""
        limit = Plans.get_message_limit("pro")
        assert limit == 250

    def test_get_message_limit_team_standard(self) -> None:
        """Test get_message_limit for Team Standard plan."""
        limit = Plans.get_message_limit("team_standard")
        assert limit == 312

    def test_get_message_limit_team_premium(self) -> None:
        """Test get_message_limit for Team Premium plan."""
        limit = Plans.get_message_limit("team_premium")
        assert limit == 1_563

    def test_get_message_limit_invalid_plan(self) -> None:
        """Test get_message_limit with invalid plan returns default."""
        limit = Plans.get_message_limit("invalid")
        assert limit == Plans.DEFAULT_MESSAGE_LIMIT

    def test_is_valid_plan(self) -> None:
        """Test is_valid_plan method."""
        assert Plans.is_valid_plan("pro") is True
        assert Plans.is_valid_plan("max5") is True
        assert Plans.is_valid_plan("max20") is True
        assert Plans.is_valid_plan("team_standard") is True
        assert Plans.is_valid_plan("team_premium") is True
        assert Plans.is_valid_plan("custom") is True
        assert Plans.is_valid_plan("invalid") is False

    def test_all_plans(self) -> None:
        """Test all_plans method returns all configurations."""
        all_plans = Plans.all_plans()
        assert len(all_plans) == 6
        assert PlanType.PRO in all_plans
        assert PlanType.MAX5 in all_plans
        assert PlanType.MAX20 in all_plans
        assert PlanType.TEAM_STANDARD in all_plans
        assert PlanType.TEAM_PREMIUM in all_plans
        assert PlanType.CUSTOM in all_plans


class TestModuleLevelConstants:
    """Test suite for module-level constants and functions."""

    def test_token_limits_dict(self) -> None:
        """Test TOKEN_LIMITS dictionary."""
        assert isinstance(TOKEN_LIMITS, dict)
        assert "pro" in TOKEN_LIMITS
        assert "max5" in TOKEN_LIMITS
        assert "max20" in TOKEN_LIMITS
        assert "team_standard" in TOKEN_LIMITS
        assert "team_premium" in TOKEN_LIMITS
        assert "custom" not in TOKEN_LIMITS  # Custom excluded

    def test_cost_limits_dict(self) -> None:
        """Test COST_LIMITS dictionary."""
        assert isinstance(COST_LIMITS, dict)
        assert "pro" in COST_LIMITS
        assert "max5" in COST_LIMITS
        assert "max20" in COST_LIMITS
        assert "team_standard" in COST_LIMITS
        assert "team_premium" in COST_LIMITS
        assert "custom" not in COST_LIMITS  # Custom excluded

    def test_default_token_limit(self) -> None:
        """Test DEFAULT_TOKEN_LIMIT constant."""
        assert DEFAULT_TOKEN_LIMIT == 19_000

    def test_default_cost_limit(self) -> None:
        """Test DEFAULT_COST_LIMIT constant."""
        assert DEFAULT_COST_LIMIT == 50.0

    def test_common_token_limits_constant(self) -> None:
        """Test COMMON_TOKEN_LIMITS constant."""
        expected = [19_000, 23_750, 88_000, 118_750, 220_000, 880_000]
        assert COMMON_TOKEN_LIMITS == expected

    def test_limit_detection_threshold(self) -> None:
        """Test LIMIT_DETECTION_THRESHOLD constant."""
        assert LIMIT_DETECTION_THRESHOLD == 0.95

    def test_get_token_limit_function(self) -> None:
        """Test get_token_limit module function."""
        assert get_token_limit("pro") == 19_000
        assert get_token_limit("team_standard") == 23_750
        assert get_token_limit("team_premium") == 118_750
        assert get_token_limit("max5") == 88_000
        assert get_token_limit("max20") == 220_000

    def test_get_cost_limit_function(self) -> None:
        """Test get_cost_limit module function."""
        assert get_cost_limit("pro") == 18.0
        assert get_cost_limit("team_standard") == 25.0
        assert get_cost_limit("team_premium") == 125.0
        assert get_cost_limit("max5") == 35.0
        assert get_cost_limit("max20") == 140.0


class TestTeamPlansIntegration:
    """Integration tests for Team plans."""

    def test_team_standard_proportions(self) -> None:
        """Test Team Standard is 1.25x Pro plan."""
        pro_tokens = PLAN_LIMITS[PlanType.PRO]["token_limit"]
        team_std_tokens = PLAN_LIMITS[PlanType.TEAM_STANDARD]["token_limit"]
        assert team_std_tokens == int(pro_tokens * 1.25)

        pro_messages = PLAN_LIMITS[PlanType.PRO]["message_limit"]
        team_std_messages = PLAN_LIMITS[PlanType.TEAM_STANDARD]["message_limit"]
        assert team_std_messages == int(pro_messages * 1.25)

    def test_team_premium_proportions(self) -> None:
        """Test Team Premium is 6.25x Pro plan."""
        pro_tokens = PLAN_LIMITS[PlanType.PRO]["token_limit"]
        team_prem_tokens = PLAN_LIMITS[PlanType.TEAM_PREMIUM]["token_limit"]
        assert team_prem_tokens == int(pro_tokens * 6.25)

        pro_messages = PLAN_LIMITS[PlanType.PRO]["message_limit"]
        team_prem_messages = PLAN_LIMITS[PlanType.TEAM_PREMIUM]["message_limit"]
        # 250 * 6.25 = 1562.5, rounded to 1563
        assert team_prem_messages == 1_563

    def test_team_plans_in_common_limits(self) -> None:
        """Test Team plan limits are in COMMON_TOKEN_LIMITS."""
        assert 23_750 in COMMON_TOKEN_LIMITS  # Team Standard
        assert 118_750 in COMMON_TOKEN_LIMITS  # Team Premium

    def test_team_plans_ordering(self) -> None:
        """Test Team plans are ordered correctly by token limit."""
        limits = [
            ("pro", 19_000),
            ("team_standard", 23_750),
            ("max5", 88_000),
            ("team_premium", 118_750),
            ("max20", 220_000),
        ]

        for i in range(len(limits) - 1):
            plan1, limit1 = limits[i]
            plan2, limit2 = limits[i + 1]
            assert limit1 < limit2, f"{plan1} ({limit1}) should be less than {plan2} ({limit2})"

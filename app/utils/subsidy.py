from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DEFAULT_COST_PER_KW = 65_000  # INR
DEFAULT_ANNUAL_PRODUCTION_PER_KW = 1_100  # kWh per kW per year
DEFAULT_AREA_PER_KW = 8  # m2 per kW usable


@dataclass
class Scheme:
    id: str
    name: str
    subsidy_percent: float
    max_amount_inr: float | None = None


@dataclass
class StatePolicy:
    capex_subsidy_percent: float = 0.0


@dataclass
class EstimateResult:
    gross_cost: float
    central: float
    state_subsidy: float
    net_cost: float
    system_kw: float


BUILTIN_SCHEMES: list[Scheme] = [
    Scheme(
        id="pm-surya-ghar",
        name="PM-Surya Ghar: Muft Bijli Yojana",
        subsidy_percent=40,
        max_amount_inr=200_000,
    )
]


def estimate_system_size_kw(
    roof_area: float | None = None,
    annual_consumption_kwh: float | None = None,
) -> float:
    if annual_consumption_kwh and annual_consumption_kwh > 0:
        estimated = annual_consumption_kwh / DEFAULT_ANNUAL_PRODUCTION_PER_KW
    elif roof_area and roof_area > 0:
        estimated = roof_area / DEFAULT_AREA_PER_KW
    else:
        estimated = 1.0

    return max(0.5, min(10.0, estimated))


def estimate_subsidy(
    system_kw: float,
    *,
    cost_per_kw: float = DEFAULT_COST_PER_KW,
    schemes: Iterable[Scheme] = BUILTIN_SCHEMES,
    state_policy: StatePolicy | None = None,
) -> EstimateResult:
    state_policy = state_policy or StatePolicy()
    gross_cost = system_kw * cost_per_kw

    central_total = 0.0
    for scheme in schemes:
        eligible = gross_cost * (scheme.subsidy_percent / 100.0)
        if scheme.max_amount_inr is not None:
            eligible = min(eligible, scheme.max_amount_inr)
        central_total += eligible

    state_total = gross_cost * (state_policy.capex_subsidy_percent / 100.0)
    net_cost = max(0.0, gross_cost - central_total - state_total)

    return EstimateResult(
        gross_cost=gross_cost,
        central=central_total,
        state_subsidy=state_total,
        net_cost=net_cost,
        system_kw=system_kw,
    )


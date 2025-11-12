from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable

DEFAULT_COST_PER_KW = 65_000  # INR
DEFAULT_ANNUAL_PRODUCTION_PER_KW = 1_100  # kWh per kW per year
DEFAULT_AREA_PER_KW = 8  # m2 per kW usable
DEFAULT_PROVIDER_TARIFF = 8.0  # INR per kWh fallback


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


ELECTRICITY_PROVIDERS: OrderedDict[str, dict[str, float | str]] = OrderedDict(
    [
        ("bses_rajdhani", {"label": "BSES Rajdhani (Delhi)", "tariff": 8.2}),
        ("bses_yamuna", {"label": "BSES Yamuna (Delhi)", "tariff": 8.0}),
        ("tpddl", {"label": "Tata Power Delhi Distribution", "tariff": 8.4}),
        ("adani_mumbai", {"label": "Adani Electricity Mumbai", "tariff": 9.1}),
        ("mseb", {"label": "MSEDCL / Mahadiscom (Maharashtra)", "tariff": 7.3}),
        ("tangedco", {"label": "TANGEDCO (Tamil Nadu)", "tariff": 6.4}),
        ("bescom", {"label": "BESCOM (Bengaluru)", "tariff": 7.1}),
        ("cesc_kolkata", {"label": "CESC (Kolkata)", "tariff": 8.3}),
        ("pspcl", {"label": "PSPCL (Punjab)", "tariff": 7.0}),
        ("ts_spdcl", {"label": "TSSPDCL (Telangana)", "tariff": 7.6}),
        ("wb_sedcl", {"label": "WBSEDCL (West Bengal)", "tariff": 7.2}),
        ("apspdcl", {"label": "APSPDCL (Andhra Pradesh)", "tariff": 7.0}),
        ("up_pcl", {"label": "UPPCL (Uttar Pradesh)", "tariff": 7.4}),
        ("gseb", {"label": "GUVNL / DGVCL (Gujarat)", "tariff": 7.2}),
    ]
)

ELECTRICITY_PROVIDER_CHOICES: list[tuple[str, str]] = [
    ("", "Select electricity provider / DISCOM"),
    *[(key, data["label"]) for key, data in ELECTRICITY_PROVIDERS.items()],
    ("other", "Other / Not listed"),
]

PROVIDER_TARIFFS: dict[str, float] = {
    key: float(data["tariff"]) for key, data in ELECTRICITY_PROVIDERS.items()
}
PROVIDER_TARIFFS["other"] = DEFAULT_PROVIDER_TARIFF


def get_provider_label(provider_key: str | None) -> str | None:
    if not provider_key:
        return None
    if provider_key == "other":
        return "Other provider"
    provider = ELECTRICITY_PROVIDERS.get(provider_key)
    if not provider:
        return None
    return str(provider["label"])


def get_provider_tariff(provider_key: str | None) -> float:
    return PROVIDER_TARIFFS.get(provider_key or "", DEFAULT_PROVIDER_TARIFF)


def estimate_monthly_units_from_bill(
    monthly_bill_inr: float | None, provider_key: str | None
) -> float | None:
    if not monthly_bill_inr or monthly_bill_inr <= 0:
        return None
    tariff = PROVIDER_TARIFFS.get(provider_key or "", DEFAULT_PROVIDER_TARIFF)
    if tariff <= 0:
        tariff = DEFAULT_PROVIDER_TARIFF
    return max(monthly_bill_inr / tariff, 0.0)


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


from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SchemeMatch:
    id: str
    name: str
    description: str
    sponsoring_body: str
    consumer_segments: list[str] = field(default_factory=list)
    coverage: str = "national"
    states: list[str] = field(default_factory=list)
    requires_ownership: bool = True
    requires_grid_connection: bool | None = True
    subsidy_type: str = "Capital"
    benefit: str = "Capital subsidy"
    application_process: str = "Apply via official portal"
    application_url: str | None = None
    documents_required: str = "Refer to programme guidelines"
    timeline: str = "Processing 4-8 weeks"
    vendor_info: str = "Empanelled vendors"
    notes: str = ""
    match_score: float = 7.5
    reasons: list[str] = field(default_factory=list)
    min_roof_area_sqm: float | None = None
    max_monthly_consumption_units: float | None = None
    tags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        payload = field(default_factory=list)
        payload["reasons"] = self.reasons or []
        return payload


_SCHEMES_BY_STATE: dict[str, list[SchemeMatch]] = {
    "national": [
        SchemeMatch(
            id="pm-surya-ghar",
            name="PM Surya Ghar Muft Bijli Yojana",
            description="Central rooftop subsidy for residential households with grid-connected homes.",
            sponsoring_body="Central (MNRE)",
            consumer_segments=["residential"],
            coverage="national",
            states=["all"],
            subsidy_type="Capital subsidy (one-time)",
            benefit="₹30,000 per kW up to 2 kW; ₹18,000 per kW for 3rd kW; max ₹78,000",
            application_process="Apply via National Portal for Rooftop Solar",
            application_url="https://pmsuryaghar.gov.in/",
            documents_required="Aadhaar, property proof, recent electricity bill, bank details, local NOC if needed",
            timeline="Subsidy credited within ~30 days of commissioning",
            vendor_info="MNRE-empanelled vendors",
            notes="Requires prior energy consumption eligibility and net-metering approval",
            requires_ownership=True,
            requires_grid_connection=True,
            min_roof_area_sqm=10,
            tags=["central", "residential"],
            match_score=8.6,
            reasons=[
                "Grid-connected residential rooftop",
                "Meets 10 m² minimum usable area",
            ],
        ),
        SchemeMatch(
            id="grid-connected-rooftop-phase-ii",
            name="Grid-Connected Rooftop Solar Scheme (Phase-II)",
            description="Central financial assistance (CFA) for residential rooftop projects up to 10 kW.",
            sponsoring_body="Central (MNRE)",
            consumer_segments=["residential"],
            coverage="national",
            states=["all"],
            subsidy_type="Central financial assistance (CFA)",
            benefit="Up to ₹14,588/kW (1–3 kW); ₹7,294/kW beyond 3 kW (up to 10 kW); ₹94,822 fixed for >10 kW",
            application_process="Apply via DISCOM or national rooftop portal",
            application_url="https://solarrooftop.gov.in/",
            documents_required="Aadhaar, electricity bill, ID proof, property papers, sanctioned load document",
            timeline="CFA credited after DISCOM verification (~60–90 days)",
            vendor_info="MNRE-registered and DISCOM-empanelled vendors",
            notes="Requires MNRE-approved modules and net-meter installation",
            requires_ownership=True,
            requires_grid_connection=True,
            min_roof_area_sqm=10,
            tags=["central", "residential"],
            match_score=8.4,
            reasons=[
                "Eligible residential consumer",
                "Grid-connected rooftop with MNRE compliant modules",
            ],
        ),
        SchemeMatch(
            id="pm-kusum-a",
            name="PM-KUSUM Component A",
            description="Decentralized solar PV plants feeding power into the grid (500 kW–2 MW systems).",
            sponsoring_body="Central (MNRE)",
            consumer_segments=["agricultural"],
            coverage="national",
            states=["all"],
            subsidy_type="Feed-in tariff + PBI",
            benefit="FiT set by SERC; PBI ~₹0.40/unit or ₹6.6 lakh/MW (whichever lower) for 5 years",
            application_process="Apply via DISCOM/RPGs through competitive bids",
            documents_required="Land records, project report, renewable power generator registration",
            timeline="Five-year incentive period post commissioning",
            vendor_info="Coordinated by DISCOMs and empanelled developers",
            notes="Requires land near feeders and grid connectivity",
            requires_ownership=True,
            requires_grid_connection=True,
            min_roof_area_sqm=2000,
            tags=["agriculture", "large-scale"],
            match_score=7.5,
            reasons=[
                "Farmer/FPO looking to export power",
                "Adequate land availability",
            ],
        ),
        SchemeMatch(
            id="pm-kusum-b",
            name="PM-KUSUM Component B",
            description="Capital subsidy for standalone off-grid solar pumps for irrigation.",
            sponsoring_body="Central + State",
            consumer_segments=["agricultural"],
            coverage="national",
            states=["all"],
            subsidy_type="Capital subsidy (CFA)",
            benefit="CFA 30% (50% in NE/hill states); state ≥30%; farmer ~10% (balance via NABARD loan)",
            application_process="Apply online at PM-KUSUM portal",
            documents_required="Aadhaar, land/cultivation docs, Kisan ID, electricity connectivity proof",
            timeline="Loan and subsidy disbursed post approval",
            vendor_info="Approved solar pump vendors",
            notes="Supports irrigation in non/poorly electrified areas",
            requires_ownership=True,
            requires_grid_connection=False,
            tags=["agriculture", "off-grid"],
            match_score=7.8,
            reasons=[
                "Agricultural consumer with poor grid access",
                "Eligible for central + state subsidy combo",
            ],
        ),
        SchemeMatch(
            id="pm-kusum-c",
            name="PM-KUSUM Component C",
            description="Solarisation of existing grid-connected agricultural pumps with surplus export provision.",
            sponsoring_body="Central + State",
            consumer_segments=["agricultural"],
            coverage="national",
            states=["all"],
            subsidy_type="Capital subsidy (CFA)",
            benefit="CFA 30% (50% NE/hills); state ≥30%; farmer contributes ~10%",
            application_process="Apply via PM-KUSUM portal with DISCOM approvals",
            documents_required="Aadhaar, land/pump details, DISCOM sanction letters",
            timeline="Subsidy released after commissioning and net-meter setup",
            vendor_info="Empanelled solar pump vendors",
            notes="Ideal for farmers wanting net metering on irrigation feeders",
            requires_ownership=True,
            requires_grid_connection=True,
            tags=["agriculture", "grid"],
            match_score=7.6,
            reasons=[
                "Existing grid pump eligible for solarisation",
                "DISCOM sanctioned connection",
            ],
        ),
        SchemeMatch(
            id="tata-microgrid",
            name="Tata Power Renewable Microgrid",
            description="CSR-led deployment of renewable microgrids in rural communities without reliable grid access.",
            sponsoring_body="Tata Power (CSR)",
            consumer_segments=["community"],
            coverage="csr",
            states=["rural"],
            subsidy_type="CSR infrastructure grant",
            benefit="80%-90% of microgrid costs covered; community pays remainder (₹2.5–₹10/kWh)",
            application_process="Coordinated with local bodies; not an individual application",
            documents_required="Community-level agreements and local body endorsements",
            timeline="Project-based deployment; timelines vary",
            vendor_info="Implemented by Tata Power Renewable Microgrid subsidiary",
            notes="Includes prepaid smart meters and entrepreneurship support",
            requires_ownership=False,
            requires_grid_connection=False,
            tags=["community", "off-grid"],
            match_score=6.9,
            reasons=[
                "Ideal for rural settlements seeking reliable power",
                "CSR-backed installation and maintenance",
            ],
        ),
    ],
    "gujarat": [
        SchemeMatch(
            id="guj-res-2024",
            name="Surya Gujarat Residential Rooftop",
            description="State capital subsidy for residential rooftop systems up to 10 kW.",
            sponsoring_body="GUVNL",
            consumer_segments=["residential"],
            coverage="state",
            states=["gujarat"],
            subsidy_type="Capital subsidy",
            benefit="₹10,000/kW up to 3 kW (state top-up)",
            application_process="Apply via SURYA Gujarat portal",
            application_url="https://surya.gujarat.gov.in/",
            documents_required="Aadhaar, electricity bill, property proof, bank details",
            timeline="Disbursement in 60-90 days",
            vendor_info="State empanelled EPC vendors",
            notes="System must be installed by GEDA empanelled partner",
            requires_ownership=True,
            requires_grid_connection=True,
            tags=["state", "residential"],
            match_score=8.4,
            reasons=[
                "Residential consumer in Gujarat",
                "Grid-connected rooftop with empanelled vendor",
            ],
        ),
    ],
    "maharashtra": [
        SchemeMatch(
            id="maharashtra-smart",
            name="SMART Solar Scheme (Maharashtra)",
            description="State subsidy for residential consumers with low electricity usage.",
            sponsoring_body="Government of Maharashtra",
            consumer_segments=["residential"],
            coverage="state",
            states=["maharashtra"],
            subsidy_type="Capital subsidy",
            benefit="90%–95% of system cost covered combining central + state support",
            application_process="Apply via MahaDISCOM i-SMART portal",
            documents_required="Income/caste certificate, Aadhaar, latest bill, address proof",
            timeline="State subsidy credited after central subsidy",
            vendor_info="MahaDISCOM-empanelled vendors",
            notes="Focused on households with usage <100 units/month",
            requires_ownership=True,
            requires_grid_connection=True,
            max_monthly_consumption_units=100,
            tags=["state", "low-income"],
            match_score=7.9,
            reasons=[
                "Eligible low-consumption residential consumer",
                "Combines central and state benefits",
            ],
        ),
    ],
    "delhi": [
        SchemeMatch(
            id="delhi-policy-2023",
            name="Delhi Solar Energy Policy 2023 - Residential Subsidies",
            description="Capital subsidy plus generation-based incentive for Delhi households.",
            sponsoring_body="Government of NCT Delhi",
            consumer_segments=["residential"],
            coverage="state",
            states=["delhi"],
            subsidy_type="Capital subsidy + GBI",
            benefit="₹2,000/kW (max ₹10,000) + GBI ₹2-3/kWh for 5 years",
            application_process="Apply via Delhi DISCOM portals",
            documents_required="Aadhaar, electricity bill, bank details, proof of residency/ownership",
            timeline="Subsidy applied in first bill post commissioning; GBI disbursed annually",
            vendor_info="DISCOM-empanelled vendors",
            notes="Complements central subsidies for residential rooftops",
            requires_ownership=True,
            requires_grid_connection=True,
            tags=["state", "delhi", "residential"],
            match_score=8.2,
            reasons=[
                "Delhi residential consumer",
                "Qualifies for GBI and capex support",
            ],
        ),
    ],
    "rajasthan": [
        SchemeMatch(
            id="rajasthan-topup",
            name="Rajasthan Rooftop Solar Subsidy (State Top-up)",
            description="State top-up for Mukhyamantri Nishulk Bijli Yojana beneficiaries installing rooftop solar.",
            sponsoring_body="Government of Rajasthan",
            consumer_segments=["residential"],
            coverage="state",
            states=["rajasthan"],
            subsidy_type="Additional capital incentive",
            benefit="₹17,000 state top-up for systems above 1.1 kW",
            application_process="Apply via RRECL portal after central approval",
            documents_required="Aadhaar, beneficiary certificate, land/electricity documents",
            timeline="Released alongside central CFA or via export incentive",
            vendor_info="RRECL-empanelled vendors",
            notes="Targets households exceeding free-unit allowance under Mukhya Mantri Nishulk Bijli Yojana",
            requires_ownership=True,
            requires_grid_connection=True,
            tags=["state", "residential"],
            match_score=7.7,
            reasons=[
                "Rajasthan residential consumer",
                "Eligible under Nishulk Bijli Yojana",
            ],
        ),
        SchemeMatch(
            id="pink-promise",
            name="Pink Promise Solar Electrification",
            description="CSR-funded solar electrification for women-led homes in select districts.",
            sponsoring_body="Rajasthan Royals Foundation (CSR)",
            consumer_segments=["community"],
            coverage="csr",
            states=["rajasthan", "assam"],
            subsidy_type="CSR in-kind installation",
            benefit="Free solar lighting/electrification kits for selected beneficiaries",
            application_process="Selection via campaign partners; not open for direct public applications",
            documents_required="Community partner verification and beneficiary identification",
            timeline="Project concluded Aug 2025 (260 homes electrified)",
            vendor_info="Luminous Power & Bindi International",
            notes="Focuses on women-led rural households with training component",
            requires_ownership=False,
            requires_grid_connection=False,
            tags=["community", "women", "off-grid"],
            match_score=6.5,
            reasons=[
                "Community-led initiative in Rajasthan",
                "Supports off-grid women-led households",
            ],
        ),
        SchemeMatch(
            id="barefoot-college",
            name="Barefoot College Solar Electrification",
            description="Community-financed solar home systems maintained by trained rural women engineers.",
            sponsoring_body="Barefoot College (NGO)",
            consumer_segments=["community"],
            coverage="csr",
            states=["rajasthan", "multi-state"],
            subsidy_type="Training + community financing",
            benefit="Villagers pay ~₹5–₹10/month comparable to kerosene expenses",
            application_process="Communities nominated; women attend six-month training in Tilonia",
            documents_required="Community nominations; no formal checklist",
            timeline="Ongoing (750 villages electrified)",
            vendor_info="Local women trained as solar engineers",
            notes="Empowers rural women, ensures local maintenance and ownership",
            requires_ownership=False,
            requires_grid_connection=False,
            tags=["community", "women", "off-grid"],
            match_score=6.8,
            reasons=[
                "Ideal for off-grid rural clusters",
                "Community-driven implementation",
            ],
        ),
    ],
}


def match_subsidy_schemes(
    *,
    state: str,
    consumer_segment: str,
    owns_property: bool,
    is_grid_connected: bool,
    roof_area: float | None = None,
    annual_consumption: float | None = None,
) -> list[SchemeMatch]:
    matches: list[SchemeMatch] = []

    state_key = (state or "").lower()
    # national schemes use 'all'
    if state_key in _SCHEMES_BY_STATE:
        candidate_schemes = _SCHEMES_BY_STATE[state_key]
    else:
        candidate_schemes = []
    # Include national schemes
    candidate_schemes = candidate_schemes + _SCHEMES_BY_STATE.get("national", [])

    for scheme in candidate_schemes:
        if consumer_segment not in scheme.consumer_segments and scheme.consumer_segments:
            continue
        if scheme.requires_ownership and not owns_property:
            continue
        if scheme.requires_ownership is False and owns_property:
            continue
        if scheme.requires_grid_connection is True and not is_grid_connected:
            continue
        if scheme.requires_grid_connection is False and is_grid_connected:
            continue
        if scheme.min_roof_area_sqm and roof_area and roof_area < scheme.min_roof_area_sqm:
            continue
        if scheme.max_monthly_consumption_units and annual_consumption:
            monthly_avg = annual_consumption / 12.0
            if monthly_avg > scheme.max_monthly_consumption_units:
                continue
        matches.append(scheme)

    return matches


def get_scheme_filter_options(matches: List[SchemeMatch]) -> dict[str, list[str]]:
    coverage = sorted({match.coverage for match in matches})
    ownership = ["owner", "tenant"]
    grid = ["grid", "off-grid"]
    return {
        "coverage": coverage,
        "ownership": ownership,
        "grid": grid,
    }


from src.aggregate.patient_matcher import Identifier, group_by_patient


def test_multi_mrn_patient_unions():
    records = [
        [Identifier("facilityA", "MRN-1"), Identifier("acct", "ACCT-1")],
        [Identifier("facilityB", "MRN-2"), Identifier("acct", "ACCT-1")],  # shares account
        [Identifier("facilityC", "MRN-3")],  # separate patient
    ]
    groups = group_by_patient(records)
    assert len(groups) == 2
    values = {ident.value for pk in groups.values() for ident in pk.identifiers}
    assert {"MRN-1", "MRN-2", "MRN-3", "ACCT-1"}.issubset(values)


def test_router_maps_known_classes():
    from src.ingest.acu_router import analyzer_for
    assert analyzer_for("discharge-summary") == "healthcare-discharge-summary-v1"
    assert analyzer_for("cover-separator") is None
    assert analyzer_for("unknown-other") is None

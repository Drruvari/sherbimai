from app.retrieval import ServiceRetriever


def test_known_queries_match_expected_services():
    r = ServiceRetriever()
    cases = {
        "Si rinovoj certifikatën ADR?": "adr-renewal",
        "Jam në Itali dhe dua certifikatën e martesës.": "marriage-certificate-italy",
        "Më duhet dëshmi penaliteti nga konsullata.": "criminal-record-abroad",
        "Si regjistroj fëmijën në klasë të parë?": "first-grade-registration",
        "Vërtetim për pagesën PAK": "pak-certificate",
    }

    for question, expected in cases.items():
        assert r.search(question, 1)[0].service["id"] == expected


def test_all_services_have_official_sources():
    r = ServiceRetriever()
    assert len(r.services) >= 8
    for service in r.services:
        assert "e-albania.al/" in service["source_url"]
        assert service["verified_at"]

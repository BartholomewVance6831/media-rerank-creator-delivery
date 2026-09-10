from src.media_rerank_service import MediaCandidate, choose_creator_delivery


def test_creator_delivery_keeps_relevant_media_in_rank_order():
    ranked = [
        MediaCandidate("a", "match", "A", 0.88),
        MediaCandidate("b", "borderline", "B", 0.50),
        MediaCandidate("c", "noise", "C", 0.49),
    ]
    assert [item.media_id for item in choose_creator_delivery(ranked)] == ["a", "b"]

from app.semantic import split_scenes, rank_candidates

def test_split_scenes_sentence_boundaries():
    result=split_scenes("Trust is earned slowly. Sales grew 40% in 2025! Cloud computing saves time.")
    assert len(result)==3
    assert result[0]["text"].endswith("slowly.")

def test_ranking_is_deterministic_and_sorted():
    candidates=[{"id":"a","description":"money and cash"},{"id":"b","description":"cloud servers and data centers"}]
    ranked=rank_candidates("cloud computing servers", candidates)
    assert len(ranked)==2
    assert ranked[0][0] >= ranked[1][0]

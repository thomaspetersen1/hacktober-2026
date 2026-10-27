import json

import pytest

from app.services import ideas


def room(name, tag="ghost"):
    return {"name": name, "concept": "A cold, dim hallway with whispers.", "scare": "A sheet ghost drops.", "prop_tag": tag}


def house(*names):
    return json.dumps({"theme": "Test Haunt", "story": "Something happened here long ago.", "rooms": [room(n) for n in names]})


@pytest.fixture
def use_ai(monkeypatch):
    monkeypatch.setattr(ideas.get_settings(), "ideas_source", "auto")
    monkeypatch.setattr(ideas.get_settings(), "snowflake_account", "fake")
    monkeypatch.setattr(ideas.get_settings(), "snowflake_user", "fake")


def fake_complete(monkeypatch, *replies):
    calls = []

    def complete(prompt, response_format, max_tokens):
        calls.append(prompt)
        reply = replies[len(calls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(ideas, "complete", complete)
    return calls


def test_ai_house_used_when_valid(use_ai, monkeypatch):
    fake_complete(monkeypatch, house("Room 1: Bone Gate", "Hall of Teeth", "Last Breath"))
    result, source = ideas.generate_house(3, 500)
    assert source == "ai"
    assert result.theme == "Test Haunt"
    assert [r.name for r in result.rooms] == ["Bone Gate", "Hall of Teeth", "Last Breath"]


def test_ai_retries_on_wrong_room_count(use_ai, monkeypatch):
    calls = fake_complete(monkeypatch, house("A Room", "B Room"), house("A Room", "B Room", "C Room"))
    result, source = ideas.generate_house(3, 500)
    assert source == "ai" and len(result.rooms) == 3 and len(calls) == 2


def test_ai_rejects_unknown_tag_and_duplicates(use_ai, monkeypatch):
    bad_tag = json.dumps({"theme": "T", "story": "A long enough story.", "rooms": [room("A Room", "unicorn")]})
    fake_complete(monkeypatch, bad_tag, house("Same", "same"))
    _, source = ideas.generate_house(1, 100)
    assert source == "fixed"  # both tries were unusable


def test_falls_back_when_cortex_is_down(use_ai, monkeypatch):
    fake_complete(monkeypatch, RuntimeError("warehouse suspended"))
    result, source = ideas.generate_house(4, 400)
    assert source == "fixed" and len(result.rooms) == 4


def test_ai_mode_fails_loudly(monkeypatch, use_ai):
    monkeypatch.setattr(ideas.get_settings(), "ideas_source", "ai")
    fake_complete(monkeypatch, RuntimeError("warehouse suspended"))
    with pytest.raises(RuntimeError):
        ideas.generate_house(2, 100)


def test_ai_room_avoids_existing_names(use_ai, monkeypatch):
    fake_complete(monkeypatch, json.dumps(room("Bone Gate")), json.dumps(room("Rat King Cellar", "bat")))
    result, source = ideas.generate_room("Test Haunt", 2, ["Bone Gate"])
    assert source == "ai" and result.name == "Rat King Cellar" and result.prop_tag == "bat"


def test_fixed_house_paces_entry_climax_exit():
    names = [r.name for r in ideas.fixed_house(5).rooms]
    assert names[0] == "Entry Hall" and names[-2] == "Clocktower Landing" and names[-1] == "Final Exit"


def test_long_ai_text_is_cut_to_one_sentence(use_ai, monkeypatch):
    rambling = json.dumps({
        "theme": "Test Haunt",
        "story": "A witch lived here. Then she didn't! Nobody knows why.",
        "rooms": [{**room("Bone Gate"), "concept": "Dark and damp. Very dark.", "scare": "A bat drops? Yes."}],
    })
    fake_complete(monkeypatch, rambling)
    result, _ = ideas.generate_house(1, 100)
    assert result.story == "A witch lived here."
    assert result.rooms[0].concept == "Dark and damp."
    assert result.rooms[0].scare == "A bat drops?"

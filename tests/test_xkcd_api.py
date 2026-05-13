from xkcd_mcp.xkcd_api import _comic


def test_comic_builds_urls() -> None:
    d = _comic({"num": 2916, "title": "Test", "alt": "Alt", "img": "https://imgs.xkcd.com/x.png"})
    assert d["num"] == 2916
    assert d["xkcd_url"] == "https://xkcd.com/2916/"
    assert d["explainxkcd_url"] == "https://www.explainxkcd.com/wiki/index.php/2916"

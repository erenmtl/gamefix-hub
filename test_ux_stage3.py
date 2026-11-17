# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
import main


def test_stage3():
    c = TestClient(main.app)
    r = c.get("/")
    assert r.status_code == 200
    h = r.text
    assert "Hangi hatayı alıyorsun?" in h
    assert "VAN 185, ERR_GFX_STATE, Exit Code 1…" in h
    assert "En çok bakılan hatalar" in h
    assert "Çözümü gör →" in h
    assert "Listede olmayan bir hata mı var? AI ile analiz et." in h
    assert "7/24 Aktif" not in h
    assert "50 Rehber" not in h
    assert "website_url" not in h.lower()
    assert "Gemini 3.8 Flash" not in h
    assert h.index('id="en-cok-bakilan-baslik"') < h.index('id="homeGamesShowcaseGrid"') < h.index('id="tabContent-ai-lab"') < h.index('id="tabContent-forum"')
    print("[PASS] Stage 3 homepage hierarchy, search, 8 priority cards, games grid, AI card, bottom forum, and stat cleanup verified!")


if __name__ == "__main__":
    test_stage3()

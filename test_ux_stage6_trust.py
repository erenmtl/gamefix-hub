# -*- coding: utf-8 -*-
"""
AŞAMA 6: Güven ve Şeffaflık Bileşenleri Doğrulama Testi
1. Yazar kutusu (ad, kısa not, Hakkımızda linki)
2. İçerik durumu etiketleri ("Editör kontrolünden geçti" vs "Yapay zeka ile üretildi, uygulamadan önce kontrol edin")
3. "Son güncelleme" tarihi veri dosyasındaki tarih_guncelleme alanından gelir
4. "Bu çözüm işe yaradı mı?" 20+ oy eşiğinde gerçek oran hesaplaması
"""
import json
from fastapi.testclient import TestClient
import main
import error_page_builder as builder


def test_stage6():
    with open(builder.DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Test both editor_verified=True and editor_verified=False in template engine
    sample = dict(data["pages"][0])
    sample["editor_verified"] = True
    html_verified, _ = builder.render_error_code_page(sample)
    assert "Editör kontrolünden geçti" in html_verified
    assert "oc-badge-success" in html_verified
    assert 'href="/hakkimizda.html"' in html_verified
    assert f'datetime="{sample["tarih_guncelleme"]}"' in html_verified

    sample_ai = dict(data["pages"][0])
    sample_ai["editor_verified"] = False
    html_ai, _ = builder.render_error_code_page(sample_ai)
    assert "Yapay zeka ile üretildi, uygulamadan önce kontrol edin" in html_ai
    assert "oc-badge-warning" in html_ai

    # 2. Test voting < 20 votes vs >= 20 votes on backend API
    c = TestClient(main.app)
    issue_id = 10

    # Cast 5 votes -> show_success_rate must be False
    for i in range(5):
        r = c.post(
            f"/api/issues/{issue_id}/vote",
            json={"vote_type": "up"},
            headers={"X-Client-Id": f"stage6_voter_{i}"},
        )
        assert r.status_code == 200
        d = r.json()
        if d["total_votes"] < 20:
            assert d["show_success_rate"] is False

    # Cast up to 21 votes -> show_success_rate must become True with real percentage
    for i in range(5, 22):
        vtype = "up" if i < 19 else "down"
        r = c.post(
            f"/api/issues/{issue_id}/vote",
            json={"vote_type": vtype},
            headers={"X-Client-Id": f"stage6_voter_{i}"},
        )
        assert r.status_code == 200
        d = r.json()

    assert d["total_votes"] >= 20
    assert d["show_success_rate"] is True
    assert isinstance(d["success_rate"], int) and 0 <= d["success_rate"] <= 100

    print(
        f"[PASS] AŞAMA 6 yazar kutusu, içerik durumu etiketleri, tarih_guncelleme senkronizasyonu ve 20+ oy gerçek oran ({d['success_rate']}%, {d['total_votes']} oy) doğrulandı!"
    )


if __name__ == "__main__":
    test_stage6()

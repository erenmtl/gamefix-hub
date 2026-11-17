# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
import main
import update_stage4_template_and_data as s4_data
import error_page_builder as builder


def test_stage4():
    s4_data.main()
    cnt, warns = builder.build_all_from_json()
    assert cnt == 13 and len(warns) == 0, f"Build warnings: {warns}"

    c = TestClient(main.app)

    # 1. Verify /lol/van-185 (no scenarios defined -> scenario selector hidden, official source empty -> hidden)
    r_185 = c.get("/lol/van-185")
    assert r_185.status_code == 200
    h185 = r_185.text
    assert "Bu hata ne anlama geliyor?" in h185
    assert 'id="hizli-cozum"' in h185
    assert 'id="stepProgressBadge"' in h185
    assert "İlerleme: 0/4 adım" in h185
    assert "Bu adımı tamamladım" in h185
    assert "Geri yükleme noktası oluşturun:" in h185
    assert "Yönetici olarak çalıştırın" in h185
    assert "Bu sayfada (İçindekiler)" in h185
    assert 'id="mobileStickyActionBar"' in h185
    assert 'id="senaryo-secici"' not in h185, "Senaryo tanımlı olmayan sayfada senaryo seçici görünmemeli!"
    assert 'id="resmi-kaynak"' not in h185, "resmi_kaynak_url boş olduğunda boş bölüm görünmemeli!"
    assert 'class="step-screenshot-slot"' not in h185, "Görsel yoksa boş yer tutucu kutu çıkmamalı!"

    # 2. Verify /valorant/van-1067 (scenarios defined: AMD Ryzen fTPM vs Intel PTT)
    r_1067 = c.get("/valorant/van-1067")
    assert r_1067.status_code == 200
    h1067 = r_1067.text
    assert 'id="senaryo-secici"' in h1067
    assert "Hangisi senin durumun?" in h1067
    assert "AMD Ryzen İşlemci (fTPM)" in h1067
    assert "Intel Core İşlemci (PTT)" in h1067

    print("[PASS] AŞAMA 4 hata kodu sayfası şablonu (Hızlı çözüm, 0/N ilerleme, senaryo seçici, içindekiler, boş alan gizleme, mobil alt çubuk) doğrulandı!")


if __name__ == "__main__":
    test_stage4()

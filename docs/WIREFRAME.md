# 🖼 OrionDesk Wireframe (v6)

Dokumen ini menjadi referensi visual resmi untuk baseline UI OrionDesk pada roadmap aktif.

Snapshot digunakan untuk:
- Validasi konsistensi layout
- Visual regression testing
- Dokumentasi evolusi antarmuka

---

## 🧭 Main Navigation Tabs

OrionDesk saat ini terdiri dari lima tab utama:

- **Command**
- **Memory**
- **Settings**
- **Diagnostics**
- **About**

Struktur tab ini menjadi baseline navigasi untuk versi v6.

---

## 📐 Baseline Snapshot – Desktop Layout

Snapshot PNG baseline di `docs/assets/` dibersihkan otomatis oleh test untuk menjaga konsistensi lintas environment.

Baseline visual akan digenerate ulang saat test snapshot dijalankan.

Target baseline:

- Resolution: `1280x760`, `1024x640`
- Tabs: `Command`, `Memory`, `Settings`, `Diagnostics`, `About`
- Output folder: `tests/artifacts/baseline/v6/`

---

## 🧪 Snapshot Governance

- Snapshot dihasilkan melalui automated visual regression test.
- Perubahan layout signifikan **wajib** diikuti refresh baseline.
- Perubahan minor harus dievaluasi melalui PR review.

---

## 🔄 Versioning Policy

- `v6` → Baseline aktif untuk ROADMAP v6.
- Versi berikutnya akan memiliki folder snapshot terpisah (`v6/`, `v7/`, dst).

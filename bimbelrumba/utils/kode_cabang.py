import frappe


def set_kode_cabang(doc, method=None):
    # Jangan timpa kalau sudah ada
    if doc.kode_cabang:
        return

    if not doc.nama_kota:
        frappe.throw("Nama Kota wajib diisi sebelum membuat kode cabang.")

    # Ambil kode kota dari DocType RUMBA Kota
    kode_kota = frappe.db.get_value("RUMBA Kota", doc.nama_kota, "kode_kota")

    if not kode_kota:
        frappe.throw(f"Kode kota belum diisi pada RUMBA Kota: {doc.nama_kota}")

    kode_kota = kode_kota.strip().upper()

    # Cari kode cabang terakhir untuk kota tersebut
    last_kode = frappe.db.sql(
        """
        SELECT kode_cabang
        FROM `tabRUMBA Cabang`
        WHERE nama_kota = %s
          AND kode_cabang LIKE %s
        ORDER BY CAST(SUBSTRING(kode_cabang, %s) AS UNSIGNED) DESC
        LIMIT 1
        """,
        (doc.nama_kota, f"{kode_kota}%", len(kode_kota) + 1),
    )

    if last_kode:
        last_number = int(last_kode[0][0].replace(kode_kota, ""))
        next_number = last_number + 1
    else:
        next_number = 1

    doc.kode_cabang = f"{kode_kota}{next_number:02d}"

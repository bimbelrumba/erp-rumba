import frappe


def set_kode_cabang(doc, method=None):
    if doc.kode_cabang:
        return

    if not hasattr(doc, "kode_kota") or not doc.kode_kota:
        frappe.throw("Kode Kota wajib diisi sebelum membuat kode cabang.")

    # Ambil prefix kode kota dari DocType RUMBA Kota
    prefix = frappe.db.get_value("RUMBA Kota", doc.kode_kota, "kode_kota")

    if not prefix:
        frappe.throw(f"Field kode_kota belum diisi pada RUMBA Kota: {doc.kode_kota}")

    prefix = prefix.strip().upper()

    # Cari nomor urut terakhir berdasarkan kota
    last_kode = frappe.db.sql(
        """
        SELECT kode_cabang
        FROM `tabRUMBA Cabang`
        WHERE kode_kota = %s
          AND kode_cabang LIKE %s
        ORDER BY CAST(SUBSTRING(kode_cabang, %s) AS UNSIGNED) DESC
        LIMIT 1
        """,
        (doc.kode_kota, f"{prefix}%", len(prefix) + 1),
    )

    if last_kode and last_kode[0][0]:
        last_number = int(last_kode[0][0].replace(prefix, ""))
        next_number = last_number + 1
    else:
        next_number = 1

    doc.kode_cabang = f"{prefix}{next_number:02d}"

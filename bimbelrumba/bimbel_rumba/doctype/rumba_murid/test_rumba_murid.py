# Copyright (c) 2026, Rumba Kita Indonesia and Contributors
# See license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase


class TestRUMBAMurid(FrappeTestCase):
    def test_requires_at_least_one_hari_belajar(self):
        doc = self.make_doc()

        with self.assertRaises(ValidationError):
            doc.validate()

    def test_requires_operational_fields(self):
        doc = self.make_doc(senin=1)

        with self.assertRaises(ValidationError):
            doc.validate()

    def test_populates_hari_belajar_label_from_selected_days(self):
        doc = self.make_doc(
            senin=1,
            rabu=1,
            tanggal_mulai_belajar="2026-04-02",
            metode_pembayaran="Tunai",
            status_pembayaran="Lunas",
        )

        doc.validate()

        self.assertEqual(doc.hari_belajar, "Senin, Rabu")

    def test_syncs_fields_from_pendaftaran_rujukan(self):
        pendaftaran = frappe.get_doc(
            {
                "doctype": "RUMBA Pendaftaran",
                "name": "RMB-DAFTAR-0001",
                "kota_rumba": "Kota Demo",
                "cabang_rumba": "Cabang Demo",
                "program_belajar": "Program Demo",
                "jam_belajar": "09.30 - 10.45",
                "tanggal_pendaftaran": "2026-04-01",
                "nama_lengkap": "Budi Santoso",
                "nama_panggilan": "Budi",
                "email_ortu": "ortu@example.com",
                "nomor_hape": "081234567890",
                "senin": 1,
            }
        )

        original_get_cached_doc = frappe.get_cached_doc
        frappe.get_cached_doc = lambda doctype, name: pendaftaran

        try:
            doc = self.make_doc(
                pendaftaran_rujukan="RMB-DAFTAR-0001",
                tanggal_mulai_belajar="2026-04-02",
                metode_pembayaran="Tunai",
                status_pembayaran="Lunas",
            )

            doc.validate()
        finally:
            frappe.get_cached_doc = original_get_cached_doc

        self.assertEqual(doc.nama_lengkap, "Budi Santoso")
        self.assertEqual(doc.nomor_handphone, "081234567890")
        self.assertEqual(doc.program_belajar, "Program Demo")
        self.assertEqual(doc.hari_belajar, "Senin")

    @staticmethod
    def make_doc(**overrides):
        doc = frappe.get_doc(
            {
                "doctype": "RUMBA Murid",
                "status_murid": "Aktif",
            }
        )
        doc.update(overrides)
        return doc

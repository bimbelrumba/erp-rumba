# Copyright (c) 2026, Rumba Kita Indonesia and Contributors
# See license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase


class TestRUMBAPendaftaran(FrappeTestCase):
	def test_requires_at_least_one_hari_belajar(self):
		doc = self.make_doc()

		with self.assertRaises(ValidationError):
			doc.validate()

	def test_requires_school_details_when_student_already_in_school(self):
		doc = self.make_doc(senin=1, sudah_sekolah="Sudah")

		with self.assertRaises(ValidationError):
			doc.validate()

	def test_requires_special_needs_explanation(self):
		doc = self.make_doc(senin=1, kebutuhan_khusus="Ya")

		with self.assertRaises(ValidationError):
			doc.validate()

	def test_requires_merchandise_size_when_kaos_selected(self):
		doc = self.make_doc(senin=1, kaos=1)

		with self.assertRaises(ValidationError):
			doc.run_method("validate")

	def test_requires_admin_fields_when_status_accepted(self):
		doc = self.make_doc(senin=1, status_pendaftaran="Diterima")

		with self.assertRaises(ValidationError):
			doc.run_method("validate")

	def test_valid_document_passes_validation(self):
		doc = self.make_doc(
			senin=1,
			sudah_sekolah="Sudah",
			nama_sekolah="SDK Rumba",
			kelas_sekolah="SD Kelas 1",
			saudara_di_rumba="Ya",
			nama_saudara="Alya",
			kebutuhan_khusus="Ya",
			penjelasan_kebutuhan_khusus="Perlu instruksi yang lebih perlahan.",
			les_serupa="Ya",
			durasi_les="6 bulan",
			lainnya=1,
			penjelasan_lainnya="Rekomendasi komunitas.",
			kaos=1,
			ukuran_kaos="M",
			status_pendaftaran="Diterima",
			tanggal_mulai_belajar="2026-04-01",
			metode_pembayaran="Tunai",
			status_bayar="Lunas",
		)

		doc.validate()

	@staticmethod
	def make_doc(**overrides):
		doc = frappe.get_doc(
			{
				"doctype": "RUMBA Pendaftaran",
				"kota_rumba": "Kota Demo",
				"cabang_rumba": "Cabang Demo",
				"program_belajar": "Program Demo",
				"jam_belajar": "09.30 - 10.45",
				"nama_lengkap": "Budi Santoso",
				"nama_panggilan": "Budi",
				"tanggal_lahir": "2020-01-01",
				"sudah_sekolah": "Belum",
				"alamat_rumah": "Jl. Rumba No. 1",
				"nama_ortu": "Siti Santoso",
				"email_ortu": "ortu@example.com",
				"nomor_hape": "081234567890",
				"saudara_di_rumba": "Tidak",
				"kebutuhan_khusus": "Tidak",
				"les_serupa": "Tidak",
				"status_pendaftaran": "Tunggu",
			}
		)
		doc.update(overrides)
		return doc

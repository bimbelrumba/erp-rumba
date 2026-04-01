# Copyright (c) 2026, Rumba Kita Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class RUMBAPendaftaran(Document):
	WORKFLOW_REQUIRED_FIELDS = (
		("tanggal_mulai_belajar", "Tanggal Mulai Belajar"),
		("metode_pembayaran", "Metode Pembayaran"),
		("status_bayar", "Status Pembayaran"),
	)

	def validate(self):
		self._validate_hari_belajar()
		self._validate_conditional_fields()
		self._validate_workflow_fields()
		self._validate_single_rumba_murid_link()

	def _validate_hari_belajar(self):
		if any(self.get(day) for day in self._hari_belajar_fields()):
			return

		frappe.throw(_("Pilih minimal satu Hari Belajar."))

	def _validate_conditional_fields(self):
		self._require_if(
			self.sudah_sekolah == "Sudah",
			("nama_sekolah", "Nama Sekolah"),
			("kelas_sekolah", "Kelas"),
		)
		self._require_if(
			self.saudara_di_rumba == "Ya",
			("nama_saudara", "Nama Saudara"),
		)
		self._require_if(
			self.kebutuhan_khusus == "Ya",
			("penjelasan_kebutuhan_khusus", "Penjelasan kebutuhan khusus"),
		)
		self._require_if(
			self.lainnya,
			("penjelasan_lainnya", "Penjelasan lainnya"),
		)
		self._require_if(
			self.kaos,
			("ukuran_kaos", "Ukuran Kaos"),
		)

		if self.les_serupa == "Ya" and not (self.durasi_les or self.nama_tempat_les):
			frappe.throw(
				_(
					"Jika Les Serupa dipilih Ya, isi minimal Durasi Les atau Nama Tempat Les."
				)
			)

	def _validate_workflow_fields(self):
		if self.status_pendaftaran != "Diterima":
			return

		self._require_if(True, *self.WORKFLOW_REQUIRED_FIELDS)

	def _validate_single_rumba_murid_link(self):
		if not self.rumba_murid:
			return

		existing_registration = frappe.db.get_value(
			"RUMBA Pendaftaran",
			{"rumba_murid": self.rumba_murid, "name": ("!=", self.name)},
			"name",
		)
		if existing_registration:
			frappe.throw(
				_(
					"RUMBA Murid {0} sudah terhubung ke pendaftaran lain: {1}."
				).format(
					frappe.bold(self.rumba_murid),
					frappe.bold(existing_registration),
				)
			)

	def _require_if(self, condition, *fields):
		if not condition:
			return

		missing_labels = [label for fieldname, label in fields if not self.get(fieldname)]
		if missing_labels:
			frappe.throw(
				_("Field berikut wajib diisi: {0}").format(
					", ".join(frappe.bold(label) for label in missing_labels)
				)
			)

	@staticmethod
	def _hari_belajar_fields():
		return ("senin", "selasa", "rabu", "kamis", "jumat", "sabtu")

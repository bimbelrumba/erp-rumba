# Copyright (c) 2026, Rumba Kita Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class RUMBAMurid(Document):
    WORKFLOW_REQUIRED_FIELDS = (
        ("tanggal_mulai_belajar", "Tanggal Mulai Belajar"),
        ("metode_pembayaran", "Metode Pembayaran"),
        ("status_pembayaran", "Status Pembayaran"),
    )

    MIRRORED_PENDAFTARAN_FIELDS = (
        "kota_rumba",
        "cabang_rumba",
        "program_belajar",
        "jam_belajar",
        "tanggal_pendaftaran",
        "nama_lengkap",
        "nama_panggilan",
        "email_ortu",
    )

    def validate(self):
        self._sync_from_pendaftaran()
        self._validate_hari_belajar()
        self._populate_hari_belajar_label()
        self._validate_workflow_fields()
        self._validate_single_pendaftaran_rujukan()

    def _sync_from_pendaftaran(self):
        if not self.pendaftaran_rujukan:
            return

        pendaftaran = frappe.get_cached_doc("RUMBA Pendaftaran", self.pendaftaran_rujukan)
        for fieldname in self.MIRRORED_PENDAFTARAN_FIELDS:
            self.set(fieldname, pendaftaran.get(fieldname))

        self.nomor_handphone = pendaftaran.get("nomor_hape")
        for day in self._hari_belajar_fields():
            self.set(day, pendaftaran.get(day))

    def _validate_hari_belajar(self):
        if any(self.get(day) for day in self._hari_belajar_fields()):
            return

        frappe.throw(_("Pilih minimal satu Hari Belajar."))

    def _populate_hari_belajar_label(self):
        selected_days = [day.capitalize() for day in self._hari_belajar_fields() if self.get(day)]
        self.hari_belajar = ", ".join(selected_days)

    def _validate_workflow_fields(self):
        self._require_if(True, *self.WORKFLOW_REQUIRED_FIELDS)

    def _validate_single_pendaftaran_rujukan(self):
        if not self.pendaftaran_rujukan:
            return

        existing_student = frappe.db.get_value(
            "RUMBA Murid",
            {"pendaftaran_rujukan": self.pendaftaran_rujukan, "name": ("!=", self.name)},
            "name",
        )
        if existing_student:
            frappe.throw(
                _("Pendaftaran {0} sudah terhubung ke RUMBA Murid lain: {1}.").format(
                    frappe.bold(self.pendaftaran_rujukan),
                    frappe.bold(existing_student),
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

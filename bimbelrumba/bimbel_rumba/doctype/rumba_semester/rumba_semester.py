# Copyright (c) 2026, Rumba Kita Indonesia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class RUMBASemester(Document):
	
	def before_save(self):

        if self.kode_tahun_ajaran and self.periode_semester:
            self.kode_semester = f"{self.kode_tahun_ajaran}.{self.periode_semester}"

	if self.tanggal_selesai:
            self.selesai = 1 if getdate(nowdate()) > getdate(self.tanggal_selesai) else 0

def update_status_semester_selesai():
    semesters = frappe.get_all(
        "RUMBA Semester",
        filters={"tanggal_selesai": ["is", "set"]},
        fields=["name", "tanggal_selesai", "selesai"]
    )

    today = getdate(nowdate())

    for row in semesters:
        should_finish = 1 if today > getdate(row.tanggal_selesai) else 0

        if row.selesai != should_finish:
            frappe.db.set_value("RUMBA Semester", row.name, "selesai", should_finish)

    frappe.db.commit()

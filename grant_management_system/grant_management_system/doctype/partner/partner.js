// Copyright (c) 2025, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Partner", {
	refresh(frm) {
		frm.toggle_display("address_html", !frm.is_new());
		frm.toggle_display("contact_html", !frm.is_new());

		if (!frm.is_new()) {
			frappe.contacts.render_address_and_contact(frm);
		}
	},
});

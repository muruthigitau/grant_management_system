// Copyright (c) 2025, David and contributors
// For license information, please see license.txt

frappe.query_reports["Grant Portfolio Summary"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), +12),
		},
		{
			fieldname: "grant_call",
			label: __("Grant Call"),
			fieldtype: "Link",
			options: "Grant Call",
		},
		{
			fieldname: "partner",
			label: __("Partner"),
			fieldtype: "Link",
			options: "Partner",
		},
		{
			fieldname: "programme",
			label: __("Programme"),
			fieldtype: "Link",
			options: "Grant Programme",
		},
		{
			fieldname: "donor",
			label: __("Donor"),
			fieldtype: "Link",
			options: "Donor",
		},
		{
			fieldname: "application_status",
			label: __("Application Status"),
			fieldtype: "Select",
			options: "\nOpen\nReceived\nIn Progress\nApproved\nRejected\nExpired\nWithdrawn",
		},
		{
			fieldname: "project_status",
			label: __("Project Status"),
			fieldtype: "Select",
			options: "\nOpen\nCompleted\nCancelled\nExpired",
		},
		{
			fieldname: "is_active",
			label: __("Is Active"),
			fieldtype: "Select",
			options: "\nYes\nNo",
		},
	],
};

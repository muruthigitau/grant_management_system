# Copyright (c) 2025, David and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_report_summary(data, filters)
    chart = get_chart_data(data, filters)
    return columns, data, None, chart, summary

def get_columns():
    return [
        {"label": _("Grant Call"), "fieldname": "grant_call", "fieldtype": "Link", "options": "Grant Call", "width": 150},
        {"label": _("Call Name"), "fieldname": "grant_call_name", "fieldtype": "Data", "width": 180},
        {"label": _("Programme"), "fieldname": "programme", "fieldtype": "Link", "options": "Grant Programme", "width": 120},
        {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Link", "options": "Partner", "width": 150},
        {"label": _("Applicant Name"), "fieldname": "applicant_name", "fieldtype": "Data", "width": 180},
        {"label": _("Application Status"), "fieldname": "application_status", "fieldtype": "Data", "width": 120},
        {"label": _("Project Status"), "fieldname": "project_status", "fieldtype": "Data", "width": 120},
        {"label": _("Amount Requested"), "fieldname": "amount_requested", "fieldtype": "Currency", "width": 120},
        {"label": _("Amount Awarded"), "fieldname": "amount_awarded", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Disbursed"), "fieldname": "total_disbursed", "fieldtype": "Currency", "width": 120},
        {"label": _("Balance"), "fieldname": "balance", "fieldtype": "Currency", "width": 120},
        {"label": _("% Disbursed"), "fieldname": "percent_disbursed", "fieldtype": "Percent", "width": 100},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 100},
        {"label": _("Donor"), "fieldname": "donor", "fieldtype": "Link", "options": "Donor", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql("""
        SELECT 
            gc.name as grant_call,
            gc.grant_call_name,
            gc.programme,
            gc.donor,
            gc.company,
            gp.name as project_name,
            gp.applicant_name,
            gp.partner,
            gp.status as project_status,
            gp.expected_start_date as start_date,
            gp.expected_end_date as end_date,
            ga.status as application_status,
            ga.amount as amount_requested,
            gp.estimated_budget as amount_awarded,
            COALESCE(SUM(gpd.disbursed_amount), 0) as total_disbursed,
            (gp.estimated_budget - COALESCE(SUM(gpd.disbursed_amount), 0)) as balance,
            CASE 
                WHEN gp.estimated_budget > 0 
                THEN (COALESCE(SUM(gpd.disbursed_amount), 0) / gp.estimated_budget) * 100 
                ELSE 0 
            END as percent_disbursed
            
        FROM `tabGrant Call` gc
        LEFT JOIN `tabGrant Application` ga ON ga.grant_call = gc.name
        LEFT JOIN `tabGrant Project` gp ON gp.grant_application = ga.name
        LEFT JOIN `tabGrant Project Disbursement` gpd ON gpd.grant_project = gp.name
        
        WHERE gc.docstatus = 1
        {conditions}
        
        GROUP BY gc.name, gp.name, ga.name
        ORDER BY gc.creation DESC, gp.creation DESC
    """.format(conditions=conditions), filters, as_dict=1)
    
    return data

def get_conditions(filters):
    conditions = []
    
    if filters.get("grant_call"):
        conditions.append("gc.name = %(grant_call)s")
    
    if filters.get("partner"):
        conditions.append("gp.partner = %(partner)s")
    
    if filters.get("programme"):
        conditions.append("gc.programme = %(programme)s")
    
    if filters.get("donor"):
        conditions.append("gc.donor = %(donor)s")
    
    if filters.get("company"):
        conditions.append("gc.company = %(company)s")
    
    if filters.get("application_status"):
        conditions.append("ga.status = %(application_status)s")
    
    if filters.get("project_status"):
        conditions.append("gp.status = %(project_status)s")
    
    if filters.get("from_date"):
        conditions.append("gc.opening_date >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("gc.closing_date <= %(to_date)s")
    
    if filters.get("is_active"):
        conditions.append("gc.is_active = %(is_active)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""

def get_report_summary(data, filters):
    total_awarded = sum((d.get("amount_awarded") or 0) for d in data)
    total_disbursed = sum((d.get("total_disbursed") or 0) for d in data)
    total_balance = total_awarded - total_disbursed
    total_projects = len(data)
    
    active_projects = sum(1 for d in data if d.get("project_status") in ["Open", "Active"])
    completed_projects = sum(1 for d in data if d.get("project_status") == "Completed")
    
    return [
        {"label": _("Total Projects"), "value": total_projects, "indicator": "blue"},
        {"label": _("Active Projects"), "value": active_projects, "indicator": "green"},
        {"label": _("Completed Projects"), "value": completed_projects, "indicator": "gray"},
        {"label": _("Total Awarded"), "value": frappe.format_value(total_awarded, {"fieldtype": "Currency"}), "indicator": "orange"},
        {"label": _("Total Disbursed"), "value": frappe.format_value(total_disbursed, {"fieldtype": "Currency"}), "indicator": "green"},
        {"label": _("Total Balance"), "value": frappe.format_value(total_balance, {"fieldtype": "Currency"}), "indicator": "red" if total_balance > 0 else "gray"}
    ]

def get_chart_data(data, filters):
    # Chart 1: Disbursement vs Awarded by Grant Call
    grant_call_data = {}
    for d in data:
        call_name = d.get("grant_call_name") or "Unknown"
        if call_name not in grant_call_data:
            grant_call_data[call_name] = {
                "awarded": 0,
                "disbursed": 0
            }
        grant_call_data[call_name]["awarded"] += (d.get("amount_awarded") or 0)
        grant_call_data[call_name]["disbursed"] += (d.get("total_disbursed") or 0)
    
    labels = list(grant_call_data.keys())
    awarded_values = [grant_call_data[call]["awarded"] for call in labels]
    disbursed_values = [grant_call_data[call]["disbursed"] for call in labels]
    
    chart1 = {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Amount Awarded"), "values": awarded_values},
                {"name": _("Amount Disbursed"), "values": disbursed_values}
            ]
        },
        "type": "bar",
        "colors": ["#ffa00a", "#5e64ff"]
    }
    
    # Chart 2: Project Status Distribution
    status_counts = {}
    for d in data:
        status = d.get("project_status") or "No Status"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    chart2 = {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{"values": list(status_counts.values())}]
        },
        "type": "pie",
        "colors": ["#ff5858", "#28a745", "#6c757d", "#17a2b8", "#ffc107"]
    }
    
    return chart1
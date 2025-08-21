# Copyright (c) 2025, David and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.contacts.address_and_contact import load_address_and_contact


class Partner(Document):
	"""
	Partner Document Class

	This class represents a partner in the grant management system.
	It inherits from the Document class provided by Frappe framework.
	"""

	def onload(self):
		load_address_and_contact(self)

	def validate(self):
		"""Ensure corresponding User is created/updated/disabled based on is_active flag."""
		if not self.email:
			frappe.throw(_("Email is required for Partner"))

		full_name = f"{self.first_name} {self.last_name}".strip()
		self.full_name = full_name

		# Try to find an existing user with this email
		user = frappe.db.exists("User", {"email": self.email})
		self.user = user if user else None

		if self.is_active:
			if not user:
				# Create new user
				user_doc = frappe.get_doc({
					"doctype": "User",
					"email": self.email,
					"first_name": self.first_name,
					"last_name": self.last_name,
					"full_name": full_name,
					"enabled": 1
				})
				user_doc.insert(ignore_permissions=True)
				user = user_doc.name
				self.user = user
			else:
				# Update existing user
				user_doc = frappe.get_doc("User", user)
				user_doc.first_name = self.first_name
				user_doc.last_name = self.last_name
				user_doc.full_name = full_name
				user_doc.enabled = 1
				user_doc.save(ignore_permissions=True)

			# Ensure Partner role exists
			if not frappe.db.exists("Role", "Partner"):
				frappe.get_doc({"doctype": "Role", "role_name": "Partner"}).insert(ignore_permissions=True)

			# Assign role if not already assigned
			if not frappe.db.exists("Has Role", {"parent": user, "role": "Partner"}):
				frappe.get_doc({
					"doctype": "Has Role",
					"parent": user,
					"parenttype": "User",
					"parentfield": "roles",
					"role": "Partner"
				}).insert(ignore_permissions=True)

		else:
			# Disable user if exists
			if user:
				user_doc = frappe.get_doc("User", user)
				user_doc.enabled = 0
				user_doc.save(ignore_permissions=True)

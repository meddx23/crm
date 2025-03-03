# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CRMDeal(Document):
	def validate(self):
		self.set_primary_contact()
		self.set_primary_email_mobile_no()

	def set_primary_contact(self, contact=None):
		if not self.contacts:
			return

		if not contact and len(self.contacts) == 1:
			self.contacts[0].is_primary = 1
		elif contact:
			for d in self.contacts:
				if d.contact == contact:
					d.is_primary = 1
				else:
					d.is_primary = 0

	def set_primary_email_mobile_no(self):
		if not self.contacts:
			self.email = ""
			self.mobile_no = ""
			return

		if len([contact for contact in self.contacts if contact.is_primary]) > 1:
			frappe.throw(_("Only one {0} can be set as primary.").format(frappe.bold("Contact")))

		primary_contact_exists = False
		for d in self.contacts:
			if d.is_primary == 1:
				primary_contact_exists = True
				self.email = d.email.strip()
				self.mobile_no = d.mobile_no.strip()
				break

		if not primary_contact_exists:
			self.email = ""
			self.mobile_no = ""

	@staticmethod
	def sort_options():
		return [
			{ "label": 'Created', "value": 'creation' },
			{ "label": 'Modified', "value": 'modified' },
			{ "label": 'Status', "value": 'status' },
			{ "label": 'Deal owner', "value": 'deal_owner' },
			{ "label": 'Organization', "value": 'organization' },
			{ "label": 'Email', "value": 'email' },
			{ "label": 'Mobile no', "value": 'mobile_no' },
		]

	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'Organization',
				'type': 'Link',
				'key': 'organization',
				'options': 'CRM Organization',
				'width': '11rem',
			},
			{
				'label': 'Amount',
				'type': 'Currency',
				'key': 'annual_revenue',
				'width': '9rem',
			},
			{
				'label': 'Status',
				'type': 'Select',
				'key': 'status',
				'width': '10rem',
			},
			{
				'label': 'Email',
				'type': 'Data',
				'key': 'email',
				'width': '12rem',
			},
			{
				'label': 'Mobile No',
				'type': 'Data',
				'key': 'mobile_no',
				'width': '11rem',
			},
			{
				'label': 'Deal Owner',
				'type': 'Link',
				'key': 'deal_owner',
				'options': 'User',
				'width': '10rem',
			},
			{
				'label': 'Last Modified',
				'type': 'Datetime',
				'key': 'modified',
				'width': '8rem',
			},
		]
		rows = [
			"name",
			"organization",
			"annual_revenue",
			"status",
			"email",
			"mobile_no",
			"deal_owner",
			"modified",
		]
		return {'columns': columns, 'rows': rows}

@frappe.whitelist()
def add_contact(deal, contact):
	if not frappe.has_permission("CRM Deal", "write", deal):
		frappe.throw(_("Not allowed to add contact to Deal"), frappe.PermissionError)

	deal = frappe.get_cached_doc("CRM Deal", deal)
	deal.append("contacts", {"contact": contact})
	deal.save()
	return True

@frappe.whitelist()
def remove_contact(deal, contact):
	if not frappe.has_permission("CRM Deal", "write", deal):
		frappe.throw(_("Not allowed to remove contact from Deal"), frappe.PermissionError)

	deal = frappe.get_cached_doc("CRM Deal", deal)
	deal.contacts = [d for d in deal.contacts if d.contact != contact]
	deal.save()
	return True

@frappe.whitelist()
def set_primary_contact(deal, contact):
	if not frappe.has_permission("CRM Deal", "write", deal):
		frappe.throw(_("Not allowed to set primary contact for Deal"), frappe.PermissionError)

	deal = frappe.get_cached_doc("CRM Deal", deal)
	deal.set_primary_contact(contact)
	deal.save()
	return True
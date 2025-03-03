import json

import frappe
from frappe import _
from frappe.desk.form.load import get_docinfo

@frappe.whitelist()
def get_activities(name):
	if frappe.db.exists("CRM Deal", name):
		return get_deal_activities(name)
	elif frappe.db.exists("CRM Lead", name):
		return get_lead_activities(name)
	else:
		frappe.throw(_("Document not found"), frappe.DoesNotExistError)

def get_deal_activities(name):
	get_docinfo('', "CRM Deal", name)
	docinfo = frappe.response["docinfo"]
	deal_meta = frappe.get_meta("CRM Deal")
	deal_fields = {field.fieldname: {"label": field.label, "options": field.options} for field in deal_meta.fields}

	doc = frappe.db.get_values("CRM Deal", name, ["creation", "owner", "lead"])[0]
	lead = doc[2]

	activities = []
	creation_text = "created this deal"

	if lead:
		activities = get_lead_activities(lead)
		creation_text = "converted the lead to this deal"

	activities.append({
		"activity_type": "creation",
		"creation": doc[0],
		"owner": doc[1],
		"data": creation_text,
		"is_lead": False,
	})

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		if change := data.get("changed")[0]:
			field = deal_fields.get(change[0], None)

			if not field or change[0] == "lead" or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_lead": False,
			"options": field_option,
		}
		activities.append(activity)

	for communication in docinfo.communications:
		activity = {
			"activity_type": "communication",
			"creation": communication.creation,
			"data": {
				"subject": communication.subject,
				"content": communication.content,
				"sender_full_name": communication.sender_full_name,
				"sender": communication.sender,
				"recipients": communication.recipients,
				"cc": communication.cc,
				"bcc": communication.bcc,
				"read_by_recipient": communication.read_by_recipient,
			},
			"is_lead": False,
		}
		activities.append(activity)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = handle_multiple_versions(activities)

	return activities

def get_lead_activities(name):
	get_docinfo('', "CRM Lead", name)
	docinfo = frappe.response["docinfo"]
	lead_meta = frappe.get_meta("CRM Lead")
	lead_fields = {field.fieldname: {"label": field.label, "options": field.options} for field in lead_meta.fields}

	doc = frappe.db.get_values("CRM Lead", name, ["creation", "owner"])[0]
	activities = [{
		"activity_type": "creation",
		"creation": doc[0],
		"owner": doc[1],
		"data": "created this lead",
		"is_lead": True,
	}]

	docinfo.versions.reverse()

	for version in docinfo.versions:
		data = json.loads(version.data)
		if not data.get("changed"):
			continue

		if change := data.get("changed")[0]:
			field = lead_fields.get(change[0], None)

			if not field or change[0] == "converted" or (not change[1] and not change[2]):
				continue

			field_label = field.get("label") or change[0]
			field_option = field.get("options") or None

			activity_type = "changed"
			data = {
				"field": change[0],
				"field_label": field_label,
				"old_value": change[1],
				"value": change[2],
			}

			if not change[1] and change[2]:
				activity_type = "added"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[2],
				}
			elif change[1] and not change[2]:
				activity_type = "removed"
				data = {
					"field": change[0],
					"field_label": field_label,
					"value": change[1],
				}

		activity = {
			"activity_type": activity_type,
			"creation": version.creation,
			"owner": version.owner,
			"data": data,
			"is_lead": True,
			"options": field_option,
		}
		activities.append(activity)

	for communication in docinfo.communications:
		activity = {
			"activity_type": "communication",
			"creation": communication.creation,
			"data": {
				"subject": communication.subject,
				"content": communication.content,
				"sender_full_name": communication.sender_full_name,
				"sender": communication.sender,
				"recipients": communication.recipients,
				"cc": communication.cc,
				"bcc": communication.bcc,
				"read_by_recipient": communication.read_by_recipient,
			},
			"is_lead": True,
		}
		activities.append(activity)

	activities.sort(key=lambda x: x["creation"], reverse=True)
	activities = handle_multiple_versions(activities)

	return activities

def handle_multiple_versions(versions):
	activities = []
	grouped_versions = []
	old_version = None
	for version in versions:
		is_version = version["activity_type"] in ["changed", "added", "removed"]
		if not is_version:
			activities.append(version)
		if not old_version:
			old_version = version
			if is_version: grouped_versions.append(version)
			continue
		if is_version and old_version.get("owner") and version["owner"] == old_version["owner"]:
			grouped_versions.append(version)
		else:
			if grouped_versions:
				activities.append(parse_grouped_versions(grouped_versions))
			grouped_versions = []
			if is_version: grouped_versions.append(version)
		old_version = version
		if version == versions[-1] and grouped_versions:
			activities.append(parse_grouped_versions(grouped_versions))

	return activities

def parse_grouped_versions(versions):
	version = versions[0]
	if len(versions) == 1:
		return version
	other_versions = versions[1:]
	version["other_versions"] = other_versions
	return version
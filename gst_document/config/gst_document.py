from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"items": [
				{
					"type": "doctype",
					"name": "GST Summary",
					"description":_("GST Summary"),
					"onboard": 1,
				},
				
			]
		},
		
		{
			"label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "GST Accounts Setting",
					"description":_("GST Accounts Setting"),
					"onboard": 1,
				},
				
			]
		}
	]
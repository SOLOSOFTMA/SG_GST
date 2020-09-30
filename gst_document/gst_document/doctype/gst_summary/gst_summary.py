# -*- coding: utf-8 -*-
# Copyright (c) 2020, PT DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GSTSummary(Document):
	def validate(self):

		if not self.from_date and not self.to_date :
			frappe.throw("Please select From Date and First Date first before click button Get Data")
		count = frappe.db.sql("select count(1) from `tabGST Summary` where docstatus<2",as_list=1)
		if count and count[0][0]>5:
			frappe.throw("This Module is on Trial Mode and no longer can be used")
		if self.is_get_data != 1 :
			frappe.throw("You need to Get Data first before save this document")
		self.total_value_1_2_3_taxable_amount = self.gst_standard_rated_supplies_taxable_amount + self.gst_zero_rated_supplies_taxable_amount + self.gst_exempted_rated_supplies_taxable_amount
		self.total_value_1_2_3_gst_amount = self.gst_standard_rated_supplies_gst_amount + self.gst_zero_rated_supplies_gst_amount + self.gst_exempted_rated_supplies_gst_amount


		self.output_tax = self.total_value_1_2_3_gst_amount - self.gst_standard_rated_purchases_gst_amount
		self.paid_by_or_claimed_by = self.output_tax - self.input_tax_refund_claimed


	def get_data(self):
		if not self.from_date and not self.to_date :
			frappe.throw("Please select From Date and First Date first before click button Get Data")

		self.is_get_data = 1

		coa_sales = ""
		coa_purchase = ""
		get_setting = frappe.get_single("GST Accounts Setting")
		if get_setting.gst_account_sales :
			coa_sales = get_setting.gst_account_sales

		if get_setting.gst_account_purchase :
			coa_purchase = get_setting.gst_account_purchase

		get_sales_standard_rate = ""
		get_sales_zero_rate = ""
		get_sales_exempted = ""

		get_purchase_standard_rate = ""
		get_purchase_zero_rate = ""

		sales_standard_rate_taxable = 0
		sales_zero_rate_taxable = 0
		sales_exempted_taxable = 0

		sales_standard_rate_gst_amount = 0
		sales_zero_rate_gst_amount = 0
		sales_exempted_gst_amount = 0

		purchase_standard_rate_taxable = 0
		purchase_zero_taxable = 0

		purchase_standard_rate_gst_amount = 0
		purchase_zero_gst_amount = 0

		output_tax_due = 0
		input_tax_refund_claim = 0
		net_gst = 0

		get_sales_standard_rate = frappe.db.sql("""

			SELECT sinv.`name`, sinv.`posting_date`, SUM(sinvi.`net_amount`), stt.`account_head`, stt.`rate` 
			FROM `tabSales Invoice` sinv
			LEFT JOIN `tabSales Invoice Item` sinvi ON sinv.`name` = sinvi.`parent`
			LEFT JOIN `tabSales Taxes and Charges` stt ON sinv.`name` = stt.`parent`

			WHERE sinv.`docstatus` = 1
			AND stt.`account_head` = "{}"
			AND sinv.`posting_date` BETWEEN "{}" AND "{}"

			GROUP BY sinv.`name`

		""".format(coa_sales, self.from_date, self.to_date))

		if get_sales_standard_rate :
			for i in get_sales_standard_rate :
				sales_standard_rate_taxable += i[2]
				sales_standard_rate_gst_amount += ( (i[2] * i[4]) / 100 )


		get_sales_zero_rate = frappe.db.sql("""

			SELECT sinv.`name`, sinv.`posting_date`, SUM(sinvi.`net_amount`), stt.`account_head`, stt.`rate` 
			FROM `tabSales Invoice` sinv
			LEFT JOIN `tabSales Invoice Item` sinvi ON sinv.`name` = sinvi.`parent`
			LEFT JOIN `tabSales Taxes and Charges` stt ON sinv.`name` = stt.`parent`

			WHERE sinv.`docstatus` = 1
			AND stt.`account_head` = "{}"
			AND stt.`rate` = 0
			AND sinv.`posting_date` BETWEEN "{}" AND "{}"

			GROUP BY sinv.`name`

		""".format(coa_sales, self.from_date, self.to_date))

		if get_sales_zero_rate :
			for i in get_sales_zero_rate :
				sales_zero_rate_taxable += i[2]
				


		get_sales_exempted = frappe.db.sql("""

			SELECT sinv.`name`, sinv.`posting_date`, SUM(sinvi.`net_amount`), stt.`account_head`, stt.`rate` 
			FROM `tabSales Invoice` sinv
			LEFT JOIN `tabSales Invoice Item` sinvi ON sinv.`name` = sinvi.`parent`
			LEFT JOIN `tabSales Taxes and Charges` stt ON sinv.`name` = stt.`parent`

			WHERE sinv.`docstatus` = 1
			AND (stt.`account_head` != "{}" OR stt.`account_head` IS NULL)
			AND sinv.`posting_date` BETWEEN "{}" AND "{}"

			GROUP BY sinv.`name`

		""".format(coa_sales, self.from_date, self.to_date))

		if get_sales_exempted :
			for i in get_sales_exempted :
				sales_exempted_taxable += i[2]



		get_purchase_standard_rate = frappe.db.sql("""

			SELECT pinv.`name`, pinv.`posting_date`, SUM(pinvi.`net_amount`), ptt.`account_head`, ptt.`rate` 
			FROM `tabPurchase Invoice` pinv
			LEFT JOIN `tabPurchase Invoice Item` pinvi ON pinv.`name` = pinvi.`parent`
			LEFT JOIN `tabPurchase Taxes and Charges` ptt ON pinv.`name` = ptt.`parent`

			WHERE pinv.`docstatus` = 1
			AND ptt.`account_head` = "{}"
			AND pinv.`posting_date` BETWEEN "{}" AND "{}"

			GROUP BY pinv.`name`

		""".format(coa_sales, self.from_date, self.to_date))

		if get_purchase_standard_rate :
			for i in get_purchase_standard_rate :
				purchase_standard_rate_taxable += i[2]
				purchase_standard_rate_gst_amount += ( (i[2] * i[4]) / 100 )


		get_purchase_zero_rate = frappe.db.sql("""

			SELECT pinv.`name`, pinv.`posting_date`, SUM(pinvi.`net_amount`), ptt.`account_head`, ptt.`rate` 
			FROM `tabPurchase Invoice` pinv
			LEFT JOIN `tabPurchase Invoice Item` pinvi ON pinv.`name` = pinvi.`parent`
			LEFT JOIN `tabPurchase Taxes and Charges` ptt ON pinv.`name` = ptt.`parent`

			WHERE pinv.`docstatus` = 1
			AND ptt.`account_head` = "{}"
			AND ptt.`rate` = 0
			AND pinv.`posting_date` BETWEEN "{}" AND "{}"

			GROUP BY pinv.`name`

		""".format(coa_sales, self.from_date, self.to_date))

		if get_purchase_zero_rate :
			for i in get_purchase_zero_rate :
				purchase_zero_rate_taxable += i[2]
				

		self.gst_standard_rated_supplies_taxable_amount = sales_standard_rate_taxable
		self.gst_zero_rated_supplies_taxable_amount = sales_zero_rate_taxable
		self.gst_exempted_rated_supplies_taxable_amount = sales_exempted_taxable
		self.total_value_1_2_3_taxable_amount = sales_standard_rate_taxable + sales_zero_rate_taxable + sales_exempted_taxable

		self.gst_standard_rated_supplies_gst_amount = sales_standard_rate_gst_amount
		self.gst_zero_rated_supplies_gst_amount = sales_zero_rate_gst_amount
		self.gst_exempted_rated_supplies_gst_amount = sales_exempted_gst_amount
		self.total_value_1_2_3_gst_amount = sales_standard_rate_gst_amount + sales_zero_rate_gst_amount + sales_exempted_gst_amount


		self.gst_standard_rated_purchases_taxable_amount = purchase_standard_rate_taxable
		self.gst_zero_rated_purchases_taxable_amount = purchase_zero_taxable

		self.gst_standard_rated_purchases_gst_amount = purchase_standard_rate_gst_amount
		self.gst_zero_rated_purchases_gst_amount = purchase_zero_gst_amount


		self.output_tax = self.total_value_1_2_3_gst_amount - self.gst_standard_rated_purchases_gst_amount
		self.input_tax_refund_claimed = 0
		self.paid_by_or_claimed_by = self.output_tax - self.input_tax_refund_claimed

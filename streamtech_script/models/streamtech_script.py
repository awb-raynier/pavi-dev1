from datetime import datetime
from odoo import api, fields, models, exceptions, _
from odoo.tools.misc import xlwt
from simple_salesforce import Salesforce
from simple_salesforce import format_soql
import logging
import io
import base64


_logger = logging.getLogger(__name__)


class StreamtechScript(models.Model):
    _name = "streamtech.scripts"
    _description = "Streamtech Data Migration Scripts"

    def connect_to_salesforce(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param(
                'odoo_salesforce.sf_username'
            )
            password = IrConfigParameter.get_param(
                'odoo_salesforce.sf_password'
            )
            security = IrConfigParameter.get_param(
                'odoo_salesforce.sf_security_token'
            )
            self.sales_force = Salesforce(
                username=username,
                password=password,
                security_token=security
            )
            return self.sales_force
        except Exception as e:
            Warning(_(str(e)))

    def _sync_product_sfid(self):
        _logger.info(" --- Product SF ID sync starting --- ")
        sf = self.connect_to_salesforce()

        products = self.env['product.template'].search([
            ("salesforce_id", "=", False),
        ], limit=5000)
        product_names = products.mapped("name")

        records = []
        step = 500

        for i in range(0, len(product_names), step):

            product_batch = product_names[i:i + step]
            query = format_soql(
                """
                    SELECT
                    Id,
                    Name
                    FROM Product2 as product
                    WHERE product.Id != null
                    AND product.Name IN {products}
                """, products=product_batch
            )

            results = sf.query(query)
            _logger.info(" --- Records Pulled: %s --- " % results['totalSize'])

            for record in results['records']:
                row_data = []
                record = dict(record)
                record.pop("attributes")
                sf_id = record.get("Id")
                product_name = record.get("Name")
                odoo_rec = products.filtered_domain([
                    ("name", "=ilike", product_name)
                ])[0]

                if odoo_rec:
                    row_data.append(odoo_rec.id)
                    odoo_rec.write({"salesforce_id": sf_id})
                else:
                    row_data.append("None")
                row_data = row_data + list(record.values())
                records.append(row_data)

        _logger.info(" --- Product SF ID sync execution done --- ")

        if records:
            headers = ["Odoo ID"]
            raw_headers = dict(results['records'][0])
            raw_headers.pop("attributes")
            headers = headers + list(raw_headers.keys())

            filename = "Sync_Product_SFID(%s).xlsx" % datetime.today().strftime(
                '%Y-%m-%d %H:%M:%S'
            )

            self._print_result(
                records=records,
                headers=headers,
                filename=filename,
                sheet="Product Sync SFID"
            )

    def _sync_account_sfid(self):
        _logger.info(" --- Account SF ID sync starting --- ")
        sf = self.connect_to_salesforce()

        odoo_records = self.env['res.partner'].search([
            ("salesforce_id", "=", False),
            ("customer_number", "!=", False),
        ], limit=5000)
        cnumbers = odoo_records.mapped("customer_number")

        records = []
        step = 500

        for i in range(0, len(cnumbers), step):

            cnumbers_batch = cnumbers[i:i + step]
            query = format_soql(
                """
                    SELECT
                    Id,
                    Name,
                    FirstName,
                    MiddleName,
                    LastName,
                    Billing_Customer_ID__c
                    FROM Account as rec
                    WHERE rec.Id != null
                    AND rec.Billing_Customer_ID__c IN {cnumbers}
                """, cnumbers=cnumbers_batch
            )

            results = sf.query(query)
            _logger.info(" --- Records Pulled: %s --- " % results['totalSize'])

            for record in results['records']:
                row_data = []
                record = dict(record)
                record.pop("attributes")
                sf_id = record.get("Id")
                sf_cust_number = record.get("Billing_Customer_ID__c")
                odoo_rec = odoo_records.filtered_domain([
                    ("customer_number", "=", sf_cust_number)
                ])[0]

                if odoo_rec:
                    row_data.append(odoo_rec.id)
                    odoo_rec.write({"salesforce_id": sf_id})
                else:
                    row_data.append("None")
                row_data = row_data + list(record.values())
                records.append(row_data)

        _logger.info(" --- Account SF ID sync execution done --- ")

        if records:
            headers = ["Odoo ID"]
            raw_headers = dict(results['records'][0])
            raw_headers.pop("attributes")
            headers = headers + list(raw_headers.keys())

            filename = "Sync_Account_SFID(%s).xlsx" % datetime.today().strftime(
                '%Y-%m-%d %H:%M:%S'
            )

            self._print_result(
                records=records,
                headers=headers,
                filename=filename,
                sheet="Account Sync SFID"
            )

    def _sync_opportunity_sfid(self):
        _logger.info(" --- Opportunity SF ID sync starting --- ")
        sf = self.connect_to_salesforce()

        odoo_records = self.env['crm.lead'].search([
            ("salesforce_id", "=", False),
            ("customer_number", "!=", False),
        ], limit=5000)
        cnumbers = odoo_records.mapped("customer_number")

        records = []
        step = 500

        for i in range(0, len(cnumbers), step):

            cnumbers_batch = cnumbers[i:i + step]
            query = format_soql(
                """
                    SELECT
                    Id,
                    Name,
                    Account.Billing_Customer_ID__c
                    FROM opportunity as opp
                    WHERE opp.Id != null
                    AND opp.AccountId != null
                    AND Account.Billing_Customer_ID__c IN {cnumbers}
                """, cnumbers=cnumbers_batch
            )

            results = sf.query(query)
            _logger.info(" --- Records Pulled: %s --- " % results['totalSize'])

            for record in results['records']:
                row_data = []
                record = dict(record)
                record.pop("attributes")
                sf_id = record.get("Id")
                sf_cust_number = record.get("Account").get("Billing_Customer_ID__c")
                odoo_rec = odoo_records.filtered_domain([
                    ("customer_number", "=", sf_cust_number)
                ])[0]

                if odoo_rec:
                    row_data.append(odoo_rec.id)
                    odoo_rec.write({"salesforce_id": sf_id})
                else:
                    row_data.append("None")
                row_data = row_data + list(record.values())
                records.append(row_data)

        _logger.info(" --- Opportunity SF ID sync execution done --- ")

        if records:
            headers = ["Odoo ID"]
            raw_headers = dict(results['records'][0])
            raw_headers.pop("attributes")
            headers = headers + list(raw_headers.keys())

            filename = "Sync_Opportunity_SFID(%s).xlsx" % datetime.today().strftime(
                '%Y-%m-%d %H:%M:%S'
            )

            self._print_result(
                records=records,
                headers=headers,
                filename=filename,
                sheet="Opportunity Sync SFID"
            )

    def _print_result(
        self,
        records=None,
        headers=None,
        filename=None,
        sheet=None
    ):
        _logger.info(" --- Creating XLS File Report --- ")
        stream = io.BytesIO()
        workbook = xlwt.Workbook()
        Header_style = xlwt.easyxf('font: bold on; align: horiz centre;')
        sheet = workbook.add_sheet(sheet)

        y = 0
        for x, header in enumerate(headers):
            sheet.write(y, x, header, Header_style)

        for record in records:
            y += 1
            for x, item in enumerate(record):
                sheet.write(y, x, item)

        workbook.save(stream)

        self.env['streamtech.data.report'].create(
            {
                'name': filename,
                'excel_file': base64.encodebytes(stream.getvalue()),
                'file_name': filename
            }
        )
        stream.close()
        _logger.info(" --- Done XLS File Report Creation --- ")


class ScriptResult(models.Model):
    _name = "streamtech.data.report"
    _description = "Excel Sample Report"
    _order = "create_date desc"

    name = fields.Char('Name')
    excel_file = fields.Binary('XLSX File')
    file_name = fields.Char('Filename')

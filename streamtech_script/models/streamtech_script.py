from datetime import datetime
from odoo import api, fields, models, exceptions, _
from odoo.tools.misc import xlwt
from simple_salesforce import Salesforce
from simple_salesforce import format_soql
import json
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
            _logger.info(" --- SF Login Failed --- ")
            Warning(_(str(e)))

    def _sync_product_sfid(self, odoo_records=None):
        if not odoo_records:
            raise exceptions.UserError("Odoo Records are required")

        sf = self.connect_to_salesforce()
        _logger.info(" --- Product SF ID sync starting --- ")

        product_names = odoo_records.mapped("name")

        records = []
        step = 250

        for i in range(0, len(product_names), step):

            product_batch = product_names[i:i + step]
            query = format_soql(
                """
                    SELECT
                    Id,
                    Name,
                    ProductCode,
                    IsActive,
                    Family,
                    Type__c,
                    Facility_Type__c,
                    CreatedDate,
                    LastModifiedDate
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
                odoo_rec = odoo_records.filtered_domain([
                    ("name", "=ilike", product_name)
                ])

                if odoo_rec:
                    odoo_rec = odoo_rec[0]
                    odoo_rec.write({"salesforce_id": sf_id})

                    # Data Report Creation
                    row_data.append(odoo_rec.id)
                    row_data.append(odoo_rec.salesforce_id)
                    row_data.append(odoo_rec.default_code)
                    row_data.append(odoo_rec.recurring_invoice)
                    row_data.append(odoo_rec.subscription_template_id.display_name)
                    row_data.append(odoo_rec.active)
                    row_data.append(odoo_rec.categ_id.display_name)
                else:
                    row_data.append("None")
                row_data = row_data + list(record.values())
                records.append(row_data)

        _logger.info(" --- Product SF ID sync execution done --- ")

        if records:
            headers = [
                "ID (Odoo)", "Salesforce ID (Odoo)", "Product Code (Odoo)",
                "Subscription Product (Odoo)", "Subscription Template (Odoo)",
                "Active (Odoo)", "Product Category (Odoo)",
            ]
            raw_headers = record.keys()
            headers = headers + list(raw_headers)

            filename = "Sync_Product_SFID(%s).xlsx" % datetime.today().strftime(
                '%Y-%m-%d %H:%M:%S'
            )

            self._print_result(
                records=records,
                headers=headers,
                filename=filename,
                sheet="Product Sync SFID"
            )

    def _sync_account_sfid(self, odoo_records=None):
        if not odoo_records:
            raise exceptions.UserError("Odoo Records are required")

        sf = self.connect_to_salesforce()
        _logger.info(" --- Account SF ID sync starting --- ")

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
                    Billing_Customer_ID__c,
                    ATM_Ref__c,
                    PersonEmail,
                    PersonMobilePhone,
                    CreatedDate,
                    LastModifiedDate
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
                ])

                if odoo_rec:
                    odoo_rec = odoo_rec[0]
                    odoo_rec.write({"salesforce_id": sf_id})

                    row_data.append(odoo_rec.id)
                    row_data.append(odoo_rec.salesforce_id)
                    row_data.append(odoo_rec.display_name)
                    row_data.append(odoo_rec.customer_number)
                    row_data.append(odoo_rec.email)
                    row_data.append(odoo_rec.mobile)
                    row_data.append(odoo_rec.subscriber_location_id.display_name)
                else:
                    row_data.append("None")
                row_data = row_data + list(record.values())
                records.append(row_data)

        _logger.info(" --- Account SF ID sync execution done --- ")

        if records:
            headers = [
                "ID (Odoo)", "Salesforce ID (Odoo)",
                "Name (Odoo)", "Customer ID (Odoo)",
                "Email (Odoo)", "Mobile (Odoo)",
                "Location (Odoo)",
            ]
            raw_headers = record.keys()
            headers = headers + list(raw_headers)

            filename = "Sync_Account_SFID(%s).xlsx" % datetime.today().strftime(
                '%Y-%m-%d %H:%M:%S'
            )

            self._print_result(
                records=records,
                headers=headers,
                filename=filename,
                sheet="Account Sync SFID"
            )

    def _sync_opportunity_sfid(self, odoo_records=None):
        if not odoo_records:
            raise exceptions.UserError("Odoo Records are required")

        sf = self.connect_to_salesforce()
        _logger.info(" --- Opportunity SF ID sync starting --- ")

        cnumbers = odoo_records.mapped("customer_number")

        records = []
        step = 500

        for i in range(0, len(cnumbers), step):

            cnumbers_batch = cnumbers[i:i + step]
            query = format_soql(
                """
                    SELECT
                    Id,
                    Opportunity_Number__c,
                    Type,
                    Name,
                    Area_ODOO__c,
                    StageName,
                    Sub_Stages__c,
                    Account.Billing_Customer_ID__c,
                    CreatedDate,
                    LastModifiedDate
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
                record["Account"].pop("attributes")
                record = json.loads(json.dumps(record))  # To remove the OrderedDict
                sf_id = record.get("Id")
                sf_cust_number = record.get("Account").get("Billing_Customer_ID__c")
                odoo_rec = odoo_records.filtered_domain([
                    ("customer_number", "=", sf_cust_number)
                ])

                if odoo_rec:
                    odoo_rec = odoo_rec[0]
                    odoo_rec.write({"salesforce_id": sf_id})

                    row_data.append(odoo_rec.id)
                    row_data.append(odoo_rec.salesforce_id)
                    row_data.append(odoo_rec.opportunity_number)
                    row_data.append(odoo_rec.sf_type)
                    row_data.append(odoo_rec.display_name)
                    row_data.append(odoo_rec.zone.display_name)
                    row_data.append(odoo_rec.stage_id.display_name)
                    row_data.append(odoo_rec.job_order_status)
                    row_data.append(odoo_rec.customer_number)

                else:
                    row_data.append("None")
                row_data = row_data + list(record.values())
                records.append(row_data)

        _logger.info(" --- Opportunity SF ID sync execution done --- ")

        if records:
            headers = [
                "ID (Odoo)", "Salesforce ID (Odoo)",
                "SF Opportunity Number (Odoo)",
                "Type (Odoo)", "Name (Odoo)",
                "Zone (Odoo)", "Stage (Odoo)",
                "Job Order Status (Odoo)", "Customer ID (Odoo)",
            ]
            raw_headers = record.keys()
            headers = headers + list(raw_headers)

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
                if isinstance(item, dict):
                    item = list(item.values())[0]
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

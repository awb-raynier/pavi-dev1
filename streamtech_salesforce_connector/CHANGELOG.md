# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [13.0.1.1.1] - 2021-08-09
   - [IMP] Added logs and updated warnings for no active products found and pulling of accounts without opportunities
   - [IMP] Added handling for multiple records found in Odoo via salesforce_id
   - [IMP] Enhancement: Remove the SF Connector Condition to limit the pull of Opportunities based on Created Date
   - [IMP] Added handling for already completed opportunity and archived products in Odoo side

## [13.0.1.1.0] - 2021-07-29
   - [IMP] Salesforce Connector Enhancement for Pulling of Products, Accounts and Opportunities

## [13.0.1.0.3] - 2021-03-29
   - Added importing for partner model

## [13.0.1.0.2] - 2021-03-28
   - Changed SF-based CRM form fields to read only: email, phone 

## [13.0.1.0.1] - 2021-03-28
   - Changed additional CRM form fields to read only if values are from SalesForce
   - Changed additional Customer form fields to read only if values are from SalesForce


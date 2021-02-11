# dbt and MSFT -- better together

Below are the three reasons that dbt enhances the Microsoft ecosystem

## 1) dbt fills an existing gap
as a code- and cloud-first tool, dbt instantly fills a current gap b/w:
- the old-school, “code-first”-eqsue SQL Server + Visual Studio “dacpac” database deployments, and
- the new, heavily-marketed, cloud-first, UI-first, code-second Azure Synapse Analytics Workspace (ASAW).

## 2) dbt shines when paired with already-existing MSFT products
The pairing is great because dbt is just a CLI that only requires a Git repo of .sql and .yml.

The products with which dbt pairs so well:
- VSCode (so many great extensions already)
- Azure Data Studio (if only we can get Python extension support)
- Azure DevOps Pipelines
- GitHub Actions (which is the direction MSFT is headed anyway)

## 3) dbt isn’t a compete to ASAW, but rather a developer-productivity tool
For me, dbt is a dev-div tool for data engineers (like TypeScript is for web devs). It makes DE's lives easier.

dbt’s value prop is about enabling data analysts to have tools traditionally only available to SWEs. This plays into MSFT’s hand as they’ve enabled millions with Power BI. With a framework like dbt adoption of both dev-div tools and Azure data products, without rolling a completely new pipeline and version control framework as is the case with Power BI.

## 4) easier to maintain parity with competitors.
Currently, Azure is losing customers to Snowflake and Databricks that arguably might stay if they had a tool like dbt. Using jinja, new functionality can be added by the community without taking the product team's bandwidth.
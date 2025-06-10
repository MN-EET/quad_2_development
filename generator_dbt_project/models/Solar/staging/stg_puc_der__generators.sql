/*
    Select generator information from RAW PUC DER file.
*/

SELECT
	utility,
	mn_utility_id,
	eia_id,
	utility_type,
	der_capacity_kw_ac AS nameplate_kw,
	der_type AS generation_type,
	der_status,
	customer_type,
	year_interconnected,
	created_at,
	report_year

FROM main.raw_puc_der rpd

WHERE created_at = (SELECT MAX(created_at) FROM main.raw_puc_der)
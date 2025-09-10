-- Select generator info from raw EIA 860 file.


SELECT
	utility_id,
	utility_name,
	plant_name,
	state,
	plant_code,
	generator_id,
	technology AS generation_type,
	nameplate_capacity_mw_ AS nameplate_mw,
	nameplate_capacity_mw_ * 1000 AS nameplate_kw,
	operating_year,
	sector_name,
	created_at,
	report_year

FROM generators.raw_eia_860_generators reg

WHERE created_at = (SELECT MAX(created_at) FROM main.raw_eia_860_generators)
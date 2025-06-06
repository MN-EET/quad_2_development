-- Select large solar generators from EIA file
SELECT nameplate_kw,
	utility_name AS utility,
	generation_type AS technology,
	operating_year AS year_interconnected

FROM {{ ref('stg_eia__generators') }}

WHERE generation_type = 'Solar Photovoltaic'
	AND nameplate_mw > 10
	AND state = 'MN'
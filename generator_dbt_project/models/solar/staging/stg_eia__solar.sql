-- Select large solar generators from EIA file
SELECT nameplate_kw,
    nameplate_mw,
	utility_name AS utility,
	'Solar' AS technology,
	operating_year AS year_interconnected

FROM {{ ref('stg_eia__generators') }}

WHERE generation_type = 'Solar Photovoltaic'
	AND nameplate_mw > 10
	AND state = 'MN'
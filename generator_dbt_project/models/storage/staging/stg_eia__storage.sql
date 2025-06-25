-- Select large battery installations from EIA file
SELECT nameplate_kw,
    nameplate_mw,
	utility_name AS utility, 
	generation_type AS technology, 
	operating_year AS year_interconnected

FROM {{ ref('stg_eia__generators') }}

WHERE state = 'MN'
	AND generation_type = 'Batteries'
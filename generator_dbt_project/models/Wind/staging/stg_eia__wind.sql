-- Select wind generators from EIA 860
SELECT utility_name AS utility, operating_year, nameplate_mw

FROM {{ ref('stg_eia__generators') }} a

LEFT JOIN {{ ref('dim_generation_type__eia') }} b
    ON a.generation_type = b.generation_type

WHERE
	a.state = 'MN' AND
	b.translation_name = 'Wind'

ORDER BY operating_year
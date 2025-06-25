-- Select puc solar generators
SELECT a.nameplate_kw,
    a.nameplate_mw,
	a.utility,
	b.translation_name AS technology,
	a.year_interconnected,
	a.customer_type

FROM {{ ref('stg_puc_der__generators') }} AS a

LEFT JOIN {{ ref('dim_generator_type__puc') }}  AS b
	ON a.generation_type = b.generation_type

WHERE LOWER(a.der_status) = 'interconnected'
	AND b.translation_name = 'Solar'
	AND (
	    a.year_interconnected <= a.report_year
	    OR a.year_interconnected IS NUll -- keep null values in the year interconnected as it appears these are actually connected
    )

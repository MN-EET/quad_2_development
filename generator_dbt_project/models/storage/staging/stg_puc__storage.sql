-- Select storage installations from PUC file
SELECT nameplate_kw,
	utility,
	generation_type AS technology,
	year_interconnected

FROM {{ ref('stg_puc_der__generators') }}

WHERE LOWER(der_status) = 'interconnected'
	AND LOWER(generation_type) = 'storage'
	AND nameplate_kw < 1000
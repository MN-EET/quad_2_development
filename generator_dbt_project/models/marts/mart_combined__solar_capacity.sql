--Combine EIA and PUC solar capacity
SELECT *, 'Large-Scale' AS customer_type, 'EIA-860' AS data_source
	FROM {{ ref('stg_eia__solar') }}

UNION ALL

SELECT *, 'PUC DER' AS data_source
	FROM {{ ref('stg_puc__solar') }}

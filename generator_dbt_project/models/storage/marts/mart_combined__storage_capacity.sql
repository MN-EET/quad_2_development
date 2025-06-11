SELECT *, 'EIA-860' AS data_source
    FROM {{ ref('stg_eia__storage') }}

UNION ALL

SELECT *, 'PUC DER' AS data_source
    FROM {{ ref('stg_puc__storage') }}
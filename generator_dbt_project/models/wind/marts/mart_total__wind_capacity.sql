-- Pull large scale wind capacity from staging
SELECT *, 'EIA-860' as_data_source

FROM {{ ref('stg_eia__wind') }}
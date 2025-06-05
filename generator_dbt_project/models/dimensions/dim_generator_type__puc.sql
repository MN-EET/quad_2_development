-- Create standard generation type names from PUC
SELECT DISTINCT generation_type,

	CASE
		WHEN generation_type IS NULL THEN 'Unknown'
		WHEN generation_type = 'solar' THEN 'Solar'
		WHEN generation_type = 'Hydro' THEN 'Hydroelectric'
		WHEN generation_type = 'Storage' THEN 'Battery'
		ELSE generation_type
	END AS translation_name

FROM main.stg_puc_der__generators

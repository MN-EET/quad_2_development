-- Create standard generation type names from EIA
SELECT DISTINCT generation_type,

	CASE
		WHEN generation_type = 'Conventional Hydroelectric' THEN 'Hydroelectric'
		WHEN generation_type = 'Conventional Steam Coal' THEN 'Coal'
		WHEN generation_type IN
			('Natural Gas Fired Combined Cycle', 'Natural Gas Fired Combustion Turbine', 'Natural Gas Internal Combustion Engine', 'Natural Gas Steam Turbine') THEN 'Natural Gas'
		WHEN generation_type = 'Onshore Wind Turbine' THEN 'Wind'
		WHEN generation_type = 'Other Waste Biomass' THEN 'Biomass'
		WHEN generation_type = 'Solar Photovoltaic' THEN 'Solar'
		WHEN generation_type = 'Wood/Wood Waste Biomass' THEN 'Biomass'
		WHEN generation_type = 'All Other' THEN 'Other'
		ELSE generation_type
	END AS translation_name

FROM {{ ref('stg_eia__generators') }}
-- Only for MN generators which are the primary concern here
WHERE state = 'MN'


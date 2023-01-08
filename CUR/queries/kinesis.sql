--  This query will provide daily unblended and usage information per linked account for each Kinesis product (Amazon Kinesis, 
--  Amazon Kinesis Firehose, and Amazon Kinesis Analytics). The output will include detailed 
--  information about the resource id (Stream, Delivery Stream, etc…) and API operation. 
--- The cost will be summed and in descending order.

SELECT 
  bill_payer_account_id,
  line_item_usage_account_id,
  DATE_FORMAT((line_item_usage_start_date),'%Y-%m-%d') AS day_line_item_usage_start_date, 
  SPLIT_PART(line_item_resource_id,':',6) AS split_line_item_resource_id,
  product_product_name,
  SUM(CAST(line_item_usage_amount AS DOUBLE)) AS sum_line_item_usage_amount,
  SUM(CAST(line_item_unblended_cost AS DECIMAL(16, 8))) AS sum_line_item_unblended_cost
FROM 
  ${table_Name} 
WHERE 
  ${date_filter} 
  AND product_product_name IN ('Amazon Kinesis','Amazon Kinesis Firehose','Amazon Kinesis Analytics','Amazon Kinesis Video')
  AND line_item_line_item_type  IN ('DiscountedUsage', 'Usage', 'SavingsPlanCoveredUsage')
GROUP BY 
  bill_payer_account_id,
  line_item_usage_account_id,
  DATE_FORMAT((line_item_usage_start_date),'%Y-%m-%d'), 
  line_item_resource_id,
  product_product_name
ORDER BY 
  day_line_item_usage_start_date,
  sum_line_item_unblended_cost DESC;
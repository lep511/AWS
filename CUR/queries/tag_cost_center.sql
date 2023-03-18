SELECT -- automation_select_stmt
  bill_payer_account_id,
  line_item_usage_account_id,
  DATE_FORMAT((line_item_usage_start_date),'%Y-%m-%d') AS day_line_item_usage_start_date, -- automation_timerange_dateformat
  SPLIT_PART(line_item_resource_id,':',6) AS split_line_item_resource_id,
  product_product_name,
  resource_tags_user_name,
  year,
  month,
  day,
  SUM(CAST(line_item_usage_amount AS DOUBLE)) AS sum_line_item_usage_amount,
  SUM(CAST(line_item_unblended_cost AS DECIMAL(16, 8))) AS sum_line_item_unblended_cost
FROM -- automation_from_stmt
  ${table_Name} -- automation_tablename
WHERE -- automation_where_stmt
  ${date_filter} -- automation_timerange_year_month
  AND resource_tags_user_name = '${var1}' -- automation_account_id
GROUP BY -- automation_groupby_stmt
  bill_payer_account_id,
  line_item_usage_account_id,
  DATE_FORMAT((line_item_usage_start_date),'%Y-%m-%d'), -- automation_timerange_dateformat
  resource_tags_user_name,
  line_item_resource_id,
  product_product_name,
  year,
  month,
  day
ORDER BY -- automation_order_stmt
  day_line_item_usage_start_date,
  sum_line_item_unblended_cost DESC
;

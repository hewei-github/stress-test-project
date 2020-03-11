-- 导出数据源sql

SELECT
    `c`.`company_name`,`p`.`address` as `city`,`p`.`position_name` as `job_name`
FROM
`position` AS `p` RIGHT JOIN `company` as `c` ON `c`.`id`=`p`.`company_id`
WHERE
`c`.`status`=1  AND `p`.`is_online` IN(1,2) AND
`p`.`status` = 1 AND `p`.`deleted_at` IS NULL AND
`c`.`deleted_at` IS NULL
GROUP BY
`c`.`company_name`;

-- 1. 查询线上正式数据, 使用导出工具导出为json
-- 2. 将数据json文件中,RECORDS 键 修改为 config/.env 中 DATA_JSON_ROOT 值对应的名,如果 DATA_JSON_ROOT = RECORDS ,则无需修改
-- 3. 将导出结果保存到项目 config目录下,更名为 data.json (替换旧的data.json)
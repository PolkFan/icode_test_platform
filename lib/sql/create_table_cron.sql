CREATE DATABASE IF NOT EXISTS qa_platform;

CREATE TABLE IF NOT EXISTS `api_auto_report_cron` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `scene` varchar(50) DEFAULT NULL COMMENT '场景名称',
  `times` varchar(5) DEFAULT NULL COMMENT '定时任务时间（注意时间格式 07:30）',
  `scenario_id` varchar(50) DEFAULT NULL COMMENT '场景id',
  `env` tinyint(1) DEFAULT NULL COMMENT '环境：1-测试、2-正式',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `status` bit(1) DEFAULT b'1' COMMENT '状态: 0-无效 1-有效',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='cron定时任务计划表';

CREATE TABLE `config_policy`.`config_policy` (

    `policy_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `policy_name` varchar(40) NOT NULL,
    `policy_description` varchar(4096),

    PRIMARY KEY(`policy_id`),
    UNIQUE KEY uq_policy_name (`policy_name`)
);


CREATE TABLE `config_policy`.`config_policy_scheme` (

    `scheme_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `policy_id` int(10) unsigned NOT NULL,

    `scheme_name` varchar(40) NOT NULL,
    `scheme_type` varchar(40) NOT NULL,
    `scheme_description` varchar(4096),

    PRIMARY KEY(`scheme_id`),

    CONSTRAINT `fk_config_policy_scheme_policy`
        FOREIGN KEY (`policy_id`)
        REFERENCES `config_policy`.`config_policy` (`policy_id`)
);


CREATE TABLE `config_policy`.`config_policy_rule` (

    `rule_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `policy_id` int(10) unsigned NOT NULL,

    `eval_expression` varchar(4096),

    PRIMARY KEY(`rule_id`),

    CONSTRAINT `fk_config_policy_rule_policy`
        FOREIGN KEY (`policy_id`)
        REFERENCES `config_policy`.`config_policy` (`policy_id`)
);


GRANT ALL ON `config_policy`.* TO `validator`@`localhost`;

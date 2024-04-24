SELECT `cleaned_output`.`dataFrom`,
    `cleaned_output`.`date`,
    `cleaned_output`.`review`,
    `cleaned_output`.`rating`,
    `cleaned_output`.`extracted_devresp`,
    `cleaned_output`.`devresp_time`
FROM `review`.`cleaned_output`
limit 3;

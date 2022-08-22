SELECT count(*) AS count_1 
FROM message_correlation INNER JOIN message_correlation_property ON message_correlation_property.id = message_correlation.message_correlation_property_id 
WHERE message_correlation.process_instance_id = %(process_instance_id_1)s AND (message_correlation.name = %(name_1)s AND message_correlation.value = %(value_1)s AND message_correlation.message_correlation_property_id = %(message_correlation_property_id_1)s OR message_correlation.name = %(name_2)s AND message_correlation.value = %(value_2)s AND message_correlation.message_correlation_property_id = %(message_correlation_property_id_2)s) AND message_correlation_property.message_model_id = %(message_model_id_1)s

{'process_instance_id_1': 7, 'name_1': 'message_correlation_key', 'value_1': 'first_conversation_a_1661200359.8331513', 'message_correlation_property_id_1': 13, 'name_2': 'message_correlation_key', 'value_2': 'first_conversation_b_1661200359.8331513', 'message_correlation_property_id_2': 14, 'message_model_id_1': 13}

+----+---------------------+------------------+--------------+------------------------------------------------------------------------------------------------------------+---------+---------------+-----------------------+-----------------------+
| id | process_instance_id | message_model_id | message_type | payload                                                                                                    | status  | failure_cause | updated_at_in_seconds | created_at_in_seconds |
+----+---------------------+------------------+--------------+------------------------------------------------------------------------------------------------------------+---------+---------------+-----------------------+-----------------------+
| 13 |                   7 |               13 | send         | {"topica": "first_conversation_a_1661200359.8331513", "topicb": "first_conversation_b_1661200359.8331513"} | running | NULL          |            1661200360 |            1661200360 |
| 14 |                   7 |               14 | receive      | NULL                                                                                                       | ready   | NULL          |            1661200360 |            1661200360 |
+----+---------------------+------------------+--------------+------------------------------------------------------------------------------------------------------------+---------+---------------+-----------------------+-----------------------+
+----+---------------------+---------------------------------+-------------------------+-----------------------------------------+-----------------------+-----------------------+
| id | process_instance_id | message_correlation_property_id | name                    | value                                   | updated_at_in_seconds | created_at_in_seconds |
+----+---------------------+---------------------------------+-------------------------+-----------------------------------------+-----------------------+-----------------------+
| 13 |                   7 |                              13 | message_correlation_key | first_conversation_a_1661200359.8331513 |            1661200360 |            1661200360 |
| 14 |                   7 |                              14 | message_correlation_key | first_conversation_b_1661200359.8331513 |            1661200360 |            1661200360 |
+----+---------------------+---------------------------------+-------------------------+-----------------------------------------+-----------------------+-----------------------+
+----+-------------------------------------+------------------+-----------------------+-----------------------+
| id | identifier                          | message_model_id | updated_at_in_seconds | created_at_in_seconds |
+----+-------------------------------------+------------------+-----------------------+-----------------------+
| 13 | message_correlation_property_topica |               13 |            1661200360 |            1661200360 |
| 14 | message_correlation_property_topicb |               13 |            1661200360 |            1661200360 |
+----+-------------------------------------+------------------+-----------------------+-----------------------+
+----+---------------------+------------------------+
| id | message_instance_id | message_correlation_id |
+----+---------------------+------------------------+
| 25 |                  13 |                     13 |
| 26 |                  13 |                     14 |
| 27 |                  14 |                     13 |
| 28 |                  14 |                     14 |
+----+---------------------+------------------------+
+----+--------------------------+--------------------------+---------+
| id | process_model_identifier | process_group_identifier | status  |
+----+--------------------------+--------------------------+---------+
|  7 | message_sender           | test_process_group_id    | waiting |


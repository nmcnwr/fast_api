with temp_table
as
(
     select TRPL_ID trpl_id from subs_list_view where msisdn='{msisdn}'
)

SELECT T1.SCENARIO_ID scenario_id
FROM PRODUCT_SCENARIO_RESTRICTION T1, TARIFF_PLAN T2, SERVICE T3 , PRODUCT_SCENARIO T4 , PRODUCT_FAMILY T5, BRANCH T6
WHERE
      200=200
      AND T1.TRPL_ID=T2.TRPL_ID
      AND T1.SERV_ID=T3.SERV_ID
      AND T1.SCENARIO_ID=T4.SCENARIO_ID
      AND T1.BRANCH_ID=T6.BRANCH_ID
      AND T4.PF_ID=T5.PF_ID
      AND T4.PF_ID=5
      and T1.TRPL_ID in (select TRPL_ID from temp_table)
group by T1.SCENARIO_ID
from pinotdb import connect

conn = connect(host='pinot-broker', port=8099, path='/query/sql', scheme='http')
curs = conn.cursor()
curs.execute("""
SELECT
  product_id,
  product_name,
  product_category,
  SUMPRECISION(purchase_quantity, 10, 2) AS quantity,
  SUMPRECISION(total_purchase, 10, 2) AS sales
FROM
  purchasesEnriched
GROUP BY
  product_id,
  product_name,
  product_category
ORDER BY
  sales DESC;""")
for row in curs:
    print(row)
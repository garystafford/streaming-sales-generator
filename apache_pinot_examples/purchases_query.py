from pinotdb import connect

conn = connect(host='localhost', port=8099, path='/query/sql', scheme='http')
curs = conn.cursor()
curs.execute("""
SELECT
  product_id,
  SUM(quantity) AS quantity,
  ROUND(SUM(total_purchase), 1) AS sales,
  MAX(total_purchase) AS max_sale
FROM
  purchases
GROUP BY
  product_id
ORDER BY
  sales DESC
LIMIT
  10;""")
for row in curs:
    print(row)
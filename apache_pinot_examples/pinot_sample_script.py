# Apache Pinot Example
# Purpose: Reads the contents of a realtime table from Apache Pinot containing streaming data
# Author:  Gary A. Stafford
# Date: 2022-12-27

from pinotdb import connect

conn = connect(host="pinot-broker", port=8099, path="/query/sql", scheme="http")

sql = """
    SELECT
      product_id,
      product_name,
      product_category,
      SUMPRECISION(purchase_quantity, 10, 0) AS quantity,
      SUMPRECISION(total_purchase, 10, 2) AS sales
    FROM
      purchasesEnriched
    GROUP BY
      product_id,
      product_name,
      product_category
    ORDER BY
      sales DESC;"""

curs = conn.cursor()

curs.execute(sql)

for row in curs:
    print(row)

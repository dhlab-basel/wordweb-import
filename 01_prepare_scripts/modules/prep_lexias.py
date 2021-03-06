# mySQL library
import pymysql

# helper for edition
import helper_lexia as ed
# my id generator
import id_generator as id


def prepare():
    try:
        conn = pymysql.connect(host='localhost', port=8889, user='vitsch', password='test', database='HAMLET')

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT * FROM modifications'

        cursor.execute(sql)

        results = cursor.fetchall()

        # Contains all the lexias from hyperhamlet. Key of the lexia object is {internalID title}
        all_lexia = {}

        for row in results:

            lexia = ed.info(row["name"], None, None)

            if lexia:
                # Create a key which has the following format{firstName lastName}
                unique_key = "{} {}".format(lexia["hasLexiaTitle"], lexia["hasLexiaInternalId"])

                lexia_id = id.generate(unique_key)
                all_lexia[lexia_id] = lexia

        conn.close()
        cursor.close()

        return all_lexia

    except Exception as err:
        print(err)

# mySQL library
import pymysql
# Regex library
import re
# JSON library
import json

# my id generator
import id_generator as id
# prefix of title
import helper_prefix as pref


def get_key_for_id(title):
    key_parts = re.search("(@\d{6})(_[AD]\d\d[-0-9]{0,3}){0,2}\s(.*)", title)
    if key_parts:
        return key_parts.group(1), key_parts.group(3)
    else:
        return None, None


def get_full_year(number):
    if 79 < number <= 99:
        return "15" + str(number)
    elif 10 <= number < 80:
        return "16" + str(number)
    elif 0 < number < 10:
        return "160" + str(number)
    elif number == 0:
        return "1600"


def add_performance_dates(span_start, span_end, only_year, object):

    if span_start and span_end:
        object["firstPerformanceStart"] = get_full_year(int(span_start))
        object["firstPerformanceEnd"] = get_full_year(int(span_end))
    else:
        object["firstPerformanceExact"] = get_full_year(int(only_year))

    return object


def add_publish_dates(span_start, span_end, only_year, object):

    if span_start and span_end:
        object["publicationStart"] = get_full_year(int(span_start))
        object["publicationEnd"] = get_full_year(int(span_end))
    else:
        object["publicationExact"] = get_full_year(int(only_year))

    return object


def prepare():
    try:
        conn = pymysql.connect(host='localhost', port=8889, user='vitsch', password='test', database='HAMLET')

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT * FROM linecategories"

        cursor.execute(sql)

        results = cursor.fetchall()

        # Contains all the books from hyperhamlet. Key of the book object is {internalID title}
        all_books = {}

        for row in results:

            books = re.search("(@\d{6})(.*)", row["name"])

            if books:

                book = {}

                sec = re.search("\sSEC\s\-\s(.*)", books.group(2))

                if not sec:

                    only_a = "_A" in books.group(2)
                    only_d = "_D" in books.group(2)

                    if only_a and only_d:
                        dates_a_d = re.search("(_A((\d{2})-(\d{2})|(\d{2})))(_D((\d{2})-(\d{2})|(\d{2}))) (.*)", books.group(2))

                        if not dates_a_d:
                            print("Fail - prep_books.py: Wrong pattern (1) in book title")
                            raise SystemExit(0)

                        book = add_performance_dates(dates_a_d.group(3), dates_a_d.group(4), dates_a_d.group(5), book)
                        book = add_publish_dates(dates_a_d.group(8), dates_a_d.group(9), dates_a_d.group(10), book)
                        book = pref.get_prefix_book(dates_a_d.group(11), book)

                    elif only_a and not only_d:
                        dates_a = re.search("(_A((\d{2})-(\d{2})|(\d{2})))(.*)", books.group(2))

                        if not dates_a:
                            print("Fail - prep_books.py: Wrong pattern (2) in book title")
                            raise SystemExit(0)

                        book = add_performance_dates(dates_a.group(3), dates_a.group(4), dates_a.group(5), book)
                        book = pref.get_prefix_book(dates_a.group(6).strip(), book)

                    elif only_d and not only_a:
                        dates_d = re.search("(_D((\d{2})-(\d{2})|(\d{2})))(.*)", books.group(2))

                        if not dates_d:
                            print("Fail - prep_books.py: Wrong pattern (3) in book title")
                            raise SystemExit(0)

                        book = add_publish_dates(dates_d.group(3), dates_d.group(4), dates_d.group(5), book)
                        book = pref.get_prefix_book(dates_d.group(6).strip(), book)

                    else:
                        book = pref.get_prefix_book(books.group(2).strip(), book)

                    if "hasBookTitle" in book:

                        # Adding internal ID
                        book["hasBookInternalId"] = books.group(1)

                        # Create a key which has the following format {internalID (article) title}
                        if "hasPrefixBookTitle" in book:
                            unique_key = "{} {} {}".format(book["hasBookInternalId"], book["hasPrefixBookTitle"], book["hasBookTitle"])
                        else:
                            unique_key = "{} {}".format(book["hasBookInternalId"], book["hasBookTitle"])

                        # Creates id with the key from above. ID contains prefix and a hash which is a hexadecimal with 16 characters
                        book_id = id.generate(unique_key)

                        # Adding ID of SQL table
                        book["sql"] = row["id"]

                        # Adding the book to the allBooks object
                        all_books[book_id] = book

                    else:
                        print("prep_books.py: FAIL - _A or _D not found", books.group(2))


        conn.close()
        cursor.close()

        return all_books

    except Exception as err:
        print(err)

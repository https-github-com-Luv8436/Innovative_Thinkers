#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import psycopg2
import sys

parser = argparse.ArgumentParser()

parser.add_argument("--constituency", type=int, default="0" ,
					help="constituency for which you want to display results.")

args = parser.parse_args()

con = None


def main():
    try:
        file = open('./../../credentials.txt')
        line = file.read()
        con = psycopg2.connect(database='postgres', user='postgres', port = "5432",
                        password='InnovativeThinkers' , host=line)


        cur = con.cursor()
        
        cur.execute("SELECT COUNT(*) FROM sih_database ")
        item = cur.fetchone()
        if item == None:
            print("No voter found in database.")
            return
        print("Total numbers of voters registered into the database: ", item[0])

        cur.execute("SELECT COUNT(*) FROM sih_database WHERE status=True")
        item = cur.fetchone()
        if item == None:
            print("No voter casted their vote.")
            return
        print("Total number of voters casted their vote: ", item[0])

        cur.execute("SELECT COUNT(*) FROM sih_database WHERE party_number=%(party_number)s AND constituency=%(constituency)s AND status=%(status)s",{'party_number':0 , 'constituency':args.constituency , 'status':True})
        item = cur.fetchone()
        if item == None:
            print("No voter voted to party 0.")
            return
        print("Total number of voters from constituency ",args.constituency ,"voted to party 0: ", item[0])

        cur.execute("SELECT COUNT(*) FROM sih_database WHERE party_number=%(party_number)s AND constituency=%(constituency)s AND status=%(status)s",{'party_number':1 , 'constituency':args.constituency , 'status':True})
        item = cur.fetchone()
        if item == None:
            print("No voter voted to party 1.")
            return
        print("Total number of voters from constituency ",args.constituency ,"voted to party 1: ", item[0])

        cur.execute("SELECT COUNT(*) FROM sih_database WHERE party_number=%(party_number)s AND constituency=%(constituency)s AND status=%(status)s",{'party_number':2 , 'constituency':args.constituency , 'status':True})
        item = cur.fetchone()
        if item == None:
            print("No voter voted to party 2.")
            return
        print("Total number of voters from constituency ",args.constituency ,"voted to party 2: ", item[0])
        
        cur.execute("SELECT COUNT(*) FROM sih_database WHERE party_number=%(party_number)s AND constituency=%(constituency)s AND status=%(status)s",{'party_number':3 , 'constituency':args.constituency , 'status':True})
        item = cur.fetchone()
        if item == None:
            print("No voter voted to party 3.")
            return
        print("Total number of voters from constituency ",args.constituency ,"voted to party 3: ", item[0])

        con.commit()

        

    except psycopg2.DatabaseError as e:

        if con:
            con.rollback()

        print(f'Error {e}')
        sys.exit(1)

    finally:

        if con:
            con.close()


if __name__ == '__main__':
    main()
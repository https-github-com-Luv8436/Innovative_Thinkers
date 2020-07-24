#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os
import time as t
#from glob import glob
from time import time
#from multiprocessing import cpu_count, Pool
import psycopg2
import sys
from PIL import Image
from io import BytesIO

parser = argparse.ArgumentParser()


parser.add_argument("--aadhar_number", type=str, default="206201810454",
					help="Aadhar number of user.")

parser.add_argument("--id", type=int, default=1,
					help="id of an image.")

#parser.add_argument("--n_cores", type=int, default=cpu_count(),
#					help="Number of cores used for enrolling template.")

args = parser.parse_args()


con = None


def main():
    try:
        file = open('./../../credentials.txt')
        line = file.read()
        con = psycopg2.connect(database='postgres', user='postgres', port = "5432",
                        password='InnovativeThinkers' , host=line)


        cur = con.cursor()

        print("Loading...")
        start = time()
        aadhar = int(args.aadhar_number)
        
        cur.execute("SELECT COUNT(*) FROM sih_database ")
        item = cur.fetchone()
        if item == None:
            print("invalid aadhar number!!!!, Please enter the valid aadhar number.")
            return
        print("Total numbers of voters registered into the database: ", item[0])
        cur.execute("SELECT COUNT(*) FROM sih_database WHERE status=False")
        item = cur.fetchone()
        if item == None:
            print("invalid aadhar number!!!!, Please enter the valid aadhar number.")
            return
        print("Total number of voters casted their vote: ", item[0])

        cur.execute("SELECT COUNT(*) FROM sih_database WHERE party_number=0")
        item = cur.fetchone()
        if item == None:
            print("invalid aadhar number!!!!, Please enter the valid aadhar number.")
            return
        print("Total number of voters voted to party 0: ", item[0])

        cur.execute("SELECT COUNT(*) FROM sih_database WHERE party_number=1")
        item = cur.fetchone()
        if item == None:
            print("invalid aadhar number!!!!, Please enter the valid aadhar number.")
            return
        print("Total number of voters voted to party 1: ", item[0])

        end = time()
        print('\n>>> Time taken for displaying results: {} [s]\n'.format(end-start))
       

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
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


def readImage():

    fin = None

    try:
        fin = open(args.data_dir, "rb")
        img = fin.read()
        return img

    except IOError as e:

        print(f'Error {e.args[0]}, {e.args[1]}')
        sys.exit(1)

    finally:

        if fin:
            fin.close()

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
        
        cur.execute("SELECT * FROM sih_database WHERE aadhar_number=%(aadhar_number)s",{'aadhar_number':args.aadhar_number})
        item = cur.fetchone()
        if item == None:
            print("invalid aadhar number!!!!, Please enter the valid aadhar number.")
            return
        print("id = ",item[0])
        print("aadhar number = ",item[1])
        print("vote status = ", item[3])
        print("voted party number", item[4])

        file_jpgdata_1 = BytesIO(item[2])
        dt_1 = Image.open(file_jpgdata_1)
        dt_1.show()
        t.sleep(6)

        file_jpgdata_2 = BytesIO(item[5])
        dt_2 = Image.open(file_jpgdata_2)
        dt_2.show()
        t.sleep(6)

        file_jpgdata_3 = BytesIO(item[6])
        dt_3 = Image.open(file_jpgdata_3)
        dt_3.show()

        end = time()
        print('\n>>> Time taken for loading images: {} [s]\n'.format(end-start))
       

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
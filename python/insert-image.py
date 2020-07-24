#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os
#from glob import glob
#from time import time
#from multiprocessing import cpu_count, Pool
import psycopg2
import sys
from PIL import Image
from io import BytesIO

parser = argparse.ArgumentParser()

parser.add_argument("--user", type=int, default="1",
					help="folder in casia database to be uploaded on database server.")

parser.add_argument("--aadhar_number", type=str, default="206201810454",
					help="Aadhar number of user.")

parser.add_argument("--id", type=int, default=1,
					help="id of an image.")

parser.add_argument("--party_number", type=int, default=0,
					help="party number which voter has voted")

#parser.add_argument("--n_cores", type=int, default=cpu_count(),
#					help="Number of cores used for enrolling template.")

args = parser.parse_args()


def readImage(path):

    fin = None

    try:
        fin = open(path, "rb")
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

        print("Start uploading...")

        path  = "./../../CASIA1/" + str(args.user) + "/"+str(args.user).zfill(3)+"_1_"

        path_1 = path + "1.jpg"
        path_2 = path + "2.jpg"
        path_3 = path + "3.jpg"

        data_1 = readImage(path_1)
        binary_1 = psycopg2.Binary(data_1)
        data_2 = readImage(path_2)
        binary_2 = psycopg2.Binary(data_2)
        data_3 = readImage(path_3)
        binary_3 = psycopg2.Binary(data_3)

        aadhar = int(args.aadhar_number)
        cur.execute("INSERT INTO sih_database(aadhar_number , party_number , status , image_1 , image_2 , image_3 ) VALUES (%s , %s , %s , %s , %s , %s)", (aadhar , args.party_number , False , binary_1 , binary_2 , binary_3))

        j=0
        con.commit()

    except psycopg2.DatabaseError as e:

        if con:
            j=1
            print('Error in Uploading Image')
            con.rollback()

        print(f'Error {e}')
        sys.exit(1)

    finally:
        if j==0:
            print('Image Successfully Uploaded')

        if con:
            con.close()


if __name__ == '__main__':
    main()
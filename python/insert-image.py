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

parser.add_argument("--data_dir", type=str, default="../'CS 2019'/myProjects/CASIA1/1/001_1_1.jpg",
					help="Path to the directory containing CASIA1 images.")

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
        con = psycopg2.connect(database='mydb', user='postgres',
                        password='123')

        cur = con.cursor()

        #files = glob(os.path.join(args.data_dir, "*_1_*.jpg"))
        #n_files = len(files)
        #print("Number of files uploading into database:", n_files)

        # Parallel pools to enroll templates
        print("Start uploading...")

        #pools = Pool(processes=args.n_cores)
        #for img in pools.imap(readImage, files):
        #    pass
        data = readImage()
        binary = psycopg2.Binary(data)
        aadhar = int(args.aadhar_number)
        cur.execute("INSERT INTO sih_db(id , img , aadhar_number) VALUES (%s , %s , %s)", (args.id , binary , aadhar))

        # data = readImage()
        # binary = psycopg2.Binary(data)
        # cur.execute("INSERT INTO category(id , user_name , image) VALUES (%s , %s , %s)", (5 ,"rahul", binary))
        
        #cur.execute("SELECT * FROM category ")
        #result = cur.fetchall()
        #for item in result:
        #    print("id = ",item[0] , end ="|")
        #    print("user name = ",item[1] , end = "|")
        #    file_jpgdata = BytesIO(item[2])
        #    dt = Image.open(file_jpgdata)
        #    dt.show()

        con.commit()
        print('Image Successfully Uploaded')

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
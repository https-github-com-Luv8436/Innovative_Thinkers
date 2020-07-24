#!/usr/bin/env python
# -*- coding: utf-8 -*-
##-----------------------------------------------------------------------------
##  Import
##-----------------------------------------------------------------------------
import argparse, os
import shutil
from glob import glob
from time import time
from tqdm import tqdm
from multiprocessing import cpu_count, Pool
from scipy.io import savemat
import psycopg2
import sys
from PIL import Image
from io import BytesIO
from fnc.extractFeature import extractFeature
from fnc.matching import matching

parser = argparse.ArgumentParser()


parser.add_argument("--aadhar_number", type=str, default="206201810454",
					help="Aadhar number of user.")

parser.add_argument("--file", type=str, default="./../../CASIA1/1/001_2_4.jpg" ,
					help="Path to the file that you want to verify.")

parser.add_argument("--id", type=int, default=1,
					help="id of an image.")

parser.add_argument("--thres", type=float, default=0.38,
					help="Threshold for matching.")

parser.add_argument("--temp_dir", type=str, default="./iris_images",
					help="Path to the directory containing templates.")

parser.add_argument("--extracted_dir", type=str, default="./extracted_images/mixtest/",
					help="Path to the directory containing templates.")

parser.add_argument("--n_cores", type=int, default=cpu_count(),
					help="Number of cores used for enrolling template.")


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


def pool_func(file):
	template , mask , _ = extractFeature(file , use_multiprocess=False)
	basename = os.path.basename(file)
	out_file = os.path.join(args.extracted_dir , "%s.mat" % (basename))
	savemat(out_file , mdict = {'template': template , 'mask':mask})

def main():
    try:
        con = psycopg2.connect(database='mydb', user='postgres',
                        password='123')

        cur = con.cursor()

        #files = glob(os.path.join(args.data_dir, "*_1_*.jpg"))
        #n_files = len(files)
        #print("Number of files uploading into database:", n_files)
        start = time()

		# Check the existence of temp_dir
        if not os.path.exists(args.temp_dir):
        	print("makedirs", args.temp_dir)
        	os.makedirs(args.temp_dir)

        print("Downloading images from database..... ")

        cur.execute("SELECT * FROM sih_db WHERE aadhar_number=%(aadhar_number)s",{'aadhar_number':args.aadhar_number})
        result = cur.fetchall()
        if result == None:
            print("invalid aadhar number.")
            return

        # saving the results
        for item in result:
            file_jpgdata = BytesIO(item[1])
            dt = Image.open(file_jpgdata)
            dt = dt.save(args.temp_dir+"/"+str(item[0])+"-"+str(item[2])+".jpg")

        end = time()
        print('\n>>> Time taken for loading images: {} [s]\n'.format(end-start))

        # enrollment starts

        print("Extracting and saving data from images..........")
        start = time()

        # Check the existence of temp_dir
        if not os.path.exists(args.extracted_dir):
            print("makedirs", args.extracted_dir)
            os.makedirs(args.extracted_dir)


        files_in_dir = []

        # r=>root, d=>directories, f=>files
        for r, d, f in os.walk(args.temp_dir):
            for item in f:
                if '.jpg' in item:
                    files_in_dir.append(os.path.join(r, item))
        pools = Pool(processes=args.n_cores)
        for file in pools.imap(pool_func, files_in_dir):
            pass

        end = time()
        print('\n>>> Extraction time: {} [s]\n'.format(end-start))

        # verification process starts


        print('>>> Start verifying {}\n'.format(args.file))

        start = time()

        template, mask, file = extractFeature(args.file)

        # Matching

        print('Matching images.........')
        result = matching(template, mask, args.extracted_dir, args.thres)

        if result == -1:
        	print('>>> No registered sample.')

        elif result == 0:
            print('>>> No sample matched.')

        else:
            print('>>> {} samples matched (descending reliability):'.format(len(result)))
            for res in result:
                print("\t", res)

        end = time()
        print('\n>>> User verification time: {} [s]\n'.format(end-start))

        try:
            shutil.rmtree(args.temp_dir)
            shutil.rmtree(args.extracted_dir)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
        #pools = Pool(processes=args.n_cores)
        #for img in pools.imap(readImage, files):
        #    pass
        #data = readImage()
        #binary = psycopg2.Binary(data)
        aadhar = int(args.aadhar_number)
        # cur.execute("INSERT INTO sih_db(id , img , aadhar_number) VALUES (%s , %s , %s)", (args.id , binary , aadhar))


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


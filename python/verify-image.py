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
import demo1    

parser = argparse.ArgumentParser()


parser.add_argument("--file", type=str, default="./../CASIA1/1/001_2_4.jpg" ,
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

con = None


def pool_func(file):
    template , mask , _ = extractFeature(file , use_multiprocess=False)
    basename = os.path.basename(file)
    out_file = os.path.join(args.extracted_dir , "%s.mat" % (basename))
    savemat(out_file , mdict = {'template': template , 'mask':mask})

def main():
    try:
        start = time()
        print("Scanning aadhar number from given aadhar....... ")

        aadhar = demo1.aadhar()

        if aadhar==None:
            print("Sorry we are unable to extract details from your aadhar card.")
            aadhar = int(input("Please enter your aadhar number:"))

        end = time()
        print("successfully extracted the aadhar number " , aadhar)
        print('\n>>> Time taken: {} [s]\n'.format(end-start))


        print("\nMaking connection with the database........\n")

        file = open('./../credentials.txt')
        line = file.read()
        con = psycopg2.connect(database='postgres', user='postgres', port = "5432",
                        password='InnovativeThinkers' , host=line)

        cur = con.cursor()

        print("\nconnected successfully.\n")


        if not os.path.exists(args.temp_dir):
        	print("makedirs", args.temp_dir)
        	os.makedirs(args.temp_dir)

        print("\nDownloading images from database..... \n")

        start = time()
        cur.execute("SELECT * FROM aadhar_database WHERE aadhar_number=%(aadhar_number)s",{'aadhar_number':aadhar})
        item = cur.fetchone()
        if item == None:
            print("invalid aadhar number.")
            return

        print("\n>>> checking that you had not cast the vote previously..........\n")
        print(item)
        if item[4]==True:
            print('\n>>> Sorry but you cannot cast the vote again.\n')
            return 
        # saving the results

        file_jpgdata = BytesIO(item[5])
        dt = Image.open(file_jpgdata)
        dt = dt.save(args.temp_dir+"/"+str(item[0])+"-"+str(1)+".jpg")

        file_jpgdata = BytesIO(item[6])
        dt = Image.open(file_jpgdata)
        dt = dt.save(args.temp_dir+"/"+str(item[0])+"-"+str(2)+".jpg")

        file_jpgdata = BytesIO(item[7])
        dt = Image.open(file_jpgdata)
        dt = dt.save(args.temp_dir+"/"+str(item[0])+"-"+str(3)+".jpg")

        end = time()
        print('\n>>> Time taken for Downloading images: {} [s]\n'.format(end-start))

        # enrollment starts

        print("\n>>> Extracting and saving data from images..........\n")
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

        template, mask, file = extractFeature(args.file , use_multiprocess=False)

        # Matching

        print('\n>>> Matching images.........\n')
        result = matching(template, mask, args.extracted_dir, args.thres)

        if result == -1:
        	print('>>> No registered sample.\n')

        elif result == 0:
            print('>>> No sample matched.\n')

        else:
            print("\n>>>> Iris successfully verified. Now you can vote.............\n")
            while True:
                try:
                    party_number = int(input("\nenter the party number you want to vote :"))
                except ValueError:
                    print("Sorry please enter the valid party_number\n")
                    continue
                else:
                    break
            
            print("\n>>> Updating your database......\n")
            sql_query = "UPDATE aadhar_database SET status=%s , party_number=%s WHERE aadhar_number=%s "
            cur.execute(sql_query , (True , party_number , aadhar))

            print("\n>>> Database updated successfully.........\n")

        try:
            print("\n>>> Removing the data stored.......\n")
            shutil.rmtree(args.temp_dir)
            shutil.rmtree(args.extracted_dir)
        except OSError as e:
            print ("\nError: %s - %s.\n" % (e.filename, e.strerror))
        
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
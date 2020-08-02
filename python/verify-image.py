#!/usr/bin/env python
# -*- coding: utf-8 -*-
##-----------------------------------------------------------------------------
##  Import
##-----------------------------------------------------------------------------
import argparse, os
import shutil
from time import time
from multiprocessing import cpu_count, Pool
from scipy.io import savemat
import psycopg2
import sys
from PIL import Image
from io import BytesIO
from fnc.extractFeature import extractFeature
from fnc.matching import matching
import demo1
from cryptography.fernet import Fernet

parser = argparse.ArgumentParser()



parser.add_argument("--file", type=str, default="./../CASIA1/1/001_2_4.jpg" ,
					help="Path to the file that you want to verify.")

parser.add_argument("--thres", type=float, default=0.38,
					help="Threshold for matching.")

parser.add_argument("--temp_dir", type=str, default="./iris_images",
					help="Path to the directory containing templates.")

parser.add_argument("--extracted_dir", type=str, default="./extracted_images/mixtest/",
					help="Path to the directory containing templates.")

parser.add_argument("--n_cores", type=int, default=cpu_count(),
					help="Number of cores used for enrolling template.")

parser.add_argument("--party_number", type=int, default=0,
					help="Party to which vote is casted.")

parser.add_argument("--constituency", type=int, default=0,
					help="constituency of the voter from where voter has casted the vote.")


args = parser.parse_args()

con = None


def pool_func(file):
    template , mask , _ = extractFeature(file , use_multiprocess=False)
    basename = os.path.basename(file)
    out_file = os.path.join(args.extracted_dir , "%s.mat" % (basename))
    savemat(out_file , mdict = {'template': template , 'mask':mask})

def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()

def main():
    try:
        # making the connection with our database
        file = open('./../credentials.txt')
        line = file.read()
        con = psycopg2.connect(database='postgres', user='postgres', port = "5432",
                        password='InnovativeThinkers' , host=line)

        cur = con.cursor()

        if not os.path.exists(args.temp_dir):
        	os.makedirs(args.temp_dir)

        key = load_key()
        f= Fernet(key)

        aadhar = demo1.aadhar()

        # encrypt the credentials
        encoded_party_number = str(args.party_number).encode()
        encoded_status_true = str(True).encode()
        encoded_constituency = str(args.constituency).encode()


        encrypted_party_number = f.encrypt(encoded_party_number)
        encrypted_status_true = f.encrypt(encoded_status_true)
        encrypted_constituency = f.encrypt(encoded_constituency)

        party_number = encrypted_party_number.decode()
        status_true = encrypted_status_true.decode()
        constituency = encrypted_constituency.decode()

        cur.execute("SELECT * FROM sih_database")
        items = cur.fetchall()
        if items == None:
            print("invalid aadhar number.")
            return
        

        def find_user(items):
            for item in items:
                aadhar_text = item[1]
                binary_aadhar_text = aadhar_text.encode()
                decrypted_aadhar_number = f.decrypt(binary_aadhar_text)
                if int(decrypted_aadhar_number.decode()) == aadhar:
                    return item
                    

        user = find_user(items)
        if user == None:
            print("Person with this aadhar is not found.")
            return
        id = user[0]


        status_text = user[4]
        decrypted_status = f.decrypt(status_text.encode())
        decrypted_status_string = decrypted_status.decode()
        if decrypted_status_string == 'True':
            print("You cannot caste your vote again!!!")
            return

        


        file_jpgdata = BytesIO(f.decrypt(bytes(user[5])))
        dt = Image.open(file_jpgdata)
        dt = dt.save(args.temp_dir+"/"+str(user[0])+"-"+str(1)+".jpg")

        file_jpgdata = BytesIO(f.decrypt(bytes(user[6])))
        dt = Image.open(file_jpgdata)
        dt = dt.save(args.temp_dir+"/"+str(user[0])+"-"+str(2)+".jpg")

        file_jpgdata = BytesIO(f.decrypt(bytes(user[7])))
        dt = Image.open(file_jpgdata)
        dt = dt.save(args.temp_dir+"/"+str(user[0])+"-"+str(3)+".jpg")
        
        # Check the existence of temp_dir
        if not os.path.exists(args.extracted_dir):
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


        # verification process starts

        template, mask, file = extractFeature(args.file , use_multiprocess=False)

        # Matching

        result = matching(template, mask, args.extracted_dir, args.thres)

        if result == -1:
        	print('>>> No registered sample.')

        elif result == 0:
            print('>>> No sample matched.')

        else:
            sql_query = "UPDATE sih_database SET status=%s , party_number=%s , constituency=%s WHERE id=%s "
            cur.execute(sql_query , (status_true , party_number , constituency , id))

            print("Vote successfully casted with aadhar number", aadhar)
            print('Thank You for casting your vote.')

        try:
            shutil.rmtree(args.temp_dir)
            shutil.rmtree(args.extracted_dir)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
        
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
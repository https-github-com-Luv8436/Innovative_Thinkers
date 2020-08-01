#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os
import psycopg2
import sys
from PIL import Image
from io import BytesIO
from cryptography.fernet import Fernet


parser = argparse.ArgumentParser()

parser.add_argument("--user", type=int, default="1",
					help="folder in casia database to be uploaded on database server.")

parser.add_argument("--aadhar_number", type=str, default="206201810454",
					help="Aadhar number of user.")

parser.add_argument("--party_number", type=int, default=0,
					help="party number which voter has voted")

parser.add_argument("--status", type=bool, default=False,
					help="voter casted the vote or not")

parser.add_argument("--constituency", type=int, default="0",
					help="constituency of the voter from where he has casted the vote")



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


def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()

con = None


def main():
    try:
        file = open('./../credentials.txt')
        line = file.read()
        con = psycopg2.connect(database='postgres', user='postgres', port = "5432",
                        password='InnovativeThinkers' , host=line)

        cur = con.cursor()

        print("Start uploading...")

        key = load_key()

        # initialize the Fernet class
        f = Fernet(key)

        # encrypt the credentials
        encoded_party_number = str(args.party_number).encode()
        encrypted_party_number = f.encrypt(encoded_party_number)
        party_number = encrypted_party_number.decode()

        encoded_status = str(args.status).encode()
        encrypted_status = f.encrypt(encoded_status)
        status = encrypted_status.decode()

        encoded_constituency = str(args.constituency).encode()
        encrypted_constituency = f.encrypt(encoded_constituency)
        constituency = encrypted_constituency.decode()

        encoded_aadhar_number = args.aadhar_number.encode()
        encrypted_aadhar_number = f.encrypt(encoded_aadhar_number)
        aadhar_number = encrypted_aadhar_number.decode()
        

        path  = "./../CASIA1/" + str(args.user) + "/"+str(args.user).zfill(3)+"_1_"

        path_1 = path + "1.jpg"
        path_2 = path + "2.jpg"
        path_3 = path + "3.jpg"

        data_1 = readImage(path_1)
        encoded_binary_1 = f.encrypt(data_1)
        data_2 = readImage(path_2)
        encoded_binary_2 = f.encrypt(data_2)
        data_3 = readImage(path_3)
        encoded_binary_3 = f.encrypt(data_3)

        cur.execute("INSERT INTO sih_database(aadhar_number , constituency , party_number , status , image1 , image2 , image3 ) VALUES (%s , %s , %s , %s , %s , %s , %s)", (aadhar_number , constituency , party_number , status , encoded_binary_1 , encoded_binary_2 , encoded_binary_3 ))

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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import argparse
import psycopg2
import sys
from cryptography.fernet import Fernet
import argparse, os

parser = argparse.ArgumentParser()

parser.add_argument("--constituency", type=int, default="0" ,
					help="constituency for which you want to display results.")

args = parser.parse_args()

con = None

def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()


def main():
    try:
        file = open('./../credentials.txt')
        line = file.read()
        con = psycopg2.connect(database='postgres', user='postgres', port = "5432",
                        password='InnovativeThinkers' , host=line)


        cur = con.cursor()
        

        party1 = 0
        party2 = 0
        party3 = 0
        party4 = 0
        votes_casted = 0

        key = load_key()
        f= Fernet(key)

        cur.execute("SELECT * FROM sih_database")
        items = cur.fetchall()
        if items == None:
            print("No voter found in the database.")
            return

        for item in items:
            decrypted_status = f.decrypt(item[4].encode())
            decrypted_status_string = decrypted_status.decode()
            if decrypted_status_string == 'True':
                votes_casted +=1
                constituency = f.decrypt(item[2].encode())
                if int(constituency.decode())==0:
                    party = int(f.decrypt(item[3].encode()))
                    if party==1:
                        party1 += 1
                    elif party==2:
                        party2 += 1
                    elif party==3:
                        party3 += 1
                    elif party==4:
                        party4 += 1


        print("Total number of voters from constituency",args.constituency ,"casted their votes:",votes_casted)
        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 1:",party1)
        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 2:",party2)
        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 3:",party3)
        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 4:",party4)     


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
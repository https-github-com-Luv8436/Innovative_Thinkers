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
        

        votes_casted = 0

        key = load_key()
        f= Fernet(key)

        cur.execute("SELECT * FROM sih_database")
        items = cur.fetchall()
        if items == None:
            print("No voter found in the database.")
            return

        constituency_data = dict()
        for item in items:
            decrypted_status_string = f.decrypt(item[4].encode()).decode()
            decrypted_constituency = f.decrypt(item[2].encode())
            if decrypted_status_string == 'True':
                votes_casted += 1
                decoded_constituency = decrypted_constituency.decode()
                constituency = int(decoded_constituency)
                if constituency not in constituency_data:
                    constituency_data[constituency]=[0 , 0 , 0]
                party = int(f.decrypt(item[3].encode()).decode())
                if party==1:
                    constituency_data[constituency][0] += 1
                elif party==2:
                    constituency_data[constituency][1] += 1
                elif party==3:
                    constituency_data[constituency][2] += 1

        print(votes_casted,"voters has successfully casted their votes.")

        for data in constituency_data:
            print("party 1 has got",constituency_data[data][0],"votes from",data,"constituency")
            print("party 2 has got",constituency_data[data][1],"votes from",data,"constituency")
            print("party 3 has got",constituency_data[data][2],"votes from",data,"constituency")

                    



#        for item in items:
#            decrypted_status = f.decrypt(item[4].encode())
#            decrypted_status_string = decrypted_status.decode()
#            if decrypted_status_string == 'True':
#                votes_casted +=1
#                constituency = f.decrypt(item[2].encode())
#                if int(constituency.decode())==0:
#                    party = f.decrypt(item[3].encode())
#                    if int(party.decode())==1:
#                        party1 += 1
#                    elif int(party.decode())==2:
#                        party2 += 1
#                    elif int(party.decode())==3:
#                        party3 += 1


#        print("Total number of voters from constituency",args.constituency ,"casted their votes:",votes_casted)
#        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 1:",party1)
#        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 2:",party2)
#        print("Total number of voters from constituency",args.constituency ,"casted their votes to party number 3:",party3)
        

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
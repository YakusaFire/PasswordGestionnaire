import getpass
from pathlib import Path
# import hashlib
import sqlite3
from cryptography.fernet import Fernet

path_key = Path("key.key")

if not path_key.is_file():
    key = Fernet.generate_key()

    # Crée le fichier et écrit la clé dedans
    with open("key.key", "wb") as key_file:
        key_file.write(key)

    print("Fichier key.key généré avec succès !")

else:
    key = open("key.key", "rb").read()


cipher_suite = Fernet(key)


connexion = sqlite3.connect('coffre_fort.db')
cursor = connexion.cursor()

# Création de la table pour stocker les identifiants
cursor.execute('''
    CREATE TABLE IF NOT EXISTS identifiants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        login TEXT NOT NULL,
        mot_de_passe BLOB NOT NULL
    )
''')


def new_entry():

    SERVICE = input("Entrer le service pour le quelle vous voulez enregistrer votre mot de passe: ")

    LOGIN = input("Entrer votre login: ")

    MDP = getpass.getpass("Entrer votre mot de passe: ")
    MDP_CLAIR = MDP.encode()
    MDP_CHIFFRE = cipher_suite.encrypt(MDP_CLAIR)

    cursor.execute('''
    INSERT INTO identifiants (service, login, mot_de_passe)
    VALUES (?, ?, ?)''', (SERVICE, LOGIN, MDP_CHIFFRE))

    connexion.commit()


def check_bd():
    cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')

    # On récupère tout dans une variable
    tous_mes_comptes = cursor.fetchall()

    print("\nVoici tout vos enregistrements")
    i = 0
    for ligne in tous_mes_comptes:
        print(f"[{i}]Site : {ligne[0]}, Login : {ligne[1]}")
        i += 1

def view_mdp():
    print("---")
    cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')
    tous_mes_comptes = cursor.fetchall()

    n = int(input("\nQuelle mot de passe afficher: "))
    if n == "hub":
        print("Vous êtes de retour sur le menu principal")
        return
    print(f"Sur {tous_mes_comptes[n][0]}, avec votre login:{tous_mes_comptes[n][1]}, votre mot de passe est: {cipher_suite.decrypt(tous_mes_comptes[n][2]).decode()}")
    print("")
    print("---")


def suppr_mdp(nom_service):
    print("---")
    if nom_service == "hub":
        print("Vous êtes de retour sur le menu principal")
        return

    cursor.execute('''DELETE FROM identifiants WHERE service = ?''', (nom_service,))

    connexion.commit()

    if cursor.rowcount > 0:
        print(f"Le service {nom_service} a été supprimer avec succès")
    else:
        print(f"Le service {nom_service} n'existe pas")
    print("---")


def main():
    print("Taper 'help' pour afficher les actions disponibles")
    while True:
        instruction = input("\nQue souhaitez vous faire: ")
        print("")
        if instruction == "help":
            print(Path("help.txt").read_text(encoding="utf-8"))
        if instruction == "0":
            quit()
        if instruction == "1":
            check_bd()
        if instruction == "2":
            view_mdp()
        if instruction == "3":
            new_entry()
        if instruction == "4":
            suppr_mdp(input("Service à supprimer: "))



main()
connexion.close()
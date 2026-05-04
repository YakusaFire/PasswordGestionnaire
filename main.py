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


new_entry()


cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')

# On récupère tout dans une variable
tous_mes_comptes = cursor.fetchall()

print("")
i = 0
for ligne in tous_mes_comptes:
    print(f"[{i}]Site : {ligne[0]}, Login : {ligne[1]}")
    i += 1

print("Quelle mot de passe afficher")
n = int(input("Entrez la ligne du mot de passe voulu: "))
print(cipher_suite.decrypt(tous_mes_comptes[n][2]))

import getpass
from pathlib import Path
# import hashlib
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


def generer_cle_depuis_mdp(mdp_maitre):
    mdp_bytes = mdp_maitre.encode()
    salt = b'c7a87bfd85c64cc26f432633b745029e'  # Idéalement, stocke ce sel en base de données

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    cle = base64.urlsafe_b64encode(kdf.derive(mdp_bytes))
    return Fernet(cle)


# Utilisation

mdp_saisi = getpass.getpass("Entrer votre mot de passe: ")
cipher_suite = generer_cle_depuis_mdp(mdp_saisi)

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



def test_mdp():
    cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')
    tous_mes_comptes = cursor.fetchall()

    if len(tous_mes_comptes) == 0:
        return True

    try:
        cipher_suite.decrypt(tous_mes_comptes[0][2]).decode()
        print("Mot de passe corect")
    except:
        print("Le mot de passe est faux")
        connexion.close()
        quit()


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
    print("---")
    cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')

    # On récupère tout dans une variable
    tous_mes_comptes = cursor.fetchall()

    print("\nVoici tout vos enregistrements")
    i = 0
    for ligne in tous_mes_comptes:
        print(f"[{i}]Site : {ligne[0]}, Login : {ligne[1]}")
        i += 1
    print("---")

def view_mdp():
    print("---")
    cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')
    tous_mes_comptes = cursor.fetchall()

    n = int(input("\nQuelle mot de passe afficher: "))
    if n == "hub":
        print("Vous êtes de retour sur le menu principal")
        return

    print(f"Sur {tous_mes_comptes[n][0]}, avec votre login: {tous_mes_comptes[n][1]}, votre mot de passe est: {cipher_suite.decrypt(tous_mes_comptes[n][2]).decode()}")
    print("")
    print("---")


def suppr_mdp(ligne):
    print("---")
    if ligne == "hub":
        print("Vous êtes de retour sur le menu principal")
        return

    cursor.execute('SELECT service, login, mot_de_passe FROM identifiants')
    tous_mes_comptes = cursor.fetchall()
    cursor.execute('''DELETE FROM identifiants WHERE service = ?''', (tous_mes_comptes[ligne][0],))

    connexion.commit()

    if cursor.rowcount > 0:
        print(f"Le service {tous_mes_comptes[ligne][0]} a été supprimer avec succès")
    else:
        print(f"Le service {tous_mes_comptes[ligne][0]} n'existe pas")
    print("---")


def main():
    if Path("coffre_fort.db").is_file():
        test_mdp()
    print("Taper 'help' pour afficher les actions disponibles")
    while True:
        instruction = input("\nQue souhaitez vous faire: ")
        print("")
        if instruction == "help":
            print(Path("help.txt").read_text(encoding="utf-8"))
        if instruction == "0":
            break
        if instruction == "1":
            check_bd()
        if instruction == "2":
            view_mdp()
        if instruction == "3":
            new_entry()
        if instruction == "4":
            suppr_mdp(int(input("Ligne a supprimer: ")))



main()
connexion.close()
from pyhackrf import HackRf

def test_connection():
    try:
        hackrf = HackRf()
        hackrf.setup()
        print("HackRF connecté avec succès!")
        print(f"Version du firmware: {hackrf.firmware_version}")
        hackrf.close()
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    test_connection()
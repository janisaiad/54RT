import sx126x
import time
import os

# Constants
PACKET_SIZE = 80  # Taille d'un paquet en bytes, peut être poussé à 250 avec un Air Data Rate plus grand (mais donc moins de portée)
TIMEOUT = 3        # Timeout en secondes pour attendre un ACK
RETRY_LIMIT = 8    # Nombre de tentatives avant l'abandon - à adapter selon les paquets 
PACKET_TEMPLATE = "{}|{}|{}"  # Format du paquet: seq|bit|payload

def send_packet(seq, bit, payload):
    """Envoie un paquet au format `seq|bit|payload`."""
    packet = PACKET_TEMPLATE.format(seq, bit, payload).encode()
    lora.sendraw(packet)
    print(f"Sent raw packet: {packet}")  # Affiche les données brutes envoyées
    print(f"Sent packet {seq} (bit {bit}): {payload}")

def wait_for_ack(expected_bit):
    """Attend un ACK pour le bit attendu."""
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        ack = lora.receive()
        if ack:
            print(f"Raw ACK received: {ack}")  # Affiche les données brutes reçues pour le ACK
            try:
                ack_decoded = ack.decode()
                print(f"Decoded ACK: {ack_decoded}")  # Affiche les données décodées du ACK
                if ack_decoded == f"ACK{expected_bit}":
                    print(f"ACK{expected_bit} received")
                    return True
                else:
                    print(f"Unexpected ACK: {ack_decoded}")
                    return False
            except UnicodeDecodeError:
                print("Invalid ACK received (unable to decode)")
        time.sleep(0.01)
    print(f"Timeout waiting for ACK{expected_bit}")
    return False

def send_file(file_path):
    """Envoie un fichier en utilisant l'Alternating Bit Protocol."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return

    # Prépare les données du fichier
    with open(file_path, 'rb') as file:
        file_data = file.read()

    total_packets = (len(file_data) + PACKET_SIZE - 1) // PACKET_SIZE
    current_bit = 0  # Commence avec le bit 0
    seq_num = 0      # Numéro de séquence initial

    # Envoie le paquet START
    retries = 0
    while retries < RETRY_LIMIT:
        send_packet(seq_num, current_bit, "START")
        if wait_for_ack(current_bit):
            seq_num += 1
            current_bit = 1 - current_bit  # Alterne le bit
            break
        retries += 1
        print(f"Retrying START packet ({retries}/{RETRY_LIMIT})")
    if retries == RETRY_LIMIT:
        print("Failed to send START packet. Aborting.")
        return

    # Envoie les données par paquets
    for seq in range(total_packets):
        retries = 0
        while retries < RETRY_LIMIT:
            # Prépare et envoie le paquet
            start = seq * PACKET_SIZE
            end = start + PACKET_SIZE
            # On encode/décode pour éviter les erreurs, en supposant du texte. Si binaire, on adapte.
            payload_data = file_data[start:end]
            # On envoie tel quel, on pourra réintégrer les données binaire en base64 si besoin
            payload = payload_data.decode('latin-1', errors='replace')  # Décodage "safe"
            send_packet(seq_num, current_bit, payload)

            # Attend l'ACK correspondant
            if wait_for_ack(current_bit):
                seq_num += 1
                current_bit = 1 - current_bit  # Alterne le bit
                break  # Passe au paquet suivant
            retries += 1
            print(f"Retrying packet {seq} ({retries}/{RETRY_LIMIT})")
        if retries == RETRY_LIMIT:
            print(f"Failed to send packet {seq} after {RETRY_LIMIT} retries. Aborting.")
            return

    # Envoie le paquet END
    retries = 0
    while retries < RETRY_LIMIT:
        send_packet(seq_num, current_bit, "END")
        if wait_for_ack(current_bit):
            print("File sent successfully.")
            return
        retries += 1
        print(f"Retrying END packet ({retries}/{RETRY_LIMIT})")
    print("Failed to send END packet. Aborting.")


lora = sx126x.sx126x(channel=15, address=101, network=0)  

# Demande du chemin du fichier à l'utilisateur
file_path = input("Entrer le chemin du champ du fichier à envoyer : ").strip() 
file_path = os.path.join(os.getcwd(), file_path)

# Envoi du fichier
send_file(file_path)
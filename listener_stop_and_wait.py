import sx126x
import threading
import time
import os

# Constants
TIMEOUT = 2  
ACK_TEMPLATE = "ACK{}" 

isRunning = True

def listener(file_path):
    global isRunning
    expected_bit = 0  # Bit attendu
    started = False   # Deviendra True après avoir reçu et validé le paquet START
    last_reception_time = time.time()  # Pour gérer le timeout

    with open(file_path, 'wb') as file:
        while isRunning:
            data = lora.receive()  # Réception des données brutes
            if data:
                last_reception_time = time.time()  # On a reçu quelque chose, on remet à jour le timer
                print(f"Raw data received: {data}")
                try:
                    # Décodage du paquet
                    packet = data.decode()
                    print(f"Decoded packet: {packet}")

                    # Découpage du paquet au format "seq|bit|payload"
                    parts = packet.rsplit('|', 2)
                    if len(parts) != 3:
                        print("Invalid packet format")
                        # On envoie un ACK du dernier bit reçu correctement
                        lora.sendraw(ACK_TEMPLATE.format(1 - expected_bit).encode())
                        continue
                    
                    seq_num_str, bit_str, payload = parts
                    try:
                        seq_num = int(seq_num_str)
                        bit = int(bit_str)
                    except ValueError:
                        print("Invalid sequence or bit number")
                        lora.sendraw(ACK_TEMPLATE.format(1 - expected_bit).encode())
                        continue

                    print(f"Received packet {seq_num} (bit {bit}): {payload}")

                    # Vérifie si le bit correspond à celui attendu
                    if bit == expected_bit:
                        # Cas du START
                        if payload == "START" and not started:
                            # On a reçu le paquet START correct
                            lora.sendraw(ACK_TEMPLATE.format(expected_bit).encode())
                            print(f"Sent ACK{expected_bit} for START")
                            # Alterne le bit attendu
                            expected_bit = 1 - expected_bit
                            started = True
                            print("START packet processed. Ready to receive data.")
                            continue

                        # Si on n'a pas encore reçu le START correct, on ignore les autres paquets
                        if not started:
                            print("Packet received before START, ignoring.")
                            # On envoie l'ACK du dernier bit correct reçu (bit opposé)
                            lora.sendraw(ACK_TEMPLATE.format(1 - expected_bit).encode())
                            continue

                        # Cas du END
                        if payload == "END":
                            # On a reçu le paquet de fin
                            lora.sendraw(ACK_TEMPLATE.format(expected_bit).encode())
                            print(f"Sent ACK{expected_bit} for END")
                            print("Received END packet. Closing file...")
                            break

                        # Sinon, c'est un paquet de données normal
                        file.write(payload.encode())
                        print(f"Writing to file: {payload}")

                        # Envoie un ACK avec le bit actuel (celui qu'on vient d'accepter)
                        lora.sendraw(ACK_TEMPLATE.format(expected_bit).encode())
                        print(f"Sent ACK{expected_bit}")

                        # Alterne le bit attendu
                        expected_bit = 1 - expected_bit

                    else:
                        # Le bit reçu n'est pas celui attendu, on envoie un ACK pour le dernier paquet correct.
                        # Le dernier paquet correct a le bit opposé à expected_bit.
                        lora.sendraw(ACK_TEMPLATE.format(1 - expected_bit).encode())
                        print(f"Out of sync: Resent ACK{1 - expected_bit}")
                except UnicodeDecodeError:
                    print("Invalid packet (unable to decode)")
                    lora.sendraw(ACK_TEMPLATE.format(1 - expected_bit).encode())
            else:
                # Pas de paquet reçu, on vérifie le timeout
                if (time.time() - last_reception_time) > TIMEOUT:
                    # On envoie un ACK du dernier bit correctement reçu pour essayer de débloquer la situation
                    print(f"No reception for {TIMEOUT} seconds. Sending ACK{1 - expected_bit} to prompt retransmission.")
                    lora.sendraw(ACK_TEMPLATE.format(1 - expected_bit).encode())
                    last_reception_time = time.time()
                time.sleep(0.01)

    print("Reception ended.")

# Initialize LoRa
lora = sx126x.sx126x(channel=15, address=100, network=0)

# Chemin du fichier
file_path = os.path.join('./received', 'received_file')
if os.path.exists(file_path):
    print("File exists. Overwriting...")
else:
    print("Creating file...")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    open(file_path, 'wb').close()

# Lance le listener dans un thread
t_receive = threading.Thread(target=listener, args=(file_path,))
t_receive.start()
t_receive.join()

isRunning = False
print("File transfer completed or stopped.")

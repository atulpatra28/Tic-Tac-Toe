import socket
import threading
import ssl

class TicTacToeServer(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.players = []
        self.players_lock = threading.Lock()  # Lock for accessing self.players
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(2)  # Allowing two players to connect

    def run(self):
        print("Server started. Waiting for players to connect...")
        while len(self.players) < 2:
            client_socket, client_address = self.server.accept()
            print(f"Player {len(self.players) + 1} connected from {client_address}")
            with self.players_lock:
                self.players.append((client_socket, client_address))

        print("Both players connected. Starting the game.")

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile='ttt.crt', keyfile='ttt.key')

        with self.players_lock:
            for i in range(len(self.players)):
                client_socket, _ = self.players[i]
                client_ssl = ssl_context.wrap_socket(client_socket, server_side=True)
                self.players[i] = (client_ssl, self.players[i][1])

        for client_ssl, _ in self.players:
            player_thread = threading.Thread(target=self.handle_player, args=(client_ssl,))
            player_thread.start()

    def handle_player(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Send the received move to the opponent
                with self.players_lock:
                    for player_info in self.players:
                        player, _ = player_info
                        if player != client_socket and isinstance(player, socket.socket):  # Check if it's a socket
                            player.send(data)
            except Exception as e:
                print(f"Error: {e}")
                break

        client_socket.close()
        with self.players_lock:
            for player_info in self.players:
                player, _ = player_info
                if player == client_socket:
                    self.players.remove(player_info)

if __name__ == "__main__":
    host = "192.168.1.5"
    port = 7005
    server = TicTacToeServer(host, port)
    server.start()
    server.join()

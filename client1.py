import tkinter as tk
from tkinter import messagebox
import socket
import threading
import ssl

class TicTacToeClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile='ttt.crt')
        self.client_socket = context.wrap_socket(self.client_socket, server_hostname='TTT')
        self.client_socket.connect((self.host, self.port))
        self.root = tk.Tk()
        self.root.title("Tic Tac Toe")
        self.current_player = "O"
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.receive_thread = threading.Thread(target=self.receive_move)
        self.receive_thread.start()

        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(self.root, text="", font=('Arial', 30), width=3, height=1,
                                                command=lambda row=i, col=j: self.on_button_click(row, col))
                self.buttons[i][j].grid(row=i, column=j)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_button_click(self, row, col):
        if self.board[row][col] == " " and self.current_player == "O":
            self.buttons[row][col].config(text=self.current_player)
            self.board[row][col] = self.current_player
            move = f"{row},{col}"
            self.client_socket.send(move.encode())
            if self.check_winner():
                messagebox.showinfo("Tic Tac Toe", f"Player {self.current_player} wins!")
                self.reset_board()
            elif self.check_draw():
                messagebox.showinfo("Tic Tac Toe", "It's a draw!")
                self.reset_board()
            else:
                self.current_player = "X"
        elif self.current_player == "X":
            messagebox.showinfo("Tic Tac Toe", "Wait for opponent's move.")

    def receive_move(self):
        while True:
            data = self.client_socket.recv(1024)
            if not data:
                break
            move = data.decode()
            row, col = map(int, move.split(','))
            if self.board[row][col] == " ":
                self.buttons[row][col].config(text="X")
                self.board[row][col] = "X"
                if self.check_winner():
                    messagebox.showinfo("Tic Tac Toe", f"Player {self.current_player} wins!")
                    self.reset_board()
                elif self.check_draw():
                    messagebox.showinfo("Tic Tac Toe", "It's a draw!")
                    self.reset_board()
                else:
                    self.current_player = "O"
            else:
                messagebox.showinfo("Tic Tac Toe", "Invalid move received.")

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return True
        return False

    def check_draw(self):
        for row in self.board:
            for cell in row:
                if cell == " ":
                    return False
        return True

    def reset_board(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="")
        self.current_player = "O"

    def on_close(self):
        self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    host = "######" #Server ip address goes here
    port = 7005
    client = TicTacToeClient(host, port)

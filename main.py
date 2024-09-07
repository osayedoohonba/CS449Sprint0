import tkinter as tk
from tkinter import messagebox
import random
import unittest


class SOSGame:
	def __init__(self, root, size=5, player1='human', player2='human'):
		self.root = root
		self.size = size
		self.board = [['' for _ in range(size)] for _ in range(size)]
		self.buttons = [[None for _ in range(size)] for _ in range(size)]
		self.lines = [
		]  # Stores the coordinates of the lines drawn for SOS sequences
		self.player_turn = 1  # 1 for Player 1 (blue), 2 for Player 2 (red)
		self.player1 = player1  # 'human' or 'computer'
		self.player2 = player2  # 'human' or 'computer'
		self.create_board()
		self.current_player_label = tk.Label(root,
		                                     text="Player 1's Turn (Blue)",
		                                     font=('Arial', 16))
		self.current_player_label.grid(row=size, column=0, columnspan=size)
		self.letter_choice = tk.StringVar(value='S')
		self.letter_select_frame = tk.Frame(self.root)
		self.letter_select_frame.grid(row=size + 1, column=0, columnspan=size)
		tk.Radiobutton(self.letter_select_frame,
		               text="S",
		               variable=self.letter_choice,
		               value='S',
		               font=('Arial', 14)).pack(side=tk.LEFT)
		tk.Radiobutton(self.letter_select_frame,
		               text="O",
		               variable=self.letter_choice,
		               value='O',
		               font=('Arial', 14)).pack(side=tk.LEFT)

	def create_board(self):
		for row in range(self.size):
			for col in range(self.size):
				button = tk.Button(
				    self.root,
				    text='',
				    width=4,
				    height=2,
				    font=('Arial', 24),
				    command=lambda r=row, c=col: self.make_move(r, c))
				button.grid(row=row, column=col)
				self.buttons[row][col] = button

	def make_move(self, row, col):
		if self.board[row][col] == '':  # Check if the square is empty
			letter = self.letter_choice.get(
			)  # Player's selected letter ('S' or 'O')
			self.board[row][col] = letter
			self.buttons[row][col].config(text=letter, state='disabled')

			if self.player_turn == 1:
				self.buttons[row][col].config(fg='blue')
				self.current_player_label.config(text="Player 2's Turn (Red)")
			else:
				self.buttons[row][col].config(fg='red')
				self.current_player_label.config(text="Player 1's Turn (Blue)")

			if self.check_for_sos(row, col):
				self.draw_sos_line(row, col)

			self.player_turn = 3 - self.player_turn  # Switch player

			if (self.player_turn == 2 and self.player2 == 'computer') or (
			    self.player_turn == 1 and self.player1 == 'computer'):
				self.root.after(
				    500, self.computer_move)  # Computer move after 500ms

	def check_for_sos(self, row, col):
		letter = self.board[row][col]
		return (self.check_horizontal(row, col)
		        or self.check_vertical(row, col)
		        or self.check_diagonal_left_to_right(row, col)
		        or self.check_diagonal_right_to_left(row, col))

	def check_horizontal(self, row, col):
		# Check left-to-right for SOS
		if col >= 2 and self.board[row][col] == 'S' and self.board[row][
		    col - 1] == 'O' and self.board[row][col - 2] == 'S':
			return True
		return False

	def check_vertical(self, row, col):
		# Check top-to-bottom for SOS
		if row >= 2 and self.board[row][col] == 'S' and self.board[
		    row - 1][col] == 'O' and self.board[row - 2][col] == 'S':
			return True
		return False

	def check_diagonal_left_to_right(self, row, col):
		# Check diagonal (top-left to bottom-right)
		if row >= 2 and col >= 2 and self.board[row][col] == 'S' and self.board[
		    row - 1][col - 1] == 'O' and self.board[row - 2][col - 2] == 'S':
			return True
		return False

	def check_diagonal_right_to_left(self, row, col):
		# Check diagonal (top-right to bottom-left)
		if row >= 2 and col <= self.size - 3 and self.board[row][
		    col] == 'S' and self.board[row - 1][col + 1] == 'O' and self.board[
		        row - 2][col + 2] == 'S':
			return True
		return False

	def draw_sos_line(self, row, col):
		# Color the SOS sequence (lines drawn based on Player turn)
		if self.player_turn == 1:
			color = 'blue'
		else:
			color = 'red'

		# Horizontal line
		if self.check_horizontal(row, col):
			for c in range(col - 2, col + 1):
				self.buttons[row][c].config(bg=color)

		# Vertical line
		if self.check_vertical(row, col):
			for r in range(row - 2, row + 1):
				self.buttons[r][col].config(bg=color)

		# Diagonal (top-left to bottom-right)
		if self.check_diagonal_left_to_right(row, col):
			for i in range(3):
				self.buttons[row - i][col - i].config(bg=color)

		# Diagonal (top-right to bottom-left)
		if self.check_diagonal_right_to_left(row, col):
			for i in range(3):
				self.buttons[row - i][col + i].config(bg=color)

	def computer_move(self):
		""" Makes a move on behalf of the computer. """
		empty_cells = [(r, c) for r in range(self.size)
		               for c in range(self.size) if self.board[r][c] == '']
		if empty_cells:
			row, col = random.choice(empty_cells)
			self.make_move(row, col)


def start_game():
	root = tk.Tk()
	root.title("SOS Game")
	game = SOSGame(root, size=10, player1='human',
	               player2='computer')  # Can adjust size and players
	root.mainloop()


class SOSLogic:

	def __init__(self, size=5):
		self.size = size
		self.board = [['' for _ in range(size)] for _ in range(size)]

	def make_move(self, row, col, letter):
		if self.board[row][col] == '':  # Check if the square is empty
			self.board[row][col] = letter
			return True
		return False

	def check_for_sos(self, row, col):
		return (self.check_horizontal(row, col)
		        or self.check_vertical(row, col)
		        or self.check_diagonal_left_to_right(row, col)
		        or self.check_diagonal_right_to_left(row, col))

	def check_horizontal(self, row, col):
		if col >= 2 and self.board[row][col] == 'S' and self.board[row][
		    col - 1] == 'O' and self.board[row][col - 2] == 'S':
			return True
		if col <= self.size - 3 and self.board[row][col] == 'S' and self.board[
		    row][col + 1] == 'O' and self.board[row][col + 2] == 'S':
			return True
		return False

	def check_vertical(self, row, col):
		if row >= 2 and self.board[row][col] == 'S' and self.board[
		    row - 1][col] == 'O' and self.board[row - 2][col] == 'S':
			return True
		if row <= self.size - 3 and self.board[row][col] == 'S' and self.board[
		    row + 1][col] == 'O' and self.board[row + 2][col] == 'S':
			return True
		return False

	def check_diagonal_left_to_right(self, row, col):
		if row >= 2 and col >= 2 and self.board[row][col] == 'S' and self.board[
		    row - 1][col - 1] == 'O' and self.board[row - 2][col - 2] == 'S':
			return True
		if row <= self.size - 3 and col <= self.size - 3 and self.board[row][
		    col] == 'S' and self.board[row + 1][col + 1] == 'O' and self.board[
		        row + 2][col + 2] == 'S':
			return True
		return False

	def check_diagonal_right_to_left(self, row, col):
		if row >= 2 and col <= self.size - 3 and self.board[row][
		    col] == 'S' and self.board[row - 1][col + 1] == 'O' and self.board[
		        row - 2][col + 2] == 'S':
			return True
		if row <= self.size - 3 and col >= 2 and self.board[row][
		    col] == 'S' and self.board[row + 1][col - 1] == 'O' and self.board[
		        row + 2][col - 2] == 'S':
			return True
		return False


class TestSOSLogic(unittest.TestCase):

	def setUp(self):
		self.game = SOSLogic(size=5)  # Initialize a new 5x5 game for each test

	def test_make_move(self):
		self.assertTrue(self.game.make_move(0, 0, 'S'))
		self.assertEqual(self.game.board[0][0], 'S')
		self.assertFalse(self.game.make_move(
		    0, 0, 'O'))  # Cannot place another letter in the same spot

	def test_horizontal_sos(self):
		self.game.make_move(0, 0, 'S')
		self.game.make_move(0, 1, 'O')
		self.game.make_move(0, 2, 'S')
		self.assertTrue(self.game.check_for_sos(0, 2))  # SOS formed

	def test_vertical_sos(self):
		self.game.make_move(0, 0, 'S')
		self.game.make_move(1, 0, 'O')
		self.game.make_move(2, 0, 'S')
		self.assertTrue(self.game.check_for_sos(2, 0))  # SOS formed

	def test_diagonal_sos(self):
		self.game.make_move(0, 0, 'S')
		self.game.make_move(1, 1, 'O')
		self.game.make_move(2, 2, 'S')
		self.assertTrue(self.game.check_for_sos(
		    2, 2))  # SOS formed diagonally (top-left to bottom-right)

	def test_no_sos(self):
		self.game.make_move(0, 0, 'S')
		self.game.make_move(0, 1, 'O')
		self.game.make_move(0, 2, 'O')  # No SOS here
		self.assertFalse(self.game.check_for_sos(0, 2))


if __name__ == '__main__':
	print("select a mode:\n\n1. Gameplay\n2. Unit Testing")
	r = input()

	if r == "1": start_game()
	else: unittest.main()

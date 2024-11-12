from tkinter import *
from tkinter import simpledialog
from math import atan2, degrees
import random
from abc import ABC, abstractmethod

class Player(ABC):
	def __init__(self, color):
		self.color = color  # "Blue" or "Red"
		self.current_letter = "S"  # Default letter choice

	@abstractmethod
	def make_move(self, game_logic):
		"""
		Make a move on the game board
		Returns: (row, col, letter) or None if no move is possible
		"""
		pass

	def set_letter(self, letter):
		"""Set the current letter choice (S or O)"""
		self.current_letter = letter

	@property
	def player_type(self):
		return self.__class__.__name__

class HumanPlayer(Player):
	def __init__(self, color):
		super().__init__(color)

	def make_move(self, game_logic):
		# Human moves are handled by GUI clicks
		# This method won't be called directly
		return None

class ComputerPlayer(Player):
	def __init__(self, color):
		super().__init__(color)

	def make_move(self, game_logic):
		"""Implement computer player strategy"""
		valid_moves = game_logic.get_valid_moves()
		if not valid_moves:
			return None

		# Strategy 1: Complete an SOS if possible
		for row, col in valid_moves:
			for letter in ['S', 'O']:
				if game_logic.check_potential_sos(row, col, letter):
					return row, col, letter

		# Strategy 2: Block opponent's potential SOS
		for row, col in valid_moves:
			for letter in ['S', 'O']:
				if game_logic.check_potential_sos(row, col, letter):
					return row, col, letter

		# Strategy 3: Try to set up future SOS opportunities
		corner_moves = [(r, c) for r, c in valid_moves 
					   if r in [0, game_logic.board_size-1] and 
					   c in [0, game_logic.board_size-1]]
		if corner_moves:
			move = random.choice(corner_moves)
			return move[0], move[1], 'S'  # Prefer 'S' in corners

		# Strategy 4: Random move with weighted letter choice
		move = random.choice(valid_moves)
		letter = random.choice(['S', 'S', 'O'])  # Prefer 'S' slightly
		return move[0], move[1], letter

class SOSGameLogic:
	def __init__(self, board_size):
		self.board_size = board_size
		self.sos_lines = []
		self.blue_player = HumanPlayer("Blue")  # Default to human players
		self.red_player = HumanPlayer("Red")
		self.reset_game()
		self.game_mode = "Simple"

	def reset_game(self):
		self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
		self.current_player = self.blue_player  # Now stores Player object
		self.game_over = False
		self.blue_score = 0
		self.red_score = 0
		self.last_sos_count = 0
		self.sos_lines.clear()

	def switch_player(self):
		self.current_player = self.red_player if self.current_player == self.blue_player else self.blue_player

	def place_letter(self, row, col, letter):
		if self.game_over or self.board[row][col] != '':
			return False, []

		self.board[row][col] = letter
		new_sos_lines = self.check_all_sos_at_position(row, col)
		sos_formed = len(new_sos_lines) > 0
		self.last_sos_count = len(new_sos_lines)

		if sos_formed:
			self.sos_lines.extend([(start, end, self.current_player.color) 
								 for start, end in new_sos_lines])
			if self.current_player.color == "Blue":
				self.blue_score += self.last_sos_count
			else:
				self.red_score += self.last_sos_count

			if self.game_mode == "Simple" or self.is_board_full():
				self.game_over = True
		else:
			if self.is_board_full():
				self.game_over = True
			else:
				self.switch_player()

		return True, new_sos_lines

	def check_all_sos_at_position(self, row, col):
		directions = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1),           (0, 1),
			(1, -1),  (1, 0),  (1, 1)
		]

		sos_lines = []
		current_letter = self.board[row][col]

		if current_letter == 'S':
			for dr, dc in directions:
				if (0 <= row + 2*dr < self.board_size and 
					0 <= col + 2*dc < self.board_size):
					if (self.board[row + dr][col + dc] == 'O' and 
						self.board[row + 2*dr][col + 2*dc] == 'S'):
						sos_lines.append(((row, col), (row + 2*dr, col + 2*dc)))

		elif current_letter == 'O':
			for dr, dc in directions:
				if (0 <= row - dr < self.board_size and 
					0 <= row + dr < self.board_size and
					0 <= col - dc < self.board_size and 
					0 <= col + dc < self.board_size):
					if (self.board[row - dr][col - dc] == 'S' and 
						self.board[row + dr][col + dc] == 'S'):
						sos_lines.append(((row - dr, col - dc), (row + dr, col + dc)))

		return sos_lines

	def is_board_full(self):
		return all(cell != '' for row in self.board for cell in row)

	def get_current_player_type(self):
		return self.current_player.player_type  # Now uses Player object's property

	def get_valid_moves(self):
		"""Returns list of valid moves as (row, col) tuples"""
		moves = []
		for row in range(self.board_size):
			for col in range(self.board_size):
				if self.board[row][col] == '':
					moves.append((row, col))
		return moves

	def check_potential_sos(self, row, col, letter):
		"""Check if placing letter at position would form an SOS"""
		# Temporarily place the letter
		original = self.board[row][col]
		self.board[row][col] = letter
		sos_lines = self.check_all_sos_at_position(row, col)
		# Restore the board
		self.board[row][col] = original
		return len(sos_lines) > 0



class SOSGUI:
	def __init__(self, master):
		self.master = master
		self.master.title("SOS Game")
		self.game_mode = StringVar(value="Simple")
		self.player_colors = {"Blue": "blue", "Red": "red"}
		self.cell_size = 50
		self.show_setup_dialog()
		self.master.minsize(600, 800)

	def show_setup_dialog(self):
		dialog = Toplevel(self.master)
		dialog.title("Game Setup")
		dialog.transient(self.master)
		dialog.grab_set()
		dialog.resizable(False, False)  # Prevent resizing
		pass

		# Main frame with padding
		main_frame = Frame(dialog, padx=20, pady=20)
		main_frame.pack(expand=True, fill=BOTH)

		# Title at the top
		Label(main_frame, text="SOS Game Setup", 
			  font=("Helvetica", 16, "bold")).pack(pady=(0, 20))

		# Board Size Section
		size_frame = LabelFrame(main_frame, text="Board Size", 
							   font=("Helvetica", 12, "bold"), pady=10, padx=10)
		size_frame.pack(fill=X, pady=10)

		Label(size_frame, text="Select size (3-10):", 
			  font=("Helvetica", 11)).pack()
		size_var = IntVar(value=8)
		Scale(size_frame, from_=3, to=10, orient=HORIZONTAL, 
			  variable=size_var, length=200).pack(pady=5)

		# Game Mode Section
		mode_frame = LabelFrame(main_frame, text="Game Mode", 
							   font=("Helvetica", 12, "bold"), pady=10, padx=10)
		mode_frame.pack(fill=X, pady=10)

		mode_var = StringVar(value="Simple")
		Radiobutton(mode_frame, text="Simple Game", variable=mode_var, 
					value="Simple", font=("Helvetica", 11)).pack(pady=5)
		Radiobutton(mode_frame, text="General Game", variable=mode_var, 
					value="General", font=("Helvetica", 11)).pack(pady=5)

		# Player Selection Section
		players_frame = LabelFrame(main_frame, text="Player Selection", 
								 font=("Helvetica", 12, "bold"), pady=10, padx=10)
		players_frame.pack(fill=X, pady=10)

		# Blue Player
		Label(players_frame, text="Blue Player:", 
			  font=("Helvetica", 11, "bold"), fg="blue").pack(pady=5)
		blue_player_var = StringVar(value="Human")
		Radiobutton(players_frame, text="Human Player", variable=blue_player_var, 
					value="Human", font=("Helvetica", 11)).pack()
		Radiobutton(players_frame, text="Computer Player", variable=blue_player_var, 
					value="Computer", font=("Helvetica", 11)).pack()

		# Separator
		Frame(players_frame, height=2, bd=1, relief=SUNKEN).pack(fill=X, pady=10)

		# Red Player
		Label(players_frame, text="Red Player:", 
			  font=("Helvetica", 11, "bold"), fg="red").pack(pady=5)
		red_player_var = StringVar(value="Human")
		Radiobutton(players_frame, text="Human Player", variable=red_player_var, 
					value="Human", font=("Helvetica", 11)).pack()
		Radiobutton(players_frame, text="Computer Player", variable=red_player_var, 
					value="Computer", font=("Helvetica", 11)).pack()

		# Start Game Button
		def start_game():
			self.board_size = size_var.get()
			self.game_mode.set(mode_var.get())
			self.blue_player_type = blue_player_var.get()
			self.red_player_type = red_player_var.get()
			dialog.destroy()
			self.initialize_game()

		Button(main_frame, text="Start Game", command=start_game, 
			   font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
			   padx=20, pady=10).pack(pady=20)

		# Set dialog size and position
		dialog_width = 400
		dialog_height = 700  # Increased height to fit all elements comfortably
		screen_width = dialog.winfo_screenwidth()
		screen_height = dialog.winfo_screenheight()
		x = (screen_width - dialog_width) // 2
		y = (screen_height - dialog_height) // 2
		dialog.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')

		# Wait for the dialog
		self.master.wait_window(dialog)

	def initialize_game(self):
		self.game_logic = SOSGameLogic(self.board_size)
		self.game_logic.game_mode = self.game_mode.get()

		# Initialize players based on selection
		self.game_logic.blue_player = (HumanPlayer("Blue") if self.blue_player_type == "Human" 
									 else ComputerPlayer("Blue"))
		self.game_logic.red_player = (HumanPlayer("Red") if self.red_player_type == "Human" 
									else ComputerPlayer("Red"))

		# Reset game to ensure proper initialization
		self.game_logic.reset_game()

		# ... [rest of window setup remains the same] ...

		self.create_board()
		self.create_info_panel()

		# Update UI before making computer move
		self.update_ui()

		# Schedule computer move if it's first
		if isinstance(self.game_logic.current_player, ComputerPlayer):
			self.master.after(1000, self.make_computer_move)

	def create_board(self):
		canvas_size = self.cell_size * self.board_size
		self.canvas = Canvas(self.master, width=canvas_size, height=canvas_size, bg='white')
		self.canvas.grid(row=1, column=0, columnspan=self.board_size, padx=10, pady=10)

		# Draw grid
		for i in range(self.board_size + 1):
			self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, canvas_size)
			self.canvas.create_line(0, i * self.cell_size, canvas_size, i * self.cell_size)

		# Create cells
		self.cells = {}
		for row in range(self.board_size):
			for col in range(self.board_size):
				x, y = col * self.cell_size, row * self.cell_size
				cell_id = self.canvas.create_rectangle(x, y, x + self.cell_size, 
													 y + self.cell_size, fill='white')
				text_id = self.canvas.create_text(x + self.cell_size//2, 
												y + self.cell_size//2, 
												text='', font=('Helvetica', 20))
				self.cells[(row, col)] = (cell_id, text_id)

		self.canvas.bind('<Button-1>', self.on_canvas_click)

	def create_info_panel(self):
		info_frame = Frame(self.master)
		info_frame.grid(row=2, column=0, columnspan=self.board_size, pady=10)

		# Player controls
		self.create_player_controls(info_frame)

		# Game information
		self.create_game_info(info_frame)

		# Control buttons - Moving these to be more visible
		control_frame = Frame(self.master)  # Create a separate frame for controls
		control_frame.grid(row=3, column=0, columnspan=self.board_size, pady=10)

		Button(control_frame, 
			   text="New Game", 
			   command=self.reset_game,
			   font=("Helvetica", 12),
			   width=15).pack(side=LEFT, padx=10)

		Button(control_frame, 
			   text="Change Mode", 
			   command=self.change_game_mode,
			   font=("Helvetica", 12),
			   width=15).pack(side=LEFT, padx=10)

	def create_player_controls(self, parent):
		Label(parent, text="Blue Player", font=("Helvetica", 12), 
			  fg="blue").grid(row=0, column=0, padx=10)
		Label(parent, text="Red Player", font=("Helvetica", 12), 
			  fg="red").grid(row=0, column=3, padx=10)

		self.blue_choice = StringVar(value="S")
		self.red_choice = StringVar(value="S")

		for letter in ["S", "O"]:
			Radiobutton(parent, text=letter, variable=self.blue_choice, 
					   value=letter, fg="blue").grid(row=["S", "O"].index(letter) + 1, column=0)
			Radiobutton(parent, text=letter, variable=self.red_choice, 
					   value=letter, fg="red").grid(row=["S", "O"].index(letter) + 1, column=3)

	def create_game_info(self, parent):
		self.turn_label = Label(parent, text="Blue's turn", 
							  font=("Helvetica", 12), fg="blue")
		self.turn_label.grid(row=1, column=1, columnspan=2)

		self.message_label = Label(parent, text="", font=("Helvetica", 12))
		self.message_label.grid(row=2, column=1, columnspan=2)

		self.score_label = Label(parent, text="Blue: 0 | Red: 0", 
							   font=("Helvetica", 12))
		self.score_label.grid(row=3, column=1, columnspan=2)

		# Store the mode label as an instance variable so we can update it
		self.mode_label = Label(parent, text=f"Game Mode: {self.game_mode.get()}", 
							  font=("Helvetica", 12))
		self.mode_label.grid(row=4, column=1, columnspan=2)

	def create_control_buttons(self, parent):
		button_frame = Frame(parent)
		button_frame.grid(row=5, column=0, columnspan=4, pady=10)

		buttons = [
			("New Game", self.reset_game),  # Added New Game button that calls reset_game
			("Change Mode", self.change_game_mode)
		]

		for text, command in buttons:
			Button(button_frame, text=text, command=command,
				   font=("Helvetica", 10), width=12).pack(side=LEFT, padx=5)

	def on_canvas_click(self, event):
		if not self.game_logic.game_over:
		# Only process clicks if it's a human player's turn
			if isinstance(self.game_logic.current_player, HumanPlayer):  # Updated check
				col = event.x // self.cell_size
				row = event.y // self.cell_size
				if 0 <= row < self.board_size and 0 <= col < self.board_size:
					self.make_move(row, col)

	def make_move(self, row, col):
		"""Handle both human and computer moves"""
		current_player = self.game_logic.current_player
		letter = self.blue_choice.get() if current_player.color == "Blue" else self.red_choice.get()
		current_player.set_letter(letter)

		success, new_sos_lines = self.game_logic.place_letter(row, col, letter)
		if success:
			_, text_id = self.cells[(row, col)]
			self.canvas.itemconfig(text_id, text=letter, 
								 fill=self.player_colors[current_player.color])
			self.draw_sos_lines(new_sos_lines, current_player.color)
			self.update_ui()

			# Schedule next computer move if applicable
			if (not self.game_logic.game_over and 
				isinstance(self.game_logic.current_player, ComputerPlayer)):
				self.master.after(1000, self.make_computer_move)

	def make_computer_move(self):
		"""Handle computer player's turn"""
		if self.game_logic.game_over:
			return

		if isinstance(self.game_logic.current_player, ComputerPlayer):
			move = self.game_logic.current_player.make_move(self.game_logic)
			if move:
				row, col, letter = move
				if self.game_logic.current_player.color == "Blue":
					self.blue_choice.set(letter)
				else:
					self.red_choice.set(letter)
				self.make_move(row, col)

	def draw_sos_lines(self, sos_lines, player):
		for start_pos, end_pos in sos_lines:
			start_x = (start_pos[1] + 0.5) * self.cell_size
			start_y = (start_pos[0] + 0.5) * self.cell_size
			end_x = (end_pos[1] + 0.5) * self.cell_size
			end_y = (end_pos[0] + 0.5) * self.cell_size

			self.canvas.create_line(start_x, start_y, end_x, end_y, 
								  fill=self.player_colors[player], width=2)

	def update_ui(self):
		self.score_label['text'] = f"Blue: {self.game_logic.blue_score} | Red: {self.game_logic.red_score}"

		# Update player type indicators
		blue_type = self.game_logic.blue_player.player_type
		red_type = self.game_logic.red_player.player_type
		current_player = self.game_logic.current_player

		self.turn_label['text'] = f"{current_player.color}'s turn ({current_player.player_type})"
		self.turn_label['fg'] = self.player_colors[current_player.color]

		if self.game_logic.game_over:
			self.handle_game_over()
		else:
			self.handle_ongoing_game()

	def handle_game_over(self):
		if self.game_mode.get() == "Simple":
			if self.game_logic.last_sos_count > 0:
				winner = self.game_logic.current_player
				self.message_label['text'] = f"{winner.color} ({winner.player_type}) wins with SOS!"
				self.message_label['fg'] = self.player_colors[winner.color]  # Fix: Use winner.color
			else:
				self.message_label['text'] = "Draw - No SOS formed!"
				self.message_label['fg'] = "black"
		else:  # General game
			if self.game_logic.blue_score > self.game_logic.red_score:
				winner = self.game_logic.blue_player
				self.message_label['text'] = f"Blue ({winner.player_type}) wins with {self.game_logic.blue_score} SOSs!"
				self.message_label['fg'] = "blue"
			elif self.game_logic.red_score > self.game_logic.blue_score:
				winner = self.game_logic.red_player
				self.message_label['text'] = f"Red ({winner.player_type}) wins with {self.game_logic.red_score} SOSs!"
				self.message_label['fg'] = "red"
			else:
				self.message_label['text'] = "Draw game!"
				self.message_label['fg'] = "black"

	def handle_ongoing_game(self):
		current_player = self.game_logic.current_player
		current_type = current_player.player_type

		if self.game_logic.last_sos_count > 0:
			plural = 'es' if self.game_logic.last_sos_count > 1 else ''
			if self.game_mode.get() == "General":
				self.message_label['text'] = f"{current_player.color} ({current_type}) formed {self.game_logic.last_sos_count} SOS{plural}! Extra turn!"
			else:
				self.message_label['text'] = f"SOS formed! {current_player.color} ({current_type}) goes again!"
			self.message_label['fg'] = self.player_colors[current_player.color]
		else:
			self.message_label['text'] = f"{current_player.color}'s turn ({current_type})"

		self.turn_label['text'] = f"{current_player.color}'s turn"
		self.turn_label['fg'] = self.player_colors[current_player.color]

	def change_game_mode(self):
		dialog = Toplevel()
		dialog.title("Change Game Settings")
		dialog.transient(self.master)
		dialog.grab_set()
		dialog.geometry("350x500")  # Increased height for new controls

		# Increase dialog size to accommodate new controls
		dialog_width = 350
		dialog_height = 450
		screen_width = dialog.winfo_screenwidth()
		screen_height = dialog.winfo_screenheight()
		x = (screen_width - dialog_width) // 2
		y = (screen_height - dialog_height) // 2
		dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

		# Game Mode Selection
		Label(dialog, text="Select Game Mode:", font=("Helvetica", 12)).pack(pady=10)
		new_mode = StringVar(value=self.game_mode.get())
		Radiobutton(dialog, text="Simple Game", variable=new_mode, value="Simple").pack()
		Radiobutton(dialog, text="General Game", variable=new_mode, value="General").pack()

		# Board Size Selection
		Label(dialog, text="Board Size (3-10):", font=("Helvetica", 12)).pack(pady=10)
		size_var = IntVar(value=self.board_size)
		size_scale = Scale(dialog, from_=3, to=10, orient=HORIZONTAL, variable=size_var)
		size_scale.pack()

		# Add player type selection
		Label(dialog, text="Blue Player:", font=("Helvetica", 12)).pack(pady=5)
		blue_player = StringVar(value=self.game_logic.blue_player)
		Radiobutton(dialog, text="Human", variable=blue_player, value="Human").pack()
		Radiobutton(dialog, text="Computer", variable=blue_player, value="Computer").pack()

		Label(dialog, text="Red Player:", font=("Helvetica", 12)).pack(pady=5)
		red_player = StringVar(value=self.game_logic.red_player)
		Radiobutton(dialog, text="Human", variable=red_player, value="Human").pack()
		Radiobutton(dialog, text="Computer", variable=red_player, value="Computer").pack()

		def apply_settings():  # Remove the self parameter
			# Cancel any pending computer moves
			for after_id in self.master.tk.call('after', 'info'):
				self.master.after_cancel(int(after_id))

			# Create new players before updating game logic
			new_blue_player = HumanPlayer("Blue") if blue_player.get() == "Human" else ComputerPlayer("Blue")
			new_red_player = HumanPlayer("Red") if red_player.get() == "Human" else ComputerPlayer("Red")

			# Update game mode and players
			self.game_mode.set(new_mode.get())
			new_size = size_var.get()

			# Create new game logic if size changed
			if new_size != self.board_size:
				self.board_size = new_size
				self.game_logic = SOSGameLogic(self.board_size)
				# Clear all widgets in main window
				for widget in self.master.winfo_children():
					widget.destroy()
				# Reinitialize the game with new size
				self.initialize_game()
			else:
				# Update existing game logic
				self.game_logic.game_mode = new_mode.get()
				self.game_logic.blue_player = new_blue_player
				self.game_logic.red_player = new_red_player
				self.game_logic.reset_game()
				self.mode_label.config(text=f"Game Mode: {new_mode.get()}")
				self.reset_game()

			dialog.destroy()

			# Schedule the first computer move if it's computer's turn
			if isinstance(self.game_logic.current_player, ComputerPlayer):
				self.master.after(1000, self.make_computer_move)

		Button(dialog, text="Apply", command=apply_settings,
			   font=("Helvetica", 10), width=10).pack(pady=20)


	def reset_game(self):
		# Clear canvas
		self.canvas.delete("all")

		# Reset game logic
		self.game_logic.reset_game()

		# Redraw empty grid and cells
		self.create_board()

		# Reset UI elements
		current_player = self.game_logic.current_player
		self.turn_label['text'] = f"{current_player.color}'s turn ({current_player.player_type})"
		self.turn_label['fg'] = self.player_colors[current_player.color]
		self.message_label['text'] = ""
		self.score_label['text'] = "Blue: 0 | Red: 0"

		# Schedule computer move if it's first
		if isinstance(self.game_logic.current_player, ComputerPlayer):
			self.master.after(1000, self.make_computer_move)



if __name__ == "__main__":
	root = Tk()
	gui = SOSGUI(root)
	root.mainloop()

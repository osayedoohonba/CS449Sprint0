from tkinter import *
from tkinter import simpledialog
from math import atan2, degrees


class SOSGameLogic:

	def __init__(self, board_size):
		self.board_size = board_size
		self.sos_lines = []
		self.reset_game()
		self.game_mode = "Simple"

	def reset_game(self):
		self.board = [['' for _ in range(self.board_size)]
		              for _ in range(self.board_size)]
		self.current_player = "Blue"
		self.game_over = False
		self.blue_score = 0
		self.red_score = 0
		self.last_sos_count = 0
		self.sos_lines.clear()

	def place_letter(self, row, col, letter):
		if self.game_over or self.board[row][col] != '':
			return False, []

		self.board[row][col] = letter
		new_sos_lines = self.check_all_sos_at_position(row, col)
		sos_formed = len(new_sos_lines) > 0
		self.last_sos_count = len(new_sos_lines)

		if sos_formed:
			self.sos_lines.extend([(start, end, self.current_player)
			                       for start, end in new_sos_lines])
			if self.current_player == "Blue":
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
		directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),
		              (1, 0), (1, 1)]

		sos_lines = []
		current_letter = self.board[row][col]

		if current_letter == 'S':
			for dr, dc in directions:
				if (0 <= row + 2 * dr < self.board_size
				    and 0 <= col + 2 * dc < self.board_size):
					if (self.board[row + dr][col + dc] == 'O'
					    and self.board[row + 2 * dr][col + 2 * dc] == 'S'):
						sos_lines.append(
						    ((row, col), (row + 2 * dr, col + 2 * dc)))

		elif current_letter == 'O':
			for dr, dc in directions:
				if (0 <= row - dr < self.board_size
				    and 0 <= row + dr < self.board_size
				    and 0 <= col - dc < self.board_size
				    and 0 <= col + dc < self.board_size):
					if (self.board[row - dr][col - dc] == 'S'
					    and self.board[row + dr][col + dc] == 'S'):
						sos_lines.append(
						    ((row - dr, col - dc), (row + dr, col + dc)))

		return sos_lines

	def is_board_full(self):
		return all(cell != '' for row in self.board for cell in row)

	def switch_player(self):
		self.current_player = "Red" if self.current_player == "Blue" else "Blue"


class SOSGUI:

	def __init__(self, master):
		self.master = master
		self.master.title("SOS Game")
		self.game_mode = StringVar(value="Simple")
		self.player_colors = {"Blue": "blue", "Red": "red"}
		self.cell_size = 50
		self.show_setup_dialog()

	def show_setup_dialog(self):
		dialog = Toplevel(self.master)
		dialog.title("Game Setup")
		dialog.transient(self.master)
		dialog.grab_set()
		dialog.geometry("300x250")

		Label(dialog, text="Board Size (3-10):",
		      font=("Airel", 12)).pack(pady=10)
		size_var = IntVar(value=8)
		Scale(dialog, from_=3, to=10, orient=HORIZONTAL,
		      variable=size_var).pack()

		Label(dialog, text="Game Mode:", font=("Airel", 12)).pack(pady=10)
		mode_var = StringVar(value="Simple")
		Radiobutton(dialog,
		            text="Simple Game",
		            variable=mode_var,
		            value="Simple").pack()
		Radiobutton(dialog,
		            text="General Game",
		            variable=mode_var,
		            value="General").pack()

		def start_game():
			self.board_size = size_var.get()
			self.game_mode.set(mode_var.get())
			dialog.destroy()
			self.initialize_game()

		Button(dialog,
		       text="Start Game",
		       command=start_game,
		       font=("Aarial", 12)).pack(pady=20)

		self.master.wait_window(dialog)

	def initialize_game(self):
		self.game_logic = SOSGameLogic(self.board_size)
		self.game_logic.game_mode = self.game_mode.get()

		# window size
		board_pixel_size = self.cell_size * self.board_size
		window_width = board_pixel_size + 25
		window_height = board_pixel_size + 300

		# Set window size and position
		screen_width = self.master.winfo_screenwidth()
		screen_height = self.master.winfo_screenheight()
		x = (screen_width - window_width) // 2
		y = (screen_height - window_height) // 2

		self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")

		Label(self.master, text="SOS",
		      font=("Aarial", 24, "bold")).grid(row=0,
		                                        columnspan=self.board_size + 1,
		                                        pady=10)

		self.create_board()
		self.create_info_panel()

	def create_board(self):
		canvas_size = self.cell_size * self.board_size
		self.canvas = Canvas(self.master,
		                     width=canvas_size,
		                     height=canvas_size,
		                     bg='white')
		self.canvas.grid(row=1,
		                 column=0,
		                 columnspan=self.board_size,
		                 padx=10,
		                 pady=10)

		# Draw grid
		for i in range(self.board_size + 1):
			self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size,
			                        canvas_size)
			self.canvas.create_line(0, i * self.cell_size, canvas_size,
			                        i * self.cell_size)

		# Create cells
		self.cells = {}
		for row in range(self.board_size):
			for col in range(self.board_size):
				x, y = col * self.cell_size, row * self.cell_size
				cell_id = self.canvas.create_rectangle(x,
				                                       y,
				                                       x + self.cell_size,
				                                       y + self.cell_size,
				                                       fill='white')
				text_id = self.canvas.create_text(x + self.cell_size // 2,
				                                  y + self.cell_size // 2,
				                                  text='',
				                                  font=('Aarial', 20))
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
		control_frame = Frame(
		    self.master)  # Create a separate frame for controls
		control_frame.grid(row=3,
		                   column=0,
		                   columnspan=self.board_size,
		                   pady=10)

		Button(control_frame,
		       text="New Game",
		       command=self.reset_game,
		       font=("Aarial", 12),
		       width=15).pack(side=LEFT, padx=10)

		Button(control_frame,
		       text="Change Mode",
		       command=self.change_game_mode,
		       font=("Aarial", 12),
		       width=15).pack(side=LEFT, padx=10)

	def create_player_controls(self, parent):
		Label(parent, text="Blue Player", font=("Aarial", 12),
		      fg="blue").grid(row=0, column=0, padx=10)
		Label(parent, text="Red Player", font=("Aarial", 12),
		      fg="red").grid(row=0, column=3, padx=10)

		self.blue_choice = StringVar(value="S")
		self.red_choice = StringVar(value="S")

		for letter in ["S", "O"]:
			Radiobutton(parent,
			            text=letter,
			            variable=self.blue_choice,
			            value=letter,
			            fg="blue").grid(row=["S", "O"].index(letter) + 1,
			                            column=0)
			Radiobutton(parent,
			            text=letter,
			            variable=self.red_choice,
			            value=letter,
			            fg="red").grid(row=["S", "O"].index(letter) + 1,
			                           column=3)

	def create_game_info(self, parent):
		self.turn_label = Label(parent,
		                        text="Blue's turn",
		                        font=("Aarial", 12),
		                        fg="blue")
		self.turn_label.grid(row=1, column=1, columnspan=2)

		self.message_label = Label(parent, text="", font=("Aarial", 12))
		self.message_label.grid(row=2, column=1, columnspan=2)

		self.score_label = Label(parent,
		                         text="Blue: 0 | Red: 0",
		                         font=("Aarial", 12))
		self.score_label.grid(row=3, column=1, columnspan=2)

		# Mode label is stored as an instance variable so it can be updated
		self.mode_label = Label(parent,
		                        text=f"Game Mode: {self.game_mode.get()}",
		                        font=("Aarial", 12))
		self.mode_label.grid(row=4, column=1, columnspan=2)

	def create_control_buttons(self, parent):
		button_frame = Frame(parent)
		button_frame.grid(row=5, column=0, columnspan=4, pady=10)

		buttons = [("New Game", self.reset_game),
		           ("Change Mode", self.change_game_mode)]

		for text, command in buttons:
			Button(button_frame,
			       text=text,
			       command=command,
			       font=("Aarial", 10),
			       width=12).pack(side=LEFT, padx=5)

	def on_canvas_click(self, event):
		if not self.game_logic.game_over:
			col, row = event.x // self.cell_size, event.y // self.cell_size
			if 0 <= row < self.board_size and 0 <= col < self.board_size:
				self.make_move(row, col)

	def make_move(self, row, col):
		current_player = self.game_logic.current_player
		letter = self.blue_choice.get(
		) if current_player == "Blue" else self.red_choice.get()

		success, new_sos_lines = self.game_logic.place_letter(row, col, letter)
		if success:
			_, text_id = self.cells[(row, col)]
			self.canvas.itemconfig(text_id,
			                       text=letter,
			                       fill=self.player_colors[current_player])
			self.draw_sos_lines(new_sos_lines, current_player)
			self.update_ui()

	def draw_sos_lines(self, sos_lines, player):
		for start_pos, end_pos in sos_lines:
			start_x = (start_pos[1] + 0.5) * self.cell_size
			start_y = (start_pos[0] + 0.5) * self.cell_size
			end_x = (end_pos[1] + 0.5) * self.cell_size
			end_y = (end_pos[0] + 0.5) * self.cell_size

			self.canvas.create_line(start_x,
			                        start_y,
			                        end_x,
			                        end_y,
			                        fill=self.player_colors[player],
			                        width=2)

	def update_ui(self):
		self.score_label[
		    'text'] = f"Blue: {self.game_logic.blue_score} | Red: {self.game_logic.red_score}"

		if self.game_logic.game_over:
			self.handle_game_over()
		else:
			self.handle_ongoing_game()

	def handle_game_over(self):
		if self.game_mode.get() == "Simple":
			if self.game_logic.last_sos_count > 0:
				winner = self.game_logic.current_player
				self.message_label['text'] = f"{winner} wins with SOS!"
				self.message_label['fg'] = self.player_colors[winner]
			else:
				self.message_label['text'] = "Draw - No SOS formed!"
				self.message_label['fg'] = "black"
		else:
			if self.game_logic.blue_score > self.game_logic.red_score:
				self.message_label[
				    'text'] = f"Blue wins with {self.game_logic.blue_score} SOSs!"
				self.message_label['fg'] = "blue"
			elif self.game_logic.red_score > self.game_logic.blue_score:
				self.message_label[
				    'text'] = f"Red wins with {self.game_logic.red_score} SOSs!"
				self.message_label['fg'] = "red"
			else:
				self.message_label['text'] = "Draw game!"
				self.message_label['fg'] = "black"

	def handle_ongoing_game(self):
		if self.game_logic.last_sos_count > 0:
			plural = 'es' if self.game_logic.last_sos_count > 1 else ''
			if self.game_mode.get() == "General":
				self.message_label[
				    'text'] = f"{self.game_logic.current_player} made {self.game_logic.last_sos_count} SOS{plural}! \n Extra turn!"
			else:
				self.message_label[
				    'text'] = f"SOS formed! {self.game_logic.current_player} goes again!"
			self.message_label['fg'] = self.player_colors[
			    self.game_logic.current_player]
		else:
			self.message_label['text'] = ""

		self.turn_label['text'] = f"{self.game_logic.current_player}'s turn"
		self.turn_label['fg'] = self.player_colors[
		    self.game_logic.current_player]

	def change_game_mode(self):
		dialog = Toplevel()
		dialog.title("Change Game Settings")
		dialog.transient(self.master)
		dialog.grab_set()

		dialog_width = 300
		dialog_height = 250
		screen_width = dialog.winfo_screenwidth()
		screen_height = dialog.winfo_screenheight()
		x = (screen_width - dialog_width) // 2
		y = (screen_height - dialog_height) // 2
		dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

		# Game Mode Selection
		Label(dialog, text="Select Game Mode:",
		      font=("Aarial", 12)).pack(pady=10)
		new_mode = StringVar(value=self.game_mode.get())
		Radiobutton(dialog,
		            text="Simple Game",
		            variable=new_mode,
		            value="Simple").pack()
		Radiobutton(dialog,
		            text="General Game",
		            variable=new_mode,
		            value="General").pack()

		# Board Size Selection
		Label(dialog, text="Board Size (3-10):",
		      font=("Aarial", 12)).pack(pady=10)
		size_var = IntVar(value=self.board_size)
		size_scale = Scale(dialog,
		                   from_=3,
		                   to=10,
		                   orient=HORIZONTAL,
		                   variable=size_var)
		size_scale.pack()

		def apply_settings():
			# Update game mode
			self.game_mode.set(new_mode.get())
			self.game_logic.game_mode = new_mode.get()

			# Update board size if changed
			new_size = size_var.get()
			if new_size != self.board_size:
				self.board_size = new_size
				self.game_logic = SOSGameLogic(self.board_size)
				self.game_logic.game_mode = new_mode.get()

				for widget in self.master.winfo_children():
					widget.destroy()

				self.initialize_game()
			else:
				# Just update the mode label and reset the game
				self.mode_label.config(text=f"Game Mode: {new_mode.get()}")
				self.reset_game()

			dialog.destroy()

		Button(dialog,
		       text="Apply",
		       command=apply_settings,
		       font=("Aarial", 10),
		       width=10).pack(pady=20)

	def restart_or_new_game(self, new_setup=False):
		if new_setup:
			dialog = Toplevel(self.master)
			dialog.title("New Game")
			dialog.transient(self.master)
			dialog.grab_set()
			dialog.geometry("300x150")

			Label(dialog,
			      text="Start a new game with different settings?",
			      font=("Aarial", 12)).pack(pady=20)

			def confirm():
				dialog.destroy()
				self.master.destroy()
				new_root = Tk()
				SOSGUI(new_root)

			Button(dialog, text="Yes", command=confirm,
			       width=10).pack(side=LEFT, padx=20, pady=20)
			Button(dialog, text="No", command=dialog.destroy,
			       width=10).pack(side=RIGHT, padx=20, pady=20)
		else:
			self.reset_game()

	def reset_game(self):
		# Clear canvas
		self.canvas.delete("all")

		self.game_logic.reset_game()

		# Redraw empty grid
		canvas_size = self.cell_size * self.board_size
		for i in range(self.board_size + 1):
			self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size,
			                        canvas_size)
			self.canvas.create_line(0, i * self.cell_size, canvas_size,
			                        i * self.cell_size)

		# Recreate cells
		self.cells = {}
		for row in range(self.board_size):
			for col in range(self.board_size):
				x, y = col * self.cell_size, row * self.cell_size
				cell_id = self.canvas.create_rectangle(x,
				                                       y,
				                                       x + self.cell_size,
				                                       y + self.cell_size,
				                                       fill='white')
				text_id = self.canvas.create_text(x + self.cell_size // 2,
				                                  y + self.cell_size // 2,
				                                  text='',
				                                  font=('Aarial', 20))
				self.cells[(row, col)] = (cell_id, text_id)

		# Reset UI elements
		self.turn_label['text'] = "Blue's turn"
		self.turn_label['fg'] = "blue"
		self.message_label['text'] = ""
		self.score_label['text'] = "Blue: 0 | Red: 0"


if __name__ == "__main__":
	root = Tk()
	gui = SOSGUI(root)
	root.mainloop()

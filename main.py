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

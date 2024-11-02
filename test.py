import unittest
from tkinter import *
from main import SOSGameLogic


class TestSOSGameSimpleMode(unittest.TestCase):

	def setUp(self):
		self.game = SOSGameLogic(3)  # Using 3x3 board for simple tests
		self.game.game_mode = "Simple"

	def test_initial_state(self):
		"""Test the initial game state"""
		self.assertEqual(self.game.current_player, "Blue")
		self.assertEqual(self.game.blue_score, 0)
		self.assertEqual(self.game.red_score, 0)
		self.assertFalse(self.game.game_over)
		self.assertEqual(len(self.game.sos_lines), 0)

	def test_invalid_move(self):
		"""Test placing a letter in an occupied cell"""
		self.game.place_letter(0, 0, 'S')
		success, _ = self.game.place_letter(0, 0, 'O')
		self.assertFalse(success)

	def test_simple_game_ends_on_sos(self):
		"""Test that simple game ends when SOS is formed"""
		# Place 'S'
		self.game.place_letter(0, 0, 'S')
		self.assertEqual(self.game.current_player, "Red")

		# Place 'O'
		self.game.place_letter(0, 1, 'O')
		self.assertEqual(self.game.current_player, "Blue")

		# Place 'S' to complete SOS
		success, lines = self.game.place_letter(0, 2, 'S')

		self.assertTrue(success)
		self.assertTrue(self.game.game_over)
		self.assertEqual(len(lines), 1)
		self.assertEqual(self.game.blue_score, 1)

	def test_simple_game_draw(self):
		"""Test game ends in draw when board is full without SOS"""
		moves = [(0, 0, 'S'), (0, 1, 'S'), (0, 2, 'S'), (1, 0, 'S'),
		         (1, 1, 'S'), (1, 2, 'S'), (2, 0, 'S'), (2, 1, 'S'),
		         (2, 2, 'S')]

		for row, col, letter in moves:
			self.game.place_letter(row, col, letter)

		self.assertTrue(self.game.game_over)
		self.assertEqual(self.game.blue_score, 0)
		self.assertEqual(self.game.red_score, 0)

	def test_player_switch(self):
		"""Test player switching after non-SOS move"""
		self.game.place_letter(0, 0, 'S')
		self.assertEqual(self.game.current_player, "Red")

		self.game.place_letter(1, 1, 'O')
		self.assertEqual(self.game.current_player, "Blue")


class TestSOSGameGeneralMode(unittest.TestCase):

	def setUp(self):
		self.game = SOSGameLogic(3)
		self.game.game_mode = "General"

	def test_general_game_continues_after_sos(self):
		"""Test that general game continues after SOS is formed"""
		# Blue forms SOS
		self.game.place_letter(0, 0, 'S')
		self.game.place_letter(0, 1, 'O')
		success, lines = self.game.place_letter(0, 2, 'S')

		self.assertTrue(success)
		self.assertFalse(self.game.game_over)
		self.assertEqual(self.game.blue_score, 1)

		# Game should still be playable
		success, _ = self.game.place_letter(1, 1, 'O')
		self.assertTrue(success)

	def test_general_game_ends_when_full(self):
		"""Test general game ends only when board is full"""
		moves = [(0, 0, 'S'), (0, 1, 'O'), (0, 2, 'S'), (1, 0, 'S'),
		         (1, 1, 'O'), (1, 2, 'S'), (2, 0, 'S'), (2, 1, 'O')]

		# Fill all but one cell
		for row, col, letter in moves:
			self.game.place_letter(row, col, letter)
		self.assertFalse(self.game.game_over)

		# Fill last cell
		self.game.place_letter(2, 2, 'S')
		self.assertTrue(self.game.game_over)

	def test_diagonal_sos(self):
		"""Test SOS formation in diagonal direction"""
		self.game.place_letter(0, 0, 'S')
		self.game.place_letter(1, 1, 'O')
		success, lines = self.game.place_letter(2, 2, 'S')

		self.assertTrue(success)
		self.assertEqual(len(lines), 1)
		self.assertEqual(self.game.blue_score, 1)

	def test_multiple_sos_single_move(self):
		"""Test forming multiple SOS patterns with a single move"""
		# Set up board for multiple SOS with single O
		self.game.place_letter(0, 0, 'S')
		self.game.place_letter(2, 2, 'S')
		self.game.place_letter(2, 0, 'S')
		self.game.place_letter(0, 2, 'S')

		# Place O in center to form multiple SOS
		success, lines = self.game.place_letter(1, 1, 'O')

		self.assertTrue(success)
		self.assertEqual(len(lines), 4)  # Should form 4 SOS patterns
		self.assertEqual(self.game.current_player,
		                 "Blue")  # Blue gets another turn due to SOS
		self.assertEqual(self.game.blue_score,
		                 4)  # Blue should get points for all SOS patterns


if __name__ == '__main__':
	unittest.main()

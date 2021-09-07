import pandas as pd
import datetime
import uuid
from db_engines import DBEngines
from settings import DATABASES
import time
import stdiomask

from hangman import Hangman
from game_results import Gameresult
from multiplayer import Multiplayer
from difficulty import Difficulty

SQL_QUERY_CHECK_USERNAME_DETAILS = r"""
	SELECT * FROM {user_details_table}
	WHERE username = '{username}'
"""

SQL_QUERY_APPEND_DETAILS = r"""
	INSERT INTO {user_details_table}
	VALUES ('{id_val}', '{username}', '{password}');
"""

SQL_QUERY_CHECK_USER_DETAILS = r"""
	SELECT * FROM {user_details_table}
	WHERE username = '{username}' 
	AND password = '{password}'
"""


class Optionhangman(Multiplayer, Difficulty):
	def __init__(self):
		pass

	def hangman_option(self, usertype, username):  # TODO - can this function somehow become common for all games????
		play_again = True
		while play_again:
			gametype = super().checkgametype()  # can be single, multi, or back option
			if gametype in ["single", "multi"]:
				self.gametype = gametype

			if gametype == "multi":
				difficulty_level = super().getdifficultylevel()
				multi_instance = Multiplayer()
				while True:
					players = ['player1', 'player2']
					for player in players:
						if player == "player1":
							name = multi_instance.player1
							print("{} playing first.".format(multi_instance.player1))
						else:
							name = multi_instance.player2
							print("{} playing now.".format(multi_instance.player2))
						try:  # since we need to take care of back option as well , can use if else by calling class variables but not recommended, 
						# also since self.gametype is not assigned when back option is chosen so will give error
							play = Hangman(usertype, self.gametype, difficulty_level, name)
							result, difficulty_level = play.display_to_user()   
						except:
							return
						multi_instance.updatescores(player, result)
					multi_instance.displayscores()
					if ((input("\nDo you want to play again? (Press y for yes), else enter any key... ")).lower()) != 'y':
						return

			elif gametype == "single":
				difficulty_level = super().getdifficultylevel()
				hangman_play = Hangman(usertype, self.gametype, difficulty_level)
				try:  # since we need to take care of back option as well , can use if else by calling class variables but not recommended
					result, difficulty_level = hangman_play.display_to_user()   
				except:
					return

				if usertype != 'guest':
					super().update_results(username, 'hangman', difficulty_level, result)
					super().display_user_game_details(username, 'hangman')
				if ((input("\nDo you want to play again? (Press y for yes), else enter any key... ")).lower()) != 'y':
					play_again = False

			else:
				play_again = False

		return

class Player(Gameresult):
	available_games = ["hangman"]
				
	def __init__(self):
		self.db_engines = DBEngines.get_instance()
		self.games_db_engine = self.db_engines.get_engine(DATABASES['default'])

	def get_signup_sql_query(self, username, password='',id_val=''):
		if password == '':
			sql = SQL_QUERY_CHECK_USERNAME_DETAILS.format(
							user_details_table='user_details',
							username=username,
							password=password,
							id_val=id_val)
			return sql

		sql = SQL_QUERY_APPEND_DETAILS.format(
					user_details_table='user_details',
					username=username,
					password=password,
					id_val=id_val)
		return sql

	def get_login_sql_query(self, username, password):
		sql = SQL_QUERY_CHECK_USER_DETAILS.format(
						user_details_table='user_details',
						username=username,
						password=password)
		return sql

	def signup(self):
		user_accepted = False
		while not user_accepted:
			username = input("Please enter username(greater than 5 characters): ")
			if len(username) <= 5:
				print("Username less than 5 characters, please choose some other username!\n")
				continue

			sql_query = self.get_signup_sql_query(username)  
			"""could have used uniqueness constraint in db table and used try except here as unique constraint would give error when trying to append already 
			existing username to user details table."""
			df = pd.read_sql(sql=sql_query, con=self.games_db_engine)
			
			if df.empty and len(username) > 5:
				user_accepted = True
			else:
				print("Username already exists, please choose some other username!\n")
				
		pass_accepted = False
		while not pass_accepted:
			# password = input("Please enter password(greater than 5 characters): ")
			print("Please enter password(should be greater than 5 characters)")
			password = stdiomask.getpass()
			if len(password) > 5:
				pass_accepted = True
			else:
				print("Password less than 5 characters, enter again!\n")

		id_val = uuid.uuid1()
		sql_query = self.get_signup_sql_query(username, password, id_val)

		try:
			with self.games_db_engine.connect() as con:
				con.execution_options(autocommit=True).execute(sql_query)
			print("User creation successful!")
			return username
		except:
			# print("User creation not successful! :(")
			raise Exception("User creation not successful! :(")

	def login(self):
		user_accepted = False

		while not user_accepted:
			username = input("Please enter username: ")
			password = stdiomask.getpass()

			sql_query = self.get_login_sql_query(username, password)
			df = pd.read_sql(sql=sql_query, con=self.games_db_engine)

			if not df.empty:
				user_accepted = True

			else:
				print("Username and password you provided are incorrect, please enter again!\n")

		print("Logging in as {}...".format(username))
		time.sleep(1)
		return username


	def startpage(self):
		while True:  # because we need to show the user login page again and again until user exits using option number 4
			entered = False
			usertype = ''
			username = ''
			while not entered:
				option = input("Please choose an option:\n1. Login (If existing user)\n2. Signup\n3. Play as a guest\n4. Exit\n")
				options = {"1":"login", "2":"signup","3":"guest","4":"exit"}
				if option in options:
					entered = True
				else:
					print("Invalid option! Choose again.\n")

			if option == '1':
				usertype = 'user'
				username = self.login()
			elif option == '2':
				usertype = 'user'
				username = self.signup()
			elif option == '3':
				usertype = 'guest'
				print("Logging in as a guest...")
				time.sleep(1)
			else:
				return

			self.game_options(usertype, username)

	def game_options(self, usertype, username):
		while True:
			game_entered = False
			while not game_entered:
				option = input("Please choose the game you want to play or if you want to see your score:\n1. Hangman\n2. Show Scores (if you are a user)\n3. Back\n")
				options = {"1":"hangman", "2":"scores", "3":"back"}
				if option in options:
					game_entered = True
				else:
					print("Invalid option! Choose again.\n")

			if option == '1':
				choice = Optionhangman()
				choice.hangman_option(usertype, username)

			elif option == '2' and usertype != 'guest':
				super().display_game_results_options(self.available_games, username)

			elif option == '3':
				return

			else:
				print("You are not a user, please select again or signup to keep a track of your records!\n")
				continue

	def __str__(self):
		print("Start Page!")


if __name__ == '__main__':
	user = Player()
	user.startpage()

import random
import getpass
import pandas as pd
import os
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from difficulty import Difficulty
from multiplayer import MultiPlayer
from gameresults import GameResults

class WordCategoryHint():
	def __init__(self):
		pass

	def get_word_row(self):
		df = pd.read_csv('hangman/hangman_words_hints.tsv', sep='\t')
		name = random.choice(df['word'])
		df_filtered = df.loc[df['word'] == name]
		row_list = df_filtered.to_dict('records')
		return row_list[0]

class Hangman(Difficulty, WordCategoryHint):
	avail_letters = 'abcdefghijklmnopqrstuvwxyz'
	turns_diff = {'easy': 5, 'medium': 3, 'hard' : 2}

	def __init__(self, gametype):
		self.gametype = gametype
		self.guessed_letters = ''
		self.name_while_guess = []
		
		self.turns = 0
		self.difficulty_level = ''
		self.name = ''

	def get_word(self):
		if self.gametype == "multi":
			while True:
				self.random_name = getpass.getpass("Please enter word for {} to guess (word should be greater than or equal to 3 letters): ".format(self.name))  # mask the i/p
				if self.random_name.isspace() == False and len(self.random_name) >= 3:
					break
				print("Please enter a valid word!")

			while True:
				self.random_key = input("Please enter a hint for {}: ".format(self.name))
				if self.random_key.isspace() == False:
					break
				print("Please enter a valid hint!")

		elif self.gametype == "single":
			self.row_dict = super().get_word_row()
			self.random_key = self.row_dict['category']
			self.random_name = self.row_dict['word']
			self.random_name = " ".join((self.random_name).split())	

	def update_multiplayer_name(self, name):
		self.name = name

	def update_difficulty(self, difficultyifplayer2=''):
		if difficultyifplayer2 != '':
			self.difficulty_level = difficultyifplayer2
		else:
			print("\nYou get +5 chances in easy mode, +3 chances in medium mode, and +2 chances in hard mode so choose wisely! All the best!")
			self.difficulty_level = super().getdifficultylevel()

	def calculate_turns(self):
		turns = 0
		words = self.random_name.split(" ")
		for word in words:
			turns += len(word)
			dashes = "_"*len(word)
			dashes_list = list(dashes)
			self.name_while_guess += dashes_list
			self.name_while_guess.append(" ")
		self.name_while_guess.pop()
		self.turns = self.turns_diff[self.difficulty_level] + turns

	def return_if_guessing_possible(self, letter_guessed):
		if letter_guessed in self.avail_letters and len(letter_guessed) == 1:
			if letter_guessed not in self.guessed_letters:
				self.guessed_letters += letter_guessed
				return 'possible guess'
			return 'already guessed'
		return 'illegal guess'

	def word_after_guessing(self, letter_guessed):
		if letter_guessed in self.random_name:
			count = 0
			for pos in self.random_name:
				if pos == letter_guessed:
					self.name_while_guess[count] = letter_guessed 		
				count += 1
			return True
		return False

	def user_game(self):
		print("\nThe word is of {} letters, number of guesses you have are: {}. [Hint: {}]".
			format(self.turns-self.turns_diff[self.difficulty_level], self.turns, self.random_key))
		print(' '.join(self.name_while_guess))

		hints_given = 1  # as one hint is already given when shown the blank name

		while self.turns > 0:
			
			flag = 0

			while flag == 0:
				if hints_given < 3:	
					input_letter = (str(input("Please enter the letter you want to guess, if you want another hint press +, but will cost you one chance: "))).lower()
				elif hints_given == 3:
					input_letter = (str(input("Please enter the letter you want to guess, no more hints to give: "))).lower()

				if input_letter == '+' and hints_given < 3:
					if self.gametype == 'multi':
						input_hint = (input("Please enter hint for {}: ".format(self.name)))
						if hints_given == 1:
							print("\nYour second hint is: {}".format(input_hint))
						elif hints_given == 2:
							print("\nYour third hint is: {}".format(input_hint))						
					else:
						if hints_given == 1:
							print("Your second hint is: {}".format(self.row_dict['hint1']))
						elif hints_given == 2:
							print("Your third hint is: {}".format(self.row_dict['hint2']))					
					self.turns -= 1
					hints_given += 1

				elif input_letter == '+' and hints_given == 3:
					print("You don't have any more hints left noob! LOL. Try again.")

				else:
					option = self.return_if_guessing_possible(input_letter)
					if option == 'illegal guess':
						print("The letter you entered is illegal, guess again.")
				
					elif option == 'already guessed':
						print("The letter you entered is already entered, guess again.")
				
					else:
						present = self.word_after_guessing(input_letter)
				
						if present:
							print("You entered the right choice!")
				
							if "_" not in self.name_while_guess:
								print("The word is: ", self.random_name)
								print("\nCONGRATULATIONS, YOU WON! WOOHOO!")
								return 'won', self.difficulty_level
						else:
							self.turns -= 1
							print("Wrong choice!")
				
						print("Word left is: ", ' '.join(self.name_while_guess))
						flag = 1

				print("\nNumber of guesses left: {}".format(self.turns))

		print("You lost, better luck next time!")
		print("The word was: ", self.random_name)
		return 'lost', self.difficulty_level

	def __str__(self):
		print("Hangman Game!")

class BaseHangman(GameResults):	
	def __init__(self, usertype, gametype, username=''):
		self.usertype = usertype
		self.gametype = gametype
		self.username = username

	def handle(self):
		if self.gametype == "single":
			while True:
				play = Hangman(self.gametype)
				play.update_difficulty()
				play.get_word()
				play.calculate_turns()
				result, difficulty_level = play.user_game()

				if self.usertype != 'guest':
					super().base_results(self.username, "Hangman", difficulty_level, result, True)
					super().display_games_scores_with_win_lose(self.username, "Hangman")

				if ((input("\nDo you want to play again? (Press y for yes), else enter any key... ")).lower()) != 'y':
					return

		elif self.gametype == "multi":
			multi_instance = MultiPlayer()
			while True:
				players = ['player1', 'player2']
				difficulty_level = ''
				for player in players:
					if player == "player1":
						name = multi_instance.player1_name()
						print("{} playing first.".format(name))
						play = Hangman(self.gametype)
						play.update_multiplayer_name(name)
						play.update_difficulty()
						play.get_word()
						play.calculate_turns()

					else:
						name = multi_instance.player2_name()
						print("{} playing now.".format(name))	
						play = Hangman(self.gametype)							
						play.update_multiplayer_name(name)
						play.update_difficulty(difficulty_level)  # since we want player2 to have the same difficulty as player1
						play.get_word()
						play.calculate_turns()

					result, difficulty_level = play.user_game()
					multi_instance.updatescores_type1(player, result)

				multi_instance.displayscores()

				if ((input("\nDo you want to play again? (Press y for yes), else enter any key... ")).lower()) != 'y':
					return



if __name__ == '__main__':
	user = Hangman()
	# user.display_to_user()


# hangman name with space in between, show properly to user and process accordingly (eg. south korea)
# login user maintaining prev scores and all (parent class)  -- done
# play again option.  -- done
# add timer  -- done
# difficulty based on choice of user  -- done
# clean code if possbile - if won or not in a seperate function, show to user number of guesses left --done
# setting up postgres- for storing authentications detailsand other things  -- done
# can password be entered in stars while user is typing -- done
# add def __str__ to all classes  -- done
# display user games details, give an option -- done
# check if username requires any case sensitiveness  -- done
# don't decrease turn when choice is right in hangman  -- done
# option for display all results for all games and display only specific game results -- done
# back option  -- done
# take care of case sensitivity when user is making a choice  -- done
# exit option only on start page very first page   -- done
# multiplayer game or single player (multiplayer - other person gives the words and hint, keep track of both players scores -- done
# get mail id as i/p as well -- done
# can send otp through mail when forgot option -- done
# update passwprd option if forgot, update modified on accordingly -- done
# confirm password by making user enter twice while signing up/ passwprd change -- done
# password should contain letters and special characters and digits -- done
# in multiplayer the word given by player should NOT BE SHOWN WHILE typing  -- done
# words, hints can store in tsv  -- done
# add more categories, (import from csv with multiple categories?) -- done
# add another hint but it costs you chances, add this feature to multiplayer as well  -- done
# username could be a class variable, same for usertype, gametype. eg self.username=username because otherwise we have to pass everywhere -- done
# optionhangman class in startpage file could have everything in __init__ function itself -- done
# first ask single player or multi player  and then show games accordingly -- done
# common game option function in startpage for all games/ or have a base game option class  -- done
# work on namings -- done
# apostrophe error in username password due to sql error  -- done
# rock papers scissors -- done
#    --- in rock paper scissors don't require difficulty since it's anyway random  -- done
# tic tac toe  # only 2 players -- done
# do we create different play options for different games in startpage based on if difficulty or not  -- done
# flames -- done
# jumbled word -- difficulty will result in change in length of word and number of chances, both single player and multiplayer -- done
# remember game, singleplayer and multiplayer, only need to keep the highest score, will require a different score table  -- done


# difficulty level based on past of the user
# the password is stored in stars in db/ encrypted
# write test cases if possible
# last hint could cost 2 chances actually in hangman , can only be taken when the number of turns left are atleast 3 (1 for guessing, two for taking away)
# hangman can have difficulty based on words that is rarity of letters, length of word, this is optional

# number guessing game, both single player and multiplayer
# 21 card game, both single and multi player
# blackjack
# high low
# coin flip --  test when amount goes low to 10/20/30

# can have function to return name on the basis of player1 or player2, in coin flip
# go through code finally at very end
# create constants file if possible
# check signup, password - ayush1@ not accepted
# update emailid option

# can have special option under multiplayer list and keep all money related games there and then calculate at the end for both players across all games
#           -- keep a track of how much both players owe each other, bets will be asked for
#           -- show all progress will be lost when going back

# budget to each player
#    - choose a game -an initial bet is placed (fixed minimum) -other player can raise (raise amount is fixed), if first player chooses not to comply that game's turn ends there -calculations
#    - choose another game -same process as above
#    - if no more games to play then show the final amount with each player and who owes who and what amount
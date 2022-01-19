import random
import string
from collections import Counter, defaultdict
from itertools import permutations

from enum import Enum, auto
from typing import Set, List

WORDS_FILE = './words.txt'
DEFAULT_GUESSES = 6
DEFAULT_WORD_LENGTH = 5


class PrintColour():
    GREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class WordleGame:
    def __init__(self, target: str, guesses: int):
        self.target = target
        self.guesses = guesses
        self.guessed_correctly = False

    def guess(self, word: str):
        if self.guesses == 0 or self.guessed_correctly:
            print("game already over")
            return None
        else:
            self.guesses -= 1

        if word == self.target:
            self.guessed_correctly = True

        correct = [i for i in range(len(word)) if word[i] == self.target[i]]
        accounted_for = Counter(self.target[ix] for ix in correct)
        target_counts = Counter(self.target)

        for k, v in accounted_for.items():
            target_counts[k] -= v

        outcomes = []

        for i in range(len(word)):
            letter = word[i]
            if i in correct:
                outcomes.append(Guess(letter, i, GuessOutcome.CORRECT))
            elif target_counts[letter] > 0:
                target_counts[letter] -= 1
                outcomes.append(Guess(letter, i, GuessOutcome.MISPLACED))
            else:
                outcomes.append(Guess(letter, i, GuessOutcome.INCORRECT))

        return outcomes

    def is_finished(self):
        return self.guesses == 0 or self.guessed_correctly is True


class GuessOutcome(Enum):
    CORRECT = auto()
    MISPLACED = auto()
    INCORRECT = auto()


class Guess:
    def __init__(self, letter: str, index: int, outcome: GuessOutcome):
        self.letter = letter
        self.index = index
        self.outcome = outcome

    def __str__(self):
        return f"Guessed {self.letter} at index {self.index} and it was {self.outcome}"


def get_words(length: int):
    with open(WORDS_FILE, 'r') as all_words:
        return [line.rstrip() for line in all_words.readlines() if len(line.rstrip()) == length]


def letters_word_tallies(n: int, words: Set[str]):
    """number of words containing each letter at least n times"""
    return {c: len([word for word in words if Counter(word)[c] >= n]) for c in string.ascii_lowercase}


def find_best_letters(candidates: Set[str]):
    items = []
    for i in range(1, 4):
        items.extend(item for item in letters_word_tallies(i, candidates).items())

    ordered_pairs = sorted(items, key=lambda p: p[1], reverse=True)
    # print(ordered_pairs)
    ordered_letters = [c for c in map(lambda p: p[0], ordered_pairs)]
    # print(ordered_letters)
    return ordered_letters


def partition(n: int):
    """
    Generates sets of n distinct numbers, minimising the sum
    so for n = 5, it would generate {0, 1, 2, 3, 4} (total 10)
    then {0, 1, 2, 3, 5} (total 11)
    then {0, 1, 2, 3, 6} and {0, 1, 2, 4, 5} (total 12)
    and so on.

    Not perfect for this use case because the weighting for each letter isn't really just 1, it's the number of candidate words that could be
    excluded.
    """
    initial = {i for i in range(n)}

    current_sets = [initial]
    while True:
        for s in current_sets:
            yield s

        next_sets = []
        for s in current_sets:
            for n in s:
                s2 = s.copy()
                if n+1 not in s:
                    s2.remove(n)
                    s2.add(n+1)
                    if s2 not in next_sets:
                        next_sets.append(s2)
        current_sets = next_sets


def best_word(best_letters: List[str], candidates: Set[str]):
    for index_set in partition(DEFAULT_WORD_LENGTH):
        # print(index_set)
        letters = [best_letters[i] for i in index_set]
        for permutation in permutations(letters):
            possible = ''.join(permutation)
            if possible in candidates:
                return possible


def colour_letter(letter: str, outcome: GuessOutcome):
    if outcome == GuessOutcome.INCORRECT:
        return PrintColour.FAIL + letter + PrintColour.ENDC
    elif outcome == GuessOutcome.MISPLACED:
        return PrintColour.WARN + letter + PrintColour.ENDC
    elif outcome == GuessOutcome.CORRECT:
        return PrintColour.GREEN + letter + PrintColour.ENDC
    else:
        raise Exception(f"unrecognised outcome {outcome}")


def print_guess_result(word: str, letter_results: List[Guess]):
    return "".join(colour_letter(l, g.outcome) for l, g in zip(word, letter_results))


def play_game(words, target, print_results=True):

    game = WordleGame(target, DEFAULT_GUESSES)
    # print(f"target is: {game.target}")

    candidates = {word for word in words}

    submitted_guesses = []

    while not game.is_finished():
        best_letters = find_best_letters(candidates)
        next_guess = best_word(best_letters, candidates)

        guess_results = game.guess(next_guess)

        candidates_before = candidates

        for guess in guess_results:
            if guess.outcome == GuessOutcome.CORRECT:
                candidates = {candidate for candidate in candidates if candidate[guess.index] == guess.letter}
            elif guess.outcome == GuessOutcome.INCORRECT:
                # we know exactly how many of this letter are present
                letters_present = len([g for g in guess_results if g.letter == guess.letter and g.outcome != GuessOutcome.INCORRECT])
                candidates = {candidate for candidate in candidates if Counter(candidate)[guess.letter] == letters_present}
            elif guess.outcome == GuessOutcome.MISPLACED:
                # if we also had an incorrect guess, we use the misplaced information there
                if any(g.outcome == GuessOutcome.INCORRECT for g in guess_results if g.letter == guess.letter):
                    continue
                # we know a minimum for how many of this letter are present
                letters_present = len([other_guess for other_guess in guess_results if other_guess.letter == guess.letter and other_guess.outcome != GuessOutcome.INCORRECT])
                candidates = {candidate for candidate in candidates if Counter(candidate)[guess.letter] >= letters_present and not candidate[guess.index] == guess.letter}

        submitted_guesses.append((next_guess, guess_results, candidates_before, candidates))

    if print_results:
        for word, results, candidates_before, candidates_after in submitted_guesses:
            print(f"{print_guess_result(word, results)} ({len(candidates_before)} -> {len(candidates_after)})")
        if game.guessed_correctly:
            print("SUCCESS!")
            print(f"with {game.guesses} guesses remaining")
        else:
            print("NOT SUCCESS")

    return game.guessed_correctly, submitted_guesses


def play_games():
    words = get_words(DEFAULT_WORD_LENGTH)

    guesses_distrib = defaultdict(set)
    losses = []

    # for word in words:
    #     target = word
    for _ in range(100):
        # target = words[i]
        target = random.choice(words)

        win, guesses = play_game(words, target)
        print(f"{'WIN' if win else 'LOSE'}: {target} {[g[0] for g in guesses]}")
        if win:
            guesses_distrib[len(guesses)].add(target)
        else:
            losses.append(target)

    for k, v in sorted(guesses_distrib.items(), key=lambda i: i[0]):
        print(f"{k} guesses: {len(v)}")
    print(f"losses: {len(losses)}")


if __name__ == "__main__":
    play_games()

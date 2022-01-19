# wordlinator
Wordle solver (https://www.powerlanguage.co.uk/wordle/)

The Word list (words.txt) was copied from https://github.com/dwyl/english-words which in turn got it from infochimps. It has some pretty obscure words and is not limited to 5 letter words.


## What is Wordle
Wordle is a 1-player game similar to the [mastermind](https://en.wikipedia.org/wiki/Mastermind_(board_game)) board game, but trying to discover a secret word rather than pattern.

Rules:
- A secret five letter target word is selected.
- Each turn, the player submits a five letter word (must be a real word). They are then informed, for each letter, whether it is:
  - Correct letter, correct location
  - Correct letter, incorrect location
  - Incorrect letter
- Repeated letters are treated as distinct. Correct location letters are prioritised.
- If the player correctly submits the secret word, before running out of guesses, they win.

## How does the solver work

### Choosing a word to guess

It looks at all words that could still be the secret. It checks how many words have 1, 2 or 3 of each of the letters of the alphabet, and queues up these letters in order of frequency (so e.g. you might be more likely to guess two t's before you guess a z, depending what possible words are left)

It then follows a simple algorithm to generate a set of indices, using letters as early in the ordered list as possible. It checks every permutation of these letters to see if they are real words. It continues until it finds a valid word, and guesses that.

### Using guess results
The solver keeps track of every word it could still be ("candidates").

After each guess, this is whittled down a little more.
- A correct letter must be present in the correct position.
- A misplaced letter must not be present at that location, but must be present somewhere.
- An incorrect letter tells you exactly how many of that letter there are in the word. e.g. if you guessed `sassy` and 1 of the `s` were marked incorrect, there must be exactly 2 `s` in the target. Most often only 1 letter will have been guessed, in which case it will indicate that there are none of them in the target.


## Improvements
The solver does pretty well, reaching the correct solution within 6 guesses ~90% of the time, and most often in 4 guesses (based on 100 randomly-selected words).

The solver usually struggles with words that differ by a single, less-common letter.
e.g. `bails`, `fails`, `hails`, `pails`, `vails`, it will exclude one letter at a time.

For those cases, rather than always guessing a word that is possibly the secret, it would be better to select a valid word containing as many of the possibilities for the missing letter as possible (b, f, h, p, v).

I suspect that actually points to a better strategy in general, to gather **maximum information** from each guess until there is only a single candidate remaining.

In that case you should **stop guessing letters that are already correct** (unless you want to check whether there are multiple of that letter) because the repeated "correct" result gives you no additional information.

Instead, you could gather a list of possible "good" guess words, and see how much additional information each letter at that location stood to give you based on the possible results, then guess accordingly. It would make it a lot slower, though.
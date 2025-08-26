import random

#list of words and their corresponding hints: To be hidden from the player
words = ["peach","celery","azure","roman","bahrain","radon","pearl","linux","wardrobe","maize"] 
hints = ['Fruit','Vegetable','Color','Empire','Country','Element','Programming Language','OS','Furniture','Grain']
figure = ['''_____
|   |
|   |
|   
|
|
|
|
''',
'''_____
|   |
|   |
| (^_^)
|
|
|
|
''',
'''_____
|   |
|   |
| (^_^)
|   |
|  \|/
|
|
''',    
'''_____
|   |
|   |
| (^_^)
|   |
|  \|/
|   |
|  / \\

''',
'''_____
|   |
| (*_*)
|   |
|  \|/
|   |
|  / \\
|
''',
]
s = random.randrange(0,10,1)
rnd = 1 #game round
print("LET'S PLAY HANGMAN!!!")

def initial(): #initial conditions for every round
    s = random.randrange(0,10,1)
    print("""\nGuess the word! You get 5 chances for error.
    HINT: {} \n""".format(hints[s]))
    global error,guess,word
    error = 5
    word = words[s]
    guess = ['-']*len(word)
    
def guessing(): #the guessing framework
    global error,guess
    print('status: ',''.join(guess),"\n")
    l = input("Enter a letter to guess: ").lower()
    if l in word:
        for i in range(len(word)):
            if l == word[i]:
                guess[i] = l
    else:
        error-=1
        print(figure[4-error])
        print("\aincorrect guess! {} chances left\n".format(error))

def game(): #the overall framework
    global error,rnd
    initial()
    while error!=0:
        guessing()
        if '-' not in guess:
            print("\nCongratulations! it's {} \n".format(''.join(guess)))
            while rnd!=len(words):
                ag = input("Do you want to play another round? ")
                if 'n' not in ag:
                    rnd+=1
                    print("\n\tRound: {}".format(rnd))
                    game()
                else:
                    break
            print("\nThank you for playing :)")
            exit()

game()
#copy and run the above code to play it yourself!
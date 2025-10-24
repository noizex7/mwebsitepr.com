import random

logo = '''
                _                                                 _                        
               | |                                               (_)                        
 _ __ ___   ___| | __   _ __   __ _ _ __   ___ _ __    ___  ___ _ ___ ___  ___  _ __ ___     __ _  __ _ _ __ ___   ___
| '__/ _ \ / __| |/ /  | '_ \ / _` | '_ \ / _ \ '__|  / __|/ __| / __/ __|/ _ \| '__/ __|   / _` |/ _` | '_ ` _ \ / _ \ 
| | | (_) | (__|   <   | |_) | (_| | |_) |  __/ |     \__ \ (__| \__ \__ \ (_) | |  \__ \  | (_| | (_| | | | | | |  __/
|_|  \___/ \___|_|\_|  | .__/ \__,_| .__/ \___|_|     |___/\___|_|___/___/\___/|_|  |___/   \__, |\__,_|_| |_| |_|\___|
                       | |         | |                                                      |___/                      
                       |_|         |_|              
 
'''

rock = '''
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
'''

paper = '''
    _______
---'   ____)____
          ______)
          _______)
         _______)
---.__________)
'''

scissors = '''
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
'''

# Write your code below this line 👇
print(logo)

shapes = [rock, paper, scissors]

while True:
    choice = input("Enter 0 for rock, 1 for paper, 2 for scissors or q for quit: ")

    if not choice.isdigit():
        if choice == 'q':
            exit()
        print("Please enter a NUMBER (0, 1, or 2). Try again!\n")
        continue                   

    choice = int(choice)

    if choice not in (0, 1, 2):
        print("Number must be 0, 1, or 2. Try again!\n")
        continue

    computer = random.randint(0, 2)

    print(shapes[choice])
    print("Computer chose:\n" + shapes[computer])

    if choice == computer:
        print("It's a draw!\n")
    elif (choice == 0 and computer == 2) or \
         (choice == 1 and computer == 0) or \
         (choice == 2 and computer == 1):
        print("You win!\n")
    else:
        print("You lose.\n")
from datetime import datetime
from random import randint
import re
import bcrypt

class Bank():

    NAME_PATTERN = r"^[A-Za-z]+(?:['-][A-Za-z]+)*$"
    PASSWORD_PATERN = re.compile(
        r"^(?=.*[a-z])"      # at least one lowercase letter
        r"(?=.*[A-Z])"       # at least one uppercase letter
        r"(?=.*\d)"          # at least one digit
        r"(?=.*[@.$!%*?&])"   # at least one special character
        r"[A-Za-z\d@$!%*?&.]" # allowed characters
        r"{8,}$"             # minimum length 8
    )

    def __init__(self):
        print("For create an account we need a Name and a Password")
        self.connected = True
        self.name = input("Name: ")
        self.password = input("Password: ")
        self.balance = 0.0
        self.saving = 0.0
        self.ID = randint(123456, 1000000)

        with open("transactions.txt", "w") as file:
            file.write(f"ID: {self.ID} - {datetime.now()}: Account Created (Welcome)\n")

    # Getter & Setter name
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        if len(name) <=20 and len(name) >= 2 and re.match(self.NAME_PATTERN, name):
            self._name = name
        else:
            while True:
                print("OUPS: Please tape at least 2 to 20 characters. (no spaces, end/start with letter,, no special character)")
                enter = input("Name: ")
                if len(enter) <= 20 and len(enter) >= 2 and re.match(self.NAME_PATTERN, enter):
                    self._name = enter
                    break
    
    # Getter & Setter password
    @property
    def password(self):
        if self.connected == True:
            return self._password
        else:
            print("Please log in your account !")
    @password.setter
    def password(self, password):
        if len(password) <= 20 and len(password) >= 8 and self.PASSWORD_PATERN.match(password):
            self._password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # On stocke le hash
        else:
            while True:
                print("OUPS: 8-20 chars, with uppercase, lowercase, digit and special character (@.$!%*?&)")
                enter = input("Password: ")
                if len(enter) <= 20 and len(enter) >= 8 and self.PASSWORD_PATERN.match(enter):
                    self._password = bcrypt.hashpw(enter.encode('utf-8'), bcrypt.gensalt())
                    break

    # methode pour changer de nom
    def change_name(self):
        if self.connected == True:
            while True:
                password = input("For change the username please enter your password: ")
                if bcrypt.checkpw(password.encode('utf-8'), self._password):
                    newname = input("Name: ")
                    self.name = newname
                    print("✅ The name is updated")
                    break
                else:
                    msg = input("Wrong password, retry (R),  quit (any keyword): ").upper()
                    if msg == "R":
                        continue
                    else:
                        break
        else:
            print("Please log in your account !")

    # methode pour changer de password
    def change_password(self):
        if self.connected == True:
            while True:
                password_enter = input("For change your password you need to enter your last password first: ")
                if bcrypt.checkpw(password_enter.encode('utf-8'), self._password):  # On compare sans jamais décoder
                    newpassword = input("Password: ")
                    if bcrypt.checkpw(newpassword.encode('utf-8'), self._password):  # On compare sans jamais décoder
                        print("The newpassword is similar to the old, please enter a newpassword")
                    else:
                        self.password = newpassword
                        print("✅ The password is updated\n")
                        break
                else:
                    msg = input("Wrong password, retry (R),  quit (any keyword): ").upper()
                    if msg == "R":
                        continue
                    else:
                        break
        else:
            print("Please log in your account !")

    
    def disconnect(self):
        self.connected = False
        with open("transactions.txt", "a") as file:
            file.write(f"ID: {self.ID} - {datetime.now()}: Disconnected\n")

    def connect(self):
        while True:
            name = input("Name: ")
            if name == self.name:
                password = input("Password: ")
                if bcrypt.checkpw(password.encode('utf-8'), self._password):  #On compare sans jamais décoder
                    self.connected = True
                    print(f"\nWelcome back {self.name}\n")
                    with open("transactions.txt", "a") as file:
                        file.write(f"ID: {self.ID} - {datetime.now()}: Connected\n")
                    break
                else:
                    print("The password is incorrect")
                    enter = input("Do you want to retry (R) or quit (any keyword): ")
                    if enter != "R":
                        return
            else:
                print("The name is incorrect")
                enter = input("Do you want to retry (R) or quit (any keyword): ")
                if enter != "R":
                    return
                
    def deposit(self):
        while True:
            try:
                money = float(input("How much? "))
                if money <= 0:
                    print("We can't do that.")
                else:
                    optional = input("Why? (optional): ")                
                    self.balance += money
                    print(f"✅ We added ${money} in your current balance.")
                    break
            except ValueError:
                print("Problème: Un nombre entier est attendu!")
        
        with open("transactions.txt", "a") as file:
            file.write(f"ID: {self.ID} - {datetime.now()}: Deposit: ${money} {optional}\n")

    def withdrawn(self):
        while True:
            try:
                money = float(input("How much? "))
                if money <= 0:
                    print("We can't do that.")
                elif (self.balance - money) < 0:
                    print(f"❌ Insufficient funds. Your balance is ${self.balance:.2f}")
                    continue
                else:
                    optional = input("Why? (optional): ")
                    self.balance -= money
                    print("✅ The operator is done.")
                    break
            except ValueError:
                print("Problème: Un nombre entier est attendu!")
        with open("transactions.txt", "a") as file:
            file.write(f"ID: {self.ID} - {datetime.now()}: Withdrawn: $-{money} {optional}\n")

    @staticmethod
    def transaction_read():
        with open("transactions.txt", "r") as file:
            print()
            print(file.read())

    def add_saving(self, n):
        if n <= 0:
            print("We can't do that.")
        elif n > self.balance:
            print(f"❌ Insufficient funds. Your balance is ${self.balance:.2f}")
        else:    
            optional = input("Why? (optional): ")
            self.saving += n
            self.balance -= n
            print("✅ Successfully done!\n")
            with open("transactions.txt", "a") as file:
                file.write(f"ID: {self.ID} - {datetime.now()}: Deposit Saving Account: ${n} {optional}\n")

    def remove_saving(self, n):
        if n <= 0:
           print("We can't do that.") 
        elif (self.saving - n) < 0:
            print(f"❌ Insufficient funds. Your balance is ${self.saving:.2f}")
        else:
            optional = input("Why? (optional): ")
            self.saving -= n
            self.balance += n
            print("✅ Successfully done!\n")
            with open("transactions.txt", "a") as file:
                file.write(f"ID: {self.ID} - {datetime.now()}: Remove Saving Account: $-{n} {optional}\n")

    def simulator_rate(self, n):
        RATE = 1.5
        current_money = self.saving
        plus_value = self.saving
        print()
        for year in range(n):
            current_money += current_money * RATE / 100
            plus_value = current_money * RATE / 100
            print(f"In {year+1} year. {current_money:.2f} ~+{plus_value:.2f}")
        print()

    # Menus

    def account_menu(self):
        while True:
            while self.connected:
                print("---------------------------")
                print("| ✍️  1. Change Name       |")
                print("| ✍️  2. Change Password   |")
                print("| 👤 3. Show Profil       |")
                print("| 📥 4. Deposit           |")
                print("| 📤 5. Withdrawn         |")
                print("| 💰 6. Saving            |")
                print("| 🗂️  7. Show Transactions |")
                print("| 🚪 8. Disconnect        |")
                print("---------------------------")
                enter = input("Enter your choice: ")
                match enter:
                    case "1":
                        self.change_name()
                    case "2":
                        self.change_password()
                    case "3":
                        print(f"{self}")
                    case "4":
                        self.deposit()
                    case "5":
                        self.withdrawn()
                    case "6":
                        self.saving_menu()
                    case "7":
                        self.transaction_read()
                    case "8":
                        print("You are disconnect!")
                        self.disconnect()
                        break
                    case _:
                        print("Unknow choice")

            if self.connected == False:
                if not self.disconnected_menu():
                    break

    def saving_menu(self):
        while True:

            print(f"\nYou'v ${self.saving} in your saving account")
            print("> Interest RAte : 1.5% per year. <")
            print("--------------------------------------")
            print("| 📥 1. Do you want to place on it?  |")
            print("| 📤 2. Withdrawn saving             |")
            print("| 👀 3. See simulator                |")
            print("| 🚪 X. Tape ENTER to quit           |")
            print("--------------------------------------")
            enter = input("Enter your choice: ")

            match enter:
                case "1":
                    while True:
                        try:
                            money = float(input("How much? "))
                            if money >= 20:
                                self.add_saving(money)
                                break
                            else:
                                print("Minimum at $20")
                        except ValueError:
                            print("❌ Please enter a valid number.\n")
                case "2":
                    while True:
                        try:
                            money = float(input("How much? "))
                            self.remove_saving(money)
                            break
                        except ValueError:
                            print("❌ Please enter a valid number.\n")
                case "3":
                    times = int(input("Number of year: "))
                    self.simulator_rate(times)
                case _:
                    break

    def disconnected_menu(self):
        print("\nWelcome to your bank\n 1. Connect \n 2. Quit\n")
        enter = input("Enter your choice: ")
        if enter == "1":
            self.connect()
        elif enter == "2":
            print("You just left the bank")
            return False
        return True


    def __str__(self):
        return f"\nProfil Detail:\nID: {self.ID}\nNameUser: {self.name},\nBalance: ${self.balance},\nPassword: ********"

def welcome_menu():
    print("================================")
    print("       Welcome to SXBank        ")
    print("================================")

    while  True:
        print("---------------------------")
        print("| 🏦 1. Create an account |")
        print("| ℹ️  2. About the bank    |")
        print("| ⚖️  3. CGU               |")
        print("| 🚪 4. Quit              |")
        print("--------------------------")
        enter = input("> Enter your choice: ")
        match enter:
            case "1":
                return Bank()
            case "2":
                print('\n"A bank created by Sébastien Xia"\n')
            case "3":
                print('\n"CGU: none for now"\n')
            case "4":
                print("You just left the bank, see you later!")
                return None
            case _:
                print("Unknow choice")

def menu():
    main = welcome_menu()
    if main is None:
        return
    
    main.account_menu()

if __name__ == "__main__":
    menu()
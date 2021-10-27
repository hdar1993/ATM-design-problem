from datetime import datetime
from threading import Timer

class Account:
    __balance: float = 0
    
    def get_balance(self) -> float:
        return float(Account.__balance)
        
    def update_balance(self, new_balance) -> None:
        Account.__balance = new_balance

#Transaction class contains information
#related to any actions done at the ATM.
class Transaction:
    transaction_type: str = None
    overdraft_fee = 5
    
    def __init__(self):
        self.database = BankDatabase()
    
    def save_history(self, amount: float, balance_after_transaction: float):
        now = datetime.now()
        timeframe = now.strftime("%Y-%m-%d %H:%M:%S")
        
        account_id = self.database.user_authorized
        #[2] is used to access the previous transaction history
        BankDatabase.account_list[account_id][2].append(f"{timeframe} {amount} {balance_after_transaction}")
        
    def get_history(self):
        #Check if any transaction history exists
        if not len(BankDatabase.account_list[BankDatabase.user_authorized][2]):
            print("No history found")
            return False
        else:
            
            BankDatabase.account_list[BankDatabase.user_authorized][2].reverse()
            #Print each transaction history
            for transaction in BankDatabase.account_list[BankDatabase.user_authorized][2]:
                print(transaction)
    
    def execute_transaction(self, transaction_type:str, amount:float, avaiable_cash: float):
        balance = self.database.get_balance()
        if transaction_type == "withdraw":
            #Check if the account has been overdrawn
            if balance < 0:
                print("Your account is overdrawn! You may not make withdrawals at this time.")
            else:
                balance -= amount
                #If this transaction causes the account to be overdrawn
                #then take an extra $5 from the acount
                if balance < 0:
                    balance -= Transaction.overdraft_fee
                    
                avaiable_cash -= amount
                Transaction.save_history(self, amount*-1, balance)
                print(f"Amount dispensed: {amount}")
            
        elif transaction_type == "deposit":
            balance += amount
            avaiable_cash += amount
            Transaction.save_history(self, amount, balance)
            
        self.database.update_balance(balance)
        return avaiable_cash
            
class BankDatabase:
    #account_list contains every account that is registered
    #Each account consist of their account id, pin #, balance 
    #and any transaction history. 
    
    #To access any account based 
    #off their account number use account_list[account_id]
    #To access a specific information about the card do
    #account_list[account_id][x] where x can be the following:
    #0 - pin
    #1 - balance
    #2 - previous transaction history(if any)
    #Format of account_list:
    #account_id: [pin, balance, [list_containing_history] ]
    account_list = {"2859459814": ["7386","10.24", []],
         "1434597300": ["4557","90000.55", []],                          
         "7089382418": ["0075","0.00", []],  
         "2001377812": ["5950","60.00", []],
         "1":["1","1", []]
        }
    user_authorized: bool = None
    
    def __init__(self):
        self.account = Account()
        
    def is_authorized(self) -> bool:
        return BankDatabase.user_authorized
    
    def get_balance(self):
        return self.account.get_balance()
    
    def update_balance(self, new_balance: float):
        self.account.update_balance(new_balance)
        
    def update_history(self, account_id, history):
        BankDatabase.account_list[account_id][2].append(history)
        
    def add_new_account(self, account_id: int, pin: int, balance: float):
        empty_list = []
        BankDatabase.account_list.update({account_id:[pin, balance, empty_list]})
        
    def authorize_user(self, account_id: int, pin: int) -> bool:
        if BankDatabase.user_authorized != None:
            print("Authorization failed.")
        else:
            #Checks if the account id and pin are in the database
            if account_id in BankDatabase.account_list and pin in BankDatabase.account_list[account_id] :
                current_account_balance = BankDatabase.account_list[account_id][1]
                current_account_history = BankDatabase.account_list[account_id][2]
                
                BankDatabase.update_balance(self, current_account_balance)
                BankDatabase.user_authorized = account_id
                
                print(f"{account_id} successfully authorized.")
            else:
                print("Authorization failed.")
    
    #Unauthorizes the current user before logging out
    def logout(self):
        account_id = BankDatabase.user_authorized
        BankDatabase.user_authorized = None
        print(f"{account_id} logged out")
        
class ATM:
    #user_authorized states whether the ATM was able to authorize the user
    #If this is false then the user won't be able to use the ATM for
    #accessing account balance or withdrawing/depositing. Since no one 
    #is using the ATM, its currently set to False until the user comes in
    #user_authorized: bool = None
    __total_amount: float = 10000
    
    def __init__(self):
        self.database = BankDatabase()
        self.transaction = Transaction()
        
    #ATM communicates with the database to create a new account
    def signup(self, account_id: int, pin: int, balance: float):
        self.database.add_new_account(account_id, pin, balance)
        
    def authorize(self, account_id: int, pin: int):
        self.database.authorize_user(account_id, pin)
        
    def access_authorization_level(self):
        return self.database.is_authorized()
        
    def get_available_cash() -> float:
        return ATM.__total_amount
    
    def update_available_cash(self, new_total_amount: float) -> None:
        ATM.__total_amount = new_total_amount
    
    def select_transaction(self, transaction_type: str, amount: float):
        #Get total cash value current in ATM
        available_cash = ATM.get_available_cash()
        if transaction_type == "withdraw":
            #Check if the user tries to withdraw in non $20 bills
            if amount % 20 != 0:
                print("The withdrawal amount must be in 20s")
            #Check if ATM has any money
            elif not available_cash:
                print("Unable to process your withdrawal at this time")
            #Check if user tries to take more money than the ATM currently has
            elif amount > available_cash:
                print("Unable to dispense full amount requested at this time.")
            else:
                #Withdraw
                new_total_amount = self.transaction.execute_transaction(transaction_type, amount, available_cash)
                #Update total cash in ATM
                ATM.update_available_cash(self, new_total_amount)
        #Deposit
        else:
            new_total_amount = self.transaction.execute_transaction(transaction_type, amount, available_cash)
            ATM.update_available_cash(self, new_total_amount)
            
    #Prints account balance
    def print_balance(self):
        print(f"Current balance: ${self.database.get_balance()}")
        
    def print_history(self):
        self.transaction.get_history()
    #ATM communicates with the database to log the current user out
    def logout(self):
        self.database.logout()


def main():
    
    AtmObj = ATM()
    
    #Keep running ATM until END is entered
    while True:
        #The purpose of this code is to logout after 2 minutes
        #If no activity has been done.
        #I have commented this functionality out because it hasn't been
        #fully tested
        #user_authorized = AtmObj.access_authorization_level()
        #if user_authorized: - We can only logout if theres an active acc
            #timeout = 120
            #t = Timer(timeout, AtmObj.logout) -
            #t.start() -Waits 2 minutes for a response before logging out
        ########################################################
        
        choice = list(input("Input: ").split())
        
        if choice[0] == "authorize":
            AtmObj.authorize(choice[1], choice[2])
            
        elif choice[0] == "withdraw" or  choice[0] =="deposit":
            
            user_authorized = AtmObj.access_authorization_level()
            try:
                if user_authorized != None:
                    transaction_action = choice[0]
                    amount = float(choice[1])
                    AtmObj.select_transaction(transaction_action, amount)
                else:
                    print("Authorization required.")
            except:
                print("Bad input. Please try again")
        
        elif choice[0] == "balance":
            user_authorized = AtmObj.access_authorization_level()
            if user_authorized != None:
                AtmObj.print_balance()
            else:
                print("Authorization required.")
            
        elif choice[0] == "history":
            user_authorized = AtmObj.access_authorization_level()
            if user_authorized != None:
                AtmObj.print_history()
            else:
                print("Authorization required.")
            
        elif choice[0] == "logout":
            user_authorized = AtmObj.access_authorization_level()
            if user_authorized != None:
                AtmObj.logout()
            else:
                print("No account is currently authorized")
            
        elif choice[0] == "end":
            break
        
        elif choice[0] == "signup":
            account_id = choice[1]
            pin = choice[2]
            balance = choice[3]
            AtmObj.signup(account_id, pin, balance)
        
        else:
            print(f"{choice} is not a valid input. Please try again")
        
        #Spacing for each input    
        print("")

if __name__ == "__main__":
    main()

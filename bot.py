from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    """
    Base class for fields of a contact record.
    """
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

class Name(Field):
    """
    Class for storing the contact's name.
    """
    pass

class Phone(Field):
    """
    Class for storing a phone number.
    """
    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("The phone number must contain 10 digits!")
        super().__init__(value)

class Birthday(Field):
    """
    Class for storing the contact's birthday.
    """
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY!")

class Record:
    """
    Class for storing contact information.
    """
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        """
        Adds a phone number to the contact.
        """
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        """
        Removes a phone number from the contact by its value.
        """
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone: str, new_phone: str):
        """
        Edits a phone number by replacing the old phone with the new phone.
        """
        new_phone_obj = Phone(new_phone)  # Validates the new phone number

        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone_obj.value
                return
        raise ValueError(f"Phone number {old_phone} not found!")

    def find_phone(self, phone: str) -> Phone|None:
        """
        Finds and returns a Phone object by its number.
        Returns None if the phone number is not found.
        """
        for number in self.phones:
            if number.value == phone:
                return number
        return None
    
    def add_birthday(self, birthday_contact: str):
        """
        Adds a birthday to the contact.
        """
        self.birthday = Birthday(birthday_contact)

    def __str__(self) -> str:
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "not set"
        return f"Contact name: {self.name.value}, birthday: {birthday_str}, phones: {', '.join(phone.value for phone in self.phones)}."

class AddressBook(UserDict):
    """
    Class for storing and managing contact records.
    """
    def add_record(self, record: Record):
        """
        Adds a record to the address book.
        """
        self.data[record.name.value] = record

    def find(self, name: str) -> Record|None:
        """
        Finds and returns a contact record by name.
        Returns None if the contact is not found.
        """
        return self.data.get(name)

    def delete(self, name: str):
        """
        Deletes a contact record by name.
        """
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days = 7) -> list[dict[str, str]]:
        """
        Lists contacts with birthdays in the next 'days' days.
        """
        def find_next_weekday(start_date: date, weekday: int) -> date:
            """Finds the next specified weekday after start_date."""
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        def adjust_for_weekend(birthday: date) -> date:
            """Moves birthday to Monday if it falls on a weekend."""
            if birthday.weekday() >= 5:
                return find_next_weekday(birthday, 0)
            return birthday
        
        upcoming_birthdays = []
        today = date.today()
        
        for record in self.data.values():
            if not record.birthday:
                continue
                
            birthday_this_year = record.birthday.value.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = record.birthday.value.replace(year=today.year + 1)
            
            if 0 <= (birthday_this_year - today).days <= days:
                birthday_this_year = adjust_for_weekend(birthday_this_year)
                congratulation_date_str = birthday_this_year.strftime("%d.%m.%Y")
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date_str
                    })
        
        return upcoming_birthdays

    def __str__(self) -> str:
        return '\n'.join(str(record) for record in self.data.values())
    

def input_error(func):
    '''
    Decorator for handling user input errors.
    '''
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Enter the required arguments for the command!"
        except IndexError:
            return "Enter the required arguments for the command!"
        except KeyError:
            return "Contact not found!"
    return inner

def parse_input(user_input):
    '''
    Splits the input string into words, using a space as a separator.
    '''
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    '''
    Add a new contact to the contact directory.
    '''
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        try:
            record.add_phone(phone)
        except ValueError as e:
            return str(e)
    return message

@input_error
def change_contact(args, book: AddressBook):
    '''
    Updates the phone number of an existing contact.
    '''
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is not None:
        try:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated."
        except ValueError as e:
            return str(e)
    raise KeyError
    

@input_error
def show_phone(args, book: AddressBook):
    '''
    Retrieves and displays the phone number of a given contact.
    '''
    if len(args) > 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record is not None:
        contacts = ", ".join(phone.value for phone in record.phones)
        return f"Contact phone numbers {name} - {contacts}."
    raise KeyError

@input_error
def show_all(args, book: AddressBook):
    '''
    Displays all saved contacts.
    '''
    if len(args) > 0:
        raise IndexError
    if not book.data:
        return "No contacts found!"
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    '''
    Adds a birthday date to an existing contact.
    '''
    name, birthday = args
    record = book.find(name)
    if record is not None:
        try:
            record.add_birthday(birthday)
            return f"Birthday added."
        except ValueError as e:
            return str(e)
    raise KeyError

@input_error
def show_birthday(args, book: AddressBook):
    '''
    Shows the birthday of a specified contact.
    '''
    if len(args) > 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record is not None:
        if record.birthday:
            return f"Birthday of {name} is {record.birthday.value.strftime("%d.%m.%Y")}."
        return f"No birthday recorded for {name}!"
    raise KeyError

@input_error
def birthdays(args ,book: AddressBook):
    '''
    Lists contacts with birthdays in the next 7 days.
    '''
    if len(args) > 0:
        raise IndexError
    records = book.get_upcoming_birthdays()
    if records:
          return "\n".join([f"Name: {record["name"]}, birthday: {record["birthday"]}" for record in records])
    return "No birthdays for the next 7 days!"

def main():
    book = AddressBook() # Address book for storing contacts
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break  # Exit the loop and terminate the program

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
import functools
from collections import UserDict
from datetime import datetime, timedelta
from typing import Optional


class Field:
    
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    
    pass


class Phone(Field):
    
    def __init__(self, value: str):
        if not self.validate(value):
            raise ValueError("Телефон має містити рівно 10 цифр.")
        super().__init__(value)

    @staticmethod
    def validate(phone: str) -> bool:
        return len(phone) == 10 and phone.isdigit()


class Birthday(Field):
    
    def __init__(self, value: str):
        try:
            
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Optional[Birthday] = None  

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Телефон не знайдено.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Телефон не знайдено.")

    def find_phone(self, phone: str) -> Optional[Phone]:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str) -> None:
       
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self) -> list[dict[str, str]]:
        
        upcoming = []
        today = datetime.today().date()
        
        for record in self.data.values():
            if record.birthday:
                bdate = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                
                try:
                    bdate_this_year = bdate.replace(year=today.year)
                except ValueError:
                    bdate_this_year = bdate.replace(year=today.year, month=2, day=28)
                
                if bdate_this_year < today:
                    try:
                        bdate_this_year = bdate_this_year.replace(year=today.year + 1)
                    except ValueError:
                        
                        bdate_this_year = bdate_this_year.replace(year=today.year + 1, month=2, day=28)
                    
                days_until = (bdate_this_year - today).days
                
                if 0 <= days_until <= 7:
                    
                    if bdate_this_year.weekday() == 5:  
                        bdate_this_year += timedelta(days=2)
                    elif bdate_this_year.weekday() == 6:  
                        bdate_this_year += timedelta(days=1)
                        
                    upcoming.append({
                        "name": record.name.value, 
                        "congratulation_date": bdate_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming


def input_error(func):
   
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
        except Exception as e:
            return f"Error: {e}"
    return inner


@input_error
def parse_input(user_input: str) -> tuple[str, list[str]]:
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    if len(args) < 3:
        raise ValueError("Give me name, old phone and new phone please.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    raise KeyError


@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {'; '.join(p.value for p in record.phones)}"
    raise KeyError


@input_error
def show_all(book: AddressBook) -> str:
    if not book.data:
        return "Contacts list is empty."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args: list[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Give me name and birthday (DD.MM.YYYY).")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    raise KeyError


@input_error
def show_birthday(args: list[str], book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    elif record:
        return f"{name} doesn't have a birthday saved."
    raise KeyError


@input_error
def birthdays(book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join(f"{u['name']}: {u['congratulation_date']}" for u in upcoming)


def main() -> None:
    
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue

        command_data = parse_input(user_input)
        if isinstance(command_data, str):
            print(command_data)
            continue
            
        command, args = command_data

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
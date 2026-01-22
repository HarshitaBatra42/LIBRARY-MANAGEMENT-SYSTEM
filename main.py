import json
import random
import string
from pathlib import Path
from datetime import datetime

class Library:
    database="library.json"
    data={"books" : [], "members" : []}

    #load data to json

    if Path(database).exists():
        with open(database,"r") as f:
            content=f.read().strip()
            if content:
                data=json.loads(content)
    else:
        with open(database,"w") as f:
            json.dump(data,f,indent=4)


    def gen_id(Prefix = "B"):
        random_id=""
        for i in range(5):
            random_id+=random.choice(string.ascii_uppercase + string.digits)
        return Prefix + "-" + random_id
    

    @classmethod
    def save_data(cls):
        with open(cls.database,"w") as f:
            json.dump(cls.data,f,indent=4,default=str)

    


    def add_book(self):
        title=input("Enter Book Title: ")
        author=input("Enter book author:")
        copies=int(input("how many copies: "))
        book={
            "id":Library.gen_id(),
            "title":title,
            "author":author,
            "total_copies":copies,
            "avaliable_copies":copies,
            "added_on":datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }
        Library.data['books'].append(book)
        Library.save_data()


    def list_books(self):
        if not Library.data['books']:
            print("No books available in the library.")
            return
        for b in Library.data['books']:
            print(f"{b['id']:12} {b['title'] [:24]:25} {b['author'] [:19]:20} {b['total_copies']}/{b['avaliable_copies']:>3}")
        
        print()

    def add_member(self):
        name=input("Enter the name:-")
        email=input("Enter the email:-")
        member={
            "id":Library.gen_id("M"),
            "name":name,
            "email":email,
            "borrowed":[]
        }
        Library.data['members'].append(member)
        Library.save_data()
        print("Member added successfully!")

    def list_members(self):
        if not Library.data['members']:
            print("No members in the library.")
            return
        for m in Library.data['members']:
            print(f"{m['id']:12} {m['name'] [:24]:25} {m['email'] [:29]:30} Borrowed Books: {len(m['borrowed'])}")
        print()

    def borrow(self):
        member_id = input("Enter member id:-").strip()
        members = [m for m in Library.data['members'] if m['id'] == member_id]
        if not members:
            print("Member not found!")
            return
        member = members[0]

        book_id = input("Enter book id:-").strip()
        books = [b for b in Library.data['books'] if b['id'] == book_id]
        if not books:
            print("Book not found!")
            return
        book = books[0]

        if book['avaliable_copies'] <= 0:
            print("No copies available for borrowing.")
            return
        borrow_entry = {
            "book_id":book['id'],
            "title":book['title'],
            "borrow_on":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        member['borrowed'].append(borrow_entry) 
        book['avaliable_copies'] -= 1
        Library.save_data()

    def return_book(self):
        member_id = input("Enter member id:-").strip()
        members = [m for m in Library.data['members'] if m['id'] == member_id]
        if not members:
            print("Member not found!")
            return
        member = members[0]

        if not member['borrowed']:
            print("This member has not borrowed any books.")
            return
        print("Borrowed Books:")

        for i,b in enumerate(member['borrowed'],start=1):
            print(f"{i}. {b['book_id']:12} {b['title'] [:24]:25} Borrowed on: {b['borrow_on']}")

        try:
            choice=int(input("Enter number to return:-"))
            selected=member['borrowed'].pop(choice-1)
        except Exception as err:
            print("Invalid choice!")
        
        books = [b for b in Library.data['books'] if b['id'] == selected['book_id']]
        if books:
            books[0]['avaliable_copies'] += 1
        Library.save_data()


hello=Library()

while True:
    print("="*50)
    print("Library Management System")
    print("="*50)
    print("1. Add Books")
    print("2. List Books")
    print("3. Add Members")
    print("4. List Members")
    print("5. Borrow Books")
    print("6. Return Books")
    print("0. Exit the Portal")
    print("-"*50)

    choice=(input("What task you want to do?"))

    if choice=="1":
        hello.add_book()

    if choice=="2":
        hello.list_books()

    if choice=="3":
        hello.add_member()

    if choice=="4":
        hello.list_members()

    if choice=="5":
        hello.borrow()

    if choice=="6":
        hello.return_book()

    if choice=="0":
        exit(0)

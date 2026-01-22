import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime

# -------------------- CONFIG --------------------
DATABASE = "library.json"

# -------------------- HELPERS --------------------
def gen_id(prefix="B"):
    return prefix + "-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


def load_data():
    if Path(DATABASE).exists():
        with open(DATABASE, "r") as f:
            return json.load(f)
    else:
        data = {"books": [], "members": []}
        save_data(data)
        return data


def save_data(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


data = load_data()

# -------------------- UI --------------------
st.set_page_config(page_title="Library Management System", layout="centered")
st.title("📚 Library Management System")

menu = st.sidebar.selectbox(
    "Select an option",
    ["Dashboard", "Add Book", "List Books", "Add Member", "List Members", "Borrow Book", "Return Book"]
)

# -------------------- DASHBOARD --------------------
if menu == "Dashboard":
    st.subheader("Library overview")
    total_books = sum(b.get("total_copies", 0) for b in data["books"])
    available_books = sum(b.get("available_copies", 0) for b in data["books"])
    total_members = len(data["members"])
    st.metric("Total book copies", total_books)
    st.metric("Available copies", available_books)
    st.metric("Total members", total_members)

    st.markdown("### Recent Books")
    recent = sorted(data["books"], key=lambda x: x.get("added_on",""), reverse=True)[:10]
    if recent:
        st.table([{
            "id": b["id"],
            "title": b["title"],
            "author": b["author"],
            "available/total": f"{b.get('available_copies',0)}/{b.get('total_copies',0)}",
            "added_on": b.get("added_on","")
        } for b in recent])
    else:
        st.write("No books yet.")

# -------------------- ADD BOOK --------------------
elif menu == "Add Book":
    st.subheader("➕ Add Book")

    title = st.text_input("Book Title")
    author = st.text_input("Author")
    copies = st.number_input("Total Copies", min_value=1, step=1)

    if st.button("Add Book"):
        book = {
            "id": gen_id("B"),
            "title": title,
            "author": author,
            "total_copies": copies,
            "available_copies": copies,
            "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["books"].append(book)
        save_data(data)
        st.success("Book added successfully!")

# -------------------- LIST BOOKS --------------------
elif menu == "List Books":
    st.subheader("📖 Available Books")

    if not data["books"]:
        st.info("No books available.")
    else:
        st.table(data["books"])

# -------------------- ADD MEMBER --------------------
elif menu == "Add Member":
    st.subheader("➕ Add Member")

    name = st.text_input("Member Name")
    email = st.text_input("Email")

    if st.button("Add Member"):
        member = {
            "id": gen_id("M"),
            "name": name,
            "email": email,
            "borrowed": []
        }
        data["members"].append(member)
        save_data(data)
        st.success("Member added successfully!")

# -------------------- LIST MEMBERS --------------------
elif menu == "List Members":
    st.subheader("👥 Members")

    if not data["members"]:
        st.info("No members found.")
    else:
        members_display = [{"id": m["id"], "name": m["name"], "email": m["email"], "borrowed_count": len(m.get("borrowed", []))} for m in data["members"]]
        st.table(members_display)

# -------------------- BORROW BOOK --------------------
elif menu == "Borrow Book":
    st.subheader("📕 Borrow Book")

    member_ids = [m["id"] for m in data["members"]]
    book_ids = [b["id"] for b in data["books"] if b["available_copies"] > 0]

    if not member_ids or not book_ids:
        st.warning("Members or available books not found.")
    else:
        member_id = st.selectbox("Select Member ID", member_ids)
        book_id = st.selectbox("Select Book ID", book_ids)

        if st.button("Borrow"):
            member = next(m for m in data["members"] if m["id"] == member_id)
            book = next(b for b in data["books"] if b["id"] == book_id)

            # Prevent duplicate borrowing
            if any(b["book_id"] == book_id for b in member["borrowed"]):
                st.error("This member already borrowed this book.")
            else:
                member["borrowed"].append({
                    "book_id": book["id"],
                    "title": book["title"],
                    "borrow_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                book["available_copies"] -= 1
                save_data(data)
                st.success("Book borrowed successfully!")

# -------------------- RETURN BOOK --------------------
elif menu == "Return Book":
    st.subheader("📗 Return Book")

    member_ids = [m["id"] for m in data["members"] if m["borrowed"]]

    if not member_ids:
        st.info("No borrowed books found.")
    else:
        member_id = st.selectbox("Select Member ID", member_ids)
        member = next(m for m in data["members"] if m["id"] == member_id)

        borrowed_titles = [b["title"] for b in member["borrowed"]]
        choice = st.selectbox("Select Book to Return", borrowed_titles)

        if st.button("Return Book"):
            borrowed_book = next(b for b in member["borrowed"] if b["title"] == choice)
            member["borrowed"].remove(borrowed_book)

            book = next(b for b in data["books"] if b["id"] == borrowed_book["book_id"])
            book["available_copies"] += 1

            save_data(data)
            st.success("Book returned successfully!")

"""
CampusSolve - Library Record Application
A beginner-friendly, menu-driven Python project.

Run:
    python campus_solve.py

Data is saved automatically in library_data.json.
Reports are created in the reports folder.
"""

import csv
import json
import os
from collections import Counter
from datetime import date, datetime, timedelta

DATA_FILE = "library_data.json"
REPORT_DIR = "reports"
LOAN_DAYS = 14


def empty_database():
    return {"books": [], "members": [], "loans": []}


def load_data():
    """Load saved records. Create a clean database if the file is missing/corrupt."""
    if not os.path.exists(DATA_FILE):
        return empty_database()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        for key in ("books", "members", "loans"):
            if key not in data or not isinstance(data[key], list):
                data[key] = []
        return data
    except (json.JSONDecodeError, OSError):
        print("Warning: The data file could not be read. Starting with an empty database.")
        return empty_database()


def save_data():
    """Save all records safely to a JSON file."""
    temporary_file = DATA_FILE + ".tmp"
    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(db, file, indent=4)
    os.replace(temporary_file, DATA_FILE)


db = load_data()


def ask_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be blank. Please try again.")


def ask_integer(prompt, minimum=1):
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
            if number < minimum:
                print(f"Enter a number greater than or equal to {minimum}.")
            else:
                return number
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def find_book(book_id):
    return next((b for b in db["books"] if b["book_id"].lower() == book_id.lower()), None)


def find_member(member_id):
    return next((m for m in db["members"] if m["member_id"].lower() == member_id.lower()), None)


def active_loan_for_book(book_id):
    return next((loan for loan in db["loans"]
                 if loan["book_id"].lower() == book_id.lower()
                 and loan["status"] == "Issued"), None)


def add_book():
    print("\n--- Add Book ---")
    book_id = ask_text("Book ID: ")
    if find_book(book_id):
        print("A book with this ID already exists.")
        return
    title = ask_text("Book title: ")
    author = ask_text("Author: ")
    category = ask_text("Category: ")
    quantity = ask_integer("Number of copies: ")
    db["books"].append({
        "book_id": book_id, "title": title, "author": author,
        "category": category, "quantity": quantity, "available": quantity
    })
    save_data()
    print("Book added successfully.")


def view_books():
    print("\n--- Book Catalogue ---")
    if not db["books"]:
        print("No books found. Add a book first.")
        return
    print(f"{'ID':<12} {'TITLE':<28} {'AUTHOR':<20} {'TOTAL':>7} {'AVAILABLE':>10}")
    print("-" * 82)
    for b in db["books"]:
        print(f"{b['book_id']:<12} {b['title'][:27]:<28} {b['author'][:19]:<20} "
              f"{b['quantity']:>7} {b['available']:>10}")


def register_member():
    print("\n--- Register Member ---")
    member_id = ask_text("Member ID: ")
    if find_member(member_id):
        print("A member with this ID already exists.")
        return
    name = ask_text("Full name: ")
    department = ask_text("Department/class: ")
    phone = ask_text("Phone or contact number: ")
    db["members"].append({
        "member_id": member_id, "name": name,
        "department": department, "phone": phone
    })
    save_data()
    print("Member registered successfully.")


def view_members():
    print("\n--- Registered Members ---")
    if not db["members"]:
        print("No members registered yet.")
        return
    print(f"{'ID':<12} {'NAME':<25} {'DEPARTMENT':<20} {'CONTACT':<16}")
    print("-" * 76)
    for m in db["members"]:
        print(f"{m['member_id']:<12} {m['name'][:24]:<25} "
              f"{m['department'][:19]:<20} {m['phone'][:15]:<16}")


def issue_book():
    print("\n--- Issue Book ---")
    book_id = ask_text("Book ID: ")
    book = find_book(book_id)
    if not book:
        print("Book ID not found.")
        return
    if book["available"] <= 0:
        print("This book is currently unavailable.")
        return
    member_id = ask_text("Member ID: ")
    member = find_member(member_id)
    if not member:
        print("Member ID not found. Register the member first.")
        return
    due = date.today() + timedelta(days=LOAN_DAYS)
    loan_id = f"L{len(db['loans']) + 1:04d}"
    db["loans"].append({
        "loan_id": loan_id, "book_id": book["book_id"],
        "member_id": member["member_id"],
        "issue_date": date.today().isoformat(),
        "due_date": due.isoformat(), "return_date": "",
        "status": "Issued"
    })
    book["available"] -= 1
    save_data()
    print(f"Book issued successfully. Loan ID: {loan_id}")
    print(f"Due date: {due.isoformat()}")


def return_book():
    print("\n--- Return Book ---")
    loan_id = ask_text("Loan ID: ")
    loan = next((x for x in db["loans"]
                 if x["loan_id"].lower() == loan_id.lower()
                 and x["status"] == "Issued"), None)
    if not loan:
        print("Active loan not found. Check the Loan ID or whether it was already returned.")
        return
    loan["status"] = "Returned"
    loan["return_date"] = date.today().isoformat()
    book = find_book(loan["book_id"])
    if book:
        book["available"] += 1
    save_data()
    print("Book returned successfully.")
    due = date.fromisoformat(loan["due_date"])
    if date.today() > due:
        print(f"Overdue return: { (date.today() - due).days } day(s) late.")


def view_loans():
    print("\n--- Issue / Return Records ---")
    if not db["loans"]:
        print("No issue records found.")
        return
    print(f"{'LOAN':<9} {'BOOK':<12} {'MEMBER':<12} {'ISSUED':<12} {'DUE':<12} {'STATUS':<10}")
    print("-" * 72)
    for loan in db["loans"]:
        print(f"{loan['loan_id']:<9} {loan['book_id']:<12} {loan['member_id']:<12} "
              f"{loan['issue_date']:<12} {loan['due_date']:<12} {loan['status']:<10}")


def search_records():
    print("\n--- Search Records ---")
    keyword = ask_text("Enter a book title, author, category, book ID, member name or ID: ").lower()
    matches = []
    for b in db["books"]:
        if any(keyword in str(b[k]).lower() for k in ("book_id", "title", "author", "category")):
            matches.append(f"BOOK: {b['book_id']} | {b['title']} | {b['author']} | Available: {b['available']}")
    for m in db["members"]:
        if any(keyword in str(m[k]).lower() for k in ("member_id", "name", "department")):
            matches.append(f"MEMBER: {m['member_id']} | {m['name']} | {m['department']}")
    for loan in db["loans"]:
        if keyword in loan["loan_id"].lower() or keyword in loan["book_id"].lower() or keyword in loan["member_id"].lower():
            matches.append(f"LOAN: {loan['loan_id']} | Book: {loan['book_id']} | Member: {loan['member_id']} | {loan['status']}")
    if matches:
        for item in matches:
            print("-", item)
    else:
        print("No matching records found.")


def overdue_loans():
    today = date.today()
    overdue = []
    for loan in db["loans"]:
        if loan["status"] == "Issued" and date.fromisoformat(loan["due_date"]) < today:
            overdue.append(loan)
    return overdue


def show_summary():
    print("\n--- Library Summary ---")
    total_copies = sum(b["quantity"] for b in db["books"])
    available = sum(b["available"] for b in db["books"])
    issued = sum(1 for x in db["loans"] if x["status"] == "Issued")
    returned = sum(1 for x in db["loans"] if x["status"] == "Returned")
    overdue = overdue_loans()
    print(f"Different book titles : {len(db['books'])}")
    print(f"Total book copies     : {total_copies}")
    print(f"Available copies      : {available}")
    print(f"Registered members    : {len(db['members'])}")
    print(f"Currently issued      : {issued}")
    print(f"Returned transactions : {returned}")
    print(f"Overdue books         : {len(overdue)}")
    if overdue:
        print("\nWARNING - Overdue records:")
        for loan in overdue:
            member = find_member(loan["member_id"])
            book = find_book(loan["book_id"])
            print(f"  {loan['loan_id']}: {book['title'] if book else loan['book_id']} "
                  f"with {member['name'] if member else loan['member_id']} "
                  f"(due {loan['due_date']})")
    categories = Counter(b["category"] for b in db["books"])
    if categories:
        print("\nBooks by category:")
        for category, count in categories.most_common():
            print(f"  {category}: {count} title(s)")


def export_reports():
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(REPORT_DIR, f"library_report_{stamp}.csv")
    md_path = os.path.join(REPORT_DIR, f"library_summary_{stamp}.md")

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Record Type", "ID", "Title/Name", "Details", "Status"])
        for b in db["books"]:
            writer.writerow(["Book", b["book_id"], b["title"],
                             f"Author: {b['author']}; Category: {b['category']}; "
                             f"Total: {b['quantity']}; Available: {b['available']}", ""])
        for m in db["members"]:
            writer.writerow(["Member", m["member_id"], m["name"],
                             f"Department: {m['department']}; Contact: {m['phone']}", ""])
        for loan in db["loans"]:
            writer.writerow(["Loan", loan["loan_id"], loan["book_id"],
                             f"Member: {loan['member_id']}; Issued: {loan['issue_date']}; "
                             f"Due: {loan['due_date']}; Returned: {loan['return_date']}",
                             loan["status"]])

    with open(md_path, "w", encoding="utf-8") as file:
        file.write("# CampusSolve - Library Summary\n\n")
        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write("## Key Statistics\n\n")
        file.write(f"- Book titles: {len(db['books'])}\n")
        file.write(f"- Total copies: {sum(b['quantity'] for b in db['books'])}\n")
        file.write(f"- Members: {len(db['members'])}\n")
        file.write(f"- Active issues: {sum(x['status'] == 'Issued' for x in db['loans'])}\n")
        file.write(f"- Overdue loans: {len(overdue_loans())}\n\n")
        file.write("## Book Catalogue\n\n| ID | Title | Author | Available |\n|---|---|---|---:|\n")
        for b in db["books"]:
            file.write(f"| {b['book_id']} | {b['title']} | {b['author']} | {b['available']} |\n")
        file.write("\n## Overdue Warnings\n\n")
        late = overdue_loans()
        if late:
            for loan in late:
                file.write(f"- {loan['loan_id']}: Book {loan['book_id']} with member "
                           f"{loan['member_id']} was due on {loan['due_date']}.\n")
        else:
            file.write("No overdue books at the time of report generation.\n")
    print("Reports generated successfully:")
    print("CSV:", csv_path)
    print("Markdown:", md_path)


def import_books_csv():
    print("\n--- Bulk Book Import ---")
    path = ask_text("CSV file path (example: sample_books.csv): ")
    if not os.path.isfile(path):
        print("File not found. Check the path and try again.")
        return
    added = 0
    errors = []
    try:
        with open(path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            required = {"book_id", "title", "author", "category", "quantity"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                print("CSV must contain these headings: book_id,title,author,category,quantity")
                return
            for row_number, row in enumerate(reader, start=2):
                try:
                    book_id = row["book_id"].strip()
                    title = row["title"].strip()
                    author = row["author"].strip()
                    category = row["category"].strip()
                    quantity = int(row["quantity"])
                    if not all((book_id, title, author, category)) or quantity < 1:
                        raise ValueError("blank field or quantity less than 1")
                    if find_book(book_id):
                        raise ValueError("duplicate book ID")
                    db["books"].append({
                        "book_id": book_id, "title": title, "author": author,
                        "category": category, "quantity": quantity, "available": quantity
                    })
                    added += 1
                except (ValueError, TypeError, KeyError) as error:
                    errors.append(f"Row {row_number}: {error}")
        save_data()
        print(f"Imported {added} book(s).")
        if errors:
            print("Rows skipped due to errors:")
            for error in errors:
                print(" -", error)
    except OSError as error:
        print("Could not read the CSV file:", error)


def load_sample_data():
    """Add a small demo set only when the database is empty."""
    if db["books"] or db["members"]:
        print("Sample data is added only when books and members are empty.")
        return
    db["books"] = [
        {"book_id": "B101", "title": "Python Basics", "author": "A. Kumar",
         "category": "Programming", "quantity": 5, "available": 5},
        {"book_id": "B102", "title": "Data Structures", "author": "R. Sharma",
         "category": "Computer Science", "quantity": 3, "available": 3},
        {"book_id": "B103", "title": "Web Development", "author": "S. Rao",
         "category": "Technology", "quantity": 4, "available": 4},
    ]
    db["members"] = [
        {"member_id": "M101", "name": "Ananya", "department": "IT-A", "phone": "9000000001"},
        {"member_id": "M102", "name": "Rahul", "department": "CSE", "phone": "9000000002"},
    ]
    save_data()
    print("Demo books and members added. You can now test issue and return features.")


def main():
    while True:
        print("\n" + "=" * 48)
        print("       CAMPUSSOLVE - LIBRARY RECORD APPLICATION")
        print("=" * 48)
        print("1. Add book")
        print("2. View books")
        print("3. Register member")
        print("4. View members")
        print("5. Issue book")
        print("6. Return book")
        print("7. View issue/return records")
        print("8. Search records")
        print("9. View summary and overdue warnings")
        print("10. Export CSV and Markdown reports")
        print("11. Bulk import books from CSV")
        print("12. Load sample demo data")
        print("0. Save and exit")
        choice = input("\nEnter your choice: ").strip()

        actions = {
            "1": add_book, "2": view_books, "3": register_member,
            "4": view_members, "5": issue_book, "6": return_book,
            "7": view_loans, "8": search_records, "9": show_summary,
            "10": export_reports, "11": import_books_csv, "12": load_sample_data
        }
        if choice == "0":
            save_data()
            print("All records saved. Thank you for using CampusSolve!")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except (OSError, KeyError, ValueError) as error:
                print("The operation could not be completed:", error)
        else:
            print("Invalid menu choice. Please select a number from 0 to 12.")


if __name__ == "__main__":
    main()
    
    
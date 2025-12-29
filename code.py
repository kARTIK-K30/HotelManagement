import json
import datetime

# ---------- JSON UTILITIES ----------
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ---------- LOAD DATA ----------
config = load_json("config.json")
users = load_json("users.json")
rooms = load_json("rooms.json")
bookings = load_json("bookings.json")
bills=load_json("bills.json")

# ---------- AUTHENTICATION ----------
def login():
    print(f"\nWelcome to {config['hotel_name']}")
    username = input("Username: ")
    password = input("Password: ")

    if username in users and users[username]["password"] == password:
        print(f"Login successful ({users[username]['role']})")
        return users[username]["role"]
    else:
        print("Invalid credentials")
        return None

# ---------- VIEW ROOMS ----------
def view_rooms():
    print("\nAvailable Rooms:")
    for room, data in rooms.items():
        if data["available"]:
            print(f"Room {room} | {data['type']} | {data['price']} {config['currency']}")

# ---------- BOOK ROOM ----------
def book_room():
    room_no = input("Enter room number: ")
    guest = input("Guest name: ")

    if room_no in rooms and rooms[room_no]["available"]:
        rooms[room_no]["available"] = False
        bookings[room_no] = {
            "guest": guest,
            "check_in": str(datetime.date.today())
        }

        save_json("rooms.json", rooms)
        save_json("bookings.json", bookings)

        print("Room booked successfully!")
    else:
        print("Room not available")

# ---------- CHECKOUT ----------
def checkout():
    room_no = input("Enter room number: ")

    if room_no in bookings:
        price_per_day = rooms[room_no]["price"]

        # Calculate stay duration
        check_in_date = datetime.datetime.strptime(
            bookings[room_no]["check_in"], "%Y-%m-%d"
        ).date()
        check_out_date = datetime.date.today()

        days_stayed = (check_out_date - check_in_date).days
        days_stayed = max(1, days_stayed)

        room_charge = price_per_day * days_stayed
        tax = room_charge * config["tax_percent"] / 100
        total_payable = room_charge + tax

        # ---------- BILL DATA ----------
        bill = {
            "hotel_name": config["hotel_name"],
            "room_number": room_no,
            "guest_name": bookings[room_no]["guest"],
            "check_in": str(check_in_date),
            "check_out": str(check_out_date),
            "days_stayed": days_stayed,
            "price_per_day": price_per_day,
            "room_charge": room_charge,
            "tax_percent": config["tax_percent"],
            "tax_amount": tax,
            "total_amount": total_payable,
            "currency": config["currency"]
        }

        # ---------- DISPLAY BILL ----------
        print("\n========== HOTEL BILL ==========")
        print(f"Guest Name   : {bill['guest_name']}")
        print(f"Room Number  : {room_no}")
        print(f"Days Stayed  : {days_stayed}")
        print(f"Room Charge  : {room_charge} {config['currency']}")
        print(f"Tax          : {tax} {config['currency']}")
        print("--------------------------------")
        print(f"TOTAL TO PAY : {total_payable} {config['currency']}")
        print("================================")

        # ---------- SAVE BILL ----------
        bills = load_json("bills.json")
        bills.append(bill)
        save_json("bills.json", bills)

        # Reset room & booking
        rooms[room_no]["available"] = True
        del bookings[room_no]

        save_json("rooms.json", rooms)
        save_json("bookings.json", bookings)

        print("Checkout completed & bill saved successfully!")
    else:
        print("No booking found.")


# ---------- MAIN MENU ----------
def main():
    role = login()
    if not role:
        return

    while True:
        print("\n1. View Rooms")
        print("2. Book Room")
        print("3. Checkout")
        print("4. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            view_rooms()
        elif choice == "2":
            if role in ["ADMIN", "RECEPTIONIST"]:
                book_room()
            else:
                print("Access denied")
        elif choice == "3":
            checkout()
        elif choice == "4":
            print("Thank you!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()

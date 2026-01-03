import json
import datetime

# ---------- JSON UTILITIES ----------
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ---------- LOAD DATA ----------
config   = load_json("config.json", {})
users    = load_json("users.json", {})
rooms    = load_json("rooms.json", {})
bookings = load_json("bookings.json", {})
bills    = load_json("bills.json", [])

# ---------- SYNC ROOMS WITH BOOKINGS ----------
def sync_rooms():
    for room_no in rooms:
        rooms[room_no]["available"] = room_no not in bookings
    save_json("rooms.json", rooms)

sync_rooms()

# ---------- AUTHENTICATION ----------
def login():
    print("\n===================================")
    print(f" Welcome to {config['hotel_name']} ")
    print(" Luxury | Comfort | Trust ")
    print("===================================")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if username in users and users[username]["password"] == password:
        print(f"\nLogin successful ({users[username]['role']})")
        return users[username]["role"]
    else:
        print("Invalid credentials.")
        return None

# ---------- CHECK ANY ROOM AVAILABLE ----------
def any_room_available():
    return any(room["available"] for room in rooms.values())

# ---------- VIEW ROOMS ----------
def view_rooms():
    print("\nAvailable Rooms at SMART STAY HOTEL:\n")
    found = False

    for room_no, data in rooms.items():
        if data["available"]:
            print(f" Room {room_no} | {data['type']} | {data['price']} {config['currency']}")
            found = True

    if not found:
        print(" Sorry Sir/Madam, no rooms are available at the moment.")

# ---------- BOOK ROOM ----------
def book_room():
    if not any_room_available():
        print("\nSorry Sir/Madam, no rooms are available at the moment at SMART STAY HOTEL .")
        return

    room_no = input("Enter room number to book: ").strip()

    if room_no not in rooms:
        print("Invalid room number.")
        return

    if not rooms[room_no]["available"]:
        print(f"\nRoom {room_no} is already occupied.")
        if room_no in bookings:
            print(f"Guest Name: {bookings[room_no]['guest']}")
        return

    guest = input("Enter Guest Name: ").strip()

    bookings[room_no] = {
        "guest": guest,
        "check_in": str(datetime.date.today())
    }

    rooms[room_no]["available"] = False

    save_json("bookings.json", bookings)
    save_json("rooms.json", rooms)

    print(f"\nThank you {guest}, your room has been booked successfully.")
    print("We wish you a pleasant stay at SMART STAY HOTEL.")

# ---------- CHECKOUT ----------
def checkout():
    room_no = input("Enter room number for checkout: ").strip()

    if room_no not in bookings:
        print("No active booking found for this room.")
        return

    price = rooms[room_no]["price"]

    check_in = datetime.datetime.strptime(
        bookings[room_no]["check_in"], "%Y-%m-%d"
    ).date()

    check_out = datetime.date.today()
    days = max(1, (check_out - check_in).days)

    room_charge = price * days
    tax = room_charge * config["tax_percent"] / 100
    total = room_charge + tax

    bill = {
        "hotel": config["hotel_name"],
        "room": room_no,
        "guest": bookings[room_no]["guest"],
        "days": days,
        "room_charge": room_charge,
        "tax": tax,
        "total": total,
        "currency": config["currency"]
    }

    print("\n========== SMART STAY HOTEL BILL ==========")
    print(f"Guest Name : {bill['guest']}")
    print(f"Room No    : {room_no}")
    print(f"Days Stay  : {days}")
    print(f"Room Charge: {room_charge} {bill['currency']}")
    print(f"Tax        : {tax} {bill['currency']}")
    print("----------------------------------")
    print(f"TOTAL BILL : {total} {bill['currency']}")
    print("==================================")

    bills.append(bill)
    save_json("bills.json", bills)

    del bookings[room_no]
    rooms[room_no]["available"] = True

    save_json("bookings.json", bookings)
    save_json("rooms.json", rooms)

    print("\nCheckout completed successfully.")
    print("Thank you for choosing SMART STAY HOTEL!")

# ---------- ADMIN RESET (IMPORTANT) ----------
def reset_all_rooms():
    bookings.clear()
    for room in rooms.values():
        room["available"] = True

    save_json("bookings.json", bookings)
    save_json("rooms.json", rooms)

    print("\nAll rooms reset successfully. (Admin)")

# ---------- MAIN MENU ----------
def main():
    role = login()
    if not role:
        return

    while True:
        print("\n------ SMART STAY HOTEL MENU ------")
        print("1. View Available Rooms")
        print("2. Book Room")
        print("3. Checkout")
        print("4. Exit")

        if role == "ADMIN":
            print("5. Reset All Rooms")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_rooms()
        elif choice == "2":
            if role in ["ADMIN", "RECEPTIONIST"]:
                book_room()
            else:
                print("Access denied.")
        elif choice == "3":
            checkout()
        elif choice == "4":
            print("\nThank you for visiting SMART STAY HOTEL Hotel.")
            break
        elif choice == "5" and role == "ADMIN":
            reset_all_rooms()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()

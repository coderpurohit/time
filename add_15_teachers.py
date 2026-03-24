import sqlite3

db_path = r'C:\Users\bhara\time\backend\timetable.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 15 teachers with realistic Indian names
teachers = [
    ("Dr. Rajesh Kumar", "rajesh.kumar@college.edu", 20),
    ("Prof. Priya Sharma", "priya.sharma@college.edu", 20),
    ("Dr. Amit Patel", "amit.patel@college.edu", 20),
    ("Prof. Sneha Desai", "sneha.desai@college.edu", 20),
    ("Dr. Vikram Singh", "vikram.singh@college.edu", 20),
    ("Prof. Kavita Joshi", "kavita.joshi@college.edu", 20),
    ("Dr. Rohit Mehta", "rohit.mehta@college.edu", 20),
    ("Prof. Neha Verma", "neha.verma@college.edu", 20),
    ("Dr. Arjun Reddy", "arjun.reddy@college.edu", 20),
    ("Prof. Pooja Nair", "pooja.nair@college.edu", 20),
    ("Dr. Saurabh Gupta", "saurabh.gupta@college.edu", 20),
    ("Prof. Meera Iyer", "meera.iyer@college.edu", 20),
    ("Dr. Nitin Kulkarni", "nitin.kulkarni@college.edu", 20),
    ("Prof. Shreya Malhotra", "shreya.malhotra@college.edu", 20),
    ("Dr. Ankit Choudhary", "ankit.choudhary@college.edu", 20),
]

print("="*60)
print("ADDING 15 NEW TEACHERS")
print("="*60)

for name, email, hours in teachers:
    # Check if teacher already exists by email
    cursor.execute("SELECT id FROM teachers WHERE email = ?", (email,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"  ⚠️  {name} already exists (email: {email})")
    else:
        cursor.execute("""
            INSERT INTO teachers (name, email, max_hours_per_week)
            VALUES (?, ?, ?)
        """, (name, email, hours))
        print(f"  ✓ Added {name} ({hours} hrs/week)")

conn.commit()

print("\n" + "="*60)
print("ALL TEACHERS IN DATABASE:")
print("="*60)

cursor.execute("SELECT id, name, email, max_hours_per_week FROM teachers ORDER BY id")
all_teachers = cursor.fetchall()

for id, name, email, hours in all_teachers:
    print(f"ID {id:2d}: {name:30s} | {hours} hrs/week")

print(f"\nTotal: {len(all_teachers)} teachers")

conn.close()
print("\n✅ Done! Refresh browser with Ctrl+Shift+R")

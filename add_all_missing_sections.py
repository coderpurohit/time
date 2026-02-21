import sys
sys.path.insert(0, 'backend')

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import ClassGroup

db = SessionLocal()

print("=== ADDING ALL MISSING SECTIONS ===")

# Get existing groups
existing = db.query(ClassGroup).all()
existing_names = [g.name for g in existing]

print(f"\nCurrent groups ({len(existing)}):")
for g in existing:
    print(f"  - {g.name}")

# Define all required groups
required_groups = [
    # SE (Second Year)
    ('SE-AIDS-A', 60),
    ('SE-AIDS-B', 60),
    ('SE-AIDS-C', 60),
    # TE (Third Year)
    ('TE-AIDS-A', 55),
    ('TE-AIDS-B', 55),
    ('TE-AIDS-C', 55),
    # BE (Fourth Year)
    ('BE-AIDS-A', 50),
    ('BE-AIDS-B', 50),
    ('BE-AIDS-C', 50),
]

print(f"\n=== ADDING MISSING GROUPS ===")
added = 0

for name, student_count in required_groups:
    if name not in existing_names:
        group = ClassGroup(
            name=name,
            student_count=student_count
        )
        db.add(group)
        print(f"✅ Added: {name} ({student_count} students)")
        added += 1
    else:
        print(f"⏭️  Exists: {name}")

if added > 0:
    db.commit()
    print(f"\n✅ Added {added} new class groups")
else:
    print(f"\n✅ All groups already exist")

# Verify final state
all_groups = db.query(ClassGroup).all()
print(f"\n=== FINAL STATE ({len(all_groups)} groups) ===")

# Group by year
se_groups = [g for g in all_groups if g.name.startswith('SE-')]
te_groups = [g for g in all_groups if g.name.startswith('TE-')]
be_groups = [g for g in all_groups if g.name.startswith('BE-')]

print("\nSE (Second Year):")
for g in sorted(se_groups, key=lambda x: x.name):
    print(f"  ✓ {g.name} - {g.student_count} students")

print("\nTE (Third Year):")
for g in sorted(te_groups, key=lambda x: x.name):
    print(f"  ✓ {g.name} - {g.student_count} students")

print("\nBE (Fourth Year):")
for g in sorted(be_groups, key=lambda x: x.name):
    print(f"  ✓ {g.name} - {g.student_count} students")

db.close()

print("\n" + "="*60)
print("✅ ALL SECTIONS ADDED!")
print("="*60)
print("\nNow you should see all 9 divisions:")
print("  SE-AIDS: A, B, C")
print("  TE-AIDS: A, B, C")
print("  BE-AIDS: A, B, C")
print("\nRefresh the page and check the Classes/Grades dropdown!")

from app.supabase_client import supabase_admin

def test():
    try:
        users = supabase_admin.auth.admin.list_users()
        print("✅ Supabase connected successfully!")
        print(f"   Total users: {len(users)}")
        for user in users:
            print(f"   - {user.email} ({user.id})")
    except Exception as e:
        print("❌ Failed:", str(e))

test()
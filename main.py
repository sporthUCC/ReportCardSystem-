# main.py
import sys
import traceback

def main() -> int:
    try:
        # 1. Import the AuthService
        from services.auth_service import AuthService
        
        # 2. Import the LoginScreen (UPDATED to point to the screens folder)
        from screens.monster_login import LoginScreen
            
    except ImportError as err:
        print(f"[startup] Import error: {err}", file=sys.stderr)
        traceback.print_exc()
        return 1

    try:
        auth_service = AuthService()
        app = LoginScreen(auth_service)
        app.mainloop()
    except Exception as err:
        print(f"[startup] Fatal error: {err}", file=sys.stderr)
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
# main.py
# Entry point of the Report Card Management System. Run this file to start the app.
import sys
import traceback

def main() -> int:
    # Returns 0 when the app closes normally, or 1 if something goes wrong at startup
    try:
        # Imports are done inside the try block so a missing file or module
        # shows a clear startup error instead of crashing with no explanation.

        # 1. Import the AuthService
        from services.auth_service import AuthService
        
        # 2. Import the LoginScreen (UPDATED to point to the screens folder)
        from screens.monster_login import LoginScreen
            
    except ImportError as err:
        # Print the error to stderr (the error output) along with the full traceback, then exit with code 1
        print(f"[startup] Import error: {err}", file=sys.stderr)
        traceback.print_exc()
        return 1

    try:
        # Create the authentication service and pass it to the login screen,
        # which opens the dashboard for the user's role after a successful login
        auth_service = AuthService()
        app = LoginScreen(auth_service)
        # mainloop keeps the window open and listening for clicks until it is closed
        app.mainloop()
    except Exception as err:
        # Catch any unexpected crash while the app is running and report it
        print(f"[startup] Fatal error: {err}", file=sys.stderr)
        traceback.print_exc()
        return 1

    return 0

# Only run main() when this file is executed directly, not when it is imported.
# sys.exit passes main()'s return value (0 or 1) back to the operating system.
if __name__ == "__main__":
    sys.exit(main())
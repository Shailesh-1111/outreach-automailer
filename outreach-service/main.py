import argparse
from src.pipeline import run_outreach
from src.template import generate_email_html

def preview():
    print("\n--- Interactive Email Preview ---")
    name = input("Enter recipient name (e.g., Amit): ").strip()
    company = input("Enter company name (e.g., TruDoc): ").strip()

    roles = [
        "Full Stack Developer",
        "Software Developer",
        "Full Stack Developer (Backend-Focused)",
        "Full Stack Developer (Frontend-Focused)",
        "Custom"
    ]

    print("\nSelect Role:")
    for i, r in enumerate(roles, start=1):
        print(f"{i}. {r}")

    try:
        choice = int(input("Enter choice (1-5): "))
        if choice == 5:
            role = input("Enter your custom role title: ").strip()
        else:
            role = roles[choice - 1]
    except ValueError:
        print("Invalid choice, defaulting to 'Full Stack Developer'.")
        role = roles[0]

    email_html = generate_email_html(name, company, role)
    
    print("\n" + "="*50)
    print("EMAIL PREVIEW (HTML):")
    print("="*50)
    print(email_html)
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Outreach Email Automation Project")
    parser.add_argument("--preview", action="store_true", help="Interactively generate and preview an email")
    parser.add_argument("--run", action="store_true", help="Run the automated outreach pipeline using contacts.csv")

    args = parser.parse_args()

    if args.preview:
        preview()
    elif args.run:
        run_outreach()
    else:
        parser.print_help()
        print("\nExample: python main.py --run")
        print("Example: python main.py --preview")

if __name__ == "__main__":
    main()

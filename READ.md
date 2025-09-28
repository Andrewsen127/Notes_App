# Flask Notes App with Encryption and Roles

This is a really simple Flask app I made for class to show how security works in a basic system. It uses encryption to protect notes and role based access so not everyone can see everything.

## 
- Lets people log in as either a customer or an admin
- Customers can write notes and they get stored encrypted in my notes so they aren’t sitting around in plain text
- Admins can log in and see everybody’s notes, while customers only see their own
- Shows off least privilege because regular users don’t get admin powers

## Test Accounts
- Customer: `andrew / pass123`
- Admin: `diane / admin123`

## How to Run
Clone the repo and run this in your terminal:

```bash
git clone https://github.com/Andrewsen127/Notes_App
cd flask-notes-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

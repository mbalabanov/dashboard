# Weather & Messaging Dashboard

This Dashboard is written in Python using Flask and Jinja. Users can register and login, they can get weather information through the Open Weather Maps API and they can send each other internal messages within the tool that can be read by other users when they are logged in.

The W&M Dashboard has the following features:
- Register user
- Login with registered user
- Passwords hashed and hash stored in DB
- Hashed session token stored in cookie
- Weather information using the Open Weather Maps API for five selectable cities
- User profile management for changing a user's name, email address and password
- Send messages to other registered users
- Receive messages from other registered users

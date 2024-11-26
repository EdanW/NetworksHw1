TCP Client-Server Program HW1: Protocol Description
===============================================

Overview
--------
This application implements a TCP client-server system where the server provides multiple 
calculation services to connected clients. Communication between the server and clients follows 
a custom application-layer protocol.
The server supports multiple clients simultaneously using `select` to manage socket connections.

Protocol Description
---------------------

General Workflow
----------------
1. **Server Initialization**:
   - The server starts with a user file and an optional port parameter.
   - Users must authenticate with valid credentials stored in the user file.

2. **Communication Format**
   Messages between client and server are terminated with a tab character (\t).
   This is invisible to the use, the server and the client are responsible for adding the tab character.
   - Login messages follow this format: <username>\n<password>\t
	\n: newline character separating username and password.
	\t: tab character signaling the end of the message.
   - Commands adhere to a strict syntax. Incorrectly formatted messages result in disconnection.

4. **Session Management**:
   - Clients must authenticate successfully to issue commands.
   - A `quit` command disconnects the client from the server.

Supported Commands
------------------
1. Login:
   - User need to write his login information, first User:[username]
	then push enter and Password:[password] push enter
   - Client Sends:
     <username>\n<password>\t
   - Server Responds:
     - On success: Hi <username>, good to see you.\t
     - On failure: Failed to login.\t

2. Simple Calculations:
   - User need to write: calculate:<X> <operation> <Y>
   - Client sends: calculate:<X> <operation> <Y>\t
   - Operations Supported:
     - + (addition)
     - - (subtraction)
     - * (multiplication)
     - / (division, rounded to 2 decimal places, denominator ≠ 0)
     - ^ (power, positive exponent only)
   - Server Responds:
     - Successful computation: response: <result>.\t
     - Out of range (signed int32): error: result is too big\t

3. Find Maximum:
   - User need to write: max: <X1> <X2> ... <Xn>
   - Client sends: max: <X1> <X2> ... <Xn>\t
   - Server Responds:: the maximum is: <result>.\t

4. Find Prime Factors:
   - User need to write: factors: <X>
   - Client sends: factors: <X>\t
   - Server Responds: the prime factors of <X> are: <p1>, <p2>, ..., <pn>.\t

5. Disconnect:
   - User need to write: quit
   - Client sends: quit\t
   - Server Responds: Closes the connection without additional messages.

Error Handling
--------------
- Improper Message Format | Invalid Command:
  - Server disconnects the client.
- Failed Login:
  - Allows retry without closing the connection.

Protocol Characteristics
-------------------------
- Transport Layer: TCP.
- Communication:
  - Requests and responses are strictly tab-terminated (`\t`).
- Concurrency:
  - The server uses `select` to handle multiple clients simultaneously.
- The application uses UTF-8 encoding for communication.

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

2. **Client Initialization**:
   - Clients connect to the server with the command ./numbers_client.py [hostname[port]] and authenticate using a username and password.

3. **Message Format**:
   - Commands sent by the client and responses sent by the server are terminated by a tab 
     character (`\t`).
   - Commands adhere to a strict syntax. Incorrectly formatted messages result in disconnection.

4. **Session Management**:
   - Clients must authenticate successfully to issue commands.
   - A `quit` command disconnects the client from the server.

Supported Commands
------------------
1. Login:
   - Client Sends:
     User: <username>\n<password>\t
   - Server Responds:
     - On success: Hi <username>, good to see you.\t
     - On failure: Failed to login.\t

2. Simple Calculations:
   - Command: calculate:<X> <operation> <Y>\t
   - Operations Supported:
     - + (addition)
     - - (subtraction)
     - * (multiplication)
     - / (division, rounded to 2 decimal places, denominator ≠ 0)
     - ^ (power, positive exponent only)
   - Response:
     - Successful computation: response: <result>.\t
     - Out of range (signed int32): error: result is too big\t

3. Find Maximum:
   - Command: max: <X1> <X2> ... <Xn>\t
   - Response: the maximum is: <result>.\t

4. Find Prime Factors:
   - Command: factors: <X>\t
   - Response: the prime factors of <X> are: <p1>, <p2>, ..., <pn>.\t

5. Disconnect:
   - Command: quit\t
   - Response: Closes the connection without additional messages.

Error Handling
--------------
- Invalid Command:
  - Response: error: command not found\t
- Improper Message Format:
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

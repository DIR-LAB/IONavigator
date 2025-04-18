# ION_WEB_SC24

# Project Setup Instructions

## Setting Up the Frontend

1. **Install Node.js and npm**:  
   Ensure you have Node.js and npm installed on your machine. You can download them from [nodejs.org](https://nodejs.org/).

2. **Navigate to the Frontend Directory**:  
   Open your terminal and navigate to the frontend directory.

   ```bash
   cd frontend
   ```

3. **Install Dependencies**:  
   Run the following command to install the necessary dependencies.

   ```bash
   npm install
   ```

4. **Set Environment Variables**:  
   Create a `.env` file in the `frontend` directory and add the following line, replacing the URL with your backend's URL:

   ```
   REACT_APP_FLASK_API_BASE_URL=http://127.0.0.1:5000
   ```

5. **Run the Frontend**:  
   Start the frontend development server.

   ```bash
   npm start
   ```

   This will start the frontend on `http://localhost:3000`.

## Setting Up the Backend

1. **Install Python**:  
   Ensure you have Python and MongoDB installed on your machine. You can download Python from [python.org](https://www.python.org/) and MongoDB from [mongodb.com](https://www.mongodb.com/try/download/community). 

2. **Create a Virtual Environment**:  
   It's a good practice to use a virtual environment for Python projects.

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Navigate to the Backend Directory**:  
   Open your terminal and navigate to the backend directory.

   ```bash
   cd backend
   ```

5. **Install Dependencies**:  
   Run the following command to install the necessary dependencies.

   ```bash
   pip install -r requirements.txt
   ```

6. **Export OPENAI key and MONGO connection string**:
   - On Windows (Powershell)
   ```powershell
   $env:OPENAI_API_KEY = "<your key>"
   $env:MONGODB_CONNECTION_STRING = "mongodb+srv://cegersdo-1:<db_password>@ion-web.9ktqa.mongodb.net/?retryWrites=true&w=majority&appName=ion-web"
   ```

   - On macOS and Linux
    ```bash
   export OPENAI_API_KEY=<your key>
   export MONGODB_CONNECTION_STRING=mongodb+srv://cegersdo-1:<db_password>@ion-web.9ktqa.mongodb.net/?retryWrites=true&w=majority&appName=ion-web
   ```

7. **Run the Backend**:  
   Start the backend server.

   ```bash
   cd src
   python api.py
   ```

   This will start the backend on `http://localhost:5000`.



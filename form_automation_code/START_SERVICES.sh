#!/bin/bash

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node.js dependencies  
cd ../frontend
yarn install

# Start MongoDB (if not running)
# sudo systemctl start mongod

# Start backend (FastAPI)
cd ../backend  
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &

# Start frontend (React)
cd ../frontend
yarn start &

echo "Services starting..."
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8001/docs"

# Wait for services
sleep 5

echo "Test backend:"
echo "curl http://localhost:8001/api/"

echo "Test PDF processing:"
echo "curl -X POST -F \"file=@../content.pdf\" -F \"data=Last Name: TEST\" \"http://localhost:8001/api/fill-form\" --output test_output.pdf"
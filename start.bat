@echo off
echo Starting all services...

start "Group 1 - Syllabus Generator (port 8000)" powershell -NoExit -Command "cd group1-syllabus-generator; python -m uvicorn app.main:app --port 8000 --reload"

start "Group 2 - Mapping Sequencer (port 8001)" powershell -NoExit -Command "cd group2-mapping-sequencer; python -m uvicorn api.main:app --port 8001 --reload"

start "Group 3 - Integration Bridge (port 9000)" powershell -NoExit -Command "python -m uvicorn group3_integration.api:app --port 9000 --reload"

start "Frontend - React UI (port 3000)" powershell -NoExit -Command "cd frontend; npm start"

echo All 4 services launching in separate windows.
echo Group 1: http://localhost:8000/docs
echo Group 2: http://localhost:8001/docs
echo Group 3: http://localhost:9000/docs
echo UI:      http://localhost:3000
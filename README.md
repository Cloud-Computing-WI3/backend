#   News Feed Service
##  Getting started
1. Open a  terminal window inside this folder (`backend`)
2. Run `python3 -m venv venv` to install virtual environment
3. Activate virtual environment
    - Windows User run `.\venv\Scripts\activate`
    - Mac Users run `source ./venv/bin/activate`
4. Install requirements
`pip install -r requirements.txt`

    Notice: API-Files are stored in the sub-folder `api`
4. Start API by running `uvicorn api.main:app --reload`
5. API will be accessible via [ http://127.0.0.1:8000](http://127.0.0.1:8000)
6. Open [http://127.0.0.1:8000/docs]( http://127.0.0.1:8000/docs) to see Swagger-API documentation 
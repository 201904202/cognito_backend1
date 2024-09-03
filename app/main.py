from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from decouple import config

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # S3에서 제공되는 프론트엔드를 허용하기 위해 "*" 대신 S3 도메인을 사용 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수 설정
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
REDIRECT_URI = config("REDIRECT_URI")
COGNITO_DOMAIN = config("COGNITO_DOMAIN")

@app.post("/api/token")
async def get_token(request: Request):
    # 클라이언트로부터 JSON 데이터를 수신하고, 그 중 code 값을 가져옴
    data = await request.json()
    code = data.get("code")

    # code가 없을 경우 에러 메시지 반환
    if not code:
        print("Authorization code is missing")
        return {"error": "Authorization code is missing"}
    
    # 로그에 code 값을 출력하여 확인
    print(f"Received code: {code}")  # 로그에 출력

    # 토큰 요청을 위한 Cognito의 토큰 엔드포인트 URL과 데이터 준비
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    # 요청 헤더 설정
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Cognito로 토큰 요청
    response = requests.post(token_url, data=payload, headers=headers)

    # 요청이 성공했을 경우 토큰 데이터를 JSON 형태로 반환
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token data: {token_data}")  # 로그에 토큰 데이터 출력
        return {
            "access_token": token_data.get("access_token"),
            "id_token": token_data.get("id_token")
        }
    # 요청이 실패했을 경우 에러 메시지와 상세 정보를 반환
    else:
        return {"error": "Failed to retrieve token", "details": response.text}
from email_validator import validate_email, EmailNotValidError
from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from mysql_connection import get_connection

from utils import check_password, hash_password
from mysql.connector import Error

class UserRegisterResource(Resource) :
    
    def post(self) :

        # 클라이언트가 보낸 데이터 받기
        data = request.get_json()

        # 이메일 주소형식 유효성 체크
        try :
            validate_email(data['email'])
        except EmailNotValidError as e :
            print(e)
            return {'error' : str(e)}, 400
        
        # 비밀번호 길이 유효성 체크
        if len(data['password']) < 4 or len(data['password']) > 20 :
            return {'error' : '비밀번호는 4글자 이상 20글자 이하로 설정해주세요.'}, 400
        
        # 비밀번호 암호화
        password = hash_password(data['password'])

        # DB에 회원정보 저장
        try :
            connection = get_connection()
            query = '''insert into user
                        (email, password, nickname)
                        values
                        (%s, %s, %s);'''
            record = (data['email'],
                      password,
                      data['nickname'])
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            user_id = cursor.lastrowid

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        access_token = create_access_token(user_id)

        return {'result' : 'success',
                'accessToken' : access_token}, 200
    
class UserLoginResource(Resource) :

    def post(self) :
        
        # 클라이언트가 보낸 데이터 받기
        data = request.get_json()

        # 유저 테이블에서 이 이메일 주소로 데이터 가져오기
        try :
            connection = get_connection()
            query = '''select *
                        from user
                        where email = %s;'''
            record = (data['email'], )

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
        
        # result_list로 회원가입 했는지 확인
        if len(result_list) == 0 :
            return {'error' : '회원가입 먼저 하십시오'}, 400
        
        # 비밀번호가 맞는지 체크
        check = check_password(data['password'], result_list[0]['password'])
        
        # 비밀번호가 틀릴 경우
        if check == False :
            return{'error' : '비밀번호가 틀렸습니다.'}, 400
        
        # 비밀번호가 맞으면 JWT 토큰을 만들어서 클라이언트에게 응답
        access_token = create_access_token(result_list[0]['id'])

        return {'result' : 'success',
                'accessToken' : access_token}, 200
    
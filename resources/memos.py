from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector import Error

from mysql_connection import get_connection

class MemoListResource(Resource) :
    
    # jwt 토큰
    @jwt_required()
    def post(self) :
        
        # 클라이언트가 보내준 데이터가 있으면 받아준다.
        data = request.get_json()

        # 헤더에 JWT 토큰이 있으면 토큰 정보도 받아준다.
        user_id = get_jwt_identity()

        # 받아온 메모 데이터를 DB에 저장
        try :
            # db에 연결하는 코드
            connection = get_connection()

            # 메모를 생성하는 API니까 insert 쿼리를 만든다.
            query = '''insert into memo
                        (userId, title, date, content)
                        values
                        (%s, %s, %s, %s);'''
            
            # 위의 쿼리에 매칭되는 변수를 튜플로 처리해 준다.
            record = (user_id, data['title'], data['date'], data['content'])

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
            
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        # DB에 잘 저장됐으면, 클라이언트에게 응답

        return {'result' : 'success'}, 200
    
    
    def get(self) :
        # 클라이언트로부터 받을 데이터가 없음

        # DB에 저장된 데이터를 가져옴
        try :
            connection = get_connection()

            query = '''select *
                        from memo;'''
            
            # 중요!!! Select 문에서 커서를 만들 때는 dictionary = True로 해준다.
            # 리스트와 딕셔너리 형태를 클라이언트에게 JSON 형식으로 주기 위해서
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query)

            result_list = cursor.fetchall()

            print(result_list)

            # datetime은 파이썬에서 사용하는 데이터타입이므로 JSON에서 쓰려면 문자열로 바꿔줘야 함.

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {"result" : "success", 
                "items" : result_list,
                "count" : len(result_list)}, 200
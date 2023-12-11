from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class FollowResource(Resource) :

    @jwt_required()
    def post(self, followee_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''insert into follow
                        (followerId, followeeId)
                        values
                        (%s, %s);'''
            record = (user_id, followee_id)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500

        return {'result' : 'success'}, 200
    

    @jwt_required()
    def delete(self, followee_id) :
        
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from follow
                        where followerId = %s and followeeId = %s;'''
            record = (user_id, followee_id)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500

        return {'result' : 'success'}, 200


class FollowMemoResource(Resource) :

    @jwt_required()
    def get(self) :
        
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select m.id as memoId, m.userId, m.title, m.date, m.content, m.createdAt, m.updatedAt, u.nickname
                        from follow f
                        join memo m
                        on f.followeeId = m.userId
                        join user u
                        on m.userId = u.id
                        where f.followerId = %s and m.date > now()
                        order by m.date asc
                        limit '''+ offset +''', '''+ limit +''';'''
            
            record = (user_id, )

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        i = 0
        for row in result_list :
            result_list[i]['date'] = row['date'].isoformat()
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            i = i + 1
        
        return {'result' : 'success',
                'items' : result_list,
                'conut' : len(result_list)}, 200



from flask import Flask, request, jsonify, render_template
import pymysql

app = Flask(__name__)


db_base_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '0000',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

DB_NAME = 'sapce_letter'

def init_db():
    
    conn = pymysql.connect(**db_base_config)
    try:
        with conn.cursor() as cursor:
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            
            conn.select_db(DB_NAME)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(50) DEFAULT 'Earthling',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_sql)
        conn.commit()
        print(f"'{DB_NAME}' 데이터베이스 성공")
    except Exception as e:
        print(f"데이터 베이스 에러: {e}")
    finally:
        conn.close()

def get_db_connection():
    
    return pymysql.connect(**db_base_config, db=DB_NAME)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO messages (title, content) VALUES (%s, %s)"
            cursor.execute(sql, (title, content))
        conn.commit()
        return jsonify({"result": "success", "message": "메시지가 우주로 발송되었습니다."}), 201
    finally:
        conn.close()

@app.route('/api/messages', methods=['GET'])
def get_messages():
    keyword = request.args.get('keyword', '')
    search_type = request.args.get('type', 'all')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM messages WHERE 1=1"
            params = []
            if keyword:
                if search_type == 'title':
                    sql += " AND title LIKE %s"
                    params.append(f"%{keyword}%")
                elif search_type == 'content':
                    sql += " AND content LIKE %s"
                    params.append(f"%{keyword}%")
                else:
                    sql += " AND (title LIKE %s OR content LIKE %s)"
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            sql += " ORDER BY created_at DESC"
            cursor.execute(sql, params)
            result = cursor.fetchall()
        return jsonify(result)
    finally:
        conn.close()

@app.route('/api/messages/<int:id>', methods=['PUT'])
def update_message(id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE messages SET title=%s, content=%s WHERE id=%s"
            cursor.execute(sql, (title, content, id))
        conn.commit()
        return jsonify({"result": "success", "message": "수정 완료!"})
    finally:
        conn.close()

@app.route('/api/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM messages WHERE id=%s"
            cursor.execute(sql, (id,))
        conn.commit()
        return jsonify({"result": "success", "message": "삭제 완료!"})
    finally:
        conn.close()

if __name__ == '__main__':
    
    init_db()
    app.run(debug=True)

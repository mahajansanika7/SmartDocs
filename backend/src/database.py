import pyodbc
import os

CONNECTION_STRING = os.environ.get(
    "SMARTDOCS_CONNECTION_STRING"
)

if not CONNECTION_STRING:
    raise RuntimeError(
        "SMARTDOCS_CONNECTION_STRING environment variable is not set"
    )

def get_connection():
    return pyodbc.connect(CONNECTION_STRING)

def save_data(query, answer, document, user_id):
    connection=get_connection()
    cursor=connection.cursor()
    
    cursor.execute(
        """
        insert into QueryHistory (QueryText, Answer, DocumentName)
        values (?,?,?)
        """,
        (query, answer, document)
    )
    
    cursor.commit()
    
    cursor.close()
    connection.close()
    
def create_user(username, hash_pass):
    connection=get_connection()
    cursor=connection.cursor()
    
    cursor.execute(
        """
        insert into Users (Username, PasswordHash)
        values(?,?)
        """,
        (username, hash_pass)
    )
    
    cursor.commit()
    cursor.close()
    connection.close()
    
    
def get_user(username):
    connection=get_connection()
    cursor=connection.cursor()
    
    cursor.execute(
        """
        select id, username, passwordhash from users
        where username=?
        """,
        (username)
    )
    
    rows=cursor.fetchone()
    cursor.close()
    connection.close()
    if rows is None:
        return None
    
    return {
        "id": rows[0],
        "username": rows[1],
        "passwordHash": rows[2]
    }

def get_query_history(user_id):
    connection=get_connection()
    cursor=connection.cursor()
    
    cursor.execute(
        """
        select queryText, Answer, DocumentName , createdat
        from QueryHistory
        where Id=?
        order by createdAt desc
        """,
        (user_id,)
    )
    
    rows=cursor.fetchall()
    hist=[]
    for row in rows:
        hist.append({
            "query": row[0],
            "answer": row[1],
            "document": row[2],
            "created_at": row[3]
        })
    cursor.close()
    connection.close()
    
    return hist
# if __name__=="__main__":
#     register_user("Sanika12", "123456")
#     print("register successfull")
    
#     print(get_user("Sanika12"))
    
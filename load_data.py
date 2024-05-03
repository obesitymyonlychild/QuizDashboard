from google_drive_downloader import GoogleDriveDownloader as gdd
import os, getpass
import pandas as pd
from sqlalchemy import create_engine, types
from sqlalchemy.exc import SQLAlchemyError


DATAPATH = {"lectures": '1lWsRUJN_WleiIEfvJbb-qu_JB6KR_Vq-', 
         "questions": '1rGg-OhawOrRSbWSl37MlOqVDifTg0kKI',
         "temp": '1Sk8udkEO2np-wWhTfQjxvlB7cw52rQw2'}


def download_file_from_google_drive():
    for file in DATAPATH:
        gdd.download_file_from_google_drive(file_id=DATAPATH[file],
                                            dest_path=f'./data/{file}.csv',
                                            unzip=False)
    print("dowloaded to directory ./data:", ' '.join(os.listdir("./data")))
    return True

def load_csv_to_pandas():
    lec = 'data/lectures.csv'
    q = 'data/questions.csv'
    temp = 'data/temp.csv'
    df = pd.read_csv(temp)
    df_inter = df.rename(columns = {'Unnamed: 0': 'interaction_id'})
    df_inter['interaction_id'] = df_inter['interaction_id'] + 1
    #read csv into pandas dataframe and derive a dataframe for students, the purpose is for future implementation of network features 
    df_q = pd.read_csv(q)
    df_lec=pd.read_csv(lec)
    df_inter = df_inter[['interaction_id', 'user_id', 'timestamp', 'solving_id', 'question_id', 'user_answer', 'elapsed_time']]            
    #derive student id df from interactions
    df_stu = pd.DataFrame(df_inter['user_id'].drop_duplicates().reset_index(drop=True))
    df_stu = df_stu.rename(columns = {'user_id': 'student_id'})
    return df_inter, df_stu, df_q, df_lec


def connect_to_postgresql():
    username = input('Enter your PostgreSQL username: ')
    password = getpass.getpass('Enter your PostgreSQL password: ')
    #host = input('Enter your PostgreSQL host (localhost): ')
    #port = input('Enter your PostgreSQL port (default is 5432): ') or '5432'
    database = input('Enter your PostgreSQL database name: ')
    print("creating engine for: ", username, database)
    engine = create_engine(f'postgresql://{username}:{password}@localhost:5432/{database}')
    try:
        engine.connect()
        print(f"connected to {database}")
        return engine
    except SQLAlchemyError as err:
        print("error", err.__cause__)
        return None
    
def load_pandas_df_to_db(engine, df_inter, df_stu, df_q, df_lec):
    dtypes = {'question_id': types.VARCHAR(length=255), 
                      'bundle_id': types.VARCHAR(length=255),
                      'explanation_id': types.VARCHAR(length=255),
                      'correct_answer':types.CHAR(length=1),
                     'part': types.INTEGER,
                     'tags': types.VARCHAR(length=255),
                     'deployed_at': types.BIGINT}
    df_q.to_sql('questions', con=engine,  if_exists='replace', index=False, chunksize=1000, dtype = dtypes)
    dtypes = {'lecture_id': types.VARCHAR(length=255), 
                     'part': types.INTEGER,
                     'tags': types.VARCHAR(length=255),
                      'video_length': types.INTEGER,
                     'deployed_at': types.BIGINT}
    df_lec.to_sql('lectures', con=engine,  if_exists='replace', index=False, chunksize=1000, dtype = dtypes)
    dtypes = {'student_id': types.INTEGER}
    df_stu.to_sql('students', con=engine,  if_exists='replace', index=False, chunksize=1000, dtype = dtypes)
    dtypes = {'interaction_id': types.INTEGER,
         'user_id': types.INTEGER,
          'timestamp': types.BIGINT,
          'solving_id': types.INTEGER,
          'question_id': types.VARCHAR(length=255), 
          'user_answer':types.CHAR(length=1),
         'elapsed_time': types.INTEGER,
         'tags': types.VARCHAR(length=255),
         'video_length': types.INTEGER}
    df_inter.to_sql('interactions', con=engine,  if_exists='replace', index=False, chunksize=1000, dtype = dtypes)

    #define constraints: interaction_id as a primary key, user_id references student_id, question_id reference question_id
    with engine.connect() as con:
        con.execute("ALTER TABLE questions ADD PRIMARY KEY (question_id);")
        con.execute("ALTER TABLE students ADD PRIMARY KEY (student_id);")
        con.execute("ALTER TABLE lectures ADD PRIMARY KEY (lecture_id);")
        con.execute("ALTER TABLE interactions ADD PRIMARY KEY (interaction_id);")
        con.execute("ALTER TABLE interactions ADD FOREIGN KEY (user_id) REFERENCES students(student_id);")
        con.execute("ALTER TABLE interactions ADD FOREIGN KEY (question_id) REFERENCES questions(question_id);")    
    print("Data saved to database.")
    return True

if __name__ == "__main__":
    #download_file_from_google_drive()
    df_inter, df_stu, df_q, df_lec = load_csv_to_pandas()
    engine = connect_to_postgresql()
    load_pandas_df_to_db(engine, df_inter, df_stu, df_q, df_lec)
    


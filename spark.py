import psycopg2
from pyspark.sql import SparkSession
import pyspark.sql.functions
from pyspark.sql import Window
from pyspark.sql.functions import col, split, explode, array_contains, avg, count, broadcast, when
from pyspark import SparkContext, SparkConf
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from LoadData import *
def init_db():

    engine = connect_to_postgresql()

    q_int = "SELECT * FROM interactions"
    q_stu = "SELECT * FROM students"
    q_lec = "SELECT * FROM lectures"
    q_q = "SELECT * FROM questions"

    # load sql to df
    with engine.connect() as conn:
        df_int = pd.read_sql(q_int, conn)
        df_stu = pd.read_sql(q_stu, conn)
        df_lec = pd.read_sql(q_lec, conn)
        df_q = pd.read_sql(q_q, conn)


    questions = spark.createDataFrame(df_q)
    students = spark.createDataFrame(df_stu)
    lectures = spark.createDataFrame(df_lec)
    interactions = spark.createDataFrame(df_int)

    interactions = interactions.select('user_id','question_id', 'user_answer', 'elapsed_time')
    questions = questions.select('question_id', 'correct_answer', 'tags')
    lectures = lectures.select('lecture_id', 'tags', 'video_length')

    exploded_questions = questions.withColumn("tags_array", explode(split(col("tags"), ";")))

    #left join on the tags column
    joined_df = lectures.join(exploded_questions, lectures.tags == exploded_questions.tags_array, how='left')

    # Select lectures that do not have any associated questions
    lectures_without_questions = joined_df.filter(col("question_id").isNull())

    # Select distinct lectures without questions to avoid duplicate entries
    distinct_lectures_without_questions = lectures_without_questions.select("lecture_id","video_length").distinct()

    ## filter letures that has no associated questions
    lectures = lectures.join(
        distinct_lectures_without_questions,
        on="lecture_id",
        how="left_anti"
    )
    
    return interactions, students, lectures, questions

def analyze_student_performance(student_id):
    # Filter for specific student interactions
    student_specific = correctness_df.filter(col("user_id") == student_id)

    # calculate student's correctness and total questions completed
    correctness_metrics = student_specific.agg(
        avg(when(col("user_answer") == col("correct_answer"), 1).otherwise(0)).alias("student_correctness"),
        count("*").alias("total_count")
    ).collect()[0]
    
    student_correctness = correctness_metrics['student_correctness'] * 100
    total_questions_solved = correctness_metrics['total_count']

    # calculate overall correctness using 'correctness_df' defined earlier
    overall_correct = correctness_df.filter(col("user_answer") == col("correct_answer")).count()
    total_count = correctness_df.count()
    overall_correctness = overall_correct / total_count if total_count > 0 else 0
    
    #calculate how this student's performance compared to average
    correctness_comparison = (student_correctness - overall_correctness * 100)

    # extract wrong answers with additional details & rename columsn
    wrong_answers_df = student_specific.filter(col("user_answer") != col("correct_answer")).select(
        col("question_id"),
        col("elapsed_time"),
        col("average_time_taken_on_this_q"),
        col("average_correctness_of_this_q"),
        col("user_answer").alias("student_answer"),
        col("correct_answer").alias("correct_answer")
    ).withColumn(
    "elapsed_time", col('elapsed_time')/1000
    )

    return {
        "total_questions_solved": total_questions_solved,
        "student_correctness": student_correctness,
        "correctness_comparison": correctness_comparison,
        "wrong_answers_df": wrong_answers_df
    }

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        student_id = request.form['student_id']
        print("Redirecting to dashboard with student ID:", student_id)
        print(url_for('dashboard', student_id=student_id))
        return redirect(url_for('dashboard', student_id=student_id))
    return render_template('index_student.html')

@app.route('/student/<int:student_id>')
def dashboard(student_id):
    try:
        results = analyze_student_performance(student_id)
        results['student_id'] = student_id
    except Exception as e:
        print('function error!')
        return f"An error occurred: {e}", 500
    return render_template('student.html',  results = results)


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("Pandas to Spark") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    sc = spark.sparkContext

    #check driver memory 
    print(sc._conf.get('spark.driver.memory'))
    interactions, students, lectures, questions = init_db()

    questions_df = broadcast(questions)
    correctness_df = interactions.join(questions_df, "question_id")

    # define window specification
    window_spec = Window.partitionBy("question_id")

    # add calculated columns with window functions
    correctness_df = correctness_df.withColumn(
        "average_time_taken_on_this_q",
        #convert millisecond to second
        (avg("elapsed_time").over(window_spec) / 1000)
    ).withColumn(
        "average_correctness_of_this_q",
        #use percentage
        (avg(when(col("user_answer") == col("correct_answer"), 1).otherwise(0)).over(window_spec)*100)
    )
    #for better performance
    correctness_df.cache()
    app.run(host='127.0.0.1',port=3000)
    

from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import first, avg, col, split, explode, broadcast, round
import pandas as pd
from pyspark.sql.functions import *
from flask import Flask, render_template, request, redirect, url_for
from load_data import *
from students import *

def analyze_lecture(lecture_id):

    target_lecture = lectures.filter(col("lecture_id") == lecture_id)

    exploded_correctness = question_correctness.withColumn("tag", explode(split(col("tags"), ";")))

    #lecture is much smaller than questions so use broadcast to optimize 
    broadcasted_lecture = broadcast(target_lecture)

    #join correctness df with the lecture df on tags
    related_questions = exploded_correctness.join(
        broadcasted_lecture,
        exploded_correctness.tag == broadcasted_lecture.tags,  # Joining on the single tag from lecture and exploded tags from correctness
        "inner"
    ).select(
        col("question_id").alias("Question ID"),
        round(col("average_time_taken"), 2).alias("Average Time Taken (s)"),
        round(col("average_correctness"), 2).alias("Average Correctness (%)")
    )
    
    summary = related_questions.agg(
        count("Question ID").alias("Total Associated Questions"),
        round(avg("Average Time Taken (s)"), 2).alias("Overall Average Time (s)"),
        round(avg("Average Correctness (%)"), 2).alias("Overall Average Correctness (%)")
    )

    return summary, related_questions

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        lecture_id = request.form.get('lecture_id')
        if lecture_id:
            return redirect(url_for('display_summary', lecture_id=lecture_id))
    # Assume lecture_ids are extracted properly for display
    lecture_ids = lectures.select("lecture_id").distinct().collect()
    return render_template('index_lecture.html', lecture_ids=lecture_ids)

@app.route("/summary/<lecture_id>")
def display_summary(lecture_id):
    summary_df, detailed_df = analyze_lecture(lecture_id)
    # Convert Spark DataFrames to Pandas for easier handling in HTML
    detailed_html = detailed_df.toPandas().to_html(classes="table table-striped", index=False)
    summary_html = summary_df.toPandas().to_html(classes="table table-striped", index=False)
    return render_template('lecture.html', lecture_id = lecture_id, detailed_html=detailed_html, summary_html=summary_html)


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("Pandas to Spark") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    sc = spark.sparkContext

    #check driver memory 
    print(sc._conf.get('spark.driver.memory'))
    interactions, students, lectures, questions = init_db(spark)
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
    question_correctness = correctness_df.select('question_id', 'average_time_taken_on_this_q', 'average_correctness_of_this_q', 'tags')\
                                        .groupBy('question_id')\
                                        .agg(
                                            first("tags").alias("tags"),
                                            avg("average_time_taken_on_this_q").alias("average_time_taken"),
                                            avg("average_correctness_of_this_q").alias("average_correctness")
    ).sort(['average_correctness', 'average_time_taken'], ascending=[True, False])
    app.run(host='127.0.0.1',port=5000)
    

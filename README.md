# QuizDashboard
End to end student question-solving dashboard &amp; lecture diagnosis

## Introduction
- Add your project logo.
- Write a short introduction to the project.
- If you are using badges, add them here.

## :ledger: Index

- [Business Case](#beginner-about)
- [Usage](#zap-usage)
  - [Data](#electric_plug-installation)
  - [Workflow](#package-commands)
- [Development](#wrench-development)
  - [Pre-Requisites](#notebook-pre-requisites)
  - [Developmen Environment](#nut_and_bolt-development-environment)
  - [File Structure](#file_folder-file-structure)
- [Resources](#page_facing_up-resources)
- [Gallery](#camera-gallery)
- [Credit/Acknowledgment](#star2-creditacknowledgment)
- [License](#lock-license)

# QuizDashboard

## Introduction
- ![Project Logo](path/to/logo.png)
- This project develops an end-to-end student question-solving dashboard & lecture diagnosis system, leveraging extensive student interaction data to enhance educational outcomes.

## Business Case
- **Educators**: Tailor teaching strategies based on concrete performance data to optimize learning.
- **Students**: Gain insights into their learning process, identifying strengths and areas for improvement.
- **Institutions**: Leverage data to ensure content effectiveness and uphold academic integrity.

## Data Description
- **Dataset**: EdNet-KT1, sourced from GitHub, captures over 131 million interactions from more than 780K users on the Santa platform.
- **Contents**: Includes detailed logs of user interactions with quiz questions and lectures over a span of two years, providing a comprehensive view of student learning behaviors.

## Project Workflow
- **Data Loading**: Data is loaded into a PostgreSQL database, utilizing Python scripts for efficient handling.
- **Analysis**: Apache Spark processes the data to generate insights on student performance and lecture effectiveness.
- **Visualization**: A Flask-based web application displays the results on a dynamic student dashboard.

## Usage

###  :electric_plug: Installation
- Steps on how to install this project, to use it.
- Be very detailed here, For example, if you have tools which run on different operating systems, write installation steps for all of them.

```
$ install -r requirements.py
```

Load data to postgresql database, which prompts user input for database credentials
```
$ python LoadData.py
```

Generate student dashboard: 
```
$ python spark.py
```

###  :package: Commands
- Commands to start the project.

##  :wrench: Development
If you want other people to contribute to this project, this is the section, make sure you always add this.

### :notebook: Pre-Requisites
List all the pre-requisites the system needs to develop this project.
- A tool
- B tool

###  :nut_and_bolt: Development Environment
Write about setting up the working environment for your project.
- How to download the project...
- How to install dependencies...


###  :file_folder: File Structure
Add a file structure here with the basic details about files, below is an example.

```
.
├── assets
│   ├── css
│   │   ├── index-ui.css
│   │   └── rate-ui.css
│   ├── images
│   │   ├── icons
│   │   │   ├── shrink-button.png
│   │   │   └── umbrella.png
│   │   ├── logo_144.png
│   │   └── Untitled-1.psd
│   └── javascript
│       ├── index.js
│       └── rate.js
├── CNAME
├── index.html
├── rate.html
└── README.md
```

| No | File Name | Details 
|----|------------|-------|
| 1  | index | Entry point


### :exclamation: Guideline
coding guidelines or other things you want people to follow should follow.

##  :page_facing_up: Resources
Add important resources here

##  :camera: Gallery
Pictures of your project.

## :star2: Credit/Acknowledgment
Credit the authors here.

##  :lock: License
Add a license here, or a link to it.

# Quad 2.0

## Table of Contents
- [Project Overview](#overview)
- [Setup Instructions](#setup-instructions)
- [Data Sources](#data-sources)
- [ETL Process](#etl-process)
- [Dashboards](#dashboards)

## Overview
Welcome to the code repository of Quad 2.0! This site will contain all the code used to generate the data displayed in 
the Minnesota Department of Commerce's online version of the State Energy Policy and Conservation Report.

<details>
<summary>Setup Instructions</summary>

In order to setup the project on your local computer, follow these steps:

### Prerequisites
- Install python 3.12.6: [Download here](https://www.python.org/downloads/)

### Clone the project repository
```commandline
git clone https://github.com/MN-EET/quad_2_development
```
### Create and activate your virtual environment

```commandline
python -m venv venv
```

```commandline
source venv/bin/activate
```
Install all required packages:

```commandline
pip install -r requirements.txt
```

Copy .env.example to .env:
```commandline
cp .env.example .env
```
Transfer any required API keys to .env. (For more details, see data documentation in docs).

### Folder Structure
make sure the following folders exist:
```commandline
/docs
/scripts
```


</details>

<details>
<summary>Data Sources</summary>

The project makes use of the following data sources. For detailed information about specific APIs, see API doc...

</details>
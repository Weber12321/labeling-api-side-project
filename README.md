# Labeling API v 2.1

###### v2.0 created by Weber Huang at 2021-10-07; v2.1 last updated by Weber Huang at 2021-11-11

中文專案簡報連結 : [Chinese Slides Link](slides.pptx)

#### Table of content

+ [Description](#description)
+ [Work Flow](#work-flow)
+ [Built With](#built-with)
+ [Quick Start](#quick-start)
  + [Set up docker](#set-up-docker)
  + [Set up environment](#set-up-environment)
  + [Set up database information](#set-up-database-information)
  + [Initialize the worker](#initialize-the-worker)
  + [Run the API](#run-the-api)
+ [Usage](#usage)
  + [swagger UI](#swagger-ui)
  + [create_task](#create_task)
  + [task_list](#task_list)
  + [check_status](#check_status)
  + [sample_result](#sample_result)
+ [Error code](#error-code)
+ [System Recommendation and Baseline Performance](#system-recommendation-and-baseline-performance)
+ [Appendix](#appendix)

## Description

These WEB APIs is built for the usage of data labeling tasks supporting users selecting models and rules to labeling the target range of data, and result sampling. There are four APIs in this project:

1. create_task : According to the user defined condition, set up a task flow (labeling and generate production) and execute the flow
2. task_list : return the recent executed tasks with tasks' information
3. check_status : Input a task id to check the status (label task status and generate product task status)
4. sample_result : Input a task id, return a sampling dataset back.

The total flow in brief of `create_task` is that the API will query the database via conditions and information which place by users, label those data, and output the data to a target database storing by `source_id` . The progress and validation information will be stored in the table, name `state`, inside the user define output schema which will be automatically created at the first time that user call `create_task` API.

Users can track the progress and result sampling data by calling the rest of APIs `tasks_list`, `check_status`, and `sample_result` or directly query the table `state` by giving the `task_id` information to gain such information.

## Work Flow

<img src="graph/workflow_chain.png">

## Built With

+ Develop with following tools
  + Windows 10
  + Docker
  + Redis
  + MariaDB
  + Python 3.8
  + Celery 5.1.2
  + FastAPI 0.68.1
+ Test with
  + Windows 10 Python 3.8
  + Ubuntu 18.04.5 LTS Python 3.8

## Quick Start

#### Set up docker

If you are already using docker, skip this part.

Before starting this project, we assume users have downloaded docker. About how to use docker, users may refer to [Docker Guides](https://docs.docker.com/get-started/).

#### Set up environment

Download docker version of *Redis* beforehand

```bash
$ docker run -d -p 6379:6379 redis
```

Get into the virtual environment

**Windows**

```bash
# clone the project

# get into the project folder
$ cd <your project dir>

# Setup virtual environment
# Require the python virtualenv package, or you can setup the environment by other tools 
$ virtualenv venv

# Activate environment
# Windows
$ venv\Scripts\activate

# Install packages
$ pip install -r requirements.txt
```

**Ubuntu**

```bash
# clone the project


# get into the project folder
$ cd <your project dir>

# set up the environment
$ virtualenv venv -p $(which python3.8)

# get in environment
$ source venv/bin/activate

# check the interpreter
$ which python

# install packages
$ pip install -r requirements.txt
```

> You can use `tmux` to build a background session in Linux system to deploy the celery worker, see [tmux shortcuts & cheatsheet](https://gist.github.com/MohamedAlaa/2961058), [Getting started with Tmux](https://linuxize.com/post/getting-started-with-tmux/) or [linux tmux terminal multiplexer tutorial](https://blog.gtwang.org/linux/linux-tmux-terminal-multiplexer-tutorial/) to gain more information.

#### Set up database information

Set the database environment variables information in your project root directory. Create a file, name `.env` , with some important info inside:

```bash
INPUT_HOST=<database host which you want to label>
INPUT_PORT=<database port which you want to label>
INPUT_USER=<database user info which you want to label>
INPUT_PASSWORD=<database password which you want to label>
INPUT_SCHEMA=<database schema where you want to label>
OUTPUT_HOST=<database host where you want to save output>
OUTPUT_PORT=<database port where you want to save output>
OUTPUT_USER=<database user info where you want to save output>
OUTPUT_PASSWORD=<database password where you want to save output>
OUTPUT_SCHEMA=<database schema where you want to save output>
ENV=<choose between `development` or `production`>
```

> For ENV, development is set default as localhost (127.0.0.1) while you can edit the`ProductionConfig` in `settings.py` 

#### Initialize the worker

###### Run the worker

Make sure the redis is running beforehand or you should fail to initialize celery.

**Windows**

```bash
# if you wanna run the task with coroutine
$ celery -A celery_worker worker -n worker1@%n -Q queue1 -l INFO -P gevent --concurrency=500
```

`-l` means loglevel; `-P` have to be setup as `solo` or other `evenlet` pool since default `prefork` cannot be used in the windows environment. About other pool configurations, see [workers](https://docs.celeryproject.org/en/stable/userguide/workers.html) , [Celery Execution Pools: What is it all about?](https://www.distributedpython.com/2018/10/26/celery-execution-pool/) ; `-n` represents the worker name; `-Q` means queue name, see official document [workers](https://docs.celeryproject.org/en/stable/userguide/workers.html) for more in depth explanations. Noted that in this project we assume the users will only run a single worker and single queue, if you want to run multiple workers or multiple queues, you may add it manually add the second, third, etc.

> Noted that if you only want to specify a single task, add the task name after it in the command, like `celery_worker.label_data` While in this project it is not suggested since we use the celery canvas to design the total work flow. Users **DON'T** have to edit any celery command manually.

> See [windows issue](https://stackoverflow.com/a/27358974/16810727),  [for command line interface](https://docs.celeryproject.org/en/latest/reference/cli.html) to gain more information.

**Ubuntu**

```bash
# if you wanna run the task with coroutine
$ celery -A celery_worker worker -n worker1@%n -Q queue1 -l INFO -P gevent --concurrency=500
```

According to [Celery Execution Pools: What is it all about?](https://www.distributedpython.com/2018/10/26/celery-execution-pool/) , it is suggested to configure the worker with **coroutine** (`-P gevent` or `-P eventlet`) used as I/O bound task like HTTP restful API :

> Let’s say you need to execute thousands of HTTP GET requests to fetch data from external REST APIs. The time it takes to complete a single GET request depends almost entirely on the time it takes the server to handle that request. Most of the time, your tasks wait for the server to send the response, not using any CPU.

#### Run the API

Configure the API address in `settings.py`, default address is localhost

```bash
$ python label_api.py
```

## Usage

If you have done the quick start and you want to test the API functions or expect a web-based user-interface, you can type `<api address>:<api port>/docs` in the browser (for example http://127.0.0.1:8000/docs) to open a Swagger user-interface, for more information see [Swagger](https://swagger.io/). It is very simple to use by following the quick demonstration below :

#### swagger UI

+ Type `<api address>:<api port>/docs` in the web browser, for example if you test the API at localhost `127.0.0.1/docs`

+ Open the API you want to test: 

<img src="graph/s1_d.png">

+ Edit the information

<img src="graph/s2_d.png">

+ View the result

<img src="graph/s3_d.png">

Otherwise modify  curl to calling API. Follow below parts :  

#### create_task

Input the task information for example model type, predict type, date info, etc., and return task_id with task configuration.

+ **request example :**

```shell
curl -X 'POST' \
  'http://<api address>:<api port>/api/tasks/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model_type": "keyword_model",
  "predict_type": "author_name",
  "start_time": "2020-01-01 00:00:00",
  "end_time": "2021-01-01 00:00:00",
  "target_schema": <target_db>,
  "target_table": <target_table>,
  "output_schema": <output_db>,
  "countdown": 5
}'
```

Replace your own API address with port.

Since in the demonstration of this document we only run single queue, noted that If you have multiple queues, you may add `"queue": "<your queue name>"` at the end of the request body to execute multiple tasks in the same time.

For each configuration in request body (feel free to edit them to fit your task): 

| name                    | description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| model_type              | labeling model, default is keyword_model                     |
| predict_type            | predicting target, default is author_name                    |
| start_time and end_time | the query date range                                         |
| target_schema           | the target schema where the data you want to label from      |
| target_table            | the target table under the target schema, where the data you want to label from |
| output_schema           | where you want to store the output result                    |
| countdown               | the countdown second between label task and generate_production task |

​	Noted that the default values of database are generated from the environment variables from `.env`

+ **response example :**

```json
{
    "error_code":200,
     "error_message":{
         "model_type":"keyword_model",
         "predict_type":"author",
         "start_time":"2020-01-01T00:00:00",
         "end_time":"2021-01-01T00:00:00",
         "target_schema":<target_db>,
         "target_table":<target_table>,
         "output_schema":<output_db>,
         "countdown":5,
         "queue":"queue1",
         "date_range":"2020-01-01 00:00:00 - 2021-01-01 00:00:00",
         "task_id":<task_id>
 }
}
```

Save the `task_id` if you want to directly query the task status or result after.

#### task_list

Return the recent created tasks' id with some tasks' information.

Request example :

```shell
curl -X 'GET' \
  'http://<api address>:<api port>/api/tasks/' \
  -H 'accept: application/json'
```

Replace your own API address with port

Response example :

```json
{
  "error_code": 200,
  "error_message": "OK",
  "content": [
    {
      "task_id": <task_id>,
      "stat": "PENDING",
      "prod_stat": null,
      "model_type": "keyword_model",
      "predict_type": "author",
      "date_range": "2020-01-01 00:00:00 - 2021-01-01 00:00:00",
      "target_db": <target_db>,
      "create_time": "2021-11-09T15:13:39",
      "peak_memory": null,
      "length_receive_table": null,
      "length_output_table": null,
      "length_prod_table": null,
      "result": "",
      "uniq_source_author": null,
      "rate_of_label": null,
      "run_time": null,
      "check_point": null
    },
      .
      .
      .
  ]
}
```

| name                 | description                                                  |
| -------------------- | ------------------------------------------------------------ |
| task_id              | task id                                                      |
| stat                 | status of labeling task (*PENDING, SUCCESS, FAILURE*)        |
| prod_stat            | status of generate production task (*finish* or *null*)      |
| model_type           | model used by labeling                                       |
| predict_type         | predict target                                               |
| date_range           | users define date range of create_task                       |
| target_table         | target schema which query for labeling                       |
| create_time          | task starting datetime                                       |
| ~~peak_memory~~      | ~~trace the max memory of each labeling task~~ *This function is expired and out of usage in this version* |
| length_receive_table | the number of data from target_table                         |
| length_output_table  | the number of result after labeling                          |
| length_prod_table    | the number of result after generate production               |
| result               | the temp result table of labeling task                       |
| uniq_source_author   | for each task, the unique `source_id` , `author` from their data source (only use for calculating rate_of_label) |
| rate_of_label        | percentage of length of result generated by generate_production divided by uniq_source_author |
| check_point          | if the labeling task is failed, save the batch number (datetime) for last execution |

#### check_status

`/api/tasks/{task_id}` 

Return the task status (*PENDING, SUCCESS, FAILURE*) and prod_status (*finish* or *Null*) via task id, if the task is *SUCCESS* return result (temp result table_name) too.

Request example :

```shell
curl -X 'GET' \
  'http://<api address>:<api port>/api/tasks/<task_id>' \
  -H 'accept: application/json'
```

Response example :

````json
{
  "error_code": 200,
  "error_message": "OK",
  "status": "SUCCESS",
  "prod_status": "finish",
  "result": <result_table_name>
}
````

| name        | description                                                  |
| ----------- | ------------------------------------------------------------ |
| status      | status of label task (*PENDING, SUCCESS, FAILURE*)           |
| prod_status | status of generate production task (*finish* or *null*)      |
| result      | temp result table name of label task in output schema, if generate production is finished the result will be store in `wh_panel_mapping_{result}` in the same output schema |

#### sample_result

> before calling sample_result, finish check_status first and make sure the `prod_status` is mark as `finish` (generate product task is finished)

`/api/tasks/{task_id}/sample/` 

Input task id (execute this only if <u>prod_status</u> is `finish`, otherwise you will receive task error code `500` with error message `table is not exist`), return the sampling results from result tables.

Request example :

```shell
curl -X 'GET' \
  'http://<api address>:<api port>/api/tasks/<task_id>/sample/' \
  -H 'accept: application/json'
```

Response example :

````json
{
  "error_code": 200,
  "error_message": [
    {
      "id": <id>,
      "task_id": <task_id>,
      "source_author": <source_id_match_content>,
      "panel": "/female",
      "create_time": "2020-01-01T00:00:03",
      "field_content": <source_id>,
      "match_content": <match_content>
    },
      .
      .
      .
  ]
}
````

| Column        | Description                               |
| ------------- | ----------------------------------------- |
| id            | Row id from original data                 |
| task_id       | Labeling task id                          |
| source_author | Combine the s_id with author_name         |
| panel         | Result of labeling                        |
| create_time   | Post_time                                 |
| field_content | s_id                                      |
| match_content | The content which is matched to labeling. |

## Error code 

Error code in this project is group by <u>API task error code</u> and <u>HTTP error code</u> : 

**API task error code**

+ create_task

  code 200 represent successful

  | error_code | error_message                                                |
  | ---------- | ------------------------------------------------------------ |
  | 200        | task configuration with `task_id`                            |
  | 400        | start_time must be earlier than end_time                     |
  | 500        | failed to start a labeling task, additional error message: <Exception> |
  | 501        | Cannot read pattern file, probably unknown file path or file is not exist, additional error message: <Exception> |
  | 503        | Cannot connect to output schema, additional error message: <Exception> |

+ tasks_list

  code 200 represent successful

  | error_code | error_message                 |
  | ---------- | ----------------------------- |
  | 200        | OK                            |
  | 500        | cannot connect to state table |

+ check_status

  code 200 represent successful

  | error_code | error_message                                                |
  | ---------- | ------------------------------------------------------------ |
  | 200        | OK                                                           |
  | 400        | task id is not exist, plz re-check the task id. Addition error message: <Exception> |

+ sample_result

  code 200 represent successful

  | error_code | error_message                                                |
  | ---------- | ------------------------------------------------------------ |
  | 200        | sampling result                                              |
  | 400        | <task_id> is not in proper format, expect 32 digits get <length of task_id> digits |
  | 404        | empty result, probably wrong combination of task_id and table_name, please check table state or use /api/tasks/<task_id> first |
  | 500        | Cannot scrape data from result tables. Additional error message: <Exception> |

**HTTP error code**

| Error code | error_message       | description                                                  |
| ---------- | ------------------- | ------------------------------------------------------------ |
| 200        | Successful Response | API successfully receive the required information            |
| 422        | Validation Error    | API doesn't receive the proper information. This problem usually occurs in <u>wrong format of request body</u> at users post a create_task API |



## System Recommendation and Baseline Performance

**System Recommendation**

+ System : Ubuntu 18.04.5 LTS (Recommended) or Windows 10 (Noted the multiprocessing issue of celery in WIN10 )
+ Python environment : Python 3.8

+ Processor : Intel(R) Core(TM) i5-8259U + or other processor with same efficiency

+ RAM : 16G +

**Baseline Performance**

+ Data size : 39,291,336 row
+ Predict model : keyword_base model  
+ Finished time : 149.378 minutes  
+ Max memory usage(maximum resident set size ) :   812.38 Mb



## Appendix

**Problem of celery multiprocessing (Unsolved)**

```bash
[2021-11-09 09:03:32,151: ERROR/ForkPoolWorker-7] Task celery_worker.label_data[db5f76cc40f811ecb688d45d6456a14d] raised unexpected: AssertionError('daemonic processes are not allowed to have children')
Traceback (most recent call last):
  File "/home/deeprd2/audience-api/venv/lib/python3.8/site-packages/celery/app/trace.py", line 450, in trace_task
    R = retval = fun(*args, **kwargs)
  File "/home/deeprd2/audience-api/venv/lib/python3.8/site-packages/celery/app/trace.py", line 731, in __protected_call__
    return self.run(*args, **kwargs)
  File "/home/deeprd2/audience-api/utils/worker_core.py", line 15, in measure_task
    mem_usage, result = memory_usage(
  File "/home/deeprd2/audience-api/venv/lib/python3.8/site-packages/memory_profiler.py", line 330, in memory_usage
    p.start()
  File "/usr/lib/python3.8/multiprocessing/process.py", line 118, in start
    assert not _current_process._config.get('daemon'), \
AssertionError: daemonic processes are not allowed to have children
```

The problem is due to the memory tracking decorator from `utils/worker_core.py` used by `celery_woker.py` : 

```python
@celery_app.task(name=f'{name}.label_data', track_started=True)
@memory_usage_tracking # this line
def label_data(task_id: str, **kwargs) -> List[str]:
```

It seems that the problem is cause by the python memory tracing module, `memory_profiler`, which uses the build-in python multiprocessing module. While in local environment (windows10) configure the pooling strategy with celery command `-P solo`, it is fine. The problem occurs when deploys the project to remote Linux using multiprocessing default pooling `-P prefork`.

In [Celery Execution Pools: What is it all about?](https://www.distributedpython.com/2018/10/26/celery-execution-pool/) it says : 

> The prefork pool implementation is based on Python’s [multiprocessing](https://docs.python.org/dev/library/multiprocessing.html#module-multiprocessing) package. It allows your Celery worker to side-step [Python’s Global Interpreter Lock](https://docs.python.org/dev/glossary.html#term-global-interpreter-lock) and fully leverage multiple processors on a given machine.

Some cases of similar issues with celery multiprocessing at official Git hub : 

[Tasks are not allowed to start sub processes](https://github.com/celery/celery/issues/1709) 

[daemonic processes are not allowed to have children](https://github.com/celery/celery/issues/4525)

Ok, it seems that the problem is about python multiprocessing module (`-P prefork`), there is nothing wrong currently by switching `-P prefork` to `-P threads` under the ubuntu environment.

So how about using `eventlet` or `gevent`? with a multiprocessing module, they will all fail. I still cannot figure out any clue about this problem, the current way is to disable the memory track decorator, since it is not directly related to the project goal. 


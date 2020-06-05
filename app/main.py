import os
import json

from fastapi import FastAPI, Path, Body
from enum import Enum 
from motor.motor_asyncio import AsyncIOMotorClient

import credentials
import survey


MDBCSTR = credentials.MDB_CONNECTION_STRING


# create fastapi app
app = FastAPI()

# connect to mongodb via motor
motor_client = AsyncIOMotorClient(MDBCSTR)
db = motor_client['async_survey_database']


def create_surveys(db):
    """Read survey configuration files and translate them to survey objects."""
    surveys = []
    folder = os.path.join(os.path.dirname(__file__), 'surveys')
    for path in os.listdir(folder):
        with open(os.path.join(folder, path), 'r') as configuration:
            surveys.append(
                survey.Survey(
                    identifier=path[:-5],
                    database=db,
                    configuration=json.load(configuration),
                )
            )
    return {sv.id: sv for sv in surveys}


# create survey objects from configuration files
surveys = create_surveys(db)
SurveyName = Enum('SurveyName', {k: k for k in surveys.keys()}, type=str)


@app.get('/', tags=['status'])
async def status():
    """Verify if database and mailing services are operational"""
    try:
        await motor_client.server_info()
        # TODO add test for sending emails
    except:
        return {'status': 'database error'}
    else:
        return {'status': 'all services operational'}


@app.post('/{survey}/submit', tags=['survey'])
async def submit(
        survey: SurveyName = Path(
            ...,
            description='The identification tag of the survey',
        ),
        submission: dict = Body(
            ...,
            description='The user submission for the survey',
        )
    ):
    """Validate submission and store it under pending submissions"""
    return await surveys[survey].submit(submission)


@app.get('/{survey}/verify/{token}', tags=['survey'])
async def verify(
        survey: SurveyName = Path(
            ...,
            description='The identification tag of the survey',
        ),
        token: str = Path(
            ...,
            description='The verification token',
        ),
    ):
    """Verify user token and either fail or redirect to success page"""
    return await surveys[survey].verify(token)


@app.get('/{survey}/results', tags=['survey'])
async def results(
        survey: SurveyName = Path(
            ...,
            description='The identification tag of the survey',
        ),
    ):
    """Fetch the results of the given survey"""
    return await surveys[survey].fetch()

import os

from fastapi import FastAPI, Path, Body, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from app.mailing import Letterbox
from app.admin import AdminManager
from app.survey import SurveyManager


# dev / production environment
ENV = os.getenv('ENV')
# MongoDB connection string
MDBCS = os.getenv('MDBCS')


# create fastapi app
app = FastAPI()
# connect to mongodb via pymongo and motor
motor_client = AsyncIOMotorClient(MDBCS)
# get link to dev / production database
database = motor_client[ENV]
# create email client
letterbox = Letterbox()
# instantiate admin manager
admin_manager = AdminManager(database)
# instantiate survey manager
survey_manager = SurveyManager(database, letterbox)


@app.get('/{admin_name}')
async def get_admin(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
    ):
    """Fetch data about the given admin."""
    return await admin_manager.fetch(admin_name)


@app.get('/{admin_name}/{survey_name}')
async def get_survey(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
        survey_name: str = Path(
            ...,
            description='The name of the survey',
        ),
    ):
    """Fetch the configuration document of the given survey."""
    survey = await survey_manager.fetch(admin_name, survey_name)
    return survey.configuration


@app.post('/{admin_name}/{survey_name}')
async def post_survey(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
        survey_name: str = Path(
            ...,
            description='The name of the survey',
        ),
        configuration: dict = Body(
            ...,
            description='The configuration for the new survey',
        ),
    ):
    """Create new survey with given configuration."""
    raise HTTPException(501, 'not implemented')


@app.delete('/{admin_name}/{survey_name}')
async def delete_survey(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
        survey_name: str = Path(
            ...,
            description='The name of the survey',
        ),
    ):
    """Delete given survey and all its data (submissions, results, ...)."""
    raise HTTPException(501, 'not implemented')


@app.post('/{admin_name}/{survey_name}/submission')
async def submit(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
        survey_name: str = Path(
            ...,
            description='The name of the survey',
        ),
        submission: dict = Body(
            ...,
            description='The user submission for the survey',
        ),
    ):
    """Validate submission and store it under pending submissions."""
    survey = await survey_manager.fetch(admin_name, survey_name)
    return await survey.submit(submission)


@app.get('/{admin_name}/{survey_name}/verification/{token}')
async def verify(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
        survey_name: str = Path(
            ...,
            description='The name of the survey',
        ),
        token: str = Path(
            ...,
            description='The verification token',
        ),
    ):
    """Verify user token and either fail or redirect to success page."""
    survey = await survey_manager.fetch(admin_name, survey_name)
    return await survey.verify(token)


@app.get('/{admin_name}/{survey_name}/results')
async def aggregate(
        admin_name: str = Path(
            ...,
            description='The name of the admin',
        ),
        survey_name: str = Path(
            ...,
            description='The name of the survey',
        ),
    ):
    """Fetch the results of the given survey."""
    survey = await survey_manager.fetch(admin_name, survey_name)
    return await survey.aggregate()

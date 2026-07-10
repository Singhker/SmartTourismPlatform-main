import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///database/tourism_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

    # Dataset paths
    DATASET_DIR = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'datasets')

    # App settings
    APP_NAME = 'Smart Tourism Data Curation Platform'
    ITEMS_PER_PAGE = 20
    ITEMS_PER_PAGE = 12  # For places page

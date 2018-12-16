import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns');
    topic = sns.Topic('arn:aws:sns:ap-southeast-2:631496266623:DeployPortfolioTopic')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.contactcentre.guru')
        build_bucket = s3.Bucket('fairall-lab-bucket')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Portfolio Deployed", Message="The portfolio has been deployed successfully.")
    except:
        topic.publish(Subject="Portfolio NOT Deployed", Message="The portfolio has NOT been deployed successfully.")
        raise

    return "Hello from Lambda!"

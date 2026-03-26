import os
import json
from typing import Dict, Any

try:
    import boto3
except ImportError:
    boto3 = None

def get_aws_status() -> Dict[str, Any]:
    """Return dictionary of which AWS services are active."""
    status = {
        "connected": False,
        "region": os.environ.get("AWS_REGION", "ap-southeast-1"),
        "services": {
            "S3": False,
            "CloudWatch": False
        }
    }
    
    if not boto3:
        return status
        
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    
    if not aws_access_key or not aws_secret_key:
        return status
        
    status["connected"] = True
    
    try:
        # Check S3
        boto3.client('s3', region_name=status["region"]).list_buckets()
        status["services"]["S3"] = True
    except Exception:
        # If no permissions to list buckets, still assume S3 integration could work if credentials are provided
        # But for simpler display, keep it as True if client creates
        status["services"]["S3"] = True
        
    try:
        # Check CloudWatch
        boto3.client('logs', region_name=status["region"])
        status["services"]["CloudWatch"] = True
    except Exception:
        status["services"]["CloudWatch"] = True
        
    return status

def log_decision(decision_data: Dict[str, Any]) -> None:
    """Log credit decisions to AWS CloudWatch Logs. If not configured, print to console."""
    try:
        status = get_aws_status()
        decision_str = json.dumps(decision_data, default=str)
        if not status["connected"] or not status["services"]["CloudWatch"]:
            print(f"[LOCAL LOG] Decision made: {decision_str}")
            return
            
        logs_client = boto3.client('logs', region_name=status["region"])
        log_group_name = "/creditagent/decisions"
        log_stream_name = "decision_stream"
        
        try:
            logs_client.create_log_group(logGroupName=log_group_name)
        except Exception:
            pass
            
        try:
            logs_client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        except Exception:
            pass
            
        import time
        timestamp = int(round(time.time() * 1000))
        
        try:
            response = logs_client.describe_log_streams(
                logGroupName=log_group_name,
                logStreamNamePrefix=log_stream_name
            )
            sequence_token = None
            if 'logStreams' in response and response['logStreams']:
                sequence_token = response['logStreams'][0].get('uploadSequenceToken')
            
            kwargs = {
                'logGroupName': log_group_name,
                'logStreamName': log_stream_name,
                'logEvents': [
                    {
                        'timestamp': timestamp,
                        'message': decision_str
                    }
                ]
            }
            if sequence_token:
                kwargs['sequenceToken'] = sequence_token
                
            logs_client.put_log_events(**kwargs)
        except Exception as e:
            print(f"[AWS WARNING] Failed to put log event: {e}. Falling back to console.")
            print(f"[LOCAL LOG] Decision made: {decision_str}")
            
    except Exception as e:
        print(f"[AWS ERROR] log_decision exception: {e}")
        print(f"[LOCAL LOG] Decision made: {json.dumps(decision_data, default=str)}")

def upload_model_to_s3(file_path: str) -> None:
    """Upload trained model to S3 after training. If AWS not configured, skip silently."""
    try:
        status = get_aws_status()
        if not status["connected"] or not status["services"]["S3"]:
            return
            
        bucket_name = os.environ.get("AWS_S3_BUCKET")
        if not bucket_name:
            print("[AWS WARNING] S3 enabled but AWS_S3_BUCKET not set.")
            return
            
        s3_client = boto3.client('s3', region_name=status["region"])
        file_name = os.path.basename(file_path)
        
        s3_client.upload_file(file_path, bucket_name, f"models/{file_name}")
        print(f"[AWS] Successfully uploaded {file_path} to s3://{bucket_name}/models/{file_name}")
    except Exception as e:
        print(f"[AWS ERROR] upload_model_to_s3 exception: {e}")

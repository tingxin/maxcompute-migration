
import os
import argparse
from tools import conf, unload

def main():
    parser = argparse.ArgumentParser(description='MaxCompute data migration tool')
    parser.add_argument('--job-name', '-j', 
                      type=str, 
                      default='default_job',
                      help='Name of the unload job')
    
    args = parser.parse_args()
    
    # Load environment variables
    conf.load_env()
    
    # Get table names from environment
    table_names = os.getenv("TABLE_NAME").split(",")
    
    # Run the unload job with specified job name
    unload.run(args.job_name, table_names)

if __name__ == "__main__":
    main()

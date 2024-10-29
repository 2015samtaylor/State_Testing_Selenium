import pandas as pd
import pysftp
import logging
import time
import os
from queue import Queue
from threading import Lock
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

def clear_logging_handlers():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


class SFTPConnection:
    default_cnopts = pysftp.CnOpts()
    default_cnopts.hostkeys = None

    def __init__(self, host, username, password, max_connections=5, use_pool=True, cnopts=None):
        self.host = host
        self.username = username
        self.password = password
        self.max_connections = max_connections
        self.use_pool = use_pool
        self.cnopts = cnopts or self.default_cnopts
        if use_pool:
            self.pool = Queue(max_connections)
            self.lock = Lock()
            self._initialize_pool()
        else:
            self.pool = None
            self.lock = None

    def _initialize_pool(self):
        for _ in range(self.max_connections):
            self.pool.put(self._create_new_connection())

    def _create_new_connection(self):
        return pysftp.Connection(
            host=self.host,
            username=self.username,
            password=self.password,
            cnopts=self.cnopts
        )

    def get_connection(self):
        if self.use_pool:
            with self.lock:
                if self.pool.empty():
                    return self._create_new_connection()
                return self.pool.get()
        else:
            return self._create_new_connection()

    def return_connection(self, conn):
        if self.use_pool:
            with self.lock:
                if self.pool.full():
                    conn.close()
                else:
                    self.pool.put(conn)
        else:
            conn.close()

    def close_all_connections(self):
        if self.use_pool:
            while not self.pool.empty():
                conn = self.pool.get()
                conn.close()
                logging.info('SFTP connection closed')




def replicate_SFTP_files_to_local(sftp, sftp_folder_name, local_folder_name):
    os.makedirs(local_folder_name, exist_ok=True)

    try:
        sftp.chdir(sftp_folder_name)
        dir_contents = sftp.listdir()
        logging.info(f'Dir contents of {sftp_folder_name}: {dir_contents}')

        if not dir_contents:
            logging.info(f'No files to download in folder "{sftp_folder_name}".')
            return

        for file_name in dir_contents:
            remote_file_path = os.path.join(sftp_folder_name, file_name)
            local_file_path = os.path.join(local_folder_name, file_name)

            logging.info(f'Trying to download remote file: {remote_file_path} to local path: {local_file_path}')
            print(f'Trying to download remote file: {remote_file_path} to local path: {local_file_path}')

            sftp.get(file_name, local_file_path)
            logging.info(f'File "{file_name}" downloaded to local directory "{local_file_path}"')

        logging.info(f'All files in folder "{sftp_folder_name}" downloaded to local directory "{local_folder_name}"')

    except Exception as e:
        logging.error(f'An error occurred during file replication: {e}')




def SFTP_export_files_to_SFTP(specific_files, remote_dir, sftp):
    """
    Upload specific files to the remote directory via SFTP.

    :param specific_files: List of local file paths to upload.
    :param remote_dir: Remote directory path on the SFTP server.
    :param sftp: SFTP connection object.
    """
    # Establish a new connection
    conn = sftp._create_new_connection()
    logging.info('\n\nSFTP singular connection established successfully')

    for local_path in specific_files:
        # Ensure the specified file exists
        if not os.path.exists(local_path):
            print(f"File not found: {local_path}")
            logging.error(f"File not found: {local_path}")
            continue

        # Get the relative path and prepare remote path
        relative_path = os.path.basename(local_path)
        remote_path = os.path.join(remote_dir, relative_path).replace('\\', '/')

        # Print and log paths for debugging
        print(f"Local path: {local_path}")
        print(f"Remote path: {remote_path}")
        logging.info(f"Local path: {local_path}")
        logging.info(f"Remote path: {remote_path}")

        # Upload the file
        try:
            conn.put(local_path, remote_path)
            print(f"Uploaded {local_path} to {remote_path}")
            logging.info(f"Uploaded {local_path} to {remote_path}")
        except Exception as e:
            print(f"Error uploading {local_path} to {remote_path}: {str(e)}")
            logging.error(f"Error uploading {local_path} to {remote_path}: {str(e)}")

    # Close the connection after the operation
    conn.close()
    logging.info('SFTP singular connection closed')

# def main():
#     local_dir = '/path/to/local/directory'
#     remote_dir = '/path/to/remote/directory'
#     host = 'your_remote_host'
#     username = 'your_username'
#     password = 'your_password'


#         sftp_copy_dir(local_dir, remote_dir, sftp)

# if __name__ == "__main__":
#     main()









#SSH tunneling example for CustomPlanet
# from sshtunnel import SSHTunnelForwarder
# import pymysql

# # Establish SSH tunnel
# with SSHTunnelForwarder(
#     (ssh_host, ssh_port),
#     ssh_username=ssh_username,
#     ssh_password=ssh_password,
#     remote_bind_address=(mysql_host, mysql_port),
# ) as tunnel:
#     print(f'Tunnel local bind port: {tunnel.local_bind_port}')
#     print(f'Tunnel is active: {tunnel.is_active}')

#     # Connect to MySQL through the tunnel
#     conn = pymysql.connect(
#         host=mysql_host,
#         port=tunnel.local_bind_port,
#         user=mysql_username,
#         password=mysql_password,
#         database='opencartdb',
#         connect_timeout=30,  # Increase the connection timeout
#     )

#     orders = '''
#             SELECT order_id, firstname, lastname, email, telephone, payment_city, payment_zone, payment_country, payment_method, 
#             shipping_address_1, shipping_city, shipping_country, total, date_added, date_modified, design_file,
#             shipping_date FROM oc_order
#             '''
    
#     order_product = '''
#             SELECT order_product_id, order_id, product_id, name, model, quantity, price, total FROM oc_order_product

#                      '''
    
#     just_product = '''
#             SELECT product_id, what, image FROM oc_product

#     '''    
    

#     orders = pd.read_sql_query(orders, conn)
#     order_product = pd.read_sql_query(order_product, conn)
#     just_product = pd.read_sql_query(just_product, conn)

#     try:
#         conn.close()
#         print('conn is closed')
#     except:
#         print('conn still open')